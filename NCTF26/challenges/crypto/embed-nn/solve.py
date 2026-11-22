import numpy as np
z=np.load('files/embed_table.npz')
E,ch,Q=z['embeddings'],z['token_char'],z['queries']
idx=((Q[:,None,:]-E[None,:,:])**2).sum(2).argmin(1)
print(''.join(chr(int(ch[i])) for i in idx))
