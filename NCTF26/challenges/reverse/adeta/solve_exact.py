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

def run_vm(candidate_input, override_mid=None, start_ip=0, stop_ip=len(code)):
    regs = list(bytes(8))
    zf = 0
    mem = bytearray(0x200)
    mem[0:0x2B] = candidate_input
    if override_mid is not None:
        mem[0x40 : 0x40 + 0x2B] = override_mid
    mem[0xC0 : 0xC0 + 0x2B] = code[0x92F : 0x92F + 0x2B]

    ip = start_ip
    while ip < stop_ip:
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
        elif raw == 0x05:
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
        elif raw == 0x11:
            a, b = code[ip] & 7, code[ip + 1] & 7
            zf = 1 if ((regs[a] ^ regs[b]) & 0xFF) == 0 else 0
            ip += 2
        elif raw == 0x1C:
            target = code[ip] | (code[ip + 1] << 8)
            ip = target if zf == 0 else ip + 2
        elif raw == 0x0A:
            ip = code[ip] | (code[ip + 1] << 8)
        elif raw == 0x06:
            return (regs.pop() & 0xFF, mem)
    return (-1, mem)

target = code[0x92F : 0x92F + 0x2B]

# Étape 1 : Résoudre mid[0..42] (mem[0x40..0x6a]) de droite à gauche (42 -> 0)
mid = bytearray(0x2B)
for i in range(0x2A, -1, -1):
    for b in range(256):
        mid[i] = b
        _, m = run_vm(bytes(0x2B), override_mid=mid, start_ip=0x362, stop_ip=0x6D0)
        if m[0x80 + i] == target[i]:
            break

# Étape 2 : Résoudre flag[0..42] de gauche à droite (0 -> 42) pour obtenir mid
flag = bytearray(0x2B)
for i in range(0x2B):
    for b in range(256):
        flag[i] = b
        _, m = run_vm(flag, start_ip=0, stop_ip=0x362)
        if m[0x40 + i] == mid[i]:
            break

ret, _ = run_vm(flag)
print("FLAG :", flag.decode(errors="replace"))
print("Validation VM :", ret)
