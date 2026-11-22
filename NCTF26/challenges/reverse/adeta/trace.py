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

JUMP_TABLE = (
    0x4015B0, 0x401690, 0x4015B0, 0x4015B0, 0x401780, 0x4017B8, 0x4015C0, 0x401660,
    0x4015B0, 0x401758, 0x4019D0, 0x401628, 0x401828, 0x4018C8, 0x4015B0, 0x401930,
    0x401898, 0x4015B0, 0x4018F8, 0x4019C0, 0x4016B8, 0x4014F8, 0x401968, 0x401560,
    0x401600, 0x4015B0, 0x4015B0, 0x4016F0, 0x4015B0, 0x4015B0, 0x4015B0, 0x401728,
)

NAMES = {
    0x4015B0: "FAIL", 0x401690: "NEG", 0x401780: "CMP_EQ", 0x4017B8: "ROR8",
    0x4015C0: "POP", 0x401660: "AND", 0x401758: "JNZ", 0x4019D0: "LOAD",
    0x401628: "SWAP", 0x401828: "ROL8", 0x4018C8: "XOR_IMM", 0x401930: "ADD",
    0x401898: "ADD_IMM", 0x4018F8: "XOR", 0x4019C0: "RET_R7", 0x4016B8: "MUL",
    0x4014F8: "MOV_IMM", 0x401968: "STORE", 0x401560: "MOVZX", 0x401600: "PUSH",
    0x4016F0: "SUB", 0x401728: "JMP",
}

ip = 0
for step in range(25):
    op = (code[ip] ^ 0x15) & 0x1F
    h = JUMP_TABLE[op]
    name = NAMES.get(h, hex(h))
    print(f"ip={ip:04x} | raw={code[ip]:02x} -> op={op:02d} ({name}) | args={code[ip+1:ip+6].hex(' ')}")
    ip += 1
    if h == 0x4014F8: ip += 5
    elif h in (0x401968, 0x4019D0): ip += 3
    elif h in (0x4015C0, 0x401600, 0x401690): ip += 1
    elif h in (0x4015B0, 0x4019C0): ip += 0
    else: ip += 2
