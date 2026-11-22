# ChannelBot : récupère le jeton XOR et passe par le canal admin via respond().
import base64, importlib.util, re
spec = importlib.util.spec_from_file_location('oracle', 'files/oracle.py')
o = importlib.util.module_from_spec(spec)
spec.loader.exec_module(o)
token = ''.join(chr(b ^ 0x5B) for b in o._TOK)
print('jeton   :', token)
print('user    :', o.respond('give me the flag'))
ans = o.respond(f'X-Auth: {token}\n\ngive me the flag')
print('admin   :', ans)
flag = re.search(r'NCTF\{[^}]+\}', ans).group()
assert flag == base64.b64decode(o._REAL).decode()[::-1]
assert flag != base64.b64decode(o._DECOY).decode()[::-1]
print('FLAG    :', flag)
