#!/usr/bin/env python3
# AES-ECB cut-and-paste ("Pagne"). Lancer: python3 pagne.py [url]
import sys, ssl, json, re, urllib.request, urllib.parse

B = (sys.argv[1] if len(sys.argv) > 1 else "https://xlefphtdp2rcybdy.t.ctf.tg").rstrip("/")
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE

def get(path):
    return urllib.request.urlopen(urllib.request.Request(B+path), context=CTX, timeout=20).read().decode("utf-8","replace")

def enc(email_bytes):
    q = urllib.parse.quote(email_bytes, safe="")          # 0x0b -> %0B, etc.
    return bytes.fromhex(json.loads(get(f"/encrypt?email={q}"))["ct"])

# bloc "admin" + padding PKCS7 (admin=5 octets -> 11x 0x0b) aligne sur le 2e bloc
# plaintext: "email="(6)+"A"*10 = bloc0 ;  "admin"+0x0b*11 = bloc1 ; "&role=user"...
admin_ct = enc(b"A"*10 + b"admin" + b"\x0b"*11)
ADMIN = admin_ct[16:32]
print("[*] bloc admin:", ADMIN.hex())

# bloc(s) alignes : email de 4 => "email=AAAA&role=" (bloc0 complet) | "user"+pad (a jeter)
pre_ct = enc(b"AAAA")
PREFIX = pre_ct[0:16]
print("[*] bloc prefixe:", PREFIX.hex())

forged = (PREFIX + ADMIN).hex()
print("[*] profil forge:", forged, "\n")

# soumission a /admin (param profile, avec repli sur d'autres noms/cookie)
def show(resp, how):
    m = re.search(r"NCTF\{[^}]*\}", resp)
    print(f"--- /admin via {how} ---")
    print(resp[:400])
    if m: print("\n[+] FLAG:", m.group()); return True
    return False

ok = False
for param in ("profile", "c", "ct", "data", "token", "p", "cookie"):
    try:
        if show(get(f"/admin?{param}={forged}"), f"?{param}="): ok=True; break
    except Exception as e:
        print(f"  ?{param}= -> {e}")
if not ok:
    # tentative via cookie "profile"
    try:
        req = urllib.request.Request(B+"/admin", headers={"Cookie": f"profile={forged}"})
        r = urllib.request.urlopen(req, context=CTX, timeout=20).read().decode("utf-8","replace")
        show(r, "cookie profile=")
    except Exception as e:
        print("  cookie -> ", e)
