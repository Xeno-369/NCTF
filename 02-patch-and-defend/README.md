# 02 — Patch & Defend (Attack / Defense)

## Quand l'utiliser
Format **Attack/Defense** (souvent étiqueté KOTH par les organisateurs) : chaque
équipe héberge **le même service vulnérable**. Tu gagnes en **attaquant** les autres
(voler leur flag, le soumettre) **et** en **défendant** le tien (rester UP + patcher).
Les flags **tournent à chaque tick** (1–5 min), donc il faut ré-attaquer en boucle.

Indices : « vous recevez une VM/un service à défendre », « flag IDs par tick »,
« SLA / uptime », « soumettez les flags adverses au serveur de score ».

## C'est un squelette — 3 choses à compléter
Ouvre `patch_and_defend.py` et cherche les `#>>> TODO` :
1. `exploit(ip)` → **ton** exploit réel ; renvoie le flag d'une équipe ou `None`.
2. `health_ok()` → comment vérifier que **ton** service est sain.
3. `PATCH_COMMAND` (+ `apply_patch` si besoin) → la commande **idempotente** qui
   corrige la faille sans casser le SLA.

Règle aussi : `SUBMIT_URL`, `SUBMIT_HEADERS` (ton token d'équipe), `FLAG_REGEX`,
`TARGETS` (IPs adverses), `SERVICE_PORT`.

## Lancement
```bash
# attaque + défense
python3 patch_and_defend.py --targets 10.60.1.2,10.60.2.2,10.60.3.2 -v

# seulement défendre (ex: pendant que tu codes l'exploit)
python3 patch_and_defend.py --no-attack -v

# seulement attaquer
python3 patch_and_defend.py --no-defense --targets 10.60.1.2 -v
```

## Bon réflexe
- **Dédup intégrée** : un même flag n'est soumis qu'une fois (set `_submitted`).
- **Patch idempotent** : il est rappelé à chaque check → il doit pouvoir tourner 100×.
- Cale `ATTACK_INTERVAL` sur la **durée d'un tick** (sinon tu soumets des flags périmés).
- Garde un terminal `../06-scoreboard-monitor/` ouvert pour suivre le classement.
- Patche **vite mais prudemment** : un service down coûte souvent plus cher en SLA
  que quelques flags volés.
