# oidc-trust (IAM OIDC GitHub Actions)

- Catégorie : misc / cloud
- Résolu : sam. 07 nov.

## Énoncé
Rôle IAM ci-deployer, trust via OIDC GitHub Actions. Trust policy + permissions + tokens capturés + secret scellé. Trouver le token qui satisfait la policy, puis récupérer le secret.

## Analyse
Conditions : aud == sts.amazonaws.com ET sub StringLike "repo:kekeli-cloud/*".
5 tokens ; seul #3 passe : repo:kekeli-cloud/media-svc-fork (fork attaquant DANS l'org de confiance -> le wildcard ne borne que l'org).
Leurres : kekeli-cloud-staging, kekelicloud, kekeli/cloud-... (ne matchent pas le préfixe exact).
Secret : keystream = SHA256(SHA256(sub) ‖ ctr_be4) CTR ; flag = cipher XOR keystream.

## Flag
`NCTF{oidc_sub_wildcard_assumed_the_role}`
