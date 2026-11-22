# yeye-lenext (hash length extension)

- Catégorie : crypto / web
- Résolu : sam. 07 nov.

## Énoncé
MAC maison SHA256(secret || data). Forger un paiement user=admin sans connaître le secret. Endpoints: GET /challenge (donne msg + mac), GET /pay?msg=&mac=.
/challenge : msg="amount=1000&user=guest", mac=sha256(secret||msg).

## Attaque
Hash length extension : forger sha256(secret || msg || glue_padding || "&user=admin") et le data correspondant, sans le secret.
- glue = padding SHA de (secret||msg) ; forger en reprenant l'état depuis le mac connu.
- brute de la longueur du secret.
- le dernier user= l'emporte -> user=admin.
Outillage : lenext.py (impl SHA256 pur python, auto-testée). Transport : nginx bloque les octets bruts (400) -> envoyer msg percent-encodé (l'app lit la query brute et percent-décode) ; sinon hex.
NB : les 1res tentatives échouaient car l'INSTANCE avait EXPIRÉ (pas un bug de l'attaque).

## Flag
`NCTF{4e72ad9191a7cf668a1de799}`
