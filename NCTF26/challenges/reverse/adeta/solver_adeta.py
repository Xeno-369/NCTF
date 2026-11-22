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

def run_vm(candidate_input):
    regs = list(bytes(8))
    stack = list(bytes(16))
    sp = 0
    zf = 0
    mem = bytearray(0x200)
    mem[0:0x2B] = candidate_input
    mem[0xC0 : 0xC0 + 0x2B] = code[0x92F : 0x92F + 0x2B]

    ip = 0
    steps = 0
    while steps < 200000 and ip < len(code):
        steps += 1
        raw = code[ip]
        ip += 1

        if raw == 0x02:  # MOV reg, imm32 (6 octets)
            r = code[ip] & 7
            regs[r] = struct.unpack_from("<I", code, ip + 1)[0]
            ip += 5
        elif raw == 0x0C:  # MOVZX dst, byte(src) (3 octets)
            dst, src = code[ip] & 7, code[ip + 1] & 7
            regs[dst] = regs[src] & 0xFF
            ip += 2
        elif raw == 0x1F:  # LOAD reg, [mem + off] (4 octets)
            r = code[ip] & 7
            off = (code[ip + 1] | (code[ip + 2] << 8)) & 0x1FF
            regs[r] = mem[off]
            ip += 3
        elif raw == 0x0D:  # STORE [mem + off], reg (4 octets)
            r = code[ip] & 7
            off = (code[ip + 1] | (code[ip + 2] << 8)) & 0x1FF
            mem[off] = regs[r] & 0xFF
            ip += 3
        elif raw == 0x18:  # XOR_IMM reg, imm8 (3 octets)
            r, imm = code[ip] & 7, code[ip + 1]
            regs[r] = (regs[r] ^ imm) & 0xFF
            ip += 2
        elif raw == 0x03:  # ADD_IMM reg, imm8 (3 octets)
            r, imm = code[ip] & 7, code[ip + 1]
            regs[r] = (regs[r] + imm) & 0xFF
            ip += 2
        elif raw == 0x19:  # ROL8 reg, shift (3 octets)
            r, s = code[ip] & 7, code[ip + 1] & 7
            v = regs[r] & 0xFF
            regs[r] = ((v << s) | (v >> (8 - s))) & 0xFF if s else v
            ip += 2
        elif raw == 0x1E:  # ROR8 reg, shift (3 octets)
            r, s = code[ip] & 7, code[ip + 1] & 7
            v = regs[r] & 0xFF
            regs[r] = ((v >> s) | (v << (8 - s))) & 0xFF if s else v
            ip += 2
        elif raw == 0x1A:  # ADD dst, src (3 octets)
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] + regs[b]) & 0xFF
            ip += 2
        elif raw == 0x0E:  # SUB dst, src (3 octets)
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] - regs[b]) & 0xFF
            ip += 2
        elif raw == 0x07:  # XOR dst, src (3 octets)
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] ^ regs[b]) & 0xFF
            ip += 2
        elif raw == 0x01:  # MUL dst, src (3 octets)
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] * regs[b]) & 0xFF
            ip += 2
        elif raw == 0x12:  # AND dst, src (3 octets)
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a] = (regs[a] & regs[b]) & 0xFF
            ip += 2
        elif raw == 0x14:  # NEG reg (2 octets)
            a = code[ip] & 7
            regs[a] = (-regs[a]) & 0xFF
            ip += 1
        elif raw == 0x1E:  # SWAP a, b
            a, b = code[ip] & 7, code[ip + 1] & 7
            regs[a], regs[b] = regs[b], regs[a]
            ip += 2
        elif raw == 0x11:  # CMP_EQ a, b (3 octets)
            a, b = code[ip] & 7, code[ip + 1] & 7
            zf = 1 if ((regs[a] ^ regs[b]) & 0xFF) == 0 else 0
            ip += 2
        elif raw == 0x1C:  # JNZ addr16 (3 octets)
            target = code[ip] | (code[ip + 1] << 8)
            ip = target if zf == 0 else ip + 2
        elif raw == 0x0A:  # JMP addr16 (3 octets)
            ip = code[ip] | (code[ip + 1] << 8)
        elif raw == 0x06:  # RET R7
            return (regs[7] & 0xFF, steps, mem)
        else:
            return (f"UNKNOWN_OP_{raw:#x}_AT_{ip-1:#x}", steps, mem)
    return (-2, steps, mem)

# Test sur une entree bidon pour voir jusqu'ou va l'execution
ret, steps, mem = run_vm(b"A" * 0x2B)
print("Status test:", ret, "| Steps:", steps)
print("Mem[0x40..0x6b]:", mem[0x40:0x6B].hex(" "))
print("Mem[0xc0..0xeb]:", mem[0xC0:0xEB].hex(" "))
