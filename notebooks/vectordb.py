import marimo

__generated_with = "0.14.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import chromadb
    import sys
    sys.path.append("genome_rag/snpedia/")
    import snpedia
    from VectorDB import VectorDB
    sys.path.append("genome_rag/genotypes/")
    from GenotypesFile import GenotypesFile
    return GenotypesFile, VectorDB


@app.cell
def _(VectorDB):
    db = VectorDB()
    db
    return (db,)


@app.cell
def _(GenotypesFile):
    gt = GenotypesFile("data/sample.tsv").get_individual_genotypes("NA00001.GT")

    print(gt)
    return (gt,)


@app.cell
def _(gt):
    list(gt.keys())
    return


@app.cell
def _(db):
    db.add_snps_to_db_if_not_added(["rs123","rs1234"])
    return


@app.cell
def _(db, gt):
    db.add_snps_to_db_if_not_added(list(gt.keys()))
    return


@app.cell
def _(db):

    db.add_snps_to_db_if_not_added(["I15006212(C;T)"])
    return


@app.cell
def _(db):
    db.pages.get()
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
