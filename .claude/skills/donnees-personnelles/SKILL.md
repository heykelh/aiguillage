---
name: donnees-personnelles
description: À utiliser dès qu'un traitement manipule du texte libre, des logs, des tickets ou des exports pouvant contenir des données personnelles (noms, e-mails, téléphones, identifiants, IP).
---

# Données personnelles (RGPD)

## Règles
1. **Masquer avant de sortir.** Avant tout envoi à un LLM, toute écriture dans un journal ou tout affichage dans un tableau de bord :
   `core/aiguillage/pii.py::masquer(texte)`. Les valeurs sont remplacées par des jetons typés (`[EMAIL]`, `[TEL]`, `[IP]`, `[MATRICULE]`, `[IBAN]`, `[NOM]`).
2. **Minimiser.** On ne conserve que les champs nécessaires à la finalité. Le journal stocke un hash SHA-256 du texte, pas le texte.
3. **Documenter.** Tout nouveau traitement ajoute ou met à jour une fiche dans `docs/RGPD_REGISTRE.md` : finalité, base légale, données, durée de conservation, destinataires, transferts hors UE.
4. **Fournisseur LLM.** Si le fournisseur est hors UE, on le note dans le registre, on n'envoie que du texte masqué et on prévoit une alternative hébergée dans l'UE ou en interne.
5. **Durée.** Le journal d'audit a une durée de conservation explicite (paramètre `AUDIT_RETENTION_JOURS`).

## Tests à écrire
- Un cas par type de donnée masquée.
- Un test « zéro fuite » : sur tout le jeu de référence, aucune donnée personnelle connue ne se retrouve dans la sortie ni dans le journal.
