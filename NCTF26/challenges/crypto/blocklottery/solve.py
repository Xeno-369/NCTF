import json
from keccak import keccak256
d=json.load(open('files/draw.json')); b=d['block']; ct=bytes.fromhex(d['cipher_hex']); n=len(ct)
packed=b['timestamp'].to_bytes(32,'big')+b['number'].to_bytes(32,'big')+int(b['prevrandao'],16).to_bytes(32,'big')
ticket=keccak256(packed)
ks=b''; c=0
while len(ks)<n: ks+=keccak256(ticket+c.to_bytes(4,'big')); c+=1
print(bytes(x^y for x,y in zip(ct,ks[:n])).decode())
