from typing import Sequence
import chromadb
from chromadb import Collection
from chromadb import QueryResult
from genome_rag.snpedia.snpedia import SNPedia
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

        for i in tqdm(range(0, len(variant_ids)), desc="Adding new SNPedia pages"):
            id = variant_ids[i]
            # Fetch and add pages for the current id
            page = wiki.get_page_text(id)
            print(id)

            # We dont need to add full text and text of page to vectordb
            # metadata, as it will be used in model context construction
            # instead we will keep it in our sqlite db for future reference.
            vectorbd_metadata = page.metadata.copy()
            vectorbd_metadata.pop("text", None)
            vectorbd_metadata.pop("raw_content", None)

            if page.text != "":
                self.vectors.add(
                    ids=[id],
                    documents=[page.text], # Use page.text
                    metadatas=[vectorbd_metadata] # type: ignore
                )
            
            db.snpediapage.create(
                data={
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
            )
        
        db.disconnect()

    def query(self, query: str, top_n: int = 10, ids = None) -> QueryResult:
        return self.vectors.query(
            query_texts=[query],
            n_results=top_n,
            ids = ids,
            where_document={"$contains" : "a"} # this is used to filter out empty documents
        )