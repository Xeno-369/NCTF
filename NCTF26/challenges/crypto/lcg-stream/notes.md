# lcg-stream (challenge.txt)

- Catégorie : crypto
- Résolu : sam. 07 nov.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/challenge.txt | df8dedc9385c364f728668ccabd817d02480ade9d76bc4010926faf1c4ce648a |

## Résolution
LCG X'=(aX+c) mod M, M=2^61-1 (premier). 6 sorties fournies.
a=(X2-X1)/(X1-X0) mod M ; c=X1-a*X0 mod M (vérifié).
Keystream = sorties À PARTIR de la 7e (après les 6 publiées), chacune to_bytes(8,'big'), concaténées.
flag = ct XOR keystream. (Crib NCTF{ a localisé le début du keystream sur la sortie d'index 6.)

## Flag
`NCTF{LCG_N0T_C5PRN6_661839204}`
