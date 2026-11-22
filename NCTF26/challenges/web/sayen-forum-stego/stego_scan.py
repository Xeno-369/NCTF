#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Scanner stego autonome pour le forum "Sayen Game". STDLIB only.
# Lancer sur Kali :  python3 stego_scan.py
import ssl, json, re, urllib.request, sys

H = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "https://6n7jdgpqzyask3wn.t.ctf.tg"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE

def get(path):
    req = urllib.request.Request(H + path, headers={"User-Agent": "scan"})
    with urllib.request.urlopen(req, context=CTX, timeout=20) as r:
        return r.read()

def bar(t): print("\n" + "=" * 10 + " " + t + " " + "=" * 10)

# -------------------------------------------------- 1) page brute : invisibles
bar("PAGE: octets & invisibles")
raw = get("/?page=1")
print("taille brute:", len(raw))
txt = raw.decode("utf-8", "replace")
INVIS = {0x200b:"ZWSP",0x200c:"ZWNJ",0x200d:"ZWJ",0x2060:"WJ",0xfeff:"BOM",
         0x200e:"LRM",0x200f:"RLM",0x00ad:"SHY",0x2061:"f-app",0x2062:"i-times",
         0x180e:"MONGO",0x2063:"i-sep",0x2064:"i-plus"}
seq = [ord(c) for c in txt if ord(c) in INVIS]
from collections import Counter
print("invisibles trouves:", {INVIS[k]:v for k,v in Counter(seq).items()})

# decodage binaire si exactement 2 types d'invisibles
def try_bin(zeros, ones, label):
    bits = "".join("0" if ord(c) in zeros else "1" for c in txt if ord(c) in zeros|ones)
    if len(bits) < 8: return
    for off in (0,):
        by = bytes(int(bits[k:k+8],2) for k in range(off, len(bits)-7, 8))
        s = "".join(chr(b) if 32<=b<127 else "." for b in by)
        tag = "  <<< NCTF" if "NCTF" in s.upper() else ""
        print(f"  [bin {label}] {s}{tag}")
        # LSB
        by2 = bytes(int(bits[k:k+8][::-1],2) for k in range(off, len(bits)-7, 8))
        s2 = "".join(chr(b) if 32<=b<127 else "." for b in by2)
        if "NCTF" in s2.upper(): print(f"  [bin {label} LSB] {s2}  <<< NCTF")

kinds = set(seq)
if len(kinds) == 2:
    a, b = sorted(kinds)
    try_bin({a},{b},f"{INVIS[a]}=0/{INVIS[b]}=1")
elif len(kinds) >= 1:
    # schemas classiques
    try_bin({0x200b},{0x200c},"ZWSP/ZWNJ")
    try_bin({0x200c},{0x200d},"ZWNJ/ZWJ")

# espaces/tabs de fin de ligne (stego snow)
bar("ESPACES DE FIN DE LIGNE")
lines = raw.split(b"\n")
tw = [ (i, len(l)-len(l.rstrip(b" \t"))) for i,l in enumerate(lines) if l.rstrip(b" \t")!=l ]
print("lignes avec espaces/tabs en fin:", len(tw))
if tw:
    bits="".join("".join("1" if ch==0x09 else "0" for ch in lines[i][len(lines[i].rstrip(b' \t')):]) for i,_ in tw)
    print("  bits:", bits[:120])

# -------------------------------------------------- 2) messages : acrostiches
bar("MESSAGES: acrostiches")
i = txt.index("const messages="); j = txt.index("];", i)+1
M = json.loads(txt[i+len("const messages="):j])
users = ["Niko","Maya","Raph","June"]
def fa(s):
    for c in s:
        if c.isalpha(): return c
    return ""
def sents(t): return [x for x in re.split(r"(?<=[.!?…])\s+", t.strip()) if x.strip()]
grp = {"ALL":M};
for u,n in enumerate(users): grp[n]=[m for m in M if m["who"]==u]
for g,seqm in grp.items():
    a1 = "".join(fa(m["text"]) for m in seqm)
    a2 = "".join(fa(s) for m in seqm for s in sents(m["text"]))
    for lab,s in [("msg1",a1),("sent1",a2)]:
        if "NCTF" in s.upper(): print(f"  {g}/{lab}: {s}  <<< NCTF")
    print(f"  {g}: msg1={a1[:40]}")

# -------------------------------------------------- 3) assets SVG
for a in ("coast","night","shore"):
    bar(f"ASSET {a}.svg")
    try:
        d = get(f"/assets/{a}.svg")
    except Exception as e:
        print("  err:", e); continue
    print("  taille:", len(d))
    s = d.decode("utf-8","replace")
    for pat,lab in [(r"NCTF\{[^}]*\}","FLAG"), (r"<!--.*?-->","comment"),
                    (r"<text[^>]*>.*?</text>","text"), (r"<desc[^>]*>.*?</desc>","desc"),
                    (r"<title[^>]*>.*?</title>","title"), (r"<metadata[^>]*>.*?</metadata>","meta")]:
        for m in re.findall(pat, s, re.S)[:5]:
            print(f"  [{lab}] {m[:200]}")
    # donnees apres </svg> ?
    end = d.rfind(b"</svg>")
    if end != -1 and len(d) > end+6+2:
        tail = d[end+6:]
        print(f"  [APRES </svg>] {len(tail)} octets: {tail[:80]!r}")
    # invisibles dans le svg
    inv = Counter(ord(c) for c in s if ord(c) in INVIS)
    if inv: print("  invisibles:", {INVIS[k]:v for k,v in inv.items()})

print("\n[fini]")
