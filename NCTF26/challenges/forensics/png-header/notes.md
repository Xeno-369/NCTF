# png-header (evidence.png)

- Catégorie : forensics
- Résolu : sam. 07 nov.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/evidence.png | ce48711c00857e24b60dbd55caeee03e9778e7e087bd508b4b028ad107d95d91 |

## Résolution
Les 8 octets de signature PNG (offset 0-7) étaient à zéro ; longueur IHDR et pixels intacts.
Remettre 89 50 4E 47 0D 0A 1A 0A -> le fichier s'ouvre (16x16 RGB).
Flag dans le chunk zTXt "Comment" (zlib) des métadonnées.

## Commande
```bash
printf '\x89PNG\r\n\x1a\n' | dd of=evidence.png bs=1 count=8 conv=notrunc
# puis lire zTXt Comment (pnginfo / python zlib)
```

## Flag
`NCTF{png_m4gic_byt3s_r3st0r3d}`
