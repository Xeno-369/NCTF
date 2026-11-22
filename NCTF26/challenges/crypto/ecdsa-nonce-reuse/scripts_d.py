import hashlib
from ecdsa import SECP256k1, NIST256p
from ecdsa_reuse import recover_from_text

# 1. Paramètres du challenge
r = 0xd018d9415797e9618f0c8ec26fd17123056bab72f509ce171e0f17a4deef6a57
s1 = 0x9508a24e2ef02af5c454e6f48d5afd87c057b8a18b5cbbc3f1d79f9435bac029
s2 = 0x136141e5fb678357fca36716078bc43f2c854c973dffc16c3e79e4f52819810f

msg1 = b"msg1"
msg2 = b"msg2"

# 2. Récupération de la clé de signature (teste SECP256k1 et NIST256p / P-256)
for nom, courbe in [("SECP256k1", SECP256k1), ("NIST256p (P-256)", NIST256p)]:
    sk = recover_from_text(courbe, r, s1, msg1, s2, msg2, hashlib.sha256)
    if sk:
        d = sk.privkey.secret_multiplier
        print(f"[+] Courbe validée : {nom}")
        print(f"[+] Clé privée (int) : {d}")
        print(f"[+] Clé privée (hex) : {hex(d)}")
        break
else:
    print("[-] Échec : vérifiez l'algorithme de hachage (sha1, sha512...) ou la courbe.")
