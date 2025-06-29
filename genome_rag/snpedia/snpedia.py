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
    geno1_summary: str
    geno2: str
    geno2_summary: str
    geno3: str
    geno3_summary: str
    raw_content: str
    text: str

@dataclass
class Wikipage:
    title: str
    text: str
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
            keys_remove_prefix = ["Summary","geno1","geno2","geno3"]
            if key in keys_remove_prefix:
                result = result.removeprefix(f"{key}=")
            return result.strip()
        except:
            return ""

    def get_page_text(self, rsid: str) -> Wikipage:
        page: Page = self.site.pages[rsid]
        title = page.name
        raw_content = page.text()

        wikicode = mwparserfromhell.parse(raw_content)

        text = wikicode.strip_code()

        geno1 = self._try_get_from_template_or_return_empty_str(wikicode, "geno1")
        geno2 = self._try_get_from_template_or_return_empty_str(wikicode, "geno2")
        geno3 = self._try_get_from_template_or_return_empty_str(wikicode, "geno3")

        if geno1 != "":
            geno1_summary = self.site.pages[rsid+geno1].text()
        else:
            geno1_summary = ""
        
        if geno2 != "":
            geno2_summary = self.site.pages[rsid+geno2].text()
        else:
            geno2_summary = ""
        
        if geno3 != "":
            geno3_summary = self.site.pages[rsid+geno3].text()
        else:
            geno3_summary = ""

        # get metadata
        metadata_dict: Metadata = {
            "Summary": self._try_get_from_template_or_return_empty_str(wikicode, "Summary"),
            "Assembly": self._try_get_from_template_or_return_empty_str(wikicode, "Assembly"),
            "Orientation": self._try_get_from_template_or_return_empty_str(wikicode, "Orientation"),
            "StabilizedOrientation": self._try_get_from_template_or_return_empty_str(wikicode, "StabilizedOrientation"),
            "geno1": geno1,
            "geno1_summary": geno1_summary,
            "geno2": geno2,
            "geno2_summary": geno2_summary,
            "geno3": geno3,
            "geno3_summary": geno3_summary,
            "raw_content": raw_content,
            "text": text,
            }
        
        # Pass the dictionary directly, as it matches the TypedDict structure
        return Wikipage(title, text, metadata_dict)
