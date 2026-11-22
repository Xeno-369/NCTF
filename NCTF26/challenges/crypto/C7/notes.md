# C7

- **Catégorie :** crypto
- **Points :** ?
- **Instance :** aucune (fichier public.json seul)
- **Début :** ven. 06 nov. 21:55
- **Fin :** ven. 06 nov. (résolu sans indice payant)

## Énoncé
Décodage par syndrome sur GF(2) : donnés une matrice de parité H, un syndrome s et un poids w = 30 (public.json), trouvez l'unique vecteur d'erreur e de poids w tel que H·eᵀ = s. Il déchiffre le flag (schéma flag_dec dans public.json).

## Fichiers
| Fichier | SHA-256 | Remarque |
|---|---|---|
| files/public.json | 27ec14f480e8dc818501a64468f413c908d7dac7d4ebbc9579cbab615fa9bc05 | n=276, k=138, w=30, H, s, flag_enc, flag_dec |

## Pistes testées
| Heure (approx.) | Hypothèse | Test | Résultat |
|---|---|---|---|
| ~21:55 | H structurée (creuse, quasi-cyclique, systématique) | poids lignes/colonnes, rang, rotations par blocs de 23 à 276 | Rien : dense (~n/2), rang 138, H d'apparence aléatoire |
| ~22:00 | ISD générique faisable | Coût estimé : Prange 2^32,5, Lee-Brickell p≤2 2^23,1 itérations | Retenue |
| ~22:05 | Lee-Brickell en C, 4 threads | Validation sur instance plantée de poids 18 (1 s), puis vraie instance | **Solution en 97 s** (602 342 itérations) |

Non nécessaires : Stern/Dumer, recherche de structure dans e, attaque de flag_dec.

## Commandes utiles
```bash
gcc -O3 -march=native -pthread -o isd isd.c
python3 -I mkinst.py files/public.json inst.txt
nice -n 10 ./isd inst.txt 4 > sol.txt
python3 -I dec.py sol.txt
```
Test sur solution connue : `python3 -I mkinst.py files/public.json test.txt 18` (e planté affiché sur stderr).

## Ce qui a marché
1. **Analyse des paramètres :** w/n ≈ 0,109 est à la borne de Gilbert-Varshamov pour un rendement 1/2 (nombre attendu de solutions aléatoires ≈ 0,036). Le e planté est donc unique, et le problème est le vrai SDP sur une matrice aléatoire : pas de raccourci algébrique.
2. **Mais n=276 est petit.** L'ISD (Information Set Decoding) choisit n-k=138 colonnes au hasard, les met en base identité par Gauss, et espère que e a très peu de bits hors de ces colonnes. Prange exige 0 bit dehors : 2^32,5 essais. Lee-Brickell en tolère jusqu'à p=2 en testant les ~9 450 paires de colonnes restantes à chaque itération : 2^23,1 essais attendus, moins coûteux au total.
3. **Implémentation** (`isd.c`) : lignes sur 5 mots de 64 bits, permutation aléatoire et Gauss complet à chaque itération, vecteurs colonnes sur 3 mots, test par popcount (poids du syndrome réduit égal à w-p). Environ 6 200 itérations/s sur 4 cœurs.
4. **Convention de s :** l'énoncé ne dit pas si la ligne 0 correspond au bit faible ou fort de s. Le solveur testait les deux en parallèle : c'est le bit de poids faible (t=0).
5. **Validation avant lancement :** une instance plantée a confirmé le solveur et la conversion des données.
6. **Vérification :** poids 30 et H·e = s confirmés par `dec.py`, indépendamment du C, puis déchiffrement SHA-256 en mode compteur selon flag_dec.

Chance : 97 s pour environ 23 min attendues à cette vitesse (602 342 itérations contre 8,69e6, durée géométrique).

e (positions) : 5 9 12 24 46 49 59 63 68 69 81 83 87 88 94 96 122 127 128 133 137 139 141 145 159 165 205 246 265 270

**À retenir :** vérifier le coût ISD réel avant de chercher une structure. Un SDP de n ≈ 300 se résout sur un portable.

## Flag
`NCTF{l4_p3rs3v3r4nc3_p41e_t0uj0urs}`
