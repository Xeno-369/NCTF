# breach (nctf_breach_investigation.pcapng — keylogger C2)

- Catégorie : forensics réseau
- Résolu : sam. 07 nov.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/nctf_breach_investigation.pcapng | b1d18e3491f9c0d38c5c10f50484ef09da8bf3ef9d03cbc1d798f1722e2fe30c |

## Analyse
- GET /keylogger.py (text/x-python) depuis C2 nctf-hotel.thm = script malveillant.
- keylogger.py : chaque frappe -> XOR(clé "NCTF2026S3cr3t"+"K3yL0gg3r!") -> base64 -> exfil dans en-tête Cookie: nctf_data=<b64> (1 frappe/requête).
- Les requêtes DNS (google, dropbox...) = bruit/leurre.

## Déchiffrement
tshark -Y http.request -e http.cookie ; pour chaque nctf_data : base64decode puis XOR(clé) ; concaténer dans l'ordre des frames = frappes = flag.
Clé = NCTF2026S3cr3tK3yL0gg3r!

## Flag
`NCTF{k3yl0gg3r_3xf1ltr4t10n_c00k13s}`
