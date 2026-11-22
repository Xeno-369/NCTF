#!/usr/bin/env python3
"""BNAT Custom VM — reference interpreter (v2.3)"""
import sys

ENTRY_POINT = 0x78

def _rotl(v, n):
    n &= 7
    return ((v << n) | (v >> (8 - n))) & 0xFF

class BnatVM:
    def __init__(self, prog):
        if len(prog) != 256:
            raise ValueError(f"program must be exactly 256 bytes (got {len(prog)})")
        self.mem  = bytearray(prog)
        self.regs = [0] * 6
        self.stack = []
        self.pc   = ENTRY_POINT
        self.z    = False
        self.n    = False
        self.halted = False
        self.output = bytearray()

    def _r(self, i):  return self.regs[i] if i < 6 else 0
    def _w(self, i, v):
        if i < 6: self.regs[i] = v & 0xFF

    def step(self):
        pc = self.pc
        op = self.mem[pc]
        if op == 0x01:   rd,im = self.mem[pc+1],self.mem[pc+2]; self._w(rd,im);                                           self.pc+=3
        elif op == 0x02: rd,im = self.mem[pc+1],self.mem[pc+2]; self._w(rd,(self._r(rd)+im)&0xFF);                        self.pc+=3
        elif op == 0x03: rd,im = self.mem[pc+1],self.mem[pc+2]; self._w(rd,(self._r(rd)*im)&0xFF);                        self.pc+=3
        elif op == 0x04: rd,im = self.mem[pc+1],self.mem[pc+2]; self._w(rd,self._r(rd)^im);                               self.pc+=3
        elif op == 0x05: rd,rs = self.mem[pc+1],self.mem[pc+2]; self._w(rd,self._r(rd)^self._r(rs));                      self.pc+=3
        elif op == 0x06: rd,n  = self.mem[pc+1],self.mem[pc+2]; self._w(rd,_rotl(self._r(rd),n));                         self.pc+=3
        elif op == 0x07: addr,rd = self.mem[pc+1],self.mem[pc+2]; self.mem[addr]=self._r(rd);                             self.pc+=3
        elif op == 0x08: rd,addr = self.mem[pc+1],self.mem[pc+2]; self._w(rd,self.mem[addr]);                             self.pc+=3
        elif op == 0x09: rd,rs = self.mem[pc+1],self.mem[pc+2]; self._w(rd,self.mem[self._r(rs)]);                        self.pc+=3
        elif op == 0x0A: rd,rs = self.mem[pc+1],self.mem[pc+2]; self.mem[self._r(rd)]=self._r(rs);                        self.pc+=3
        elif op == 0x0B: rd,im = self.mem[pc+1],self.mem[pc+2]; v=self._r(rd); self.z=(v==im); self.n=(v<im);            self.pc+=3
        elif op == 0x0C: rd,rs = self.mem[pc+1],self.mem[pc+2]; a,b=self._r(rd),self._r(rs); self.z=(a==b); self.n=(a<b);self.pc+=3
        elif op == 0x0D:
            rel = self.mem[pc+1]; rel = rel-256 if rel>=128 else rel
            self.pc = (pc+2+rel)&0xFF if self.z else pc+2
        elif op == 0x0E:
            rel = self.mem[pc+1]; rel = rel-256 if rel>=128 else rel
            self.pc = (pc+2+rel)&0xFF if not self.z else pc+2
        elif op == 0x0F: self.stack.append(pc+2); self.pc=self.mem[pc+1]
        elif op == 0x10: self.pc=self.stack.pop()
        elif op == 0x11: self.halted=True
        elif op == 0x12:
            rd=self.mem[pc+1]; b=sys.stdin.buffer.read(1)
            self._w(rd,b[0] if b else 0); self.pc+=2
        elif op == 0x13: addr,n=self.mem[pc+1],self.mem[pc+2]; self.output+=self.mem[addr:addr+n]; self.pc+=3
        elif op == 0x14: rd=self.mem[pc+1]; self._w(rd,(self._r(rd)+1)&0xFF); self.pc+=2
        elif op == 0x15: rd=self.mem[pc+1]; self._w(rd,(self._r(rd)-1)&0xFF); self.pc+=2
        elif op == 0x16: rd,rs=self.mem[pc+1],self.mem[pc+2]; self._w(rd,self._r(rs)); self.pc+=3
        elif op == 0x17: rd=self.mem[pc+1]; self._w(rd,(~self._r(rd))&0xFF); self.pc+=2
        else: raise RuntimeError(f"unknown opcode {op:#04x} @ {pc:#04x}")

    def run(self):
        while not self.halted and self.pc < 256:
            self.step()
        sys.stdout.buffer.write(self.output)

def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <program.bnat>", file=sys.stderr); sys.exit(1)
    prog = open(sys.argv[1], 'rb').read()
    BnatVM(prog).run()

if __name__ == '__main__':
    main()
