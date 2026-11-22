# Keccak-256 (Ethereum), pur Python.
def keccak256(msg: bytes) -> bytes:
    RC=[0x0000000000000001,0x0000000000008082,0x800000000000808A,0x8000000080008000,
    0x000000000000808B,0x0000000080000001,0x8000000080008081,0x8000000000008009,
    0x000000000000008A,0x0000000000000088,0x0000000080008009,0x000000008000000A,
    0x000000008000808B,0x800000000000008B,0x8000000000008089,0x8000000000008003,
    0x8000000000008002,0x8000000000000080,0x000000000000800A,0x800000008000000A,
    0x8000000080008081,0x8000000000008080,0x0000000080000001,0x8000000080008008]
    r=[[0,36,3,41,18],[1,44,10,45,2],[62,6,43,15,61],[28,55,25,21,56],[27,20,39,8,14]]
    M=(1<<64)-1
    rol=lambda x,n:((x<<n)|(x>>(64-n)))&M
    S=[[0]*5 for _ in range(5)]
    rate=136
    m=bytearray(msg); m.append(0x01)
    while len(m)%rate: m.append(0)
    m[-1]^=0x80
    for off in range(0,len(m),rate):
        for i in range(rate//8):
            S[i%5][i//5]^=int.from_bytes(m[off+i*8:off+i*8+8],'little')
        for rc in RC:
            C=[S[x][0]^S[x][1]^S[x][2]^S[x][3]^S[x][4] for x in range(5)]
            D=[C[(x-1)%5]^rol(C[(x+1)%5],1) for x in range(5)]
            for x in range(5):
                for y in range(5): S[x][y]^=D[x]
            B=[[0]*5 for _ in range(5)]
            for x in range(5):
                for y in range(5): B[y][(2*x+3*y)%5]=rol(S[x][y],r[x][y])
            for x in range(5):
                for y in range(5): S[x][y]=B[x][y]^((~B[(x+1)%5][y])&B[(x+2)%5][y])
            S[0][0]^=rc
    out=b''
    for i in range(4): out+=int.to_bytes(S[i%5][i//5],8,'little')
    return out[:32]
if __name__=='__main__':
    assert keccak256(b'').hex()=='c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470', keccak256(b'').hex()
    assert keccak256(b'abc').hex()=='4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45', keccak256(b'abc').hex()
    print('keccak256 OK')
