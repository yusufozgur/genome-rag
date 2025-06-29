from google import genai
from google.genai import types
from google.genai.chats import Chat
from genome_rag.genotypes.Genotype import Genotype
from genome_rag.snpedia.VectorDB import VectorDB
class LLM:

    chat: Chat
    db: VectorDB
    variant_ids: list[str]
    user_genotypes: dict[str, Genotype]
    top_n: int

    system_prompt = """<System>
        You are a helpful assistant helping people interpret their genotyping results.
        Your context will include snpedia articles that have been retrieved due to their relevance.
        Use the provided context to answer questions.
        Context is provided as json. Object ids are variant ids. Document is the text in the SNPedia page. Metadata contains technical information regarding the variant.
        If applicable, you can start by summarizing which articles were retrieved due to user's query, then answer the user.
        While talking about articles in snpedia, give links in the format of "https://www.snpedia.com/index.php/<rsid>"
        </System>"""

    def __init__(self, db: VectorDB, api_key, variant_ids: list[str], user_genotypes: dict[str, Genotype], top_n: int):
        client = genai.Client(
            api_key=api_key
        )
        
        self.chat = client.chats.create(
            model="gemini-2.5-flash",
            )

        self.db = db
        self.top_n = top_n
        self.variant_ids = variant_ids
        self.user_genotypes = user_genotypes

    def _vector_search(self, query: str):
        rag_close_vectors = self.db.query(query, ids = self.variant_ids, top_n=self.top_n)
        #manipulate response into a correct format
        context = {
            id: {
            "document": rag_close_vectors["documents"][0][i], # type: ignore
            "metadata": rag_close_vectors["metadatas"][0][i], # type: ignore
            "users_genotype": str(self.user_genotypes[id]),
            "vector_search_distance": rag_close_vectors["distances"][0][i],
            } 
            for i, id in enumerate(rag_close_vectors["ids"][0])
        }

        return context, rag_close_vectors
    
    def _get_context_prompt(self, context):
        return f"""
        <Context>
        {str(context)}
        </Context>
        """

    def send_message(self, msg: str):

        msg=f"""
        <User>
        User's question: {msg}
        </User>
        """

        context, rag_close_vectors = self._vector_search(msg)
        
        response = self.chat.send_message(
            msg,
            config=types.GenerateContentConfig(
                system_instruction = f"{self.system_prompt}\n{self._get_context_prompt(context)}",
                )
        )
        
        return response.text, context