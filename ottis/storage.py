"""Écriture des chapitres sur disque.

data/<NOVEL>/<SITE>/
    raw/<NOVEL>_<NNNN>_<SITE>.html   page complète, telle que reçue
    txt/<NOVEL>_<NNNN>_<SITE>.txt    texte extrait, un paragraphe par bloc
    index.json                       métadonnées de chaque chapitre récupéré
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .naming import chapter_basename
from .sites import Chapter


class Store:
    def __init__(self, data_dir: Path, novel_code: str, novel_title: str, site_code: str):
        self.novel_code = novel_code
        self.site_code = site_code
        self.dir = data_dir / novel_code / site_code
        self.raw_dir = self.dir / "raw"
        self.txt_dir = self.dir / "txt"
        self.index_file = self.dir / "index.json"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.txt_dir.mkdir(parents=True, exist_ok=True)
        if self.index_file.exists():
            self.index = json.loads(self.index_file.read_text(encoding="utf-8"))
        else:
            self.index = {"novel": novel_title, "code": novel_code, "site": site_code, "chapters": {}}

    def _paths(self, number: int) -> tuple[Path, Path]:
        name = chapter_basename(self.novel_code, number, self.site_code)
        return self.raw_dir / f"{name}.html", self.txt_dir / f"{name}.txt"

    def has(self, number: int) -> bool:
        return all(p.exists() for p in self._paths(number))

    def save(self, chapter: Chapter, html: str, url: str):
        raw_path, txt_path = self._paths(chapter.number)
        _atomic_write(raw_path, html)
        _atomic_write(txt_path, chapter.to_text())
        self.index["chapters"][str(chapter.number)] = {
            "title": chapter.title,
            "url": url,
            "paragraphs": len(chapter.paragraphs),
            "scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        self.index["chapters"] = dict(sorted(self.index["chapters"].items(), key=lambda kv: int(kv[0])))
        _atomic_write(self.index_file, json.dumps(self.index, ensure_ascii=False, indent=2) + "\n")


def _atomic_write(path: Path, content: str):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
