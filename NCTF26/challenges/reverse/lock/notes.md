# lock (chall, byte-drift)

- **Catégorie :** reverse
- **Points :** ?
- **Instance :** aucune (binaire seul)
- **Début :** ven. 06 nov. 23:02

## Énoncé
Lock program chall. Demande une passphrase, dit "unlocked" ou "locked". ELF x86-64 strippé. La passphrase correcte EST le flag. Tout est dans le fichier, pas de réseau.

## Fichiers
| Fichier | SHA-256 | Remarque |
|---|---|---|
| files/chall | be3cf80de56cb50a8232536f7fb358bb12829728bc2bca1c27601c2baa3baac9 | ELF64 PIE strippé, droit d'exécution retiré après lecture |

## Pistes testées
| Heure (approx.) | Hypothèse | Test | Résultat |
|---|---|---|---|
| ~23:02 | Comparaison à une constante embarquée | objdump, lecture de la routine de check | Transformation byte-drift + table à 0x2070 |
| ~23:04 | Inversion directe du calcul | solve.py, re-vérif sens direct | **Flag, vérifié** |

## Ce qui a marché
Longueur exigée : 30. Pour chaque i de 0 à 29 :
`rol8(input[i] + 3*i + 7, (i%7)+1) ^ 0x5c == cible[i]`
cible = 30 octets à .rodata 0x2070.

Inversion : `input[i] = ror8(cible[i] ^ 0x5c, (i%7)+1) - 3*i - 7 (mod 256)`.
Revérifié dans le sens direct : les 30 octets reproduisent la table. Aucune exécution du binaire.

## Commandes utiles
```bash
python3 -I solve.py
```

## Flag
`NCTF{inv3rt_th3_drift_by_h4nd}`
