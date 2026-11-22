# Vérifie e (sol.txt) contre public.json, puis déchiffre flag_enc selon flag_dec.
import json, re, sys
from hashlib import sha256
d = json.load(open('files/public.json'))
n, w = d['n'], d['w']
R = [int(x, 16) for x in d['H_rows_hex']]
s = int(d['s_hex'], 16)
m = len(R)
line = open(sys.argv[1] if len(sys.argv) > 1 else 'sol.txt').read().strip()
t = int(re.search(r't=(\d)', line).group(1))
pos = [int(x) for x in line.split(':')[1].split()]
e = sum(1 << j for j in pos)
got = sum((bin(R[i] & e).count('1') & 1) << i for i in range(m))
want = s if t == 0 else int(format(s, f'0{m}b')[::-1], 2)
print('t', t, 'poids', bin(e).count('1'), 'attendu', w, 'H.e==s', got == want)
e_be = e.to_bytes(35, 'big')
key = sha256(b'C7|' + e_be).digest()
ct = bytes.fromhex(d['flag_enc_hex'])
ks = b''
ctr = 0
while len(ks) < len(ct):
    ks += sha256(key + b'|' + ctr.to_bytes(4, 'big')).digest()
    ctr += 1
print(bytes(a ^ b for a, b in zip(ct, ks)))
