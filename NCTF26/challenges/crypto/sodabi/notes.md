# sodabi (two-time pad)

- Catégorie : crypto
- Résolu : sam. 07 nov.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/challenge.txt | 2a4ba0d6ab3b3eb3ea57617e2b55e7d041310c3d300dc8617c093470f9c34941 |

## Résolution
Réutilisation de clé XOR : c2 chiffre un message public connu.
key = c2 XOR known ; flag = c1 XOR key (c1 = 32 octets).

## Flag
`NCTF{S0D4B1_K3Y_R3U53_129384756}`
