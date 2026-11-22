# lock-sh (lock.sh)

- Catégorie : misc (crypto/shell)
- Résolu : sam. 07 nov. (statique, script non exécuté)

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/lock.sh | c39547a291dd631f1a1eda4fa47b09a5d4611cc179c96e64666fac101606a1be |

## Résolution
- \_k = hex ; password = octets de \_k XOR 0x2a = "sh3ll_w1zard".
- flag = base64decode(\_b) XOR password (clé répétée).
- Tout calculé hors ligne, sans lancer le script.

## Flag
`NCTF{sh3ll_self_d3crypt_pe3led}`
