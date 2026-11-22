# admin-note (web medium) — creator: isid0r3

**Flag : `NCTF{31315d816bdf5bacf7cc54c1}`**

## Cible
App Flask "Carnet" (notes). Auth par **JWT RS256** en cookie `token`.
- Header JWT : `{"alg":"RS256","jku":"/.well-known/jwks.json","kid":"carnet-notes-key-1"}`
- Payload : `{"sub","uid","role":"member",...}` → but : passer `role:admin`.
- Footer + header exposent `/.well-known/jwks.json` (clé publique RSA).
- Chaque note publique a une page `/notes/<id>/raw` → **text/plain, contenu brut, accessible anonymement**.

## Vulnérabilité : injection `jku` (JWT key confusion)
Le serveur récupère la clé de vérification depuis l'URL du header `jku`. Il n'exige qu'une
URL **même-origine en chemin relatif** (l'absolu `https://host/...` est rejeté). On héberge
donc notre propre JWKS sur une note publique.

## Exploit (voir solve.py)
1. Générer une paire RSA 2048.
2. Créer une note **publique** dont le contenu = `{"keys":[{...ma clé pub...,"kid":"pwn"}]}`.
   → URL `jku = /notes/<id>/raw`.
3. Forger un JWT : header `{"alg":"RS256","jku":"/notes/<id>/raw","kid":"pwn"}`,
   payload copié du token member avec `role=admin`, signé **avec ma clé privée**.
4. `GET /admin` avec le token forgé → 200 (accès admin).
   La note admin `8a5c7105-efea-4b6f-972d-7673f78e18a3` contient le flag.

## Pièges
- La note doit être **publique** : le serveur fetch le `jku` **sans** notre cookie.
- `jku` **relatif** obligatoire (absolu même-origine → rejeté, redirige /admin en 302).
- Le cookie `session` (Flask) reste nécessaire à côté du `token` forgé.
