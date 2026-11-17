# King of the Hill — Boîte à outils NCTF26 (équipe 1HUNTERS)

Scripts génériques et robustes pour les challenges **King of the Hill (KOTH)** de la
finale du **NCTF26**. Chaque variante a son dossier, son script **autonome** (copiable
seul sur une box) et son README. L'objectif : le jour J, tu changes **2-3 variables**
(ou tu passes des options en ligne de commande) et tu lances.

> ⚠️ **Cadre** : ces outils sont pour les services **de la compétition pour laquelle tu
> es autorisé** (NCTF26) et l'entraînement sur tes propres cibles. Ne vise jamais une
> infra hors périmètre du CTF.

---

## 🎯 Choisir le bon script le jour J

Lis l'énoncé, puis suis l'arbre :

```
L'énoncé parle de...
│
├─ « garder le contrôle / le plus récent gagne / le score retombe si tu t'arrêtes »
│   et un simple endpoint de soumission, PAS de rate-limit visible
│        → 01-throne-flood        (marteler la soumission, N workers)
│
├─ pareil MAIS réponses 429 / « rate limit » / bans temporaires
│        → 04-web-api-ratelimit   (débit auto-ajusté AIMD, respecte Retry-After)
│
├─ « premier à soumettre la preuve gagne le round » / nouveau flag toutes les N s
│        → 03-fastest-exploit     (latence minimale, connexion pré-chauffée)
│
├─ « laissez votre identifiant dans un fichier/endpoint », agent qui lit « le roi »,
│   1 point par tick de possession (type CTFd / TryHackMe)
│        → 05-flag-ownership      (re-implante ton marqueur, mesure la possession)
│
├─ « défendez votre service ET attaquez les autres », flags qui tournent par tick,
│   SLA/uptime (format Attack/Defense)
│        → 02-patch-and-defend    (orchestre défense + attaque + soumission)
│
└─ Dans TOUS les cas, en parallèle, pour suivre ton rang en direct :
         → 06-scoreboard-monitor  (rang, écart au leader, alerte quand tu recules)
```

**Doute entre deux ?** Lance d'abord `06-scoreboard-monitor`, puis teste `01-throne-flood`
à faible débit : s'il y a des 429 → bascule sur `04`. Si le score ne dépend pas de la
fréquence mais d'un « qui contrôle quoi » → c'est `05` (ou `02` s'il faut aussi défendre).

---

## 📦 Les variantes couvertes

| # | Dossier | Scénario KOTH | Idée clé |
|---|---------|---------------|----------|
| 01 | `01-throne-flood/` | Garder le trône par ré-soumission continue (« Colline ») | débit brut, N workers |
| 02 | `02-patch-and-defend/` | Attack/Defense : défendre son service + piller les autres | orchestrateur 3 boucles |
| 03 | `03-fastest-exploit/` | Le plus rapide à soumettre la preuve prend le round | latence minimale |
| 04 | `04-web-api-ratelimit/` | Débit max sous un rate-limit (429) | contrôleur adaptatif AIMD |
| 05 | `05-flag-ownership/` | Garder son marqueur « king » planté (agent CTFd) | plant → verify → re-plant |
| 06 | `06-scoreboard-monitor/` | Suivi live du classement + alertes | compagnon universel |
| — | `common/koth_lib.py` | Plomberie réutilisable (session, retry, stats, log) | pour scripts custom |

---

## ⚙️ Conventions communes à tous les scripts

Tous partagent la même ergonomie, donc un seul réflexe à avoir :

- **Config en haut du fichier** : un bloc `# ===== CONFIG =====` avec des constantes
  claires (URL, port, intervalle, workers, headers, format du flag…).
- **Surcharge en ligne de commande** : les réglages fréquents ont une option
  (`--url`, `--workers`, `--interval`, `--header`, `-v`…). `-h` liste tout.
- **Robustesse réseau garantie** : timeout, connexion refusée, **HTTP 429**
  (respect de `Retry-After`), 5xx → **backoff exponentiel + jitter**. Aucun script
  ne plante sur une erreur réseau ; un worker qui tombe est isolé.
- **Logs lisibles** : horodatés, colorés en terminal, avec un résumé périodique
  (`STATS | …`) : requêtes envoyées, succès/échecs, 429, débit réel, score/rang.
- **Arrêt propre** : `Ctrl-C` stoppe tous les workers et imprime un résumé final.

### Pré-requis
```bash
pip install requests          # unique dépendance Python
# (01-throne-flood a aussi un fallback bash pur curl : throne_flood.sh)
```

### Rendre les scripts exécutables
```bash
chmod +x */*.py 01-throne-flood/throne_flood.sh
```

### Aide d'un script
```bash
python3 01-throne-flood/throne_flood.py -h
```

---

## 🧪 Routine conseillée pendant le match

1. Terminal 1 → `06-scoreboard-monitor` (ton tableau de bord).
2. Terminal 2 → le script de la variante identifiée, **démarré doux**.
3. Monte progressivement le débit / l'agressivité en surveillant les 429 et ton rang.
4. Si ça sature (429, bans) → bascule/ajuste vers `04-web-api-ratelimit`.
5. Note dans un coin l'URL, le format de flag et les réglages qui marchent (réutiles
   pour le challenge suivant).

> 💡 Chaque `02/03/05` contient des fonctions marquées `#>>> TODO` : c'est là que tu
> branches **ton** exploit / ta méthode d'écriture spécifiques au challenge. Le reste
> (robustesse, boucle, stats) est déjà fait.

---

## 📚 Références (formats KOTH publics)

- CTFd — King of the Hill : <https://docs.ctfd.io/docs/custom-challenges/king-of-the-hill>
- CTFd — Créer un challenge KoTH (agent) : <https://docs.ctfd.io/tutorials/challenges/creating-koth-challenges>
- rCTF — Scoring dynamique (KoTH / attack-defense) : <https://rctf.osec.io/admin/scoring/>
- TryHackMe — King of the Hill overview : <https://help.tryhackme.com/en/articles/6498315-king-of-the-hill-overview>
- Guide KoTH (ctf-kit) : <https://cywf.github.io/ctf-kit/docs/king-of-the-hill-ctf.html>
- Flaghammer (outil KoTH, 0x00sec) : <https://0x00sec.org/t/flaghammer-a-tool-for-king-of-the-hill-ctfs/2971>

---

*Bonne chance à 1HUNTERS pour la finale du NCTF26 ! 🏔️👑*
