"""Navigateur partagé par tous les sites, avec gestion du challenge Cloudflare.

On utilise patchright (fork de Playwright patché contre la détection) : le
Playwright standard est bloqué par le challenge "managed" de Cloudflare, même
en mode visible. Le profil est persistant pour conserver le cookie cf_clearance
entre deux lancements.
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path

from patchright.sync_api import sync_playwright

log = logging.getLogger(__name__)

CHALLENGE_TITLES = ("just a moment", "un instant", "attention required")


class CloudflareBlocked(RuntimeError):
    pass


@dataclass
class Page:
    url: str
    title: str
    html: str


class Browser:
    def __init__(self, profile_dir: Path, headless: bool = False):
        self.profile_dir = profile_dir
        self.headless = headless

    def __enter__(self):
        self._pw = sync_playwright().start()
        self._ctx = self._pw.chromium.launch_persistent_context(
            str(self.profile_dir),
            headless=self.headless,
            no_viewport=True,
        )
        self._page = self._ctx.pages[0] if self._ctx.pages else self._ctx.new_page()
        return self

    def __exit__(self, *exc):
        self._ctx.close()
        self._pw.stop()

    def get(self, url: str, challenge_timeout: float = 60) -> Page:
        self._page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        self._pass_challenge(challenge_timeout)
        self._page.wait_for_load_state("domcontentloaded")
        return Page(url=self._page.url, title=self._page.title(), html=self._page.content())

    def _is_challenge(self) -> bool:
        return self._page.title().strip().lower().startswith(CHALLENGE_TITLES)

    def _pass_challenge(self, timeout: float):
        deadline = time.monotonic() + timeout
        if not self._is_challenge():
            return
        log.info("Challenge Cloudflare détecté, tentative de résolution...")
        last_click = 0.0
        while time.monotonic() < deadline:
            self._page.wait_for_timeout(1000)
            if not self._is_challenge():
                log.info("Challenge passé")
                return
            # Un clic trop tôt ou répété fait échouer la vérification : on laisse
            # au widget le temps de répondre avant de recliquer.
            if time.monotonic() - last_click > 10 and self._click_turnstile():
                last_click = time.monotonic()
        raise CloudflareBlocked(f"Challenge Cloudflare non résolu après {timeout}s")

    def _click_turnstile(self) -> bool:
        """Clique sur la case à cocher du widget Turnstile s'il est affiché."""
        for frame in self._page.frames:
            if "challenges.cloudflare.com" not in frame.url:
                continue
            try:
                box = frame.frame_element().bounding_box()
            except Exception as e:  # iframe détachée pendant le rechargement
                log.debug("Turnstile introuvable : %s", e)
                continue
            if box and box["width"] > 0:
                # La case est sur la gauche du widget
                self._page.mouse.click(box["x"] + 30, box["y"] + box["height"] / 2)
                log.debug("Clic sur la case Turnstile")
                return True
        return False
