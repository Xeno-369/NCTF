# NCTF

Dépôt générique et réutilisable pour le **NCTF** (CTF national du Togo, organisé par
le CERT.tg). Chaque **édition** a son propre dossier à la racine du dépôt — on ajoute
`NCTF27/`, `NCTF28/`, etc. les années suivantes comme dossiers frères, sans rien
mélanger entre éditions.

```
NCTF/
├── NCTF26/            ← édition 2026 (finale à Lomé, 19–20 nov.)
│   ├── CLAUDE.md          contexte permanent de l'édition
│   ├── scoreboard.md      suivi local des challenges et des flags
│   ├── challenges/        épreuves rangées par catégorie
│   │   ├── boot2root/  crypto/  forensics/  misc/
│   │   ├── pwn/  reverse/  stego/  web/
│   ├── kingofthehill/     boîte à outils King of the Hill (6 variantes)
│   ├── tools/             utilitaires (connexion TLS, triage, snippets)
│   └── templates/         gabarits notes.md / solve.py / exploit.py
└── NCTF27/            ← (à venir)
```

## Organisation d'une épreuve

Chaque challenge vit dans `NCTF26/challenges/<catégorie>/<nom>/` et contient en général :

- `files/` — les fichiers fournis par l'organisation (binaires, captures, archives…),
  **laissés intacts** ;
- `notes.md` — énoncé, pistes et processus de résolution ;
- `solve.py` (ou `exploit.py`, `solve.sage`, scripts ad hoc) — la résolution.

## Réutilisation d'une année sur l'autre

Les épreuves sont conservées pour pouvoir être réutilisées lors de futurs
*challenge-making* (par exemple en changeant le format de flag, `NCTF26{...}` →
`IAICTF{...}`). **Le contenu des fichiers de challenge n'est pas modifié ici** : les
flags d'origine restent en place et seront remplacés au moment de la réutilisation.

> Équipe : 1HUNTERS — joueur : xeno369 (Kali Linux, Lomé).
