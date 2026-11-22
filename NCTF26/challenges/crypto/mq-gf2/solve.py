import re, hashlib
from pycryptosat import Solver
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

base='files/'
lines=[l.strip() for l in open(base+'system.txt') if l.strip() and not l.strip().startswith('#')]
NV=57; nextvar=NV+1; pairs={}; and_cl=[]; eqs=[]
for ln in lines:
    ln=ln.replace('= 0','').replace('=0','').strip()
    xs=[]; const=0
    for t in [t.strip() for t in ln.split('+') if t.strip()]:
        if t=='1': const^=1; continue
        m=re.findall(r'x(\d+)',t)
        if '*' in t:
            i,j=sorted((int(m[0]),int(m[1])))
            if (i,j) not in pairs:
                av=nextvar; nextvar+=1; pairs[(i,j)]=av
                and_cl += [[-av,i+1],[-av,j+1],[av,-(i+1),-(j+1)]]
            xs.append(pairs[(i,j)])
        else: xs.append(int(m[0])+1)
    eqs.append((xs,const))
print('eqs',len(eqs),'monomes quad',len(pairs))
s=Solver(threads=4)
for c in and_cl: s.add_clause(c)
for xs,const in eqs: s.add_xor_clause(xs, bool(const))
sat,sol=s.solve()
print('SAT',sat)
bits=[1 if sol[i+1] else 0 for i in range(NV)]
print('x0..x56:',''.join(map(str,bits)))

ct=bytes.fromhex(open(base+'vault.txt').read().split('ciphertext =')[1].strip())
nonce=bytes.fromhex([l for l in open(base+'vault.txt') if 'nonce' in l][0].split('=')[1].strip())
def intbits(bits): 
    v=0
    for b in bits: v=(v<<1)|b
    return v
candidates={}
v=intbits(bits)
candidates['8B x0=MSB(bit56)']=v.to_bytes(8,'big')
candidates['8B left-align x0=MSB(bit63)']=(v<<7).to_bytes(8,'big')
candidates['minlen big']=v.to_bytes((v.bit_length()+7)//8,'big')
# reversed bit order
vr=intbits(bits[::-1])
candidates['8B reversed']=vr.to_bytes(8,'big')
for name,sb in candidates.items():
    key=hashlib.sha256(sb).digest()
    try:
        pt=AESGCM(key).decrypt(nonce,ct,None)
        print('*** OK',name,'->',pt)
    except Exception as e:
        pass
