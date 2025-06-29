import chromadb
from chromadb import Collection
from chromadb import QueryResult
from genome_rag.snpedia.snpedia import SNPedia
from tqdm import tqdm # Import tqdm


class VectorDB:
    """
    Acts as a vector storage for snpedia rsid variant pages.
    """
    
    pages: Collection

    def __init__(self):
        chroma_client = chromadb.PersistentClient(path="data/chroma")
        self.pages = chroma_client.get_or_create_collection(name="snpedia")

    def add_snps_to_db_if_not_added(self, variant_ids: list[str]):
        existing_pages = self.pages.get(ids=variant_ids)
        existing_ids = set(existing_pages["ids"])
        non_existent_ids = set(variant_ids) - existing_ids
        if non_existent_ids:
            print(f"VectorDB: Adding these new variants: {variant_ids}.")
            self._add_new_pages_to_db(non_existent_ids)
        else:
            print(f"VectorDB: All required variants exist in DB.")


    def _add_new_pages_to_db(self, variant_ids: set[str]):
        wiki = SNPedia()
        # Wrap the loop with tqdm for a progress bar
        for id in tqdm(variant_ids, desc="Adding new SNPedia pages"):
            page = wiki.get_page_text(id)
            self.pages.add(
                ids=[id],
                documents=[page.content],
                metadatas=[(page.metadata)] # type: ignore
            )

    def query(self, query: str, top_n: int = 10) -> QueryResult:
        return self.pages.query(
            query_texts=[query],
            n_results=top_n,
        )