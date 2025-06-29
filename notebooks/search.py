import marimo

__generated_with = "0.14.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import re
    import sys
    sys.path.append("genome_rag/snpedia/")

    return (mo,)


@app.cell
def _():
    from snpedia import SNPedia
    from VectorDB import VectorDB
    db = VectorDB()
    return (db,)


@app.cell
def _(mo):
    rsid_text_default = """
        rs53576, rs1815739, rs7412, rs429358, rs6152, rs333, rs1800497, rs1805007, rs9939609, rs662799, rs7495174, rs12913832, rs7903146, rs12255372, rs1799971, rs17822931, rs4680, rs1333049, rs1051730, rs3750344, rs4988235
        """

    variant_ids_input = mo.ui.text_area(
        label="Enter variant IDs (comma-separated):",
        placeholder="e.g., variant_A, variant_B, variant_C",
        value=rsid_text_default # Set the default value here
    )
    variant_ids_input
    return (variant_ids_input,)


@app.cell
def _(mo, variant_ids_input):
    # Process the input to get a list of variant IDs
    # This cell will automatically re-execute when variant_ids_input.value changes
    variant_ids = [
        v.strip() for v in variant_ids_input.value.split(',') if v.strip()
    ]

    mo.md(f"**Variant IDs to be processed:** {variant_ids}")
    return (variant_ids,)


@app.cell
def _(db, variant_ids):
    db.add_snps_to_db_if_not_added(variant_ids)
    return


@app.cell
def _(db):
    db.query(
        "I like smoking"
    )
    return


if __name__ == "__main__":
    app.run()
