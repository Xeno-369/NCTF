import sys, numpy as np
from PIL import Image
im = Image.open('files/affiche.png').convert('RGB')
out = sys.argv[1]
im.crop((70, 950, 200, 972)).resize((1040, 176), Image.NEAREST).save(out + '/legende.png')
a = np.array(im)
bits = (a[:, :, 0] & 1).flatten()
b = np.packbits(bits).tobytes()
L = int.from_bytes(b[:4], 'big')
tail = b[4 + L:]
print('L', L, 'apres message: octets', len(tail), 'distincts', sorted(set(tail))[:12], 'debut', tail[:24].hex())
# zones ou le LSB rouge est porteur vs zones naturelles
print('bits de message occupent', (4 + L) * 8, 'pixels sur la 1re ligne de', a.shape[1])
