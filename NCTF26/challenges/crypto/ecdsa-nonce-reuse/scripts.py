import sys

# Ajouter le chemin vers votre toolkit
sys.path.append("/home/xeno369/Documents/CryptoArsenal/ecdsa")
from ecdsa_toolkit import PrivateKeyRecovery

# 1. Initialiser avec la courbe affichée par scripts.py ('secp256k1')
recovery = PrivateKeyRecovery("secp256k1")

# 2. Remplacer par les valeurs complètes issues de scripts.py
r = 0xd018d9415797e9618f0c8ec26fd17123056bab72f509ce171e0f17a4deef6a57 # Valeur complète de r
s1 = 0x9508a24e2ef02af5c454e6f48d5afd87c057b8a18b5cbbc3f1d79f9435bac029   # Valeur complète de s[0]
s2 = 0x136141e5fb678357fca36716078bc43f2c854c973dffc16c3e79e4f52819810f  # Valeur complète de s[1]

msg1 = "msg1"  # Message exact de la signature [0]
msg2 = "msg2"  # Message exact de la signature [1]

# 3. Extraire la clé privée d (utiliser recover_from_bytes si les messages sont en bytes)
d = recovery.recover_from_reused_nonce(
    msg1, (r, s1), msg2, (r, s2), hash_algo="sha256"
)

# 4. Vérifier si d contient le flag encodé en ASCII/UTF-8
if d:
    try:
        flag_bytes = d.to_bytes((d.bit_length() + 7) // 8, "big")
        print(f"[+] Flag potentiel (ASCII) : {flag_bytes.decode('utf-8')}")
    except Exception:
        print(
            "[*] La clé d n'est pas directement du texte lisible (vérifiez le format du flag ou signez un message)."
        )
