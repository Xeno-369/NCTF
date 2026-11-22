L=open('files/data.txt').read().split('\n')
pat,text=L[0],L[1]
out=[]; i=text.find(pat)
while i!=-1:
    if i+len(pat)<len(text): out.append(text[i+len(pat)])
    i=text.find(pat,i+1)
print(''.join(out))
