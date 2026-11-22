#!/usr/bin/env python3
import sys, base64
try:
    import requests
except ImportError:
    sys.exit("pip install requests")
import urllib3; urllib3.disable_warnings()

B=sys.argv[1].rstrip('/') if len(sys.argv)>1 else "https://jdy7ea6gcyrwvpho.t.ctf.tg"
S=requests.Session(); S.verify=False
BS=16

def enc(data: bytes) -> bytes:
    r=S.get(B+"/enc", params={"pt":data.hex()}, timeout=30)
    return bytes.fromhex(r.json()["ct"])

# --- détecter la longueur du suffixe secret ---
base=len(enc(b""))
i=1
while len(enc(b"A"*i))==base: i+=1
secret_len=base-i
print(f"[*] bloc={BS}, enc(vide)={base}o, saut a i={i} -> suffixe={secret_len} octets")

# --- ECB byte-at-a-time ---
known=b""
for idx in range(secret_len):
    pad=BS-1-(idx%BS)
    blk=idx//BS
    target=enc(b"A"*pad)[blk*BS:(blk+1)*BS]
    for b in range(256):
        if enc(b"A"*pad+known+bytes([b]))[blk*BS:(blk+1)*BS]==target:
            known+=bytes([b]); break
    else:
        print("[!] arret a l'octet",idx); break
    print(f"\r[+] suffixe: {known!r}", end="", flush=True)
print()
SECRET=known
print("[*] SUFFIXE SECRET =", repr(SECRET), "| hex:", SECRET.hex(),
      "| b64:", base64.b64encode(SECRET).decode())

# --- deverrouillage : essayer X-Unlock sous plusieurs formes ---
def grep_flag(t):
    import re
    m=re.search(r"NCTF\{[^}]+\}", t)
    return m.group(0) if m else None

forms={"raw":SECRET.decode('latin1'),"hex":SECRET.hex(),"b64":base64.b64encode(SECRET).decode()}
for name,val in forms.items():
    for path in ["/challenge","/check"]:
        params={}
        if path=="/check":
            # /check veut un ct : on lui passe enc(vide) (ou le challenge) a defaut
            params={"ct":enc(b"").hex()}
        r=S.get(B+path, headers={"X-Unlock":val}, params=params, timeout=30)
        print(f"\n[{name}] GET {path} -> {r.status_code}\n{r.text[:400]}")
        f=grep_flag(r.text)
        if f:
            print("\n########## FLAG ##########\n"+f); sys.exit(0)
print("\n[i] Pas de flag direct. Colle-moi les reponses /challenge et /check ci-dessus,")
print("    surtout si /challenge renvoie un ct a passer a /check.")
