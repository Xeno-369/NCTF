# shallow (crypto medium) — DH / Pohlig-Hellman, creator: komisergio

**Flag : `NCTF{the_deep_river_was_forded_by_shallow_crossings}`**

## Énoncé
DH près de Sokodé. `pubkey.txt` donne p, g, A=g^x, g_q (générateur du "courant profond",
ordre q). Le griot jure que le secret "chevauche le courant profond" et est increvable.
`river.enc` = flag chiffré. Un oracle ("passeur") existe mais est **inutile**.

## Clé : x est minuscule, pas dans q
`p-1 = 2·3·5·7·11·13·17·19·23·29·31·37·41·43 × q` avec q ~160 bits.
La partie lisse M = produit des petits premiers ≈ 54 bits.
**Pohlig-Hellman sur les petits sous-groupes** (direct sur A, aucun oracle) :
pour chaque petit premier r : résoudre `(A^((p-1)/r)) = (g^((p-1)/r))^(x mod r)` par brute (r≤43),
puis CRT → `x mod M`. Vérif `g^(x mod M) == A` ⇒ x = x mod M = **5899745426912701**.
Le "courant profond" (q) est un leurre : jamais besoin du log discret dans le gros sous-groupe.

## Déchiffrement river.enc
AES-256-CBC, IV = 16 premiers octets, **clé = SHA256(long_to_bytes(x))**, padding PKCS7.
```python
from Crypto.Cipher import AES; import hashlib
x=5899745426912701
def lb(n): h=hex(n)[2:]; return bytes.fromhex(('0'+h) if len(h)%2 else h)
d=open('files/river.enc','rb').read()
k=hashlib.sha256(lb(x)).digest()
print(AES.new(k,AES.MODE_CBC,d[:16]).decrypt(d[16:]))
```

## Leçon
Diffie-Hellman avec `p-1` partiellement lisse + exposant privé petit = Pohlig-Hellman.
Vérifier toujours `g^(x mod smooth)==A` : si vrai, x était entièrement dans la partie lisse.
Cf. mnémo : "L'eau n'a pas changé ; ce sont les questions qui changent" = on attaque les
petits sous-groupes. Voir aussi [[hastad-broadcast]], [[kamina-hastad]] (autres pièges RSA).
