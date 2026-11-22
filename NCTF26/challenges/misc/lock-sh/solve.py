import base64
pw=bytes(c^0x2a for c in bytes.fromhex('5942194646755d1b504b584e'))
b=base64.b64decode('PStnKhcsHwIWDS0XFgRVMwhsFEMDEQY7Aw0AAAk7Cg==')
print('password',pw.decode())
print(bytes(b[i]^pw[i%len(pw)] for i in range(len(b))).decode())
