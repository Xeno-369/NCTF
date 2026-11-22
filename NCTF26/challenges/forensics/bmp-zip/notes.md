# bmp-zip (banner.bmp)

- Catégorie : forensics
- Résolu : sam. 07 nov.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/banner.bmp | 1c82294408b7a5c042d947b9e6b05407541111fbc57cae069f196e8591e60f27 |

## Résolution
BMP 80x80 24bpp : fin des pixels à l'offset 19254, mais fichier = 19416 o -> 162 o en trop.
Un ZIP appendé (binwalk) contenant secret/flag.txt.

## Commande
```bash
dd if=banner.bmp bs=1 skip=19254 of=x.zip && unzip x.zip && cat secret/flag.txt
# ou : binwalk -e banner.bmp
```

## Flag
`NCTF{zip_hides_past_the_pixels}`
