#!/usr/bin/env bash
# Crée challenges/<catégorie>/<nom>/{notes.md,files/,solve.py} et ajoute une ligne au scoreboard.
# Usage : new_chall.sh <catégorie> <nom>
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
CATEGORIES="web forensics reverse pwn crypto misc boot2root"

if [ $# -ne 2 ]; then
  echo "Usage : $(basename "$0") <catégorie> <nom>  (catégories : $CATEGORIES)" >&2
  exit 2
fi

category=${1,,}
name=$2

case " $CATEGORIES " in
  *" $category "*) ;;
  *) echo "Catégorie inconnue : $category (attendu : $CATEGORIES)" >&2; exit 2 ;;
esac

if ! [[ $name =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "Nom invalide : lettres, chiffres, . _ - uniquement" >&2
  exit 2
fi

dir="$ROOT/challenges/$category/$name"
if [ -e "$dir" ]; then
  echo "Existe déjà : $dir" >&2
  exit 1
fi

fill() {
  sed -e "s/{{NOM}}/$name/g" -e "s/{{CATEGORIE}}/$category/g" -e "s/{{DATE}}/$(date '+%a %d %b %H:%M')/g" "$1"
}

mkdir -p "$dir/files"
fill "$ROOT/templates/notes.md" > "$dir/notes.md"
case $category in
  pwn|crypto) fill "$ROOT/templates/exploit.py" > "$dir/solve.py" ;;
  *)          fill "$ROOT/templates/solve.py" > "$dir/solve.py" ;;
esac
chmod +x "$dir/solve.py"

printf '| %s | %s | ? | à faire |  |  |\n' "$name" "$category" >> "$ROOT/scoreboard.md"

echo "$dir"
