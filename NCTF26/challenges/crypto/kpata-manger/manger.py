import http.client, ssl, json, time, hashlib
HOST='l726eaofb7dbvwt4.t.ctf.tg'
ctx=ssl._create_unverified_context()
conn=None
def _newconn():
    global conn
    try:
        if conn: conn.close()
    except: pass
    conn=http.client.HTTPSConnection(HOST,context=ctx,timeout=20)
def get(path):
    global conn
    for att in range(30):
        try:
            if conn is None: _newconn()
            conn.request('GET',path); r=conn.getresponse(); return json.loads(r.read().decode())
        except Exception:
            _newconn(); time.sleep(min(0.2*(att+1),3))
    raise RuntimeError('fail definitif')
ch=get('/challenge'); n=ch['n']; e=ch['e']; c0=ch['c']
k=(n.bit_length()+7)//8; B=1<<(8*(k-1))
print('k',k,'2B<n',2*B<n,flush=True)
cnt=[0]
def oracle_less(f):
    c=(pow(f,e,n)*c0)%n; cnt[0]+=1
    if cnt[0]%100==0: print('...req',cnt[0],flush=True)
    return get('/oracle?c=%d'%c)['valid']==True
# Step 1
f1=2
while oracle_less(f1): f1*=2
print('step1 done f1 bits',f1.bit_length(),'req',cnt[0],flush=True)
# Step 2
f2=((n+B)//B)*(f1//2)
while not oracle_less(f2): f2+=f1//2
print('step2 done req',cnt[0],flush=True)
# Step 3
mmin=-(-n//f2); mmax=(n+B)//f2
while mmin<mmax:
    ftmp=(2*B)//(mmax-mmin); i=(ftmp*mmin)//n; f3=-(-(i*n)//mmin)
    if oracle_less(f3): mmax=(i*n+B)//f3
    else: mmin=-(-(i*n+B)//f3)
print('step3 done req',cnt[0],flush=True)
m0=mmin; EM=m0.to_bytes(k,'big'); open('EM.bin','wb').write(EM)
print('EM[:3]',EM[:3].hex(),flush=True)
def mgf1(seed,ln,h):
    out=b''; i=0
    while len(out)<ln: out+=hashlib.new(h,seed+i.to_bytes(4,'big')).digest(); i+=1
    return out[:ln]
for hname in ('sha256','sha1'):
    hlen=hashlib.new(hname).digest_size; lhash=hashlib.new(hname,b'').digest()
    maskedSeed=EM[1:1+hlen]; maskedDB=EM[1+hlen:]
    seed=bytes(a^b for a,b in zip(maskedSeed,mgf1(maskedDB,hlen,hname)))
    DB=bytes(a^b for a,b in zip(maskedDB,mgf1(seed,k-1-hlen,hname)))
    if DB[:hlen]==lhash:
        rest=DB[hlen:]; idx=rest.find(b'\x01'); print('FLAG (',hname,'):',rest[idx+1:],flush=True); break
    else: print('mismatch',hname,DB[:hlen].hex()[:16],'vs',lhash.hex()[:16],flush=True)
