# pattern-after (data.txt)

- Catégorie : misc (string search)
- Résolu : sam. 07 nov.

## Énoncé
data.txt : ligne1 = motif, ligne2 = gros texte. Le caractère juste après chaque occurrence du motif, dans l'ordre, = flag.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/data.txt | 7a662485dff05ce8335d1af8bdde67de75efd44cf7b6b840196fde448321f5b8 |

## Résolution
Motif 'Qx7#zZ', 40 occurrences dans le texte. Caractère suivant chaque occurrence concaténé. Chevauchement ou non : identique.

## Flag
`NCTF{z_function_finds_every_needle_fast}`
