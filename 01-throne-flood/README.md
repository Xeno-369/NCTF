# 01 — Throne Flood (variante « Colline »)

## Quand l'utiliser
Le challenge donne le **trône / score max** à l'équipe qui **re-soumet le plus
récemment ou le plus souvent** une preuve/flag. Le classement bouge en continu :
dès qu'un adversaire soumet, il passe devant. Il faut donc **marteler l'endpoint
de soumission** sans jamais s'arrêter.

Indices dans l'énoncé qui pointent vers cette variante :
- « gardez le contrôle », « le plus récent gagne », « throne », « hold the hill »,
- un endpoint unique de soumission, un score qui **retombe** si tu arrêtes,
- la session « Colline » des présélections (plusieurs requêtes/seconde).

## Lancement rapide
```bash
# Python (recommandé)
python3 throne_flood.py \
  --url http://10.10.10.5:1337/submit \
  --method POST \
  --data 'flag=NCTF{xxx}&team=1HUNTERS' \
  --workers 8 --interval 0.2 -v

# corps JSON + token
python3 throne_flood.py --url http://cible/submit \
  --json '{"flag":"NCTF{xxx}","team":"1HUNTERS"}' \
  --header 'Authorization: Bearer TOKEN' --workers 6

# Fallback bash (si pas de requests)
#  -> édite le bloc CONFIG en haut de throne_flood.sh puis :
./throne_flood.sh
```

## Réglages clés
| Paramètre | Rôle | Conseil |
|-----------|------|---------|
| `--workers` | threads parallèles | monte progressivement (4 → 8 → 16) |
| `--interval` | délai entre 2 envois / worker | baisse jusqu'à la limite avant les 429 |
| `--success-regex` | détecte « tu tiens le trône » | adapte au texte réel de la réponse |
| `--score-regex` | extrait ton score/rang | adapte au JSON/HTML renvoyé |
| `--max-retries` / `--backoff-*` | robustesse réseau | laisse par défaut au début |

## Méthode le jour J
1. Envoie **une** requête à la main (curl / Burp) pour voir la réponse exacte en cas
   de succès → cale `--success-regex` et `--score-regex` dessus.
2. Démarre doux (`--workers 4 --interval 0.5`), regarde les STATS.
3. Si **pas** de 429 → augmente les workers / baisse l'intervalle.
4. Si beaucoup de 429 → le script back-off tout seul ; remonte un peu l'intervalle
   pour trouver le point d'équilibre (débit max sans ban).
5. Garde un œil sur le score via `../06-scoreboard-monitor/`.

> ⚠️ Débit = pour **ton** service de compétition autorisé uniquement. Ne vise jamais
> une infra hors périmètre du CTF.
