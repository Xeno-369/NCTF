#!/usr/bin/env python3
"""NCTF Reverse Hard - stateful bytecode machine."""
import sys

PROGRAM = [4, 2, 7, 5, 3, 1, 6, 4, 2, 7, 5, 3, 1, 6, 4, 2, 7, 5, 3, 1, 6, 4, 2, 7, 5, 3, 1, 6, 4, 2, 7, 5, 3, 1, 6, 4, 2, 7, 5, 3, 1, 6, 4, 2]
EXPECTED = [219, 51, 235, 59, 6, 32, 224, 96, 68, 124, 212, 137, 97, 170, 59, 11, 68, 24, 82, 241, 145, 161, 133, 191, 188, 35, 42, 129, 154, 110, 142, 191, 128, 86, 71, 68, 42, 228, 127, 36, 198, 231, 121, 34]
INITIAL_KEY = 0x6D
INITIAL_ACC = 0xA9

def rol8(x, n):
    n &= 7
    return ((x << n) | (x >> (8-n))) & 0xff if n else x

def execute(data: bytes):
    key, acc = INITIAL_KEY, INITIAL_ACC
    trace = []
    for i, byte in enumerate(data):
        # VM instruction sequence:
        # LOAD byte; XOR key; ROL immediate; ADD accumulator; STORE accumulator.
        x = rol8(byte ^ key, PROGRAM[i])
        acc = (x + acc) & 0xff
        trace.append(acc)
        key = rol8((key + 0x3d) & 0xff, 1)
    return trace

def verify(candidate):
    raw = candidate.encode()
    return len(raw) == len(EXPECTED) and execute(raw) == EXPECTED

if __name__ == "__main__":
    guess = input("Flag: ").strip()
    print("Access granted." if verify(guess) else "Access denied.")
