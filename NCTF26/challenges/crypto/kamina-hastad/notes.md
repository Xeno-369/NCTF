# kamina / "orders" (crypto) — station Kamina, août 1914

**Flag : `NCTF{the_same_order_to_three_posts_unsealed_the_airwaves}`**

## Énoncé
3 postes relais (Lomé, Palimé, Sokodé) reçoivent **le même message scellé**.
Fichiers : `orders.enc`, `pubkey.txt` (n1,n2,n3 + e=3), `vigenere_note.txt`.
"L'opérateur a laissé une note perso bien en vue. Il en était fier."

## Observation clé
`e = 3` et les **3 ciphertexts sont identiques** (c1 = c2 = c3 = C).
Donc `m^3` n'a jamais été réduit modulo n (m^3 < n_i) → **C = m^3 dans ℤ**.
→ racine cubique entière : `m = C^(1/3)` (exacte). C'est le Håstad dégénéré.
`m` = 32 octets binaires (les "orders" RSA bruts — pas le flag).

## Le flag est dans la note de l'opérateur
`vigenere_note.txt` : clé `KAMINA1914`, blob base64. Le "vieux chiffre de la Marne"
n'est pas un Vigénère alphabétique mais un **XOR répété** avec la clé.
```
base64 -> octets, puis octet[i] XOR KAMINA1914[i % 10]  ->  flag ASCII
```
→ `NCTF{the_same_order_to_three_posts_unsealed_the_airwaves}`

## Leçon
Même plaintext + petit exposant e=3 + chiffrés identiques = cassage trivial par racine
cubique (Håstad broadcast quand les C diffèrent → CRT puis racine cubique).
