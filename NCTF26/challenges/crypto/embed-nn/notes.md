# embed-nn (embed_table.npz)

- **Catégorie :** crypto / ml
- **Résolu :** sam. 07 nov.

## Énoncé
embed_table.npz : table d'embeddings de tokens (chacun un caractère) + un batch de queries bruitées. Chaque query vient d'exactement un token. Décoder chaque query vers son token, dans l'ordre = flag.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/embed_table.npz | 16d5ed7e2008b0964ff9753d778a3549126005ff40f8944d8475e3397d6780ac |

## Résolution
- embeddings (43,16), token_char (43,) = codes ASCII, queries (38,16).
- Pour chaque query : plus proche embedding (distance euclidienne), lire token_char -> caractère.
- Euclidien et cosinus donnent le même résultat (robuste).

## Commande
```bash
python3 solve.py
```

## Flag
`NCTF{cosine_hop_walks_the_token_chain}`
