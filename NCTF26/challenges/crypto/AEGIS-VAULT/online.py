#!/usr/bin/env python3
# Usage: python3 online.py https://<id>.t.ctf.tg
# 24 requetes /query (probe = 255*e_j) -> s(p) exact -> record ; puis /submit.
import sys, json, math, urllib.request
import numpy as np
sys.path.insert(0, 'files')
from model import Vault, D, C0

BASE = sys.argv[1].rstrip('/')
V = Vault('files/weights.npz')
Minv = np.linalg.inv(V.M)

def post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

b = np.empty(D)
for j in range(D):
    probe = [255 if k == j else 0 for k in range(D)]
    c = post('/query', {'probe': probe})['confidence']
    b[j] = math.log(c['SEALED'] / c['OTHER']) - C0     # = (M r)_j / 255
    print(f'  probe {j:2d}  s={b[j]+C0:+.6f}')
r = Minv @ (255.0 * b)
rec = np.clip(np.rint(r), 0, 255).astype(int).tolist()
print('record reconstruit :', rec)
print('residu max au rint :', float(np.max(np.abs(r - np.rint(r)))))
out = post('/submit', {'record': rec})
print('submit ->', json.dumps(out, ensure_ascii=False))
