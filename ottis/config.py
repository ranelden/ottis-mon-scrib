"""Lecture de config/novels.json (liste des novels à scraper et leurs sources)."""

import json
from dataclasses import dataclass
from pathlib import Path

from .naming import novel_code

ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT / "config" / "novels.json"
DATA_DIR = ROOT / "data"
PROFILE_DIR = ROOT / ".browser_profile"


@dataclass
class Novel:
    title: str
    code: str
    sources: dict[str, str]  # clé du site -> slug du novel sur ce site


def load_novels(path: Path = CONFIG_FILE) -> dict[str, Novel]:
    entries = json.loads(path.read_text(encoding="utf-8"))
    novels = {}
    for entry in entries:
        code = novel_code(entry["title"], entry.get("short"))
        novels[code] = Novel(title=entry["title"], code=code, sources=entry["sources"])
    return novels
