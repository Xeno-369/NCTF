# Bit-flip AES-CBC sur l'IV : guest -> admin dans le 1er bloc (offset 10).
import urllib.request,urllib.error,ssl
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
B='https://<INSTANCE>.t.ctf.tg'
C=bytes.fromhex(urllib.request.urlopen(B+'/profile',context=ctx).read().decode().split('"')[3])
iv=bytearray(C[:16]); ct=C[16:]
for k,(g,a) in enumerate(zip(b'guest',b'admin')): iv[10+k]^=g^a
import json
print(urllib.request.urlopen(B+'/admin?cookie='+(bytes(iv)+ct).hex(),context=ctx).read().decode())
