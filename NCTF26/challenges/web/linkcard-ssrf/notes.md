# LinkCard (web) — SSRF + bypass filtre d'hôte, creator: isid0r3

**Flag : `NCTF{dcf4a4146e51b772dee6b886}`**

## Cible
`https://<id>.t.ctf.tg/` — fil social "LinkCard". Login/register (captcha = X+Y stocké en session).
Poster un message : **les URLs deviennent une carte de preview** → le serveur fetch l'URL
(SSRF) et affiche son `<title>`. Canal de fuite = le titre uniquement.

## Exploit
1. Register (parser "combien font X + Y ?") + login.
2. Poster un message contenant : `http://127.1:8081/`
3. La carte de preview montre : `LinkCard Internal Admin — NCTF{dcf4a4146e51b772dee6b886}`

## Démarche
- SSRF confirmé (preview de example.com OK).
- Filtre d'hôte : `127.0.0.1`/`localhost`/`0.0.0.0`/`[::1]`/`LOCALHOST` → "hôte non autorisé"
  (blocklist de chaînes). **Bypass** : `127.1`, `2130706433` (décimal), `0x7f000001` (hexa),
  `0177.0.0.1` (octal), `127.0.0.1.nip.io`, `localtest.me`.
- Les messages d'erreur du preview = oracle d'état : titre (200), "302 reçue",
  "404 Not Found", "connexion refusée" (port fermé), "hôte non autorisé".
- Scan de ports via le SSRF : 80 (landing statique), 5000 (app Flask, / → 302 login),
  **8081 = LinkCard Internal Admin** (flag dans le `<title>`).

## Leçon
Filtre SSRF par blocklist de chaînes = contournable (127.1 / IP décimale / nip.io).
L'admin interne sur un port non exposé reste atteignable par SSRF. Canal restreint au
`<title>` → scanner les ports par les messages d'erreur du preview. Cf. [[linkify-ssrf]]
(même créateur, /internal/flag) et [[ingestd-deser]].
