#!/usr/bin/env bash
# Diagnostic réseau NCTF26 : DNS, absence de VPN commercial, connectivité, tunnel WireGuard.
# Usage : check_env.sh [--instance <id>.t.ctf.tg] [--ping 10.100.x.y] [--geo]
#   --instance  teste aussi le DNS et le TLS (ports 1337 puis 443) de cette instance
#   --ping      cible du ping dans le tunnel : une machine désignée par un challenge
#   --geo       affiche le pays de l'IP publique (interroge ipinfo.io, désactivé par défaut)
# Code de sortie : 0 si aucun échec, 1 sinon. Ne nécessite pas root.
set -u

ARENA=arena.ctf.tg
WILDCARD=nctfcheck.t.ctf.tg
PUBLIC_DNS=1.1.1.1
INSTANCE="" PING_TARGET="" GEO=0
n_ok=0 n_warn=0 n_fail=0

usage() { sed -n '2,7p' "$0" | sed 's/^# \?//'; }

while [ $# -gt 0 ]; do
  case $1 in
    --instance) [ $# -ge 2 ] || { usage >&2; exit 2; }; INSTANCE=${2#*://}; INSTANCE=${INSTANCE%%/*}; shift 2 ;;
    --ping)     [ $# -ge 2 ] || { usage >&2; exit 2; }; PING_TARGET=$2; shift 2 ;;
    --geo)      GEO=1; shift ;;
    -h|--help)  usage; exit 0 ;;
    *)          usage >&2; exit 2 ;;
  esac
done

if [ -n "$PING_TARGET" ] && ! [[ $PING_TARGET =~ ^10\.100\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
  echo "--ping n'accepte qu'une adresse 10.100.x.y" >&2
  exit 2
fi

if [ -t 1 ]; then G=$'\e[32m' Y=$'\e[33m' E=$'\e[31m' B=$'\e[1m' N=$'\e[0m'; else G="" Y="" E="" B="" N=""; fi
section() { printf '\n%s== %s ==%s\n' "$B" "$1" "$N"; }
ok()   { printf '%s[OK]%s    %s\n' "$G" "$N" "$1"; n_ok=$((n_ok + 1)); }
warn() { printf '%s[WARN]%s  %s\n' "$Y" "$N" "$1"; n_warn=$((n_warn + 1)); }
fail() { printf '%s[FAIL]%s  %s\n' "$E" "$N" "$1"; n_fail=$((n_fail + 1)); }
info() { printf '[INFO]  %s\n' "$1"; }

resolve() { # hôte [serveur]
  local server=${2:+@$2}
  # shellcheck disable=SC2086
  dig +short +time=3 +tries=1 $server "$1" A 2>/dev/null | grep -E '^[0-9.]+$' | sort | tr '\n' ' '
}

check_dns() {
  local host=$1 mine public
  mine=$(resolve "$host")
  public=$(resolve "$host" "$PUBLIC_DNS")
  if [ -n "$mine" ] && [ -n "$public" ]; then
    ok "$host : mon DNS -> $mine| $PUBLIC_DNS -> $public"
  elif [ -n "$public" ]; then
    fail "$host : mon DNS ne répond pas, $PUBLIC_DNS -> $public(changer de résolveur)"
  elif [ -n "$mine" ]; then
    warn "$host : mon DNS -> $mine| $PUBLIC_DNS ne répond pas (port 53 filtré ?)"
  else
    fail "$host : aucune résolution, ni par mon DNS ni par $PUBLIC_DNS"
  fi
}

# --- DNS -------------------------------------------------------------------
section "DNS"
resolvers=$(awk '/^nameserver/ {print $2}' /etc/resolv.conf | tr '\n' ' ')
info "Résolveurs système : ${resolvers:-aucun}"
case " $resolvers " in
  *" $PUBLIC_DNS "*) info "$PUBLIC_DNS figure déjà parmi eux : la comparaison ci-dessous est peu discriminante" ;;
esac
check_dns "$ARENA"
check_dns "$WILDCARD"
[ -n "$INSTANCE" ] && check_dns "$INSTANCE"

# --- VPN commercial --------------------------------------------------------
section "VPN commercial"
wg_ifaces=$(ip -o link show type wireguard 2>/dev/null | awk -F': ' '{print $2}' | cut -d@ -f1)

is_nctf_iface() {
  [[ $1 == nctf* ]] || ip -4 -o addr show dev "$1" 2>/dev/null | grep -q ' 10\.100\.'
}

suspects=""
for iface in $(ip -br link | awk '{print $1}' | cut -d@ -f1); do
  case $iface in
    tun*|tap*|proton*|pvpn*|nordlynx*|nordtun*|mullvad*|tailscale*|wgcf*|warp*|CloudflareWARP*|surfshark*|expressvpn*|windscribe*)
      is_nctf_iface "$iface" || suspects+="$iface " ;;
  esac
done
for iface in $wg_ifaces; do
  case " $suspects " in *" $iface "*) continue ;; esac
  is_nctf_iface "$iface" || suspects+="$iface "
done
if [ -n "$suspects" ]; then fail "Interface(s) VPN suspecte(s) : $suspects"; else ok "Aucune interface de VPN tiers"; fi

procs=$(pgrep -a 'openvpn|nordvpnd|protonvpn|expressvpn|mullvad|surfshark|windscribe|warp-svc|tailscaled' 2>/dev/null)
if [ -n "$procs" ]; then fail "Processus VPN actif(s) : $(echo "$procs" | cut -c1-60 | tr '\n' ';')"; else ok "Aucun processus VPN connu"; fi

nm_vpn=$(nmcli -t -f NAME,TYPE con show --active 2>/dev/null | grep -E ':(vpn|wireguard)$' | grep -v '^nctf' | cut -d: -f1 | tr '\n' ' ')
if [ -n "$nm_vpn" ]; then fail "Connexion(s) VPN NetworkManager : $nm_vpn"; else ok "Aucune connexion VPN NetworkManager"; fi

egress=$(ip -o route get "$PUBLIC_DNS" 2>/dev/null | sed -n 's/.* dev \([^ ]*\).*/\1/p')
case " $(echo "$wg_ifaces" | tr '\n' ' ') " in
  *" $egress "*) fail "Le trafic Internet sort par le tunnel $egress (AllowedIPs trop large ?)" ;;
  *) ok "Sortie Internet directe par ${egress:-inconnue}" ;;
esac

# --- Connectivité ----------------------------------------------------------
section "Connectivité"
if ping -c 1 -W 3 "$PUBLIC_DNS" >/dev/null 2>&1; then ok "Ping $PUBLIC_DNS"; else warn "Ping $PUBLIC_DNS sans réponse (ICMP peut être filtré)"; fi

code=$(curl -sS -o /dev/null -I --max-time 10 -w '%{http_code}' "https://$ARENA" 2>/dev/null)
case $code in
  2*|3*) ok "HTTPS $ARENA : $code" ;;
  000|"") fail "HTTPS $ARENA injoignable" ;;
  *) warn "HTTPS $ARENA : code $code" ;;
esac

if [ -n "$INSTANCE" ]; then
  reached=""
  for port in 1337 443; do
    if timeout 8 openssl s_client -brief -connect "$INSTANCE:$port" -servername "$INSTANCE" </dev/null >/dev/null 2>&1; then
      reached=$port
      break
    fi
  done
  if [ -n "$reached" ]; then ok "TLS $INSTANCE:$reached"; else fail "TLS $INSTANCE injoignable sur 1337 et 443 (instance éteinte ?)"; fi
fi

if [ "$GEO" = 1 ]; then
  country=$(curl -sS --max-time 8 https://ipinfo.io/country 2>/dev/null | tr -d '[:space:]')
  case $country in
    TG) ok "IP publique au Togo" ;;
    "") warn "Pays de l'IP publique non déterminé" ;;
    *)  warn "IP publique géolocalisée en $country (attendu : TG)" ;;
  esac
fi

# --- WireGuard -------------------------------------------------------------
section "WireGuard"
if command -v wg-quick >/dev/null; then ok "wireguard-tools présent"; else warn "wireguard-tools absent (sudo apt install wireguard-tools)"; fi

tunnels=""
for iface in $wg_ifaces; do is_nctf_iface "$iface" && tunnels+="$iface "; done
if [ -z "$tunnels" ]; then
  info "Aucun tunnel NCTF monté (normal hors boot2root)"
else
  for iface in $tunnels; do
    addr=$(ip -4 -o addr show dev "$iface" | awk '{print $4}' | head -1)
    ok "Interface $iface montée, adresse ${addr:-aucune}"
    route_dev=$(ip -o route get 10.100.0.1 2>/dev/null | sed -n 's/.* dev \([^ ]*\).*/\1/p')
    if [ "$route_dev" = "$iface" ]; then ok "10.100.0.0/16 routé par $iface"; else fail "10.100.0.0/16 routé par ${route_dev:-rien} au lieu de $iface"; fi
    if [ "$(id -u)" = 0 ]; then
      hs=$(wg show "$iface" latest-handshakes | awk '{print $2}' | sort -n | tail -1)
      if [ "${hs:-0}" -gt 0 ]; then ok "Dernier handshake il y a $(($(date +%s) - hs)) s"; else fail "Aucun handshake : tunnel monté mais inactif"; fi
    else
      info "Handshake : relancer avec sudo, ou : sudo wg show $iface"
    fi
  done
  if [ -n "$PING_TARGET" ]; then
    if ping -c 2 -W 3 "$PING_TARGET" >/dev/null 2>&1; then ok "Ping $PING_TARGET"; else fail "Ping $PING_TARGET sans réponse"; fi
  else
    info "Ping : préciser --ping 10.100.x.y (machine désignée par un challenge)"
  fi
fi

# --- Bilan -----------------------------------------------------------------
section "Bilan"
printf '%s OK, %s avertissement(s), %s échec(s)\n' "$n_ok" "$n_warn" "$n_fail"
[ "$n_fail" -eq 0 ]
