#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Scan EXHAUSTIF des codepoints non-ASCII + decodage selecteurs de variation / tags.
# python3 scan2.py https://<instance>.t.ctf.tg
import ssl, urllib.request, sys
from collections import Counter

H = (sys.argv[1] if len(sys.argv) > 1 else "https://6n7jdgpqzyask3wn.t.ctf.tg").rstrip("/")
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
raw = urllib.request.urlopen(urllib.request.Request(H+"/?page=1"), context=CTX, timeout=20).read()
txt = raw.decode("utf-8", "surrogatepass") if False else raw.decode("utf-8", "replace")
print("taille:", len(raw), "octets ;", len(txt), "caracteres")

# histogramme complet des non-ASCII
hist = Counter(c for c in txt if ord(c) > 127)
FR = set("àâäéèêëîïôöùûüçœÀÂÄÉÈÊËÎÏÔÖÙÛÜÇŒ’—–…“”«»€°·•★♥♡↗←→›✓＋㉿─┌└")
print("\n== codepoints > 127 ==")
for c, n in sorted(hist.items(), key=lambda kv: -kv[1]):
    flag = "" if c in FR else "   <<< INATTENDU"
    try: name = __import__("unicodedata").name(c)
    except ValueError: name = "?"
    print(f"  U+{ord(c):04X} x{n:<4} {name}{flag}")

# selecteurs de variation / tags / autres invisibles non standard
VS1 = range(0xFE00, 0xFE10)        # VS1-16
VS2 = range(0xE0100, 0xE01F0)      # VS17-256
TAGS = range(0xE0000, 0xE0080)     # tag chars
hidden = [c for c in txt if ord(c) in VS1 or ord(c) in VS2 or ord(c) in TAGS
          or 0x200B <= ord(c) <= 0x200F or ord(c) in (0x2060,0x2061,0x2062,0x2063,0x2064,0xFEFF,0x00AD,0x180E)]
print(f"\n== caracteres de smuggling trouves: {len(hidden)} ==")

def decode_vs(seq):
    out = bytearray()
    for c in seq:
        o = ord(c)
        if 0xFE00 <= o <= 0xFE0F: out.append(o - 0xFE00)
        elif 0xE0100 <= o <= 0xE01EF: out.append(o - 0xE0100 + 16)
        elif 0xE0000 <= o <= 0xE007F: out.append(o - 0xE0000)  # tags -> ASCII direct
    return bytes(out)

if hidden:
    b = decode_vs(hidden)
    s = "".join(chr(x) if 32 <= x < 127 else "." for x in b)
    print("  decode direct:", s)
    # si tags: mappe E0000+ascii
    tagtxt = "".join(chr(ord(c)-0xE0000) for c in hidden if 0xE0000 <= ord(c) <= 0xE007F)
    if tagtxt: print("  tags->ascii :", tagtxt)
    if "NCTF" in s.upper() or "NCTF" in tagtxt.upper():
        print("  <<< NCTF TROUVE")
else:
    print("  (aucun) -> pas de stego par caractere invisible, meme etendu.")
