# postcard (postcard.bmp)

- Catégorie : forensics / stégo LSB
- Résolu : sam. 07 nov.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/postcard.bmp | b0c7c2ce7c66c692540fc4839a85b56d2f8fdb799a9d08f2c9a1fae4ddd5c81d |

## Résolution
BMP 96x64 24-bit (dégradé). Message en LSB du canal BLEU (b1,b,lsb). `zsteg postcard.bmp`.
Vérifié avec numpy (packbits sur canal B & 1).

## Flag
`NCTF{lsb_blue_channel_whispers}`
