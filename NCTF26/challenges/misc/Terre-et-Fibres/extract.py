# Extrait le message LSB du canal rouge : uint32 big-endian (longueur) puis UTF-8.
import sys, numpy as np
from PIL import Image
a = np.array(Image.open('files/affiche.png').convert('RGB'))
print('shape', a.shape, 'couleurs', len(np.unique(a.reshape(-1, 3), axis=0)))
for ch, nom in enumerate('RGB'):
    for bp in (0, 1):
        bits = ((a[:, :, ch] >> bp) & 1).astype(np.uint8)
        for order, label in (('msb', 'msb'), ('lsb', 'lsb')):
            b = np.packbits(bits.flatten(), bitorder='big' if order == 'msb' else 'little').tobytes()
            L = int.from_bytes(b[:4], 'big')
            print(nom, 'bit', bp, label, 'L', L, 'head', b[:12].hex(), 'ones', round(float(bits.mean()), 3))
            if 0 < L < len(b) - 4:
                try:
                    t = b[4:4 + L].decode('utf-8')
                    print('  TEXTE', repr(t))
                except Exception as e:
                    print('  bytes', b[4:4 + min(L, 60)], e)
