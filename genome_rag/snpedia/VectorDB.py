from typing import Sequence
import chromadb
from chromadb import Collection
from chromadb import QueryResult
from genome_rag.snpedia.snpedia import SNPedia
from tqdm import tqdm # Import tqdm
from genome_rag.genotypes.Genotype import VariantId



class VectorDB:
    """
    Acts as a vector storage for snpedia rsid variant pages.
    """

    pages: Collection

    def __init__(self):
        chroma_client = chromadb.PersistentClient(path="data/chroma")
        self.pages = chroma_client.get_or_create_collection(name="snpedia")

    def add_snps_to_db_if_not_added(self, variant_ids: list[str]):
        # Process variant_ids in slices of 100
        slice_size = 100
        non_existent_ids = set()
        print(f"VectorDB: Checking for existing variants in batches of {slice_size}.")

        for i in tqdm(range(0, len(variant_ids), slice_size), desc="Checking existing SNPedia pages"):
            current_slice = variant_ids[i:i + slice_size]
            existing_pages = self.pages.get(ids=current_slice)
            existing_ids = set(existing_pages["ids"])
            non_existent_ids.update(set(current_slice) - existing_ids)

        if non_existent_ids:
            print(f"VectorDB: Adding these new variants: {list(non_existent_ids)}.")
            self._add_new_pages_to_db(non_existent_ids)
        else:
            print(f"VectorDB: All required variants exist in DB.")


    def _add_new_pages_to_db(self, variant_ids: set[str]):
        wiki = SNPedia()
        # Wrap the loop with tqdm for a progress bar
        # Process adding in batches as well, although get_page_text is one by one
        slice_size = 100
        variant_ids_list = list(variant_ids) # Convert set to list for slicing
        for i, id in tqdm(enumerate(variant_ids_list), desc="Adding new SNPedia pages"):
            # Fetch and add pages for the current id
            page = wiki.get_page_text(id)
            self.pages.add(
                ids=[id],
                documents=[page.content],
                metadatas=[(page.metadata)] # type: ignore
            )

    def query(self, query: str, top_n: int = 10, ids = None) -> QueryResult:
        return self.pages.query(
            query_texts=[query],
            n_results=top_n,
            ids = ids,
            where_document={"$contains" : "a"} # this is used to filter out empty documents
        )