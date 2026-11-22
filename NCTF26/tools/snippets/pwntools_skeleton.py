#!/usr/bin/env python3
"""Connexion TLS minimale à une instance. Usage : pwntools_skeleton.py <id>.t.ctf.tg"""
import re
import sys

from pwn import remote

host = sys.argv[1]
io = remote(host, 1337, ssl=True, sni=host)

print(io.recvrepeat(timeout=2).decode(errors="replace"))
io.sendline(b"")
data = io.recvrepeat(timeout=2)
print(data.decode(errors="replace"))
print(re.findall(rb"NCTF\{.*?\}", data))
io.close()
