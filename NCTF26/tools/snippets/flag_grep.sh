#!/usr/bin/env bash
# Cherche NCTF{...} dans des fichiers ou dossiers : brut, UTF-16 et préfixe base64.
# Usage : flag_grep.sh <fichier|dossier>...
set -u
export LC_ALL=C

if [ $# -lt 1 ]; then
  sed -n '2,3p' "$0" | sed 's/^# \?//' >&2
  exit 2
fi

grep -raoP 'NCTF\{.*?\}' -- "$@"
grep -rlaP 'TkNURn[s-v]' -- "$@" | sed 's/^/[base64 NCTF{ ?] /'
find "$@" -type f -print0 | while IFS= read -r -d '' f; do
  strings -a -el "$f" | grep -aoP 'NCTF\{.*?\}' | sed "s|^|$f (UTF-16) : |"
done
exit 0
