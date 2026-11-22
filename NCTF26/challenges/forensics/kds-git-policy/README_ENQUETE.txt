KDS — export git policy (lab IR)
================================
Un admin a poussé une série de commits « reformat ».
Le RSSI suspecte un canal hors bande dans l'historique.

Piste : certains outils ignorent les changements d'espaces
(`git diff -w`, `git show -w`). Compare avec le diff complet.

Fichier d'intérêt probable : policy/indent.conf
Commit message suspect : « normalize indent »
