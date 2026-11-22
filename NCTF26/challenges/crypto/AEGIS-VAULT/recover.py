# Reconstruit r a partir de 24 requetes a confidence. Mode --offline teste la maths.
import sys, json, math
import numpy as np
sys.path.insert(0, 'files')
from model import Vault, D, S, C0
V = Vault('files/weights.npz')
Minv = np.linalg.inv(V.M)

def logit(conf):
    p0, p1 = conf['OTHER'], conf['SEALED']
    return math.log(p1 / p0)   # = s(p) exact

def recover(query):
    # query(list_of_probes) -> list_of_confidence dict ; s-C0 = (1/S^2) p^T M r
    b = np.empty(D)
    probes = []
    for j in range(D):
        p = [0]*D; p[j] = 255
        probes.append(p)
    confs = query(probes)
    for j in range(D):
        s = logit(confs[j])
        b[j] = s - C0                       # = (255/S^2)(M r)_j = (M r)_j /255
    Mr = 255.0 * b                          # (M r)_j
    r = Minv @ Mr
    return r

if __name__ == '__main__' and '--offline' in sys.argv:
    rng = np.random.default_rng(1)
    secret = rng.integers(0, 256, D)
    def q(ps): return [V.confidence(p, secret) for p in ps]
    r = recover(q)
    rr = np.clip(np.rint(r), 0, 255).astype(int)
    print('vrai   ', secret.tolist())
    print('reconst', rr.tolist())
    print('erreur Linf', int(np.max(np.abs(rr - secret))), 'exact', bool((rr==secret).all()))
