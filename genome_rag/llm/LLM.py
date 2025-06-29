from google import genai
from google.genai import types
from google.genai.chats import Chat
from genome_rag.snpedia.VectorDB import VectorDB
import os
from dotenv import load_dotenv  # Add this import
load_dotenv()  # Load environment variables from .env
api_key = os.getenv("GOOGLE_API_KEY")

class LLM:

    chat: Chat
    db: VectorDB
    system_prompt = """<System>
        You are a helpful assistant helping people interpret their genotyping results.
        Your context will include snpedia articles that have been retrieved due to their relevance.
        Use the provided context to answer questions.
        Context is provided as json. Object ids are variant ids. Document is the text in the SNPedia page. Metadata contains technical information regarding the variant.
        </System>"""

    def __init__(self, db: VectorDB):
        client = genai.Client(
            api_key=api_key
        )
        
        self.chat = client.chats.create(
            model="gemini-2.5-flash",
            )

        self.db = db

    def _vector_search(self, query: str):
        rag_close_vectors = self.db.query(query)
        #manipulate response into a correct format
        context = {
            id: {
            "document": rag_close_vectors["documents"][0][i], # type: ignore
            "metadata": rag_close_vectors["metadatas"][0][i], # type: ignore
            } 
            for i, id in enumerate(rag_close_vectors["ids"][0])
        }

        return context
    
    def _get_context_prompt(self, query: str):
        return f"""
        <Context>
        {str(self._vector_search(query))}
        </Context>
        """

    def send_message(self, msg: str):

        msg=f"""
        <User>
        User's question: {msg}
        </User>
        """
        
        response = self.chat.send_message(
            msg,
            config=types.GenerateContentConfig(
                system_instruction = f"{self.system_prompt}\n{self._get_context_prompt(msg)}",
                )
        )
        
        return response.text