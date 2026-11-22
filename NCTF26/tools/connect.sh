#!/usr/bin/env bash
# Connexion TLS à une instance : ncat --ssl, avec repli sur openssl s_client.
# Usage : connect.sh <host> [port]    (port par défaut : 1337 ; https:// et / finaux tolérés)
set -u

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
  sed -n '2,3p' "$0" | sed 's/^# \?//' >&2
  exit 2
fi

host=${1#*://}
host=${host%%/*}
port=${2:-1337}

use_openssl() {
  exec openssl s_client -quiet -connect "$host:$port" -servername "$host"
}

command -v ncat >/dev/null || use_openssl

# Échec immédiat de ncat = connexion impossible : on tente openssl.
# Une session qui a duré se termine normalement : pas de reconnexion.
start=$SECONDS
ncat --ssl --ssl-servername "$host" "$host" "$port"
rc=$?
if [ "$rc" -ne 0 ] && [ $((SECONDS - start)) -lt 3 ]; then
  echo "[connect.sh] ncat a échoué (code $rc), repli sur openssl s_client" >&2
  use_openssl
fi
exit "$rc"
