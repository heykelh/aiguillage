# Fiche AI Act : assistant de tri des incidents

> Dernière revue : 2026-11-23. Prochaine revue : à chaque modification substantielle, et au plus tard dans 6 mois.

## Finalité
Aider les agents de support et d'exploitation à faire le premier tri d'un ticket : catégorie, priorité, fiches de procédure, résumé.
L'outil suggère, l'humain valide. Il ne crée, ne modifie ni ne ferme aucun ticket.

## Niveau de risque
**Risque minimal.**
- Ce n'est pas une pratique interdite (article 5).
- Ce n'est pas un système à haut risque (annexe III) : il ne prend aucune décision sur des personnes (recrutement, évaluation, attribution de tâches à une personne nommée),
  et il n'est pas un composant de sécurité d'une infrastructure critique. Il traite des incidents informatiques, avec une validation humaine systématique.
- Point de vigilance : si l'outil servait un jour à router automatiquement des incidents de sécurité ferroviaire, ou à mesurer la performance des agents,
  la classification serait à refaire avec le référent IA.

## Rôle
La DSI est **fournisseur** (elle développe le système) et **déployeur** (elle l'utilise en interne).

## Transparence
L'interface indique que les suggestions sont produites par un outil automatique, précise si le résumé vient d'un LLM ou du mode déterministe,
et affiche la justification de chaque décision.

## Supervision humaine
- Toutes les sorties portent `validation_humaine_requise: true`.
- Les cas peu sûrs sont classés « À qualifier par un humain » au lieu de forcer une catégorie.
- Les décisions qui comptent (catégorie, priorité) sont prises par des règles lisibles et testées, que l'équipe propriétaire peut modifier.

## Journalisation
Chaque tri produit une entrée d'audit : horodatage, empreinte du ticket (pas le texte), catégorie, priorité, fiches, alerte de sécurité,
types de données masquées, source du résumé, modèle, version des règles, coût estimé. Conservation : 90 jours.

## Données
Pas d'entraînement de modèle. Contexte : fiches de procédure internes. Données d'entrée : texte des tickets, masqué avant tout envoi à un fournisseur.
Voir `docs/RGPD_REGISTRE.md`.

## Limites connues
- Le classement repose sur un vocabulaire et des fiches : un ticket très court ou hors sujet part en « À qualifier ».
- Les métriques actuelles sont mesurées sur des tickets fictifs. Elles devront être remesurées sur de vrais tickets annotés avant tout déploiement.
- Le masquage par motifs ne détecte pas tous les noms propres sans civilité.
