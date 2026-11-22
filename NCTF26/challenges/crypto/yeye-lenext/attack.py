import http.client, ssl, struct, urllib.parse, sys, time
HOST='bwitph2ipsyqdnbr.t.ctf.tg'
orig=b'amount=1000&user=guest'; mac='b4776addd3c88ddbf4df5830d5a36a083ce90cefd30ba03612a2c6627b2c26bd'; append=b'&user=admin'
_K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2]
def rr(x,n): return ((x>>n)|(x<<(32-n)))&0xffffffff
def comp(st,blk):
    w=list(struct.unpack('>16L',blk))
    for i in range(16,64):
        s0=rr(w[i-15],7)^rr(w[i-15],18)^(w[i-15]>>3); s1=rr(w[i-2],17)^rr(w[i-2],19)^(w[i-2]>>10); w.append((w[i-16]+s0+w[i-7]+s1)&0xffffffff)
    a,b,c,d,e,f,g,h=st
    for i in range(64):
        S1=rr(e,6)^rr(e,11)^rr(e,25); ch=(e&f)^(~e&g); t1=(h+S1+ch+_K[i]+w[i])&0xffffffff
        S0=rr(a,2)^rr(a,13)^rr(a,22); mj=(a&b)^(a&c)^(b&c); t2=(S0+mj)&0xffffffff
        h,g,f,e,d,c,b,a=g,f,e,(d+t1)&0xffffffff,c,b,a,(t1+t2)&0xffffffff
    return [(x+y)&0xffffffff for x,y in zip(st,[a,b,c,d,e,f,g,h])]
def pad(ln): return b'\x80'+b'\x00'*((56-(ln+1)%64)%64)+struct.pack('>Q',ln*8)
def forge(sl):
    total=sl+len(orig); glue=pad(total); st=list(struct.unpack('>8L',bytes.fromhex(mac)))
    nt=total+len(glue)+len(append); m=append+pad(nt)
    for i in range(0,len(m),64): st=comp(st,m[i:i+64])
    return orig+glue+append, struct.pack('>8L',*st).hex()
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
def req(path):
    for _ in range(3):
        try:
            c=http.client.HTTPSConnection(HOST,context=ctx,timeout=12); c.request('GET',path); r=c.getresponse(); b=r.read().decode(errors='replace'); c.close(); return r.status,b
        except Exception: time.sleep(1)
    return 0,'TIMEOUT'
for sl in range(96,257):
    forged,fmac=forge(sl)
    path='/pay?msg='+urllib.parse.quote(forged,safe='')+'&mac='+fmac
    code,body=req(path)
    if 'NCTF' in body or (code==200 and 'bad' not in body.lower()):
        print('*** HIT secret_len',sl,code,body[:300],flush=True); break
    if sl%16==0: print('...',sl,'dernier:',code,body[:20],flush=True)
else: print('rien 1..96',flush=True)
