"""Registre des sites supportés. Pour ajouter un site : créer un module ici
avec une sous-classe de Site, puis l'ajouter à SITES."""

from .base import Chapter, Site
from .empirenovel import EmpireNovel

SITES: dict[str, Site] = {site.key: site for site in (EmpireNovel(),)}

__all__ = ["SITES", "Chapter", "Site"]
