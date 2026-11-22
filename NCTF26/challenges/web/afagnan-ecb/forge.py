#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Afagnan ECB -- forge de jeton d'agent privilegie. STDLIB UNIQUEMENT (pas de pip).
#   /enc?pt=<hex>   -> ECB_k( pt || "unlock=9c6e08a2" )   (oracle de chiffrement)
#   /check?ct=<hex> -> {"valid": bool}                    (valide un jeton)
# But : trouver le prefixe d'agent qui fait repondre AUTRE CHOSE que valid:true/false
#       (ou un valid:true la ou les autres sont false => format admin correct).
# Lancer sur Kali (VPN NCTF actif) :  python3 forge.py
import sys, json, ssl, itertools, urllib.request, urllib.parse

B = "https://jdy7ea6gcyrwvpho.t.ctf.tg"
UNLOCK = "9c6e08a2"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def _get(path, params):
    url = f"{B}{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"X-Unlock": UNLOCK})
    with urllib.request.urlopen(req, context=CTX, timeout=15) as r:
        return r.read().decode("utf-8", "replace").strip()

def enc(data: bytes) -> bytes:
    """ECB_k(data || SECRET), renvoie le ciphertext complet (= jeton forge)."""
    return bytes.fromhex(json.loads(_get("/enc", {"pt": data.hex()}))["ct"])

def check_raw(ct: bytes) -> str:
    return _get("/check", {"ct": ct.hex()})

def forge_and_check(prefix: str):
    ct = enc(prefix.encode())
    txt = check_raw(ct)
    norm = txt.replace(" ", "")
    boring = norm in ('{"valid":true}', '{"valid":false}')
    valid  = norm.startswith('{"valid":true')
    return txt, (not boring), valid

def banner(t): print("\n" + "=" * 8 + " " + t + " " + "=" * 8)

# ---------------------------------------------------------------- baseline
banner("BASELINE (logique de /check)")
for p in ["", "A", "AAAA", "admin", "guest", "xyz123"]:
    txt, interesting, valid = forge_and_check(p)
    print(f"  pt={p!r:<10} -> {txt}{'   <<< INTERESSANT' if interesting else ''}")

# ---------------------------------------------------------------- sweep
banner("SWEEP agents privilegies")
values = ["admin", "administrator", "root", "superadmin", "superuser",
          "system", "sysadmin", "flag", "ctf", "true", "1", "yes"]
keys   = ["", "role=", "agent=", "user=", "name=", "id=", "is_admin=",
          "admin=", "priv=", "level="]
delims = ["", "&", ";", ",", "|", ":", " "]

hits, true_hits, tried = [], [], set()
for key, val, d in itertools.product(keys, values, delims):
    prefix = f"{key}{val}{d}"
    if prefix in tried:
        continue
    tried.add(prefix)
    try:
        txt, interesting, valid = forge_and_check(prefix)
    except Exception as e:
        print(f"  [err] {prefix!r}: {e}"); continue
    if interesting:
        hits.append((prefix, txt)); print(f"  !!! pt={prefix!r:<22} -> {txt}")
    elif valid:
        true_hits.append(prefix)

# ---------------------------------------------------------------- resultats
banner("RESULTATS")
print(f"[+] prefixes testes      : {len(tried)}")
print(f"[+] reponses NON standard: {len(hits)}")
for pfx, txt in hits:
    print(f"      {pfx!r:<22} -> {txt}")
print(f"[+] jetons valid:true    : {len(true_hits)}")
if true_hits:
    print("    (ex. formats acceptes) :", true_hits[:15])

if any("NCTF" in t for _, t in hits):
    for pfx, txt in hits:
        if "NCTF" in txt:
            print(f"\n[FLAG?] via pt={pfx!r} -> {txt}")
elif not hits:
    print("\n[-] Aucune reponse speciale : /check ne distingue pas l'agent par le texte.")
    print("    -> fallback: POST /check, param de revelation, ou INDICE du challenge.")
