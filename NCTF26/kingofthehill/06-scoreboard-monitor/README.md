# 06 — Scoreboard Monitor (compagnon de tous les scripts)

## Quand l'utiliser
**Toujours**, en parallèle de la variante active (01→05). Il interroge le scoreboard
en boucle, affiche ton **rang**, ton **score**, l'**écart avec le leader**, et
t'**alerte** (bip `\a` + ligne rouge) dès que tu perds la tête ou que tu recules.
C'est ton tableau de bord pour régler le débit/l'agressivité des autres scripts.

## Deux modes de parsing
- **JSON** (défaut) : auto-détecte une liste d'entrées `{nom, score}`. Si l'auto ne
  marche pas, précise les champs : `--name-field team --score-field points`.
- **HTML** : donne une regex à **2 groupes** (nom, score) :
  `--regex '<td>([^<]+)</td>\s*<td>(\d+)</td>'`

## Lancement
```bash
# API JSON
python3 scoreboard_monitor.py \
  --url http://cible:8080/api/scoreboard \
  --team 1HUNTERS --interval 3

# Page HTML
python3 scoreboard_monitor.py \
  --url http://cible/scoreboard \
  --team 1HUNTERS \
  --regex '<tr>.*?>([^<]+)</td>.*?>(\d+)</td>' -v
```

## Sortie type
```
rang=1/12 score=4200 | 👑 LEADER | 1er=1HUNTERS(4200)
⚠️  TU RECULES (1->2) ! rang=2/12 score=4200 | écart au 1er=150 | 1er=TeamX(4350)
```

## Astuce
Lance-le dans un **terminal à part** (ou `tmux`) à côté du script d'attaque : quand
l'alerte « TU RECULES » sonne, augmente le débit (01/04) ou baisse `--interval` (05).
