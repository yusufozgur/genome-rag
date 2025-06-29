from dataclasses import dataclass
import mwclient
from mwclient.page import Page
import mwparserfromhell

class SNPedia():

    @dataclass
    class Wikipage:
        title: str
        content: str

    def __init__(self):
        agent = 'MySNPBot using mwclient'
        self.site = mwclient.Site('bots.snpedia.com', path='/', clients_useragent=agent, scheme='https')

    def get_page_text(self, rsid: str) -> Wikipage:
        page: Page = self.site.pages[rsid]
        title = page.name
        content = page.text()

        wikicode = mwparserfromhell.parse(content)

        content = wikicode.strip_code()

        return self.Wikipage(title, content)
    