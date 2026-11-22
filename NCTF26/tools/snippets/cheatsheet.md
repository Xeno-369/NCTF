# Aide-mémoire

## Flag
```bash
grep -raoP 'NCTF\{.*?\}' .                 # regex de référence
tools/snippets/flag_grep.sh files/         # brut + UTF-16 + préfixe base64
tshark -r c.pcap -Y 'frame contains "NCTF"' -T fields -e frame.number
```

## Encodages
```bash
tools/snippets/encodings.py 'TkNURntleGVtcGxlfQ=='  # cascade automatique + XOR 1 octet
echo -n 'x' | base64 -d ; echo -n 'x' | xxd -r -p ; echo 'x' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

## Fichiers et métadonnées
```bash
tools/snippets/file_triage.sh files/*      # sans exécution ni extraction
strings -a -n 6 f ; strings -a -el f       # ASCII puis UTF-16
exiftool -a -u -g1 f ; pngcheck -v f
binwalk -e --directory=extrait f           # extraction : à faire dans un dossier dédié
foremost -i f -o extrait_foremost
steghide info f ; steghide extract -sf f -p ''
```

## Réseau (forensics)
```bash
tshark -r c.pcap -q -z conv,tcp
tshark -r c.pcap -q -z follow,tcp,ascii,0
tshark -r c.pcap --export-objects http,objets_http
```

## Web — débit limité, sur l'instance désignée uniquement
```bash
curl -sSik https://<id>.t.ctf.tg/
curl -sS https://<id>.t.ctf.tg/robots.txt
ffuf -u https://<id>.t.ctf.tg/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt -rate 20 -t 5 -mc all -fc 404
sqlmap -u 'https://<id>.t.ctf.tg/?id=1' --batch --threads=1 --delay=1 --level=1 --risk=1
```

## Reverse et pwn
```bash
checksec chall ; r2 -AA chall ; ghidra
ROPgadget --binary chall | grep -E ': (pop rdi|ret)$'
tools/connect.sh <id>.t.ctf.tg
```

## Hashes — hors ligne
```bash
hashid -m h.txt ; john --wordlist=/usr/share/wordlists/rockyou.txt h.txt
hashcat -m 0 h.txt /usr/share/wordlists/rockyou.txt
```

## WireGuard
```bash
sudo wg-quick up ./nctf-vpn.conf ; sudo wg show ; sudo wg-quick down ./nctf-vpn.conf
```
