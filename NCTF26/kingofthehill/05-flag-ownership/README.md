# 05 — Flag Ownership (garder son marqueur « king »)

## Quand l'utiliser
Le KOTH « classique » façon **agent CTFd** / **TryHackMe** : tu as un accès en
écriture sur une box/un service partagé, et un **agent** regarde périodiquement
**qui est le roi** en lisant un **marqueur** (fichier, clé, valeur). L'équipe dont
l'identifiant est présent marque **1 point par tick**. Les autres **écrasent** ton
marqueur → il faut le **ré-implanter en boucle** pour maximiser ta **durée de possession**.

Indices : « laissez votre identifiant dans `/root/king.txt` », « conservez le
contrôle », « 1 point par minute de possession », un fichier/endpoint « king/owner ».

## À compléter
Dans `flag_ownership.py`, cherche `#>>> TODO` :
- `plant(session)` → **comment tu écris** ton marqueur (POST/PUT, ou via web shell :
  remplace le corps par un `subprocess` / une requête vers ton RCE).
- `verify(session)` → **comment tu lis** le roi courant et compares à `MARKER`.
- Règle `TARGET_BASE`, `PLANT_PATH`, `VERIFY_PATH`, `MARKER`, `HEADERS`.

> 💡 Si ton contrôle passe par du RCE (web shell), `plant()` peut exécuter par ex.
> `echo 1HUNTERS > /root/king.txt` et `verify()` lire ce fichier. Le script reste
> le même, seules ces 2 fonctions changent.

## Lancement
```bash
python3 flag_ownership.py \
  --base http://10.10.10.5:9000 \
  --marker 1HUNTERS \
  --interval 1.0 -v
```

## Lecture des STATS
```
STATS | cycles=120 possession=93% perdus=8 replants=8
```
- **possession %** = ta part de temps en tant que roi → c'est ça que tu maximises.
- **perdus / replants** élevés = un adversaire agressif ; baisse `--interval` pour
  reprendre plus vite (quitte à consommer plus de requêtes).

## Astuce anti-écrasement
Si plusieurs équipes se battent, descendre `--interval` sous le tick de l'agent
garantit que **ton** marqueur est presque toujours celui lu au moment du check.
