# Convertit public.json en instance pour isd.c. Mode test : planter un e connu de poids w.
import json, random, sys
d = json.load(open(sys.argv[1]))
n, k, w = d['n'], d['k'], d['w']
R = [int(x, 16) for x in d['H_rows_hex']]
m = len(R)
s = int(d['s_hex'], 16)
if len(sys.argv) > 3:                     # test : <poids>
    w = int(sys.argv[3])
    R = [random.getrandbits(n) for _ in range(m)]
    e = sum(1 << j for j in random.sample(range(n), w))
    s = sum((bin(R[i] & e).count('1') & 1) << i for i in range(m))
    print('planted', sorted(j for j in range(n) if e >> j & 1), file=sys.stderr)
srev = int(format(s, f'0{m}b')[::-1], 2)  # t=1 : ligne 0 = bit de poids fort de s
with open(sys.argv[2], 'w') as f:
    f.write(f'{n} {m} {w}\n')
    for i, r in enumerate(R):
        x = r | ((s >> i & 1) << n) | ((srev >> i & 1) << (n + 1))
        f.write(' '.join(f'{(x >> (64 * b)) & (2**64 - 1):x}' for b in range(5)) + '\n')
