# npm-typosquat (package-lock + .tgz)

- Catégorie : forensics / supply-chain npm
- Résolu : sam. 07 nov.

## Énoncé
package-lock.json + tous les .tgz verrouillés. Une dépendance n'est pas ce qu'elle prétend. La trouver, ouvrir son archive, récupérer le flag.

## Analyse
- Tous les integrity (sha512) matchent les .tgz fournis -> pas un mismatch de hash.
- La fraude = typosquat : node_modules/**expres** (sans 2e s), version inexistante 4.18.9,
  resolved depuis **npm-registry-mirror.dev** (pas registry.npmjs.org).
- expres-4.18.9.tgz : package/index.js cache var _p (base64) ; obfuscation = ROT13 sur la chaîne base64 puis décodage.

## Flag
`NCTF{typ0squ4t_expres_not_express_7c2e}`
