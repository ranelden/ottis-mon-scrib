# Ottis

Scraper de light novels : il parcourt des sites de lecture en ligne, récupère chaque chapitre d'un novel
et l'enregistre sur disque, pour constituer une base de données personnelle.

Chaque site est structuré différemment, donc chaque site a son propre module dans `ottis/sites/`.
Le reste (navigateur, gestion de Cloudflare, nommage, stockage, CLI) est commun.

## Avancement

- [x] Venv Python + dépendances
- [x] Navigateur patchright qui passe le challenge Cloudflare (Turnstile) d'EmpireNovel
- [x] Site **EmpireNovel** : chapitres, détection du dernier chapitre, chapitres manquants
- [x] Sauvegarde HTML brut + texte extrait + index JSON, reprise sans re-télécharger
- [x] CLI `list` / `scrape`
- [ ] Scraper TBATE en entier (530 chapitres)
- [ ] Post-traitement du texte (voir *Problèmes connus*)
- [ ] Autres sites
- [ ] Base de données (pour l'instant : fichiers)
- [ ] Interface

## Sites supportés

| Site | Clé CLI | Code fichiers | Notes |
|------|---------|---------------|-------|
| [EmpireNovel](https://www.empirenovel.com) | `empirenovel` | `EMN` | Cloudflare : nécessite une fenêtre visible |

## Installation

Python 3.12+ requis (testé avec 3.14).

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/patchright install chromium
```

Si `python3 -m venv` échoue avec *ensurepip is not available*, soit installer `python3-venv`
(`sudo apt install python3.14-venv`), soit :

```bash
python3 -m venv --without-pip .venv
curl -sS https://bootstrap.pypa.io/get-pip.py | .venv/bin/python
```

## Utilisation

```bash
source .venv/bin/activate

python -m ottis list                                # novels configurés
python -m ottis scrape TBATE                        # tous les chapitres, jusqu'au dernier publié
python -m ottis scrape TBATE --from 200 --to 250    # une plage
python -m ottis scrape TBATE --delay 3 8            # pause aléatoire entre chapitres (défaut : 2 à 5 s)
python -m ottis scrape TBATE --force                # re-télécharge même si déjà présent
python -m ottis -v scrape TBATE                     # logs détaillés
```

Une fenêtre Chromium s'ouvre : c'est normal, Cloudflare bloque le mode headless (option `--headless` dispo
mais elle ne passe pas sur EmpireNovel). Le challenge est résolu automatiquement au premier chapitre, puis
le cookie est conservé dans `.browser_profile/`, donc les lancements suivants passent généralement sans
challenge.

Les chapitres déjà présents sont sautés : on peut interrompre (`Ctrl+C`) et relancer sans rien perdre.

### Ajouter un novel

Dans `config/novels.json` :

```json
{
  "title": "The Beginning After The End",
  "sources": { "empirenovel": "the-beginning-after-the-end" }
}
```

Le slug est la partie de l'URL du site : `empirenovel.com/novel/<slug>`.
Clé optionnelle `"short"` pour imposer le code du novel au lieu de celui calculé.

## Nomenclature et sortie

Fichiers : `<NOVEL>_<CHAPITRE sur 4 chiffres>_<SITE>`, par exemple `TBATE_0209_EMN.txt`.

- **NOVEL** : initiales du titre (`The Beginning After The End` → `TBATE`), ou le titre entier s'il
  tient en un mot (`Overlord` → `Overlord`).
- **SITE** : code court du site (`EMN` pour EmpireNovel).

```
data/TBATE/EMN/
├── raw/TBATE_0209_EMN.html   page complète telle que reçue (pour retraiter plus tard)
├── txt/TBATE_0209_EMN.txt    texte du chapitre, paragraphes séparés par une ligne vide
└── index.json                titre, URL, nombre de paragraphes et date de récupération par chapitre
```

`data/` et `.browser_profile/` sont ignorés par git.

## Architecture

```
ottis/
├── __main__.py      CLI
├── browser.py       navigateur patchright + résolution du challenge Cloudflare
├── scraper.py       boucle de récupération (indépendante du site)
├── storage.py       écriture raw / txt / index.json
├── naming.py        nomenclature des fichiers
├── config.py        chargement de config/novels.json
└── sites/
    ├── base.py          interface Site + dataclass Chapter
    └── empirenovel.py   implémentation EmpireNovel
```

### Ajouter un site

1. Créer `ottis/sites/<site>.py` avec une sous-classe de `Site` (`key`, `code`, `novel_url`,
   `chapter_url`, `parse_latest_chapter`, `parse_chapter`).
2. L'ajouter dans `SITES` (`ottis/sites/__init__.py`).
3. Ajouter la source dans `config/novels.json`.

## Choix techniques

- **patchright** plutôt que Playwright : Playwright standard reste bloqué sur « Just a moment... » même
  en mode visible. patchright est un remplaçant drop-in patché contre la détection d'automatisation.
- **Clic Turnstile unique** : cliquer plusieurs fois de suite sur la case fait échouer la vérification,
  on attend 10 s entre deux clics.
- **HTML brut conservé** : le texte extrait est minimal, tous les nettoyages se feront après coup à
  partir du HTML.

## Problèmes connus

- Le texte d'EmpireNovel contient des artefacts d'anti-copie hérités de sa source
  (`ma.s.sive`, `s.h.i.+fting`) : à nettoyer en post-traitement.
- Certains chapitres n'ont pas de ligne « Chapter N: titre » (ex. 529) : le titre est alors `null`
  dans `index.json`.
- Le chapitre 530 de TBATE sur EmpireNovel est un contenu bidon recopié d'un autre site.
