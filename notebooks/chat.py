import marimo

__generated_with = "0.14.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from google import genai
    from google.genai import types
    return genai, mo, types


@app.cell
def _():
    import os
    from dotenv import load_dotenv  # Add this import
    load_dotenv()  # Load environment variables from .env
    api_key = os.getenv("GOOGLE_API_KEY")
    return (api_key,)


@app.cell
def _():
    import sys
    sys.path.append("genome_rag/snpedia/")
    from VectorDB import VectorDB
    db = VectorDB()
    return (db,)


@app.cell
def _(api_key, genai):
    client = genai.Client(
        api_key=api_key
    )
    return (client,)


@app.cell
def _(db):
    rag_query = db.query("sample_query")
    {
        id: {
        "document": rag_query["documents"][0][i],
        "metadata": rag_query["metadatas"][0][i],
        } 
        for i, id in enumerate(rag_query["ids"][0])
    }
    return


@app.cell
def _(client, db, mo, types):
    def chat_callback(msgs: list[str], config: mo.ai.ChatModelConfig = None):
        print(msgs)
        user_msg = msgs[-1].content

        rag_query = db.query(user_msg)
        context = {
            id: {
            "document": rag_query["documents"][0][i],
            "metadata": rag_query["metadatas"][0][i],
            } 
            for i, id in enumerate(rag_query["ids"][0])
        }

    
        system_prompt = f"""
        <System>
        You are a helpful assistant helping people interpret their genotyping results.
        Your context will include snpedia articles that have been retrieved due to their relevance.
        Use the provided context to answer questions.
        Context is provided as json. Object ids are variant ids. Document is the text in the SNPedia page. Metadata contains technical information regarding the variant.
        </System>
        <Context>
        {str(context)}
        </Context>
        """

        response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        ),
        contents=f"""
        <User>
        User's question: {user_msg}
        </User>
        """
    )
    
        return response.text
    return (chat_callback,)


@app.cell
def _(chat_callback, mo):
    question_input = mo.ui.chat(
        model=chat_callback
    )
    question_input
    return


if __name__ == "__main__":
    app.run()
