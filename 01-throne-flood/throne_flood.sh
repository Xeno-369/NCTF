#!/usr/bin/env bash
# ============================================================================
# 01 — THRONE FLOOD (fallback bash, si Python/requests indisponible)
# ============================================================================
# Garde le trône KOTH en ré-envoyant une soumission en boucle, en parallèle.
# Robuste : curl gère timeouts/retries, la boucle ne s'arrête jamais seule.
#
# ADAPTER : édite le bloc CONFIG, puis :  ./throne_flood.sh
# Dépendance : curl (présent par défaut sur Kali).
# ----------------------------------------------------------------------------
set -u

# ===== CONFIG =====
URL="http://CHANGE_ME:PORT/submit"
METHOD="POST"
DATA="flag=NCTF{CHANGE_ME}&team=1HUNTERS"   # corps form-urlencoded
HEADERS=(-H "Content-Type: application/x-www-form-urlencoded")
# Exemple token : HEADERS=(-H "Authorization: Bearer XXX" -H "Content-Type: ...")
WORKERS=4
INTERVAL=0.5          # secondes entre deux envois par worker
TIMEOUT=5             # timeout curl (s)
SUCCESS_PATTERN="throne|king|roi|accepted|success|leader"
# ==================

if [[ "$URL" == *CHANGE_ME* ]]; then
  echo "[!] Configure URL/DATA dans le bloc CONFIG avant de lancer." >&2
  exit 2
fi

cleanup() { echo; echo "[*] Arrêt, on tue les workers…"; kill 0 2>/dev/null; }
trap cleanup INT TERM

worker() {
  local id="$1" n=0 ok=0
  while true; do
    n=$((n+1))
    body=$(curl -s --max-time "$TIMEOUT" --retry 2 --retry-delay 1 \
                -X "$METHOD" "${HEADERS[@]}" --data "$DATA" "$URL" 2>/dev/null)
    rc=$?
    if [[ $rc -ne 0 ]]; then
      printf '[w%s] #%s erreur réseau (curl rc=%s)\n' "$id" "$n" "$rc"
    elif echo "$body" | grep -Eqi "$SUCCESS_PATTERN"; then
      ok=$((ok+1))
      printf '[w%s] #%s TRÔNE OK (succès cumulés=%s)\n' "$id" "$n" "$ok"
    else
      printf '[w%s] #%s envoyé (réponse: %.60s)\n' "$id" "$n" "$body"
    fi
    sleep "$INTERVAL"
  done
}

echo "[*] Throne flood -> $METHOD $URL | $WORKERS workers | intervalle ${INTERVAL}s"
echo "[*] Ctrl-C pour arrêter."
for i in $(seq 1 "$WORKERS"); do
  worker "$i" &
done
wait
