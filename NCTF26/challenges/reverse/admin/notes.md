# admin (chall, bss overflow)

- Catégorie : reverse / pwn
- Résolu : sam. 07 nov. (statique)

## Énoncé
Binaire x86-64. Enregistrer un nom, le flag est réservé aux admins. Devenir admin et lire ce qu'il affiche.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/chall | 6d389981f805415da116f5094f686722ec7c2a0e01b4fc28f77cc182899e9b93 |

## Faille
.bss : user @0x404060, is_admin @0x4040a0 = user+0x40 (offset 64), mis à 0 au départ.
read(0, user, 0x80) lit 128 octets -> dépasse offset 64 -> écrase is_admin.
is_admin != 0 -> reveal(). Envoyer 65 octets (64 padding + 1 non nul).

## reveal()
Déchiffre 0x23=35 octets de enc @0x402040 par XOR 0x3c. Flag obtenu statiquement.

## Commande
```bash
python3 -c "import sys;sys.stdout.buffer.write(b'A'*0x40+b'\x01')" | ./chall
```

## Flag
`NCTF{bss_overflow_flipped_is_admin}`
