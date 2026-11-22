#!/usr/bin/env python3
# MD5 length-extension sur /sign -> /admin. Autonome. python3 agbale.py [url]
import sys, ssl, json, re, struct, math, urllib.request, urllib.parse

B = (sys.argv[1] if len(sys.argv)>1 else "https://j6v5uatoxkxuqdd3.t.ctf.tg").rstrip("/")
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
def get(path):
    return urllib.request.urlopen(urllib.request.Request(B+path),context=CTX,timeout=20).read().decode("utf-8","replace")

# ---- MD5 resumable ----
_s=[7,12,17,22]*4+[5,9,14,20]*4+[4,11,16,23]*4+[6,10,15,21]*4
_K=[int(abs(math.sin(i+1))*2**32)&0xffffffff for i in range(64)]
def _comp(st,blk):
    a,b,c,d=st; M=struct.unpack('<16I',blk); A,B,C,D=a,b,c,d
    for i in range(64):
        if i<16:f=(B&C)|(~B&D);g=i
        elif i<32:f=(D&B)|(~D&C);g=(5*i+1)%16
        elif i<48:f=B^C^D;g=(3*i+5)%16
        else:f=C^(B|(~D&0xffffffff));g=(7*i)%16
        f=(f+A+_K[i]+M[g])&0xffffffff;A=D;D=C;C=B
        B=(B+(((f<<_s[i])|(f>>(32-_s[i])))&0xffffffff))&0xffffffff
    return [(a+A)&0xffffffff,(b+B)&0xffffffff,(c+C)&0xffffffff,(d+D)&0xffffffff]
def pad(n):
    p=b'\x80'+b'\x00'*((56-(n+1)%64)%64)+struct.pack('<Q',n*8);return p
def extend(h,add,prefix_len):
    st=list(struct.unpack('<4I',bytes.fromhex(h)))
    processed=prefix_len+len(pad(prefix_len))
    data=add+pad(processed+len(add))
    for i in range(0,len(data),64): st=_comp(st,data[i:i+64])
    return struct.pack('<4I',*st).hex()

# ---- 1) /sign : recupere message + signature ----
raw = get("/sign"); print("[/sign] ", raw[:300])
j = json.loads(raw)
mkey = next((k for k in ("message","msg","data","token","cmd","command","text","user","profile") if k in j), None)
skey = next((k for k in ("sig","signature","mac","hash","tag","hmac","token") if k in j and k!=mkey), None)
message = j[mkey].encode(); sig = j[skey]
print(f"[*] mkey={mkey} skey={skey}\n[*] message={message!r}\n[*] sig={sig}")

# ---- 2) forge + soumet ----
appends=[b"&role=admin",b"&admin=true",b"&admin=1",b";role=admin",b"&is_admin=1",b"&role=admin&x=",b"admin=true",b"&user=admin"]
def hit(resp):
    m=re.search(r"NCTF\{[^}]*\}",resp)
    if m: print("\n[+] FLAG:",m.group()); return True
    return False

found=False
for klen in range(1,65):
    for add in appends:
        newmsg = message + pad(klen+len(message)) + add
        newsig = extend(sig, add, klen+len(message))
        q = f"/admin?{mkey}={urllib.parse.quote(newmsg,safe='')}&{skey}={newsig}"
        try:
            r = get(q)
        except Exception:
            continue
        if ("admin" in r.lower() and "NCTF" in r) or hit(r):
            print(f"[*] klen={klen} add={add!r}\n[/admin] {r[:300]}")
            found=True; break
    if found: break
if not found:
    print("\n[-] Pas de flag. Montre-moi la reponse brute de /sign et un essai /admin pour ajuster les noms de parametres/append.")
