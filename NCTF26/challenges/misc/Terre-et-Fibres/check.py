import hashlib, itertools, re
import numpy as np
from PIL import Image
a = np.array(Image.open('files/affiche.png').convert('RGB')).astype(int)
# glyphes légende : colonnes de carrés
sub = a[955:970, 70:200].sum(axis=2)
dark = (sub < 500).any(axis=0)
runs = []; x = None
for i, d in enumerate(list(dark) + [False]):
    if d and x is None: x = i
    if not d and x is not None: runs.append((x + 70, i + 70)); x = None
print('runs', runs)
tof = [r for r in runs if r[1] - r[0] >= 4]
crops = {r: a[955:970, r[0]:r[1], :].tobytes() for r in tof}
print('larges', tof, 'distincts', len(set(crops.values())))
# fin de fichiers
b = open('files/affiche.png', 'rb').read()
i = b.rindex(b'IEND') + 8
print('apres IEND', len(b) - i)
p = open('files/guide-motifs.pdf', 'rb').read()
print('apres EOF', len(p) - p.rindex(b'%%EOF') - 5, 'taille flux decl 418 reel', p.index(b'endstream') - p.index(b'stream') - 7)
print('non-ascii pdf', [hex(c) for c in p if c > 126])
print('tous tEXt', re.findall(rb'(?:tEXt|iTXt)[^\x00]+\x00[^\x00]*', b[:0x140]))
# hash : ○ = n'importe quel hex, casse variable, nombreuses sources
bases = ['D4P40NG_T1SS3R4NDS','d4p40ng_t1ss3r4nds','NCTF{D4P40NG_T1SS3R4NDS','DAPAONG_TISSERANDS','dapaong_tisserands','Dapaong Terre & Fibres','Dapaong Terre et Fibres','dapaong-terre-fibres','affiche','Terre-et-Fibres','terre-et-fibres','Terre & Fibres','tisserands','Tisserands','NCTF','NCTF26','nctf26','C7']
pat = re.compile('29549db55.2c')
for s in bases:
    for h in ('md5', 'sha1', 'sha256', 'sha512', 'blake2b', 'sha3_256'):
        d = hashlib.new(h, s.encode()).hexdigest()
        if pat.search(d): print('MATCH', s, h, d)
print('fin hash')
