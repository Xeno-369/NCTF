# authlog (auth.log — intrusion SSH)

- Catégorie : forensics
- Résolu : sam. 07 nov.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/auth.log | 0c74a677b54979255e107d2ba9eec92283379155866733955377c3a249047445 |

## Analyse
- Bruit : milliers de "Failed password" (brute-force internet).
- Vraie intrusion : "Accepted password for root from 203.0.113.45" (root par MOT DE PASSE), session sshd[25605].
- Commande de l'intrus (audit[25605] USER_CMD) :
  echo ZmxhZz1...fQ== | base64 -d > /root/.ok
  -> base64 décode en "flag=NCTF{brut3f0rc3_th3n_succ3ss_0n_r00t}".
- Leurres : USER_CMD des sessions publickey deploy/ubuntu/git = admin légitime (systemctl restart nginx, tail syslog, git pull).

## Flag
`NCTF{brut3f0rc3_th3n_succ3ss_0n_r00t}`
