# uart (capture.csv, logic analyzer)

- **Catégorie :** reverse / hardware (signaux)
- **Résolu :** sam. 07 nov.

## Énoncé
Dump logic analyzer d'une ligne série. Colonnes time_ns, d0_uart, d1_refclk. Un court message ASCII est transmis. Le flag = le texte.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/capture.csv | 35c15f59bef8dfe72c6c5e2516059553fea7d2546fcf3e35a34369bb42bdeed8 |

## Résolution
- Échantillonnage 1 MHz (pas 1 µs). d1_refclk = horloge 6 µs (166 kHz), non utilisée.
- Transitions de d0 toutes multiples de **8000 ns** => période de bit = 8 µs => **125000 baud**.
- Décodage UART **8N1, LSB first** : idle=1, start=0, 8 bits data LSB d'abord, stop=1.
- Échantillonnage au centre de chaque bit (start + T*(k+1.5)).

## Commande
```bash
python3 solve.py
```

## Flag
`NCTF{uart_8n1_lsb_first_125k}`
