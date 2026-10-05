"""Interface commune à tous les sites. Chaque site = une sous-classe de Site."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Chapter:
    number: int
    title: str | None
    paragraphs: list[str]

    def to_text(self) -> str:
        return "\n\n".join(self.paragraphs) + "\n"


class Site(ABC):
    key: str  # identifiant utilisé dans la config et la CLI, ex. "empirenovel"
    code: str  # abréviation utilisée dans les noms de fichiers, ex. "EMN"

    @abstractmethod
    def novel_url(self, slug: str) -> str:
        """URL de la page de présentation du novel."""

    @abstractmethod
    def chapter_url(self, slug: str, number: int) -> str:
        """URL d'un chapitre."""

    @abstractmethod
    def parse_latest_chapter(self, html: str) -> int | None:
        """Numéro du dernier chapitre disponible, lu sur la page du novel."""

    @abstractmethod
    def parse_chapter(self, html: str, number: int) -> Chapter | None:
        """Extrait le chapitre, ou None si la page n'existe pas."""
