# AEGIS-VAULT

- **Catégorie :** crypto (extraction de modèle, système linéaire)
- **Points :** ?
- **Instance :** https://u5yekx2iaeyhaebg.t.ctf.tg (per-team)
- **Début :** ven. 06 nov. 23:07 — **Résolu** le soir même

## Énoncé
Le vault a mémorisé un record scellé (24 octets 0..255). L'API /query ne rend qu'une confidence OTHER/SEALED pour une probe. /submit rend le flag si le record proposé matche à L-inf <= 2. Artefacts : weights.npz (E, 40x24), model.py (scoreur exact).

## Fichiers
| Fichier | SHA-256 | Remarque |
|---|---|---|
| files/weights.npz | d6b147176747093c2042e181d15e927c727815e8693184f8dba1d3beace13bcf | embedding E (40x24) ; était weights(1).npz dans Téléchargements |
| files/model.py | (fourni) | scoreur exact ; M = E^T E |

## Faille
Le logit SEALED est **linéaire** en r :
`s(p) = (1/S^2) p^T M r + C0`, S=255, M=E^T E connu.
La confidence donne s(p) sans perte : `s = ln(p1/p0)` (softmax 2 classes, OTHER=0).

En sondant `p = 255*e_j` : `s_j - C0 = (M r)_j / 255`, donc 24 probes donnent M r,
puis `r = M^{-1} (M r)`. Pas de lecture attribut par attribut : résolution globale.

## Ce qui a marché
1. Validation hors ligne (recover.py --offline) : record aléatoire reconstruit exactement.
2. online.py : 24 requetes /query, reconstruction, /submit.
3. Instance : residu max a l'arrondi 5.7e-13 (exact), serveur linf=0, flag rendu.

## Commandes
```bash
python3 -I recover.py --offline              # preuve maths
python3 online.py https://u5yekx2iaeyhaebg.t.ctf.tg
```

Record : [110, 20, 230, 111, 67, 107, 22, 12, 102, 19, 91, 111, 219, 59, 82, 172, 245, 230, 204, 48, 180, 243, 14, 223]

## Flag
`NCTF{a2a1b49268e667c9ba63f7a3}`
