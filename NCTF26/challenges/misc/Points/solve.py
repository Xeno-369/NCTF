# Enveloppe convexe (chaîne monotone d'Andrew), lue dans les deux sens, plus couches successives.
import collections
L = open('files/points.txt').read().split('\n')
N = int(L[0])
P = []
for l in L[1:]:
    if not l.strip(): continue
    x, y, c = l.split()
    P.append((int(x), int(y), c))
print('N', N, 'lus', len(P), 'uniques xy', len({p[:2] for p in P}))
def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
def hull(pts):
    pts = sorted(pts)
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and cross(h[-2], h[-1], p) <= 0: h.pop()
            h.append(p)
        return h[:-1]
    return half(pts) + half(pts[::-1])
rest = list(P)
layer = 0
while len(rest) >= 3 and layer < 8:
    h = hull(rest)
    s = ''.join(p[2] for p in h)
    print(f'couche {layer} n={len(h)} ccw={s}')
    for name, t in (('ccw', h), ('cw', h[::-1])):
        c = ''.join(p[2] for p in t)
        i = (c + c).find('NCTF{')
        if i >= 0:
            print('  ->', name, (c + c)[i:i + len(c)], 'depart', t[i][:2])
    hs = set(h)
    rest = [p for p in rest if p not in hs]
    layer += 1
