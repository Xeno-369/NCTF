# rsa-leak-p (output.txt)

- Catégorie : crypto / RSA
- Résolu : sam. 07 nov.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/output.txt | 8687f842ace5446579bb8d42586978e1a90de1f4d4ad51877e506251ec12d1e0 |

## Faille
"Erreur de divulgation" = p est donné en plus de n,e,c.
q=n/p ; phi=(p-1)(q-1) ; d=e^-1 mod phi ; m=c^d mod n.

## Flag
`NCTF{W4b3_f4ct0r!zat1on_nt!_m!l3_d0u4y4_L3_FiY3}`
