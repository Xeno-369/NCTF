# lock : inverse la transformation byte-drift pour retrouver la passphrase (= flag).
T = bytes.fromhex('f66957398d839f7915f8c5acbb179412809688f58717f272b60b3e3f2333')
ror8 = lambda x, r: ((x >> (r & 7)) | (x << (8 - (r & 7)))) & 0xff
out = bytes((ror8(t ^ 0x5c, (i % 7) + 1) - 3 * i - 7) & 0xff for i, t in enumerate(T))
print(out.decode())
