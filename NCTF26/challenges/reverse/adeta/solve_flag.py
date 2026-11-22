import struct

with open("./adeta", "rb") as f:
    elf = f.read()

adeta_off = elf.index(b"ADET\x15\x00\x00\x00")
code = bytearray(elf[adeta_off + 0x18 : adeta_off + 0x18 + 0x95A])

state = 0xE71C2EC1
for i in range(len(code)):
    state = (state * 0x19660D + 0x3C6EF35F) & 0xFFFFFFFF
    state ^= state >> 13
    state = ((state << 7) | (state >> 25)) & 0xFFFFFFFF
    code[i] ^= (state >> 11) & 0xFF

def transform(candidate_input):
    regs = list(bytes(8))
    mem = bytearray(0x200)
    mem[0:0x2B] = candidate_input
    mem[0xC0 : 0xC0 + 0x2B] = code[0x92F : 0x92F + 0x2B]

    ip = 0
    while ip < 0x36C:
        raw = code[ip]
        ip += 1
        if raw == 0x02:
            regs[code[ip] & 7] = int.from_bytes(code[ip + 1 : ip + 5], "little")
            ip += 5
        elif raw == 0x0C:
            regs[code[ip] & 7] = regs[code[ip + 1] & 7] & 0xFF
            ip += 2
        elif raw == 0x1F:
            off = (code[ip + 1] | (code[ip + 2] << 8)) & 0x1FF
            regs[code[ip] & 7] = mem[off]
            ip += 3
        elif raw == 0x0D:
            off = (code[ip + 1] | (code[ip + 2] << 8)) & 0x1FF
            mem[off] = regs[code[ip] & 7] & 0xFF
            ip += 3
        elif raw == 0x18:
            regs[code[ip] & 7] = (regs[code[ip] & 7] ^ code[ip + 1]) & 0xFF
            ip += 2
        elif raw == 0x03:
            regs[code[ip] & 7] = (regs[code[ip] & 7] + code[ip + 1]) & 0xFF
            ip += 2
        elif raw == 0x19:
            r, s = code[ip] & 7, code[ip + 1] & 7
            v = regs[r] & 0xFF
            regs[r] = ((v << s) | (v >> (8 - s))) & 0xFF if s else v
            ip += 2
        elif raw == 0x1E:
            r, s = code[ip] & 7, code[ip + 1] & 7
            v = regs[r] & 0xFF
            regs[r] = ((v >> s) | (v << (8 - s))) & 0xFF if s else v
            ip += 2
        elif raw == 0x1A:
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] + regs[b]) & 0xFF
            ip += 2
        elif raw == 0x0E:
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] - regs[b]) & 0xFF
            ip += 2
        elif raw == 0x07:
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] ^ regs[b]) & 0xFF
            ip += 2
        elif raw == 0x01:
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] * regs[b]) & 0xFF
            ip += 2
        elif raw == 0x12:
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] & regs[b]) & 0xFF
            ip += 2
        elif raw == 0x14:
            a = code[ip] & 7
            regs[a] = (-regs[a]) & 0xFF
            ip += 1
        else:
            break
    return mem

target = code[0x92F : 0x92F + 0x2B]
flag = bytearray(b"A" * 0x2B)

# Résolution séquentielle caractère par caractère (gère les dépendances gauche -> droite)
for i in range(0x2B):
    for ch in range(32, 127):
        flag[i] = ch
        mem = transform(flag)
        if mem[0x40 + i] == target[i]:
            break

# Vérification complète (et seconde passe si dépendance droite -> gauche)
mem = transform(flag)
if mem[0x40 : 0x40 + 0x2B] != target:
    for i in range(0x2A, -1, -1):
        for ch in range(32, 127):
            flag[i] = ch
            mem = transform(flag)
            if mem[0x40 + i] == target[i]:
                break

print("FLAG :", flag.decode(errors="replace"))
print("Match exact :", transform(flag)[0x40 : 0x40 + 0x2B] == target)
