# drifttoken (ERC20 allowance bug)

- **Catégorie :** crypto / smart-contract
- **Points :** ?
- **Instance :** aucune (fichiers)
- **Résolu :** sam. 07 nov. (sans indice)

## Énoncé
ERC20 maison DriftToken.sol + token_state.json (balance victime, allowance détenue, note cipher_hex). Vider la victime et déchiffrer la note.

## Fichiers
| Fichier | SHA-256 |
|---|---|
| files/DriftToken.sol | 4277b1a8156048d59663ba543fec28e0cce528f002caa966e84bb3386761cb1f |
| files/token_state.json | cb99deba0523446faab2f90c2a0320dbda3a85c03b261abbfed95d066afbcb4f |

## Faille + solution
transferFrom ne décrémente jamais l'allowance -> une approbation se dépense à l'infini,
plafonnée à allowance (3000) par appel.
Vider 1 000 000 : ceil(1000000/3000) = **334 appels** (333x3000 + 1x1000).
Note chiffrée : keystream = keccak256( uint256(334) big-endian ‖ ctr_be4 ), ctr=0,1,...
flag = cipher XOR keystream. (keccak256 = hash Ethereum.)

## Commandes
```bash
python3 solve.py          # brute des schémas -> HIT
python3 keccak.py         # auto-test keccak256
```

## Flag
`NCTF{allowance_never_decremented}`
