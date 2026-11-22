#!/bin/sh
# Croise les hash des binaires avec le flux known-bad, extrait le flag du composant compromis.
cd "$(dirname "$0")/files"
for b in component-*.bin; do
  h=$(sha256sum "$b" | cut -d' ' -f1)
  if grep -qi "$h" known-bad-hashes.txt; then
    echo "COMPROMIS: $b ($h)"
    grep -oE "'[A-Za-z0-9+/=]+'" "$b" | tr -d "'" | base64 -d; echo
  fi
done
