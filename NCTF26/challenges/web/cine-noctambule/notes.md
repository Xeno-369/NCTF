# Ciné Noctambule (web) — script.js caché

**Flag : `NCTF{e1eb07860dea12bc58dafdc6}`**
Leurres : `NCTF{th1s_1s_n0t_7h3_r34l_fl46}` (JS en dur), `NCTF{n1c3_7ry_bu7_th1s_1s_n0t_1t}` (POST mauvaise clé), `pr0j3ct0r_r00m_ma5t3r_k3y` = clé maître (GET /keys.php), pas le flag.

## Cible
`https://<id>.t.ctf.tg/` — site de cinéma. Commentaire HTML :
`<!-- TODO(dev): retirer ce script de debug -->` avant `<script src="script.js">`.

## Déobfuscation
1. `script.js` = **jjencode** (JS non-alphanumérique, `$=~[];$={...}`).
   Décodé statiquement en Python (pas d'exécution JS) : reconstruire l'objet `$`,
   évaluer la concaténation, puis `decode('unicode_escape')` (échappements octaux).
2. À l'intérieur : **packer Dean Edwards** `eval(function(p,a,c,k,e,d){...}(...))`.
   Dictionnaire (split '|') :
   `xhr|endpoint|function|cinemaAPI|var|flag|NCTF|th1s_|1s_|n0t_|7h3_|r34l_|fl46|new|XMLHttpRequest|keys|php|open|GET|true|send|null`
3. Dépacké :
   ```js
   function cinemaAPI(){
     var flag='NCTF{'+'th1s_'+'1s_'+'n0t_'+'7h3_'+'r34l_'+'fl46'+'}',   // LEURRE
         xhr=new XMLHttpRequest(),
         endpoint='/keys'+'.php';
     xhr.open('GET',endpoint,true); xhr.send(null);
   }
   ```

## Exploit
```bash
# 1) clé maître (GET) : réponse hex -> pr0j3ct0r_r00m_ma5t3r_k3y
curl -sk https://<id>.t.ctf.tg/keys.php | xxd -r -p
# 2) la reposter pour "entrer dans la salle"
curl -sk -X POST https://<id>.t.ctf.tg/keys.php -d "key=pr0j3ct0r_r00m_ma5t3r_k3y"
```
→ `NCTF{e1eb07860dea12bc58dafdc6}` (bonne clé) ; mauvaise clé -> leurre.

## Leçon
Deux couches d'obfuscation JS (jjencode + packer) + flag leurre en dur.
Le vrai flag n'est pas dans le JS : il faut appeler l'endpoint `/keys.php` que le XHR révèle.
Le code de déob (jjdec.py) est dans files/.
