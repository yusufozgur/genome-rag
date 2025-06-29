from google import genai
from google.genai import types
from google.genai.chats import Chat
from genome_rag.snpedia.VectorDB import VectorDB
class LLM:

    chat: Chat
    db: VectorDB
    variant_ids: list[str]

    system_prompt = """<System>
        You are a helpful assistant helping people interpret their genotyping results.
        Your context will include snpedia articles that have been retrieved due to their relevance.
        Use the provided context to answer questions.
        Context is provided as json. Object ids are variant ids. Document is the text in the SNPedia page. Metadata contains technical information regarding the variant.
        </System>"""

    def __init__(self, db: VectorDB, api_key, variant_ids: list[str]):
        client = genai.Client(
            api_key=api_key
        )
        
        self.chat = client.chats.create(
            model="gemini-2.5-flash",
            )

        self.db = db

        self.variant_ids = variant_ids

    def _vector_search(self, query: str):
        rag_close_vectors = self.db.query(query, ids = self.variant_ids)
        #manipulate response into a correct format
        context = {
            id: {
            "document": rag_close_vectors["documents"][0][i], # type: ignore
            "metadata": rag_close_vectors["metadatas"][0][i], # type: ignore
            } 
            for i, id in enumerate(rag_close_vectors["ids"][0])
        }

        return context
    
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

        context = self._vector_search(msg)
        
        response = self.chat.send_message(
            msg,
            config=types.GenerateContentConfig(
                system_instruction = f"{self.system_prompt}\n{self._get_context_prompt(context)}",
                )
        )
        
        return response.text, context