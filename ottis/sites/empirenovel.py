"""https://www.empirenovel.com

- Page novel : /novel/<slug>          -> lien "Last Chapter" vers le dernier chapitre
- Chapitre   : /novel/<slug>/<numéro> -> texte dans div#read-novel, un <p> par paragraphe
- Chapitre inexistant : titre de page "Not Found", pas de div#read-novel
"""

import re

from bs4 import BeautifulSoup

from .base import Chapter, Site

CHAPTER_TITLE_RE = re.compile(r"^Chapter\s*\d+\s*[:\-–—]\s*\S")


class EmpireNovel(Site):
    key = "empirenovel"
    code = "EMN"
    base_url = "https://www.empirenovel.com"

    def novel_url(self, slug: str) -> str:
        return f"{self.base_url}/novel/{slug}"

    def chapter_url(self, slug: str, number: int) -> str:
        return f"{self.base_url}/novel/{slug}/{number}"

    def parse_latest_chapter(self, html: str) -> int | None:
        soup = BeautifulSoup(html, "lxml")
        for a in soup.find_all("a", href=True):
            if "Last Chapter" in a.get_text(" ", strip=True):
                m = re.search(r"/(\d+)/?$", a["href"])
                if m:
                    return int(m.group(1))
        return None

    def parse_chapter(self, html: str, number: int) -> Chapter | None:
        soup = BeautifulSoup(html, "lxml")
        content = soup.select_one("div#read-novel")
        if content is None:
            return None
        paragraphs = [" ".join(p.get_text().split()) for p in content.find_all("p")]
        paragraphs = [p for p in paragraphs if p]
        if not paragraphs:
            return None
        title = next((p for p in paragraphs[:5] if CHAPTER_TITLE_RE.match(p)), None)
        return Chapter(number=number, title=title, paragraphs=paragraphs)
