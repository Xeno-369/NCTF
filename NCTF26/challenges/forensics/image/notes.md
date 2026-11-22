# image (stégano LSB)

- **Catégorie :** forensics / stégano
- **Points :** ?
- **Instance :** aucune
- **Début :** ven. 06 nov. 23:17

## Énoncé
Une image image.png cache un secret… mais lequel ?

## Fichiers
| Fichier | SHA-256 | Remarque |
|---|---|---|
| files/image.png | ca0ee37e03de0f6d95178757dd97316a0777c2bc05161da7e8b430ed5814ed4b | PNG 400x300 RGB, compression 7,2% (LSB bruités) |

## Pistes testées
| Heure (approx.) | Hypothèse | Test | Résultat |
|---|---|---|---|
| ~23:17 | Métadonnées / trailer | exiftool, pngcheck, après IEND | Rien |
| ~23:18 | LSB | zsteg, puis extraction numpy | **Flag en b1,rgb,lsb,xy** |

## Ce qui a marché
Compression PNG faible = LSB à forte entropie. `zsteg` lit le flag dans le canal
`b1,rgb,lsb,xy` (bit de poids faible des 3 canaux, ordre pixel R,G,B).
Revérifié avec numpy (packbits sur R,G,B & 1) : même flag.

## Commandes utiles
```bash
zsteg files/image.png
```

## Flag
`NCTF{K4B0U_L5B_5T3G4N0_PN66_1192837465}`
