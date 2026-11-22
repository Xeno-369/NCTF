import numpy as np
from PIL import Image
a = np.array(Image.open('files/affiche.png').convert('RGB')).astype(int)
z = a[902:1020, 702:820]
d = (z.sum(axis=2) < 200)
ys, xs = np.nonzero(d)
print('bbox', ys.min()+902, ys.max()+902, xs.min()+702, xs.max()+702)
x0, y0, c = xs.min(), ys.min(), 12
n = (xs.max()-x0+1)//c
m = (ys.max()-y0+1)//c
print('grille', m, n)
for r in range(m):
    print(''.join('#' if d[y0+r*c+6, x0+k*c+6] else '.' for k in range(n)))
ok = all(d[y0+r*c+6, x0+k*c+6] == ((r+k)%2==0) for r in range(m) for k in range(n))
print('damier parfait', ok)
print('couleurs zone', len({tuple(p) for p in z.reshape(-1,3)}))
