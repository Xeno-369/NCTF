vals={}
for line in open('files/output.txt'):
    if '=' in line:
        k,v=line.split('=',1); vals[k.strip()]=int(v.strip())
n,e,c,p=vals['n'],vals['e'],vals['c'],vals['p']
q=n//p; d=pow(e,-1,(p-1)*(q-1)); m=pow(c,d,n)
print(m.to_bytes((m.bit_length()+7)//8,'big').decode())
