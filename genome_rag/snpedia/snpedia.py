from dataclasses import dataclass
import mwclient
from mwclient.page import Page
import mwparserfromhell
from typing import TypedDict # Import TypedDict

# Convert Metadata dataclass to TypedDict
class Metadata(TypedDict):
    Summary: str
    Assembly: str
    Orientation: str
    StabilizedOrientation: str
    geno1: str
    geno2: str
    geno3: str

@dataclass
class Wikipage:
    title: str
    content: str
    metadata: Metadata # Use the TypedDict here

class SNPedia():

    def __init__(self):
        agent = 'MySNPBot using mwclient'
        self.site = mwclient.Site('bots.snpedia.com', path='/', clients_useragent=agent, scheme='https')

    @staticmethod
    def _try_get_from_template_or_return_empty_str(
            wikicode,
            key: str,
            template_index = 0) -> str:

        try:
            template = wikicode.filter_templates()[template_index]

            result = str(template.get(key))
            if key == "Summary" and result.startswith("Summary="):
                result = result.removeprefix("Summary=")
            return result.strip()
        except:
            return ""

    def get_page_text(self, rsid: str) -> Wikipage:
        page: Page = self.site.pages[rsid]
        title = page.name
        content = page.text()

        wikicode = mwparserfromhell.parse(content)

        content = wikicode.strip_code()

        # get metadata
        metadata_fields = [
        ]

        metadata_dict: Metadata = {
            "Summary": self._try_get_from_template_or_return_empty_str(wikicode, "Summary"),
            "Assembly": self._try_get_from_template_or_return_empty_str(wikicode, "Assembly"),
            "Orientation": self._try_get_from_template_or_return_empty_str(wikicode, "Orientation"),
            "StabilizedOrientation": self._try_get_from_template_or_return_empty_str(wikicode, "StabilizedOrientation"),
            "geno1": self._try_get_from_template_or_return_empty_str(wikicode, "geno1"),
            "geno2": self._try_get_from_template_or_return_empty_str(wikicode, "geno2"),
            "geno3": self._try_get_from_template_or_return_empty_str(wikicode, "geno3"),
            }
        
        # Pass the dictionary directly, as it matches the TypedDict structure
        return Wikipage(title, content, metadata_dict)
