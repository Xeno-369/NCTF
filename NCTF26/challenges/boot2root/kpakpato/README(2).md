# Kpakpato Dépôt — énoncé participant

> **Catégorie** : `b2r` (boot2root)
> **Difficulté** : Easy
>
> Le dépôt Kpakpato permet à quelques techniciens de consulter et pousser du code à distance. Un compte de service est disponible pour les tests de routine.
>
> Objectif : partir de ce compte et atteindre le contrôle total de la machine.

## Accès

| Service | Adresse |
|---|---|
| Point d'accès | `ssh -p 30022 deploy@<IP>` (mot de passe communiqué séparément) |

## Objectif

Obtenir un accès **root** sur la machine.

Trois validations existent, une par étape franchie. Les rendre toutes les trois.

## Règles

- Le format des validations est `NCTF{...}`.
- Trois validations, une par étape.
- Ne pas casser le service ni supprimer les éléments utiles à la validation.
