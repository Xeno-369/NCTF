import numpy as np
from PIL import Image
from collections import Counter
a = np.array(Image.open('files/affiche.png').convert('RGB')).astype(int)
L = int.from_bytes(np.packbits(a[:,:,0].flatten() & 1).tobytes()[:4], 'big')
msg = np.packbits((a[:,:,0].flatten() & 1).astype(np.uint8)).tobytes()[4:4+L]
print('msg', msg)
# bandes : colonne x=450 (hors texte)
col = a[:, 450]
bands = []
y = 0
bg = tuple(a[300-1, 50]) 
print('fond bandes', bg)
ys = []
for y in range(190, 900):
    c = tuple(col[y])
    if not ys or c != ys[-1][1]:
        ys.append([y, c])
for i, (y, c) in enumerate(ys):
    print(y, c, end=' | ')
print()
stripes = [(y, c) for y, c in ys if c[2] < 100]
print('nb bandes', len(stripes))
rows = []
for i, (y, c) in enumerate(stripes):
    m = msg[i] if i < len(msg) else None
    # chaque bande : couleurs distinctes sur toute sa largeur et hauteur
    seg = a[y:y+10, 60:840].reshape(-1, 3)
    u = Counter(map(tuple, seg))
    rows.append((i, y, c, m, chr(m) if m and 32 <= m < 127 else m, len(u)))
    print(i, y, c, 'msg', m, chr(m) if m and 32 <= m < 127 else '.', 'hexR', hex(c[0]), 'G', hex(c[1]), 'B', hex(c[2]), 'couleurs', len(u), u.most_common(3))
# LSB G/B non nuls
for ch, nom in ((1, 'G'), (2, 'B')):
    ys2, xs = np.nonzero(a[:, :, ch] & 1)
    print(nom, 'n', len(ys2), 'bbox', ys2.min(), ys2.max(), xs.min(), xs.max(), 'lignes', sorted(Counter(ys2.tolist()).items())[:20])
# hors message : LSB R par zone
r = a[:, :, 0] & 1
print('LSB R par ligne (1res):', [int(r[y].sum()) for y in range(0, 8)], 'ligne 0 fin', r[0, 340:360].tolist())
print('moyenne LSB R hors zone texte, ligne 300', r[300].mean(), 'ligne 1100', r[1100].mean())
