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

def run_full_vm(candidate_input):
    regs = list(bytes(8))
    stack = list(bytes(16))
    sp = 0
    zf = 0
    mem = bytearray(0x200)
    mem[0:0x2B] = candidate_input
    mem[0xC0 : 0xC0 + 0x2B] = code[0x92F : 0x92F + 0x2B]

    ip = 0
    while ip < len(code):
        raw = code[ip]
        ip += 1
        if raw == 0x02:  # MOV reg, imm32
            regs[code[ip] & 7] = int.from_bytes(code[ip + 1 : ip + 5], "little")
            ip += 5
        elif raw == 0x0C:  # MOVZX dst, byte(src)
            regs[code[ip] & 7] = regs[code[ip + 1] & 7] & 0xFF
            ip += 2
        elif raw == 0x1F:  # LOAD reg, [mem + off]
            off = (code[ip + 1] | (code[ip + 2] << 8)) & 0x1FF
            regs[code[ip] & 7] = mem[off]
            ip += 3
        elif raw == 0x0D:  # STORE [mem + off], reg
            off = (code[ip + 1] | (code[ip + 2] << 8)) & 0x1FF
            mem[off] = regs[code[ip] & 7] & 0xFF
            ip += 3
        elif raw == 0x18:  # XOR_IMM reg, imm8
            regs[code[ip] & 7] = (regs[code[ip] & 7] ^ code[ip + 1]) & 0xFF
            ip += 2
        elif raw == 0x05:  # ADD_IMM reg, imm8 (0x05 ^ 0x15 = 0x10 -> 0x401898)
            regs[code[ip] & 7] = (regs[code[ip] & 7] + code[ip + 1]) & 0xFF
            ip += 2
        elif raw == 0x19:  # ROL8 reg, shift
            r, s = code[ip] & 7, code[ip + 1] & 7
            v = regs[r] & 0xFF
            regs[r] = ((v << s) | (v >> (8 - s))) & 0xFF if s else v
            ip += 2
        elif raw == 0x1E:  # ROR8 reg, shift
            r, s = code[ip] & 7, code[ip + 1] & 7
            v = regs[r] & 0xFF
            regs[r] = ((v >> s) | (v << (8 - s))) & 0xFF if s else v
            ip += 2
        elif raw == 0x1A:  # ADD dst, src
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] + regs[b]) & 0xFF
            ip += 2
        elif raw == 0x0E:  # SUB dst, src
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] - regs[b]) & 0xFF
            ip += 2
        elif raw == 0x07:  # XOR dst, src
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] ^ regs[b]) & 0xFF
            ip += 2
        elif raw == 0x01:  # MUL dst, src
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] * regs[b]) & 0xFF
            ip += 2
        elif raw == 0x12:  # AND dst, src
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] & regs[b]) & 0xFF
            ip += 2
        elif raw == 0x14:  # NEG reg
            a = code[ip] & 7
            regs[a] = (-regs[a]) & 0xFF
            ip += 1
        elif raw == 0x11:  # CMP_EQ a, b
            a, b = code[ip] & 7, code[ip + 1] & 7
            zf = 1 if ((regs[a] ^ regs[b]) & 0xFF) == 0 else 0
            ip += 2
        elif raw == 0x1C:  # JNZ addr16
            target = code[ip] | (code[ip + 1] << 8)
            ip = target if zf == 0 else ip + 2
        elif raw == 0x0A:  # JMP addr16
            ip = code[ip] | (code[ip + 1] << 8)
        elif raw == 0x06:  # RET R7
            return (regs.pop() & 0xFF, mem)
        else:
            return (f"OP_{raw:#x}_AT_{ip-1:#x}", mem)
    return (-1, mem)

# 1. Vérifions d'abord que la VM atteint la comparaison finale sans aucune opcode inconnue !
ret, mem = run_full_vm(b"ADETA{" + b"A" * 36 + b"}")
print("Test VM status :", ret)

# 2. Résolution en 2 étapes :
# Étape A : retrouver mem[0x40..0x6a] (42 -> 0) pour produire mem[0x80..0xaa] == mem[0xc0..0xea]
# Étape B : retrouver flag[0..42] (0 -> 42) pour produire mem[0x40..0x6a]
target = code[0x92F : 0x92F + 0x2B]
flag = bytearray(b"A" * 0x2B)

# Grâce au double CBC (avant puis arrière), chaque octet i influence mem[0x80 + i] de manière bijective :
# On résout d'abord de droite à gauche (42 -> 0) puis de gauche à droite (0 -> 42) en 2 passes !
for _ in range(3):
    for i in range(0x2A, -1, -1):
        for ch in range(32, 127):
            flag[i] = ch
            _, m = run_full_vm(flag)
            if m[0x80 + i] == target[i]:
                break
    for i in range(0x2B):
        for ch in range(32, 127):
            flag[i] = ch
            _, m = run_full_vm(flag)
            if m[0x80 + i] == target[i]:
                break

ret, m = run_full_vm(flag)
print("FLAG TROUVE :", flag.decode(errors="replace"))
print("Validation VM :", ret)
