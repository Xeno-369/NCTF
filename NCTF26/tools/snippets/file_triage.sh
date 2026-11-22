#!/usr/bin/env bash
# Tri rapide de fichiers fournis, sans jamais les exécuter ni rien extraire.
# Usage : file_triage.sh <fichier>...
set -u
HERE=$(cd "$(dirname "$0")" && pwd)

if [ $# -lt 1 ]; then
  sed -n '2,3p' "$0" | sed 's/^# \?//' >&2
  exit 2
fi

for f in "$@"; do
  [ -f "$f" ] || { echo "Ignoré (pas un fichier) : $f" >&2; continue; }
  case $f in -*) f=./$f ;; esac
  echo "===== $f ====="
  type=$(file -b -- "$f")
  echo "Type   : $type"
  echo "Taille : $(stat -c %s -- "$f") octets"
  echo "SHA256 : $(sha256sum -- "$f" | cut -d' ' -f1)"

  echo "--- métadonnées"
  exiftool -- "$f" | grep -vE '^(ExifTool Version|File Name|Directory|File Permissions|File (Modification|Access|Inode Change)|File Size)'

  echo "--- signatures embarquées"
  timeout 60 binwalk "$f" | tail -n +4

  case $type in
    *ELF*)
      echo "--- protections"
      checksec "$f" 2>&1 ;;
    *pcap*|*"capture file"*)
      echo "--- protocoles"
      timeout 60 tshark -q -z io,phs -r "$f" 2>/dev/null ;;
    *PNG*|*"PC bitmap"*)
      echo "--- stégano LSB"
      timeout 60 zsteg "$f" 2>/dev/null | cut -c1-120 | head -30 ;;
  esac

  echo "--- chaînes intéressantes"
  strings -a -n 6 -- "$f" | grep -iE 'flag|pass|secret|key|http|admin|nctf' | head -30

  echo "--- recherche de flag"
  "$HERE/flag_grep.sh" "$f"
  echo
done
