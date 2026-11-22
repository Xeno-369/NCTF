# Points

- **Catégorie :** misc
- **Points :** ?
- **Instance :** aucune
- **Début :** ven. 06 nov. 22:33

## Énoncé
points.txt lists a few hundred 2-D points, each tagged with a single character. Most of the tags are noise. A small subset of the points, read in the right geometric order, spells the flag. Recover that order and read off the flag.

## Fichiers
| Fichier | SHA-256 | Remarque |
|---|---|---|
| files/points.txt | e77cf6935ce9c5379e1867d45cf3e437a9cf951b5177d21f839adcd8253cc6b3 | 441 points : x y caractère |

## Pistes testées
| Heure (approx.) | Hypothèse | Test | Résultat |
|---|---|---|---|
| ~22:33 | Enveloppe convexe, sens antihoraire | Chaîne monotone d'Andrew | **Flag complet** |

Couches internes de l'enveloppe : bruit, ce qui confirme que seule la couche externe porte le message.

## Commandes utiles
```bash
python3 -I solve.py
```

## Ce qui a marché
1. 441 points, peu de points utiles, « ordre géométrique » : l'enveloppe convexe est le sous-ensemble naturel.
2. L'enveloppe a 41 sommets ; lus en sens antihoraire, ils donnent une rotation du flag.
3. Rotation à partir de « NCTF{ » : départ au sommet (0, -1000000), le point le plus bas. Les 41 sommets sont tous utilisés.

## Flag
`NCTF{convex_hull_walks_the_perimeter_ccw}`
