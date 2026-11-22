# firewall-acl (ruleset.json)

- **Catégorie :** misc
- **Résolu :** sam. 07 nov.

## Énoncé
ACL firewall + flux candidats (ruleset.json). Déterminer les flux réellement laissés passer ; tags des flux acceptés, par id croissant = flag.

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/ruleset.json | c52319eec4a29e930df9ad0082f26a5b20dc1d2d5ea88987724a16ff84850dfc |

## Résolution
Politique : first-match-wins, DENY implicite par défaut. 7 règles, 83 flux.
Pour chaque flux : première règle qui matche (src CIDR, dst CIDR, proto [any], dport [any/num]) -> action.
Aucune correspondance -> deny. 39 flux acceptés, triés par id, tags concaténés.

## Commande
```bash
python3 -I solve.py
```

## Flag
`NCTF{acl_first_match_wins_default_deny}`
