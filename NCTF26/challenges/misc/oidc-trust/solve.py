import json,hashlib,base64,fnmatch
tk=json.load(open('files/oidc-token.json'))['CapturedTokens']
sec=json.load(open('files/release-secret.json')); ct=base64.b64decode(sec['SecretStringCiphertextB64']); n=len(ct)
win=[t for t in tk if t['aud']=='sts.amazonaws.com' and fnmatch.fnmatchcase(t['sub'],'repo:kekeli-cloud/*')][0]
key=hashlib.sha256(win['sub'].encode()).digest()
ks=b'';c=0
while len(ks)<n: ks+=hashlib.sha256(key+c.to_bytes(4,'big')).digest(); c+=1
print('sub gagnant:',win['sub'])
print(bytes(a^b for a,b in zip(ct,ks[:n])).decode())
