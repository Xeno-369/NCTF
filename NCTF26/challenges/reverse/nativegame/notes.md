# nativegame (APK JNI)

- **Catégorie :** reverse (Android natif)
- **Résolu :** sam. 07 nov.

## Énoncé
nativegame.apk valide le flag dans une lib native. Routine JNI décompilée + assets/enc.bin fournis. Retrouver l'entrée acceptée = le flag.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/nativegame.apk | 463dae08242c68d4ab1e9b0af979ea132265883a0a1eb9d353c5120b2ca6c721 |

## Transformation (JNI_checkFlag)
Par octet i : t=(flag[i]+i)&0xff ; t^=KEY[i%6] ; enc[i]=SBOX[t]. Comparé à enc.bin.
KEY=13 37 42 9a 5c e1. SBOX = table 256 (rodata).

## Inversion
INV=SBOX^-1 ; flag[i]=((INV[enc[i]]^KEY[i%6])-i)&0xff. Vérifié en sens direct.

## Flag
`NCTF{n4t1v3_x0r_t4bl3_unr0ll3d}`
