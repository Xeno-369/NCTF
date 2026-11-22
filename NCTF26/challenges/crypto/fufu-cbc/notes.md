# fufu-cbc (bit-flipping AES-CBC sur IV)

- Catégorie : crypto / web
- Résolu : sam. 07 nov.

## Énoncé
Cookie IV||ciphertext AES-CBC encode le rôle, non authentifié. Passer de guest à admin via l'IV. Endpoints: GET /profile (donne un cookie), GET /admin?cookie=...

## Attaque
P0 = AES_dec(C0) XOR IV. Modifier l'IV change le 1er bloc de plaintext.
"guest" est à l'offset 10 du bloc 0 (plaintext ~ {"role": "guest"...).
new_IV[10+k] = IV[10+k] XOR ("guest"[k] XOR "admin"[k]) pour k=0..4.
/admin?cookie=<IV'||CT> -> {"role":"admin"} -> flag. (Offset trouvé par brute 0..11.)

## Flag
`NCTF{86ab0a364b5a0d47870923a5}`
