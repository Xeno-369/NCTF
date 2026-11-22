#!/usr/bin/env python3
"""sbom (forensics) — à lancer depuis le dossier du challenge."""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = HERE / "files"
FLAG_RE = re.compile(r"NCTF\{.*?\}")


def solve() -> str:
    """Renvoie le texte contenant le flag."""
    raise NotImplementedError("À écrire : logique de résolution")


def main() -> None:
    output = solve()
    flags = FLAG_RE.findall(output)
    print("\n".join(flags) if flags else output)


if __name__ == "__main__":
    main()
