# badge-png-chunks (forensics) — données dans chunks PNG tEXt

**Flag : `NCTF{ancillary_png_chunks_carry_secrets}`**

## Énoncé
`badge.png` (96x96) "porte plus que des pixels". Démonter le conteneur et réassembler
ce qui est planqué dedans.

## Analyse des chunks
Parser la structure PNG : IHDR, IDAT, puis **10 chunks `tEXt`** avec clés `frg00`..`frg09`
(5 caractères chacun), + un tEXt "Comment" leurre.

## Solve
Réordonner par index 00→09, concaténer, **décoder base85 (RFC 1924)** :
```python
import struct, base64
d=open('files/badge.png','rb').read(); i=8; frag={}
while i<len(d):
    ln=struct.unpack('>I',d[i:i+4])[0]; typ=d[i+4:i+8]; data=d[i+8:i+8+ln]
    if typ==b'tEXt':
        k,_,v=data.partition(b'\x00')
        if k.startswith(b'frg'): frag[k.decode()]=v
    i+=12+ln
    if typ==b'IEND': break
s=b''.join(frag['frg%02d'%n] for n in range(10))
print(base64.b85decode(s))   # NCTF{...}
```
Réassemblé = `PD4~idtq*4X>4p^a(Q2HZf9R(XmxIDb6;a&a&mcJb7f<4Wps0W` → base85 → flag.

## Leçon
Les chunks **ancillaires** PNG (tEXt/zTXt/iTXt + types custom) peuvent cacher des données.
Toujours énumérer TOUS les chunks (pas juste IDAT). Indices base85 : présence de `~ * > ^ ( &`.
