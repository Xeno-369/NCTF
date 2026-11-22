# Verifie que chaque payload, deserialisé, rend bien le contenu du fichier cible.
import pickle, subprocess, sys, os, tempfile
d = tempfile.mkdtemp()
fake = os.path.join(d, 'flag')
open(fake, 'w').write('NCTF{faux_flag_pour_test_1234}\n')
subprocess.run([sys.executable, 'gen.py', fake], check=True)
for name in ('linecache', 'pathlib'):
    data = open(f'payload_{name}.pkl', 'rb').read()
    # charge dans un process isolé -I pour simuler
    obj = pickle.loads(data)
    print(f'{name:10s} repr -> {obj!r}')
