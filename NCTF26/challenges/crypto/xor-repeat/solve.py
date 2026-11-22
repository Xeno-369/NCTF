ct=bytes.fromhex(open('files/output.txt').read().strip())
key=b'1337'
print(bytes(ct[i]^key[i%len(key)] for i in range(len(ct))).decode())
