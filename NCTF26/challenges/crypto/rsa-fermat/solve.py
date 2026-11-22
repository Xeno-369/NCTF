import math
from cryptography.hazmat.primitives.serialization import load_pem_public_key
k=load_pem_public_key(open('files/pubkey.pem','rb').read()).public_numbers()
n,e=k.n,k.e
a=math.isqrt(n)+1
while True:
    b2=a*a-n; b=math.isqrt(b2)
    if b*b==b2: p,q=a-b,a+b; break
    a+=1
d=pow(e,-1,(p-1)*(q-1))
c=int(open('files/ciphertext.txt').read().strip(),16)
m=pow(c,d,n)
print(m.to_bytes((m.bit_length()+7)//8,'big').decode())
