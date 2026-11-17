# 04 — API Rate Optimizer (débit max sans ban)

## Quand l'utiliser
Même idée que la variante 01 (marteler l'API) **mais** le service applique un
**rate-limit** (HTTP 429, bans temporaires). Trop lent → on te double ; trop rapide
→ 429 et cycles perdus. Ce script **trouve tout seul** le débit juste sous la limite
et le **tient**, même si la limite change en cours de partie.

Indices : réponses `429 Too Many Requests`, en-tête `Retry-After`, « rate limit »,
WAF, bans de quelques secondes.

## Comment ça marche : AIMD (comme TCP)
- **Additive Increase** : tant que ça passe, +`--increase` req/s par fenêtre propre.
- **Multiplicative Decrease** : au moindre 429, débit ×`--decrease` et on respecte
  `Retry-After`, puis on remonte prudemment.

Résultat : convergence automatique vers le débit maximal soutenable.

## Lancement
```bash
python3 api_rate_optimizer.py \
  --url http://cible:1337/action \
  --method POST \
  --start-rps 2 --min-rps 0.5 --max-rps 30 \
  --concurrency 4 -v
```
Le corps de requête (`FORM` / `JSON`) et les `HEADERS` se règlent en haut du fichier.

## Lecture des STATS
```
STATS | débit_cible=8.5 req/s réel=8.1 | ok=243 429=4 (2%) net_err=0
```
- **débit_cible** monte puis se stabilise → tu es à la limite.
- **% 429** doit rester faible (quelques %). S'il grimpe, baisse `--max-rps` ou
  `--increase`, ou monte `--decrease` vers 0.7 (recul plus doux).

## Conseils
- Commence `--max-rps` bas, laisse le contrôleur monter : tu verras le plateau réel.
- Si le serveur bannit l'IP (et pas juste 429), ajoute de la marge : `--decrease 0.3`.
- Combine avec `../06-scoreboard-monitor/` pour vérifier que le débit tenu te garde
  bien en tête.
