# desk-photo / Good_Luck (mot de passe clavier)

- **Catégorie :** forensics / osint
- **Statut :** hypothèse forte (à confirmer plateforme)

## Énoncé
Grace D. arrive 8h52, tape son mot de passe en quelques secondes, part en urgence. Photo du bureau. "Peut-on en déduire que le mot de passe était particulièrement court ?"

## Fichier
| Fichier | SHA-256 |
|---|---|
| files/Good_Luck.jpg | ae053f1be9ec59e86d4ec84facd7b36f1ba1a857df9f1c1fc9e4c23eea3b6b22 |

## Analyse
- JPEG PROPRE : pas d'EXIF, pas de commentaire, rien après FFD9, aucun fichier embarqué (binwalk/foremost), un seul JPEG.
- steghide : ECARTE. Testé pass vide + rockyou complet (stegseek) + ~1500 candidats scène (FR/EN, Grace, 8h52, GoodLuck, INVESTIGATE, E-YOOSO, codes paquet, keyboard-walks). Aucun hit.
- Objets : clavier E-YOOSO 60%, tel Galaxy S9 (dos), paquet "Super Milk Flavor Biscuit" (code de lot imprimé ~2760523/28037026/2027 = leurre), note "NCTF INVESTIGATE", mousepad topographique.

## Solution (visuelle)
Les capuchons GRIS (accent, diffusent le jaune) = **1,2,3,Q,W,E,A,S,D,Z,X,C**.
Ces 12 touches = le keyboard-walk **1qaz2wsx3edc** (descente par colonnes 1-Q-A-Z / 2-W-S-X / 3-E-D-C).
=> Mot de passe long (12) mais tapé en 1 s car motif clavier. Répond "non" à la question piège.

## Flag (candidats, priorité)
1. `NCTF{1qaz2wsx3edc}`
2. `NCTF{1qaz2wsx3edc4rfv}`
3. `NCTF{qweasdzxc}`
4. `NCTF{1QAZ2WSX3EDC}`
