# ChannelBot

- **Catégorie :** misc
- **Points :** ?
- **Instance :** aucune (hors ligne)
- **Début :** ven. 06 nov. 22:30

## Énoncé
ChannelBot ships as oracle.py (respond(prompt)). Ask it for the flag and it gives you one right away -- but submitting that answer will not score. ChannelBot serves different channels, and only one of them is telling the truth. Offline only -- no network, no real model. Call the shipped oracle, reach the privileged channel, and recover the real flag.

## Fichiers
| Fichier | SHA-256 | Remarque |
|---|---|---|
| files/oracle.py | 8f464d08a644285de30d3af1cd07a23aaa51e8d06cdb86f4050467ab71e85eb4 | Stub Python, lu avant exécution : base64 et XOR uniquement |

## Pistes testées
| Heure (approx.) | Hypothèse | Test | Résultat |
|---|---|---|---|
| ~22:30 | Le canal user renvoie un leurre | Lecture du code, appel de respond() | Confirmé (canary) |
| ~22:31 | Jeton admin récupérable par XOR 0x5B | Décodage de _TOK, en-tête X-Auth | **Canal admin atteint** |

## Commandes utiles
```bash
python3 -I solve.py
```

## Ce qui a marché
1. respond() renvoie le leurre pour toute demande contenant flag/secret/key/token.
2. Le vrai flag n'est servi que si l'en-tête X-Auth du prompt vaut le jeton de maintenance.
3. _TOK XOR 0x5B donne ce jeton ; on l'envoie sur une ligne `X-Auth: <jeton>`.
4. Le flag rendu par le canal admin correspond bien à _REAL décodé et diffère du leurre.

## Flag
`NCTF{r34l_fl4g_l1v3s_1n_4dm1n_ch4nn3l}`
