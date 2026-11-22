#!/usr/bin/env python3
"""
the-darknova / seccomp-shadow-ipc — génère les 2 trames (64 o chacune) qui
débloquent le secret. Valse en 2 temps :
  Trame 1 (op=1) : enregistre le chemin "/public//vault/key"  (passe le préfixe /public/)
  Trame 2 (op=2) : flags=0x0400, strip_len=8, checksum = hash(chemin) XOR 0xf1bbcdcbfa53e0a8
  -> après strip des 8 octets "/public/", il reste "/vault/key" == cible.

Usage :
  python3 solve_shadow.py            # affiche les 2 lignes hex à envoyer
  python3 solve_shadow.py ./shadow_ipc   # teste en local
  (distant)  (echo TRAME1; echo TRAME2) | nc <host> <port>
"""
import sys, subprocess

MASK = (1 << 64) - 1
BASIS = 0xcbf29ce484222325
PRIME = 0x100000001b3
XORK  = 0xf1bbcdcbfa53e0a8
PATH  = b"/public//vault/key"
TARGET_OK = b"Shadow IPC Canonical Checksum Verified"

def rol(x, r): return ((x << r) | (x >> (64 - r))) & MASK

def path_hash(p: bytes) -> int:
    # h = basis ; pour chaque octet : h = rol((b ^ h) * prime, 19)
    h = BASIS
    for b in p:
        h = rol(((b ^ h) * PRIME) & MASK, 19)
    return h

def build_frames():
    cs = path_hash(PATH)
    provided = cs ^ XORK
    # Trame 1 : op=1, chemin à l'offset 16
    f1 = bytearray(64)
    f1[0:2] = (1).to_bytes(2, "little")
    f1[16:16+len(PATH)] = PATH               # reste à 0x00 (NUL-terminé)
    # Trame 2 : op=2, flags, strip_len, checksum
    f2 = bytearray(64)
    f2[0:2]  = (2).to_bytes(2, "little")      # op = 2
    f2[2:4]  = (0x0400).to_bytes(2, "little") # flags
    f2[4:8]  = (8).to_bytes(4, "little")      # strip_len
    f2[8:16] = provided.to_bytes(8, "little") # checksum fourni
    return f1.hex(), f2.hex(), cs, provided

def main():
    h1, h2, cs, provided = build_frames()
    print(f"[i] chemin           : {PATH.decode()}")
    print(f"[i] checksum calculé : 0x{cs:016x}")
    print(f"[i] checksum à fournir : 0x{provided:016x}  (= hash XOR 0x{XORK:016x})")
    print("\n=== TRAME 1 (op=1, register) ===\n" + h1)
    print("\n=== TRAME 2 (op=2, verify) ===\n" + h2)

    if len(sys.argv) > 1:
        binpath = sys.argv[1]
        payload = (h1 + "\n" + h2 + "\n").encode()
        print(f"\n[*] test local sur {binpath} ...")
        out = subprocess.run([binpath], input=payload, capture_output=True, timeout=10).stdout
        print(out.decode(errors="replace"))
        print("[+] SUCCÈS" if TARGET_OK in out or b"Secret unlocked" in out else "[-] échec")

if __name__ == "__main__":
    main()
