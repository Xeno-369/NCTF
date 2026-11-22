# Enchaînement d'une épreuve
1. **Créer** : `tools/new_chall.sh <catégorie> <nom>`, copier l'énoncé dans `notes.md`, passer le statut à « en cours ».
2. **Lire** l'énoncé deux fois : titre, points, indices, format attendu, périmètre exact de l'instance.
3. **Reconnaissance légère** : `tools/snippets/file_triage.sh files/*`, puis navigation ou `tools/connect.sh <host>`.
4. **Hypothèses** : écrire 3 à 5 pistes classées par probabilité avant tout outil lourd.
5. **Tester** une piste à la fois, de la moins chère à la plus chère, une seule variable changée à chaque essai.
6. **Consigner** chaque essai dans « Pistes testées », y compris les échecs (heure, test, résultat).
7. **Limiter** tout fuzzing : débit faible, liste courte, uniquement sur l'instance désignée.
8. **45 min sans progrès** : noter où on en est, passer à « bloqué », changer d'épreuve ou passer la main.
9. **Progrès** = nouvelle information vérifiée ; répéter le même essai avec une autre charge n'en est pas un.
10. **Flag trouvé** : le noter, mettre à jour `scoreboard.md`, le soumettre soi-même sur la plateforme.
11. **Clôturer** : compléter « Ce qui a marché » pour qu'un coéquipier puisse rejouer la résolution.
12. **Rien ne sort** de l'équipe : ni flag, ni solution, ni write-up avant la clôture officielle.
