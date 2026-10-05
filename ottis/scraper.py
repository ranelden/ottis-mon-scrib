"""Boucle de récupération des chapitres, indépendante du site."""

import logging
import random
import time

from .browser import Browser, CloudflareBlocked
from .config import DATA_DIR, Novel
from .sites import Site
from .storage import Store

log = logging.getLogger(__name__)

MAX_RETRIES = 3


def scrape(
    browser: Browser,
    novel: Novel,
    site: Site,
    start: int = 1,
    end: int | None = None,
    delay: tuple[float, float] = (2.0, 5.0),
    force: bool = False,
):
    slug = novel.sources[site.key]
    store = Store(DATA_DIR, novel.code, novel.title, site.code)

    if end is None:
        page = browser.get(site.novel_url(slug))
        end = site.parse_latest_chapter(page.html)
        if end is None:
            raise RuntimeError("Impossible de trouver le dernier chapitre, utilise --to")
        log.info("Dernier chapitre disponible : %d", end)

    saved, skipped, missing = 0, 0, []
    for number in range(start, end + 1):
        if not force and store.has(number):
            skipped += 1
            continue

        url = site.chapter_url(slug, number)
        page = _fetch(browser, url)
        chapter = site.parse_chapter(page.html, number)
        if chapter is None:
            log.warning("Chapitre %d introuvable (%s)", number, page.title)
            missing.append(number)
        else:
            store.save(chapter, page.html, url)
            saved += 1
            log.info("[%d/%d] %s", number, end, chapter.title or f"Chapitre {number}")

        time.sleep(random.uniform(*delay))

    log.info("Terminé : %d récupérés, %d déjà présents, %d introuvables %s",
             saved, skipped, len(missing), missing or "")


def _fetch(browser: Browser, url: str):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return browser.get(url)
        except (CloudflareBlocked, TimeoutError) as e:
            log.warning("Échec %d/%d sur %s : %s", attempt, MAX_RETRIES, url, e)
            if attempt == MAX_RETRIES:
                raise
            time.sleep(10 * attempt)
