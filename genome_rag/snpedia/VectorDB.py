from typing import Sequence
import chromadb
from chromadb import Collection
from chromadb import QueryResult
from genome_rag.snpedia.snpedia import Metadata, SNPedia
from tqdm import tqdm # Import tqdm
from genome_rag.genotypes.Genotype import VariantId

from prisma import Prisma

class VectorDB:
    """
    Acts as a vector storage for snpedia rsid variant pages.
    """

    #vectors for snpedia pages
    vectors: Collection

    def __init__(self):
        chroma_client = chromadb.PersistentClient(path="data/chroma")
        self.vectors = chroma_client.get_or_create_collection(name="snpedia")


    def add_snps_to_db_if_not_added(self, variant_ids: list[str]):
        """
        Get a list of variant ids. If those variant ids are not already added to db, add them.
        There is two dbs, one for snpedia scraped cache. One for vector storage and search.
        """

        db = Prisma()
        db.connect()

        # Process variant_ids in slices due to computational constraints
        slice_size = 1000

        non_existent_ids = set()
        print(f"VectorDB: Checking for existing variants in batches of {slice_size}.")

        for i in tqdm(range(0, len(variant_ids), slice_size), desc="Checking existing SNPedia pages"):
            
            var_ids_current_slice = variant_ids[i:i + slice_size]

            existing_variants = db.snpediapage.find_many(
                where={
                    "variant_id": {
                        "in": var_ids_current_slice
                    }
                }
            )

            existing_var_ids = [x.variant_id for x in existing_variants]

            non_existent_ids.update(set(var_ids_current_slice) - set(existing_var_ids))

        db.disconnect()

        if non_existent_ids:
            print(f"VectorDB: Adding {len(non_existent_ids)} new variants.")
            self._add_new_pages_to_db(list(non_existent_ids))
        else:
            print(f"VectorDB: All required variants exist in DB.")




    def _add_new_pages_to_db(self, variant_ids: list[str]):
        wiki = SNPedia()
        db = Prisma()
        db.connect()

        slice_size = 2
        for i in tqdm(range(0, len(variant_ids), slice_size), desc="Adding new SNPedia pages to db"):
            
            var_ids_current_slice = variant_ids[i:i + slice_size]
            
            pages_slice = []
            embedding_pages = []
            embedding_pages_ids = []
            for id in tqdm(var_ids_current_slice, desc="Fetching SNPedia pages"):
                page = wiki.get_page_text(id)
                pages_slice.append(page)
                if page.text != "":  # Only add non-empty pages
                    embedding_pages.append(page)
                    embedding_pages_ids.append(id)

            # We dont need to add full text and text of page to vectordb
            # metadata, as it will be used in model context construction
            # instead we will keep it in our sqlite db for future reference.
            def remove_text_and_raw_content_from_metadata(metadata: Metadata):
                metadata.pop("text", None)
                metadata.pop("raw_content", None)
                return metadata
            
            vectorbd_metadatas = [remove_text_and_raw_content_from_metadata(page.metadata.copy()) for page in embedding_pages]

            embedding_pages_texts = [page.text for page in embedding_pages]

            #only add if current slice has any valid embedding worthy pages
            if embedding_pages_ids:
                self.vectors.add(
                    ids=embedding_pages_ids,
                    documents=embedding_pages_texts, # Use page.text
                    metadatas=vectorbd_metadatas # type: ignore
                )

            #all pages will be added to the db
            
            db.snpediapage.create_many(
                data=[
                    {
                        "variant_id": id,
                        "summary": page.metadata.get("Summary", ""), # Use .get for safety
                        "assembly": page.metadata.get("Assembly", ""),
                        "orientation": page.metadata.get("Orientation", ""),
                        "stabilizedOrientation": page.metadata.get("StabilizedOrientation", ""),
                        "geno1": page.metadata.get("geno1", ""),
                        "geno1_summary": page.metadata.get("geno1_summary", ""), # Add new field
                        "geno2": page.metadata.get("geno2", ""),
                        "geno2_summary": page.metadata.get("geno2_summary", ""), # Add new field
                        "geno3": page.metadata.get("geno3", ""),
                        "geno3_summary": page.metadata.get("geno3_summary", ""), # Add new field
                        "text": page.text, # Use page.text for the text field
                        "raw_content": page.metadata.get("raw_content", ""), # Add new field
                    }
                    for id, page in zip(var_ids_current_slice, pages_slice)
                ] # type: ignore
            ) 
        
        db.disconnect()

    def query(self, query: str, variant_ids: list[str], top_n: int = 10, ) -> QueryResult:

        #filter variant ids by those in the db, so we dont get too many sql objects error


        existing_vars = set(self.vectors.get(include=[])["ids"])
        common = set(variant_ids).intersection(existing_vars)
        variant_ids_common = list(common)

        return self.vectors.query(
            query_texts=[query],
            n_results=top_n,
            ids = variant_ids_common
        )