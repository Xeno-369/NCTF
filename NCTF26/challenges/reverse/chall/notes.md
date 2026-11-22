# chall

- **Catégorie :** reverse / pwn (ret2win)
- **Points :** ?
- **Instance :** aucune fournie (binaire seul)
- **Début :** ven. 06 nov. 22:46

## Énoncé
Binaire x86-64 Linux, chall. Lit une entrée et affiche « bye ». Une fonction decode et affiche un flag mais n'est jamais appelee sur le chemin normal. L'atteindre et capturer ce qu'elle affiche.

## Fichiers
| Fichier | SHA-256 | Remarque |
|---|---|---|
| files/chall | 154670eab589cacb9db2955c20e36cbbccb622336ecea4b7d42d45074fbc79f9 | ELF64 EXEC, non strippé, No PIE, droit d'exécution retiré après lecture |

## Pistes testées
| Heure (approx.) | Hypothèse | Test | Résultat |
|---|---|---|---|
| ~22:46 | Fonction cachée win() | nm / objdump, lecture statique | win à 0x4011b6, jamais appelée |
| ~22:47 | win déchiffre le flag en clair | XOR 0x5a sur enc (38 octets), reproduit en Python | **Flag obtenu sans exécution** |

## Ce qui a marché
1. `nm` révèle win (0x4011b6) et vuln (0x401233). main appelle vuln puis affiche « bye » ; win n'est jamais appelée.
2. win lit 38 octets à `enc` (0x402040), applique XOR 0x5a, écrit le résultat puis un '\n'.
3. Déchiffrement statique de enc : flag en clair. Aucune exécution du binaire.

Voie d'exploitation prévue (non nécessaire pour le flag) : vuln déborde un buffer, binaire sans canary et sans PIE, donc ret2win vers 0x4011b6 (`offset*b'A' + p64(0x4011b6)`).

## Flag
`NCTF{ret2win_no_canary_no_pie_smashed}`
