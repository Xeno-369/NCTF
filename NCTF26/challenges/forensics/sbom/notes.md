# sbom (supply chain CycloneDX)

- Catégorie : forensics / supply-chain
- Résolu : sam. 07 nov.

## Énoncé
SBOM CycloneDX (bom.json) + binaires des composants + known-bad-hashes.txt (SOC). Trouver le composant compromis et récupérer son flag.

## Résolution
SHA-256 de chaque component-*.bin croisé avec known-bad-hashes.txt.
Match : component-acme-updater.bin = cb512bc9c1addaa11efd905a870dc559818497eac0cfdfdb23e1d30cfac0892b = "acme-updater-backdoor".
Le binaire contient var cfg = base64 -> flag.

## Flag
`NCTF{sb0m_component_hash_pivot_9f4c}`
