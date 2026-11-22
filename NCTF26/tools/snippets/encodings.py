#!/usr/bin/env python3
"""Décodage automatique : essaie les encodages courants, en cascade.

Usage : encodings.py [--depth N] [<texte>]     (lit stdin sans texte)
        encodings.py -f fichier
Affiche chaque résultat lisible ; signale tout flag NCTF{...} trouvé.
"""
import argparse
import base64
import codecs
import html
import re
import string
import sys
import urllib.parse

FLAG_RE = re.compile(rb"NCTF\{.*?\}")
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
PRINTABLE = set(string.printable.encode())


def b58(data: bytes) -> bytes:
    n = 0
    for ch in data.decode().strip():
        n = n * 58 + B58.index(ch)
    return n.to_bytes((n.bit_length() + 7) // 8, "big")


def bits(data: bytes) -> bytes:
    s = re.sub(rb"[\s]", b"", data)
    if len(s) % 8 or set(s) - b"01":
        raise ValueError
    return int(s, 2).to_bytes(len(s) // 8, "big")


def decimal(data: bytes) -> bytes:
    return bytes(int(x) for x in data.replace(b",", b" ").split())


def rot47(data: bytes) -> bytes:
    return bytes(33 + (c - 33 + 47) % 94 if 33 <= c <= 126 else c for c in data)


DECODERS = {
    "base64": lambda d: base64.b64decode(d.strip() + b"=" * (-len(d.strip()) % 4), validate=True),
    "base64url": lambda d: base64.urlsafe_b64decode(d.strip() + b"=" * (-len(d.strip()) % 4)),
    "base32": lambda d: base64.b32decode(d.strip() + b"=" * (-len(d.strip()) % 8)),
    "base85": lambda d: base64.b85decode(d.strip()),
    "ascii85": lambda d: base64.a85decode(d.strip()),
    "base58": b58,
    "hex": lambda d: bytes.fromhex(re.sub(rb"0x|[\s:,]", b"", d).decode()),
    "binaire": bits,
    "décimal": decimal,
    "url": lambda d: urllib.parse.unquote_to_bytes(d),
    "html": lambda d: html.unescape(d.decode()).encode(),
    "rot13": lambda d: codecs.encode(d.decode(), "rot13").encode(),
    "rot47": rot47,
    "reverse": lambda d: d[::-1],
}


def readable(data: bytes) -> bool:
    return bool(data) and sum(c in PRINTABLE for c in data) / len(data) > 0.95


def xor_search(data: bytes) -> None:
    for key in range(1, 256):
        plain = bytes(c ^ key for c in data)
        if b"NCTF{" in plain:
            print(f"[FLAG] xor 0x{key:02x} : {plain!r}")


def explore(data: bytes, depth: int) -> None:
    seen = {data}
    queue = [(data, "")]
    for _ in range(depth):
        following = []
        for current, path in queue:
            for name, decode in DECODERS.items():
                try:
                    out = decode(current)
                except Exception:
                    continue
                if out in seen or not readable(out):
                    continue
                seen.add(out)
                chain = f"{path} > {name}" if path else name
                following.append((out, chain))
                mark = "[FLAG] " if FLAG_RE.search(out) else ""
                print(f"{mark}{chain} : {out[:200]!r}")
        queue = following


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("text", nargs="?")
    parser.add_argument("-f", "--file")
    parser.add_argument("--depth", type=int, default=2)
    opts = parser.parse_args()
    if opts.file:
        with open(opts.file, "rb") as fh:
            data = fh.read()
    elif opts.text is not None:
        data = opts.text.encode()
    else:
        data = sys.stdin.buffer.read()
    explore(data.strip(), opts.depth)
    xor_search(data)


if __name__ == "__main__":
    main()
