import marimo

__generated_with = "0.14.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import sys
    sys.path.append("genome_rag/snpedia/")
    import snpedia
    return (snpedia,)


@app.cell
def _(snpedia):
    page = snpedia.SNPedia().site.pages["rs5376"]
    return (page,)


@app.cell
def _(page):
    page.info
    return


if __name__ == "__main__":
    app.run()
