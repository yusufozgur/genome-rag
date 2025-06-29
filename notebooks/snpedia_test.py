import marimo

__generated_with = "0.14.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from genome_rag.snpedia.snpedia import SNPedia
    return (SNPedia,)


@app.cell
def _(SNPedia):
    snp = SNPedia()
    return (snp,)


@app.cell
def _(snp):
    snp.get_page_text("Rs53576").metadata
    return


@app.cell
def _(snp):
    gt = "Rs53576"+snp.get_page_text("Rs53576").metadata["geno1"]
    gt
    return (gt,)


@app.cell
def _():

    import mwclient
    from mwclient.page import Page
    import mwparserfromhell
    return (mwclient,)


@app.cell
def _(gt, mwclient):

    agent = 'MySNPBot using mwclient'
    site = mwclient.Site('bots.snpedia.com', path='/', clients_useragent=agent, scheme='https')
    site.pages[gt].text()
    return


if __name__ == "__main__":
    app.run()
