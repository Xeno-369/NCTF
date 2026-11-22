# hastad-broadcast (crypto) — RSA e=3, même message à N destinataires

**Flag : `NCTF{Y0u_3XPl0!t_h4st4d_br04dc45t_4tt4ck}`**

## Énoncé
Admin envoie le MÊME message à plusieurs destinataires, petit exposant public `e=3`,
clés (n) différentes. `output(2).txt` = `{e:3, data:[{n,c}×3]}`.

## Observation
Les 3 `c` sont **identiques** → m³ < n_i pour tous → aucune réduction modulo →
`c = m³` dans ℤ. Racine cubique entière (cube parfait) → message.

```python
import json
d=json.load(open('files/output.txt')); c=d['data'][0]['c']
def iroot(x,n):
    lo,hi=0,1<<((x.bit_length()//n)+2)
    while lo<hi:
        m=(lo+hi)//2
        lo,hi=(m+1,hi) if m**n<x else (lo,m)
    return lo
m=iroot(c,3); h=hex(m)[2:]; h=('0'+h) if len(h)%2 else h
print(bytes.fromhex(h))   # NCTF{...}
```

## Cas général (si les c diffèrent)
Vrai Håstad : avec e chiffrés c_i sous n_i premiers entre eux, CRT → C = m^e mod (∏n_i),
puis racine e-ième entière de C. Voir aussi [[kamina-hastad]] (même attaque, thème 1914).

## Réponse au chall
Non sécurisé : petit e + même message = récupération du clair sans aucune clé privée.
