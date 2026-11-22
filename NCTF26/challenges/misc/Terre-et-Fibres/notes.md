# Terre-et-Fibres

- **Catégorie :** misc (stégano)
- **Points :** ?
- **Instance :** aucune
- **Début :** ven. 06 nov. 22:02

## Énoncé
Festival fictif Dapaong Terre & Fibres : affiche officielle + guide des motifs. Retrouve le message tissé destiné aux partenaires.

## Fichiers
| Fichier | SHA-256 | Remarque |
|---|---|---|
| files/affiche.png | 9006fa8568cdc84324514fc8d357387636465d474c25e75007ae683943632a03 | PNG 900x1200 RGB, note dans le chunk iTXt Comment |
| files/guide-motifs.pdf | 9286d683cf2bcf0c85688cad167b8f39704d9cba717509f8c25fbeb3a226f644 | Règles de lecture, texte brut |
| files/README_vitrine.txt | d6a0a7918621a2277d81823094eb10bc311306f06b929059f0e9de51d93a1bc1 | 3e fichier du challenge, 105 octets |

## Pistes testées
| Heure (approx.) | Hypothèse | Test | Résultat |
|---|---|---|---|
| ~22:02 | Indices dans les métadonnées | exiftool, pngcheck, pdftotext | Comment : canal rouge, longueur puis motifs |
| ~22:03 | LSB du rouge, ordre MSB, uint32 BE + UTF-8 | extract.py (R, G, B ; bits 0 et 1) | **Message de 39 octets** ; aucun autre canal utile |
| ~22:04 | Légende lisible sur l'affiche | Zoom x8 | Non : 5 carrés identiques (glyphes manquants) |
| ~22:05 | Suffixe = hash connu | md5/sha1/sha256 de variantes du texte | Pas de correspondance, casse non confirmée |

## Commandes utiles
```bash
exiftool files/affiche.png
pdftotext -layout files/guide-motifs.pdf -
python3 -I extract.py
```

## Ce qui a marché
1. Le chunk iTXt `Comment` de l'affiche pointe vers le canal rouge, puis « longueur puis motifs ».
2. Le guide précise : uint32 big-endian, puis motifs UTF-8.
3. LSB du rouge, pixels en ordre ligne par ligne, bits regroupés MSB d'abord : longueur 39, puis `NCTF{D4P40NG_T1SS3R4NDS_29549DB55○2C}`.
4. `○` (3 octets UTF-8, d'où 39 octets) : le guide dit « Hex a reste une voyelle ». Dans le suffixe hexadécimal, c'est donc le `a`, pas un B. Les autres voyelles du message sont en leet (4, 1, 3, 0).

Hors périmètre : `README_vitrine.txt` indique que le QR / vitrine.local est hors périmètre CTF. Non visité.

**Refusés par la plateforme :** les deux premiers candidats (corps en majuscules, hex majuscule ou minuscule).

## Reprise après refus
- Bandes (39 + 1 ligne de cadre) : couleurs en progression arithmétique, aucun encodage. La coïncidence avec L=39 est fortuite.
- LSB vert/bleu : uniquement l'antialiasing du texte. LSB rouge : rien après le message (344 premiers pixels de la ligne 0).
- Hypothèse révisée : les exemples du guide (n, s, r, b) sont exactement les lettres du corps du flag, écrites en minuscules, et « Hex a » aussi. Les motifs mettraient donc le corps en majuscules ; il serait en minuscules dans le flag réel.

## Flag
Candidat 1 (refusé) : `NCTF{D4P40NG_T1SS3R4NDS_29549DB55A2C}`
Candidat 2 (refusé) : `NCTF{D4P40NG_T1SS3R4NDS_29549db55a2c}`
Candidat 3 (refusé) : `NCTF{d4p40ng_t1ss3r4nds_29549db55a2c}`
Candidat 4 (lecture littérale, seul ○ remplacé, refusé) : `NCTF{D4P40NG_T1SS3R4NDS_29549DB55a2C}`

## Contrôles après le 3e refus
- Les 5 glyphes de la légende sont identiques au pixel près : le ○ n'est pas confirmable par l'affiche.
- Rien après IEND ; PDF : seulement un saut de ligne après %%EOF, aucun octet non ASCII, le « ? » du guide est un vrai « ? ».
- Hash du suffixe (○ = n'importe quel hex) sur 18 chaînes et 6 algorithmes : aucune correspondance.
- Bloqué : utiliser un indice plutôt que multiplier les soumissions.

## Contrôles du 3e fichier
- README_vitrine.txt : examiné octet par octet, texte brut, aucun caractère caché.
- « QR » de l'affiche : simple damier régulier (lecture locale), aucune donnée. vitrine.local non contacté.
- Fichiers retéléchargés à 22:17 : SHA-256 identiques, flag non propre à une mise à jour.
