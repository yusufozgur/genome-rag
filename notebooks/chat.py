import marimo

__generated_with = "0.14.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import sys
    sys.path.append("genome_rag/snpedia/")
    from VectorDB import VectorDB
    db = VectorDB()
    return (db,)


@app.cell
def _():
    return


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
def _():
    return


@app.cell
def _(chat_callback, mo):
    question_input = mo.ui.chat(
        model=chat_callback
    )
    question_input
    return


if __name__ == "__main__":
    app.run()
