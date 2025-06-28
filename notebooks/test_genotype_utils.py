import marimo

__generated_with = "0.14.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return


@app.cell
def _():
    import sys
    sys.path.append("genome_rag/genotypes/")
    return


@app.cell
def _():
    from GenotypesFile import GenotypesFile
    return (GenotypesFile,)


@app.cell
def _():
    from Genotype import Genotype
    return (Genotype,)


@app.cell
def _(GenotypesFile):
    tmp = GenotypesFile("data/sample.tsv").get_individual_genotypes("NA00001.GT")

    print(tmp)
    return


@app.cell
def _(GenotypesFile):
    GenotypesFile("data/sample.tsv").get_snp_ids()
    return


@app.cell
def _(Genotype):
    Genotype("A/C") == Genotype("A|a")
    return


if __name__ == "__main__":
    app.run()
