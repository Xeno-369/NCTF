# SHA-256 length extension (pur Python). Forge MAC = SHA256(secret || data || padding || suffix)
# à partir d'un MAC connu SHA256(secret || data), sans connaître secret.
import struct

_K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2]
def _rr(x,n): return ((x>>n)|(x<<(32-n)))&0xffffffff
def _compress(state,block):
    w=list(struct.unpack('>16L',block))
    for i in range(16,64):
        s0=_rr(w[i-15],7)^_rr(w[i-15],18)^(w[i-15]>>3)
        s1=_rr(w[i-2],17)^_rr(w[i-2],19)^(w[i-2]>>10)
        w.append((w[i-16]+s0+w[i-7]+s1)&0xffffffff)
    a,b,c,d,e,f,g,h=state
    for i in range(64):
        S1=_rr(e,6)^_rr(e,11)^_rr(e,25); ch=(e&f)^(~e&g)
        t1=(h+S1+ch+_K[i]+w[i])&0xffffffff
        S0=_rr(a,2)^_rr(a,13)^_rr(a,22); maj=(a&b)^(a&c)^(b&c)
        t2=(S0+maj)&0xffffffff
        h,g,f,e,d,c,b,a=g,f,e,(d+t1)&0xffffffff,c,b,a,(t1+t2)&0xffffffff
    return [(x+y)&0xffffffff for x,y in zip(state,[a,b,c,d,e,f,g,h])]
def _pad(msglen):
    pad=b'\x80'; pad+=b'\x00'*((56-(msglen+1)%64)%64); pad+=struct.pack('>Q',msglen*8); return pad
def extend(orig_mac_hex, orig_len, append, secret_len=None):
    # retourne (nouveau_data_apres_orig, nouveau_mac) ; orig_len = len(secret||data) connu? on prend secret_len+len(data)
    assert secret_len is not None
    total=secret_len+orig_len  # orig_len = len(data)
    glue=_pad(total)
    state=list(struct.unpack('>8L',bytes.fromhex(orig_mac_hex)))
    # nouveau total avant d'ajouter append
    newtotal=total+len(glue)+len(append)
    msg=append+_pad(newtotal)
    for i in range(0,len(msg),64):
        state=_compress(state,msg[i:i+64])
    new_mac=struct.pack('>8L',*state).hex()
    return glue, new_mac   # data forgée = data_original + glue + append
if __name__=='__main__':
    # auto-test vs hashlib
    import hashlib
    secret=b'S3cr3tKey!!'; data=b'user=guest&amount=1'
    mac=hashlib.sha256(secret+data).hexdigest()
    glue,fmac=extend(mac, len(data), b'&user=admin', secret_len=len(secret))
    forged=data+glue+b'&user=admin'
    assert hashlib.sha256(secret+forged).hexdigest()==fmac, 'KO'
    print('auto-test OK ; glue=',glue, '; forged=',forged)
