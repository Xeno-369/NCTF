import json, hashlib, math
from keccak import keccak256
d=json.load(open('files/token_state.json'))
bal=d['victim_balance']; allow=d['your_allowance']; ct=bytes.fromhex(d['cipher_hex'])
n=len(ct); N=math.ceil(bal/allow)
amounts=[allow]*(bal//allow)+([bal%allow] if bal%allow else [])
ints=[N, bal//allow, bal, allow, len(amounts), sum(amounts), bal%allow, N*allow]
raws=[]
for v in ints:
    raws += [str(v).encode(), str(v).encode().hex().encode(),
             int(v).to_bytes(32,'big'), int(v).to_bytes(32,'little'),
             int(v).to_bytes((int(v).bit_length()+7)//8 or 1,'big')]
for pre in (b'drift',b'DriftToken',b'DriftToken|',b'drift|',b'NCTF|',b'note|',b'key|'):
    for v in ints: raws.append(pre+str(v).encode())
raws.append(str(amounts).encode()); raws.append(','.join(map(str,amounts)).encode())
def streams(key):
    outs=[]
    if key: outs.append(('rawrep',(key*((n//len(key))+1))[:n]))
    for name,H in (('sha256',lambda b:hashlib.sha256(b).digest()),('keccak',keccak256),('sha3',lambda b:hashlib.sha3_256(b).digest())):
        dig=H(key); outs.append((name+'-rep',(dig*((n//32)+1))[:n]))
        for sep in (b'', b'|'):
            o=b''; c=0
            while len(o)<n: o+=H(key+sep+c.to_bytes(4,'big')); c+=1
            outs.append((name+'-ctr'+('p' if sep else ''), o[:n]))
    return outs
hit=False
for raw in raws:
    if not raw: continue
    for name,ks in streams(raw):
        pt=bytes(a^b for a,b in zip(ct,ks))
        if b'NCTF{' in pt:
            print('HIT raw=',repr(raw),'scheme=',name,'\nFLAG=',pt.decode('latin1')); hit=True; break
    if hit: break
if not hit: print('N=',N,'sum=',sum(amounts),'-> aucun hit, elargir')
