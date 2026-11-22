import jwt
import time

with open("cle_privee.pem", "r") as f:
    secret_hex = f.read().strip()

payload = {
    "sub": "1234567890",
    "iat": int(time.time()),
    "exp": int(time.time()) + 3600
}

# Option A : Le secret est utilisé tel quel (chaîne hexadécimale)
token = jwt.encode(payload, secret_hex, algorithm="HS256")

# Option B : Le secret correspond aux 32 octets bruts décodés
# secret_bytes = bytes.fromhex(secret_hex.removeprefix("0x"))
# token = jwt.encode(payload, secret_bytes, algorithm="HS256")

print(token)
