import json
import hashlib
from Crypto.Cipher import AES

# Chargement des fichiers
with open("public.json") as f:
    pub = json.load(f)
with open("flag(1).enc") as f:
    enc = json.load(f)

p = pub["p"]
a = pub["a"]
b = pub["b"]
wbits = pub["wbits"]

E = EllipticCurve(GF(p), [a, b])
G = E(pub["G"][0], pub["G"][1])
Q = E(pub["Q"][0], pub["Q"][1])

print("[*] Recherche de x (2^63)...")
# Pour accélérer : on peut aussi réduire l'intervalle si on connaît un bit, sinon :
x = discrete_log_lambda(Q, G, bounds=(0, 2**wbits), operation='+')
print(f"[+] x trouvé : {x}")

# Déchiffrement AES-256-GCM
key = hashlib.sha256(str(x).encode()).digest()
nonce = bytes.fromhex(enc["nonce"])
ct = bytes.fromhex(enc["ciphertext"])
tag = bytes.fromhex(enc["tag"])

cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
flag = cipher.decrypt_and_verify(ct, tag)
print(f"[+] FLAG : {flag.decode()}")
