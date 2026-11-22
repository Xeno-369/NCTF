# vault (chall, super-secret vault — leurre)

- Catégorie : reverse
- Résolu : sam. 07 nov. (statique)

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/chall | 6788208da7d4d2bab2bb71525eb357ed15fd301f58ee729efedc33aadae32630 |

## Énoncé
Le binaire affiche un flag dans la bannière -> rejeté. Trouver le vrai flag. ELF PIE strippé.

## Analyse
- Bannière NCTF{y0u_grepp3d_th3_f4ke_0ne} = leurre (il le dit : "grepped the fake one").
- Vérif passphrase (23 car.) : (input[i]^0x5a)+(3+7*i) == check[i]  (check @0x20c0).
  -> pp[i] = ((check[i]-(3+7*i))&0xff)^0x5a = "unw1nd_th3_math_by_h4nd".
- Vrai flag (31 o, encodé @0x20a0) : flag[i] = pp[i%23] ^ enc[i]. Affiché seulement si passphrase correcte.

## Flag
`NCTF{str1ngs_l1e_read_the_c0de}`
