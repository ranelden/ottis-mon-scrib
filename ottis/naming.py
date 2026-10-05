"""Nomenclature des fichiers : <NOVEL>_<chapitre sur 4 chiffres>_<SITE>.

Le code du novel est formé des initiales du titre ("The Beginning After The End"
-> "TBATE"), sauf si le titre tient en un seul mot ("Overlord" -> "Overlord").
Un code explicite peut être donné dans la config avec la clé "short".
"""

import re


def novel_code(title: str, short: str | None = None) -> str:
    if short:
        return short
    words = re.findall(r"[^\W_]+", title)
    if len(words) == 1:
        return words[0]
    return "".join(w[0].upper() for w in words)


def chapter_basename(novel: str, chapter: int, site_code: str) -> str:
    return f"{novel}_{chapter:04d}_{site_code}"
