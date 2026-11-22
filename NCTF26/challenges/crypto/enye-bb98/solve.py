#!/usr/bin/env python3
"""enye-bb98 (crypto) — squelette pwntools.

Distant (TLS) : ./solve.py --host <id>.t.ctf.tg
Local         : ./solve.py --bin files/chall
Local + GDB   : ./solve.py --bin files/chall --gdb
Options       : --port N  --libc files/libc.so.6  --debug
"""
import argparse
import re

from pwn import *

FLAG_RE = re.compile(rb"NCTF\{.*?\}")
GDBSCRIPT = """
continue
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", help="instance distante (connexion TLS avec SNI)")
    parser.add_argument("--port", type=int, default=1337)
    parser.add_argument("--bin", help="binaire local (cible locale, et symboles en distant)")
    parser.add_argument("--libc", help="libc fournie")
    parser.add_argument("--gdb", action="store_true", help="lancer sous GDB (local seulement)")
    parser.add_argument("--debug", action="store_true", help="journaliser tous les échanges")
    opts = parser.parse_args()
    if not opts.host and not opts.bin:
        parser.error("indiquer --host ou --bin")
    if opts.host and opts.gdb:
        parser.error("--gdb ne s'utilise qu'en local")
    return opts


def start(opts: argparse.Namespace):
    if opts.host:
        return remote(opts.host, opts.port, ssl=True, sni=opts.host)
    if opts.gdb:
        return gdb.debug([opts.bin], gdbscript=GDBSCRIPT)
    return process([opts.bin])


def exploit(io, elf, libc) -> None:
    """Logique d'exploitation. elf et libc valent None s'ils ne sont pas fournis."""
    io.interactive()


def main() -> None:
    opts = parse_args()
    context.log_level = "debug" if opts.debug else "info"
    elf = ELF(opts.bin) if opts.bin else None
    if elf:
        context.binary = elf
    libc = ELF(opts.libc) if opts.libc else None

    io = start(opts)
    try:
        exploit(io, elf, libc)
        data = io.recvall(timeout=3) if io.connected() else b""
        for flag in FLAG_RE.findall(data):
            log.success(flag.decode(errors="replace"))
    finally:
        io.close()


if __name__ == "__main__":
    main()
