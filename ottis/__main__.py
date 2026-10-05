"""Point d'entrée : python -m ottis <commande> ..."""

import argparse
import logging
import sys

from .browser import Browser
from .config import PROFILE_DIR, load_novels
from .scraper import scrape
from .sites import SITES


def cmd_list(args):
    for code, novel in load_novels().items():
        print(f"{code:<12} {novel.title}  [{', '.join(novel.sources)}]")


def cmd_scrape(args):
    novels = load_novels()
    novel = novels.get(args.novel)
    if novel is None:
        sys.exit(f"Novel inconnu : {args.novel}. Disponibles : {', '.join(novels)}")

    site_key = args.site
    if site_key is None:
        if len(novel.sources) > 1:
            sys.exit(f"Plusieurs sources pour {novel.code}, précise --site parmi : {', '.join(novel.sources)}")
        site_key = next(iter(novel.sources))
    if site_key not in novel.sources:
        sys.exit(f"{novel.code} n'a pas de source {site_key}")
    if site_key not in SITES:
        sys.exit(f"Site non supporté : {site_key}. Supportés : {', '.join(SITES)}")

    with Browser(PROFILE_DIR, headless=args.headless) as browser:
        scrape(browser, novel, SITES[site_key], start=args.start, end=args.end,
               delay=tuple(args.delay), force=args.force)


def main():
    parser = argparse.ArgumentParser(prog="ottis", description="Scraper de light novels")
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(required=True)

    p_list = sub.add_parser("list", help="liste les novels configurés")
    p_list.set_defaults(func=cmd_list)

    p_scrape = sub.add_parser("scrape", help="récupère les chapitres d'un novel")
    p_scrape.add_argument("novel", help="code du novel, ex. TBATE (voir `list`)")
    p_scrape.add_argument("--site", help="clé du site, obligatoire si plusieurs sources")
    p_scrape.add_argument("--from", dest="start", type=int, default=1, help="premier chapitre (défaut : 1)")
    p_scrape.add_argument("--to", dest="end", type=int, help="dernier chapitre (défaut : le dernier publié)")
    p_scrape.add_argument("--delay", type=float, nargs=2, default=[2.0, 5.0], metavar=("MIN", "MAX"),
                          help="pause aléatoire entre deux chapitres, en secondes (défaut : 2 5)")
    p_scrape.add_argument("--force", action="store_true", help="re-télécharge les chapitres déjà présents")
    p_scrape.add_argument("--headless", action="store_true",
                          help="sans fenêtre (bloqué par Cloudflare sur empirenovel pour l'instant)")
    p_scrape.set_defaults(func=cmd_scrape)

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
    args.func(args)


if __name__ == "__main__":
    main()
