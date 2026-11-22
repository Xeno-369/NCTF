import sys, json, urllib.request
BASE = sys.argv[1].rstrip('/')
mods = """io codecs numpy pandas sklearn joblib torch scipy PIL shutil fileinput
tempfile gzip bz2 lzma tarfile zipfile configparser csv json mmap ctypes pty
pydoc platform socket base64 binascii struct array collections functools operator
itertools warnings logging pickle marshal sqlite3 webbrowser glob runpy code
codeop ast dis inspect types gc pickletools posix nt _io builtins os subprocess
numpy.core numpy.lib joblib.numpy_pickle sklearn.base sklearn.utils _pickle
pandas.core antigravity cProfile timeit site pkgutil email xml.sax""".split()
def q(mod):
    data = ('c%s\nx\n.' % mod).encode()
    req = urllib.request.Request(BASE + '/validate', data=data,
                                 headers={'Content-Type': 'application/octet-stream'})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())
    except Exception as e:
        return {'status': 'neterr', 'reason': str(e)}
allowed = []
for m in mods:
    res = q(m)
    reason = res.get('reason', '')
    blocked = 'blocked' in reason
    tag = 'BLOQUE' if blocked else ('AUTORISE' if res.get('status') in ('error','ok') else '?')
    if not blocked and res.get('status') in ('error','ok'):
        allowed.append(m)
    print(f'{m:22s} {tag:9s} {res.get("status"):8s} {reason[:60]}')
print('\nAUTORISES:', allowed)
