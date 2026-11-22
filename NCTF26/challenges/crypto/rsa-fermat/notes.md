# rsa-fermat (pubkey.pem + ciphertext.txt)

- Catégorie : crypto / RSA
- Résolu : sam. 07 nov.

## Faille
RSA 1024 textbook, e=65537. p et q très proches -> factorisation de Fermat réussit en 1 itération.
d=e^-1 mod (p-1)(q-1) ; m=c^d mod n.

## Flag
`NCTF{fermat_factoring_when_p_and_q_are_neighbours}`
