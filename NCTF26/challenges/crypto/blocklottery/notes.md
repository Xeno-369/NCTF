# blocklottery (BlockLottery.sol)

- Catégorie : crypto / smart-contract
- Résolu : sam. 07 nov.

## Fichiers
| Fichier | SHA-256 |
|---|---|
| files/BlockLottery.sol | 1ae64db24845ccc23117bd207763d4d01ec1ca641e8260ed0efdbb75d001cfe0 |
| files/draw.json | 5885c75b7d8eea118af3d0b812cfcc729d87852fdd677816adc09a53264e8a8a |

## Faille + solution
draw() = uint256(keccak256(abi.encodePacked(block.timestamp, block.number, block.prevrandao))) -> 100% déterministe.
Chaque champ packé sur 32 octets (uint256). ticket = keccak256(ts32‖num32‖prevrandao32).
Pot scellé : keystream = keccak256(ticket ‖ ctr_be4) CTR ; flag = cipher XOR keystream.

## Commande
```bash
python3 solve.py    # keccak.py requis dans le dossier
```

## Flag
`NCTF{blockhash_is_not_randomness}`
