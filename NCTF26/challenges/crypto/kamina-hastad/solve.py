#!/usr/bin/env python3
# kamina : e=3, 3 ciphertexts identiques => m = cuberoot(C) ; flag dans la note XOR.
import base64

C = 1105065419768621914303167724317305126870039587753981868761793285366001341802347543781199112429559217683098895108076993514328071448234593785050119246360128516206051556904807714109738558174107966929666316193359361231648587083427437

def iroot(x, n):
    lo, hi = 0, 1 << ((x.bit_length()//n)+2)
    while lo < hi:
        mid = (lo+hi)//2
        if mid**n < x: lo = mid+1
        else: hi = mid
    return lo

m = iroot(C, 3)
assert m**3 == C, "pas un cube parfait"
h = hex(m)[2:]; h = ('0'+h) if len(h) % 2 else h
print('orders RSA (m):', bytes.fromhex(h))   # 32 octets binaires

# note perso = XOR répété clé KAMINA1914
blob = 'BQIZDzU1WVxuRyosKBYhM1VcQ2s/LhI9JjNUXG5EJDI5OhE0X0pUVSckKRY6KVRmUF05Niw/KzJM'
data = base64.b64decode(blob)
key = b'KAMINA1914'
flag = bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))
print('FLAG:', flag.decode())
