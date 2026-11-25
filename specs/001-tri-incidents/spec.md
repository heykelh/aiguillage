# Spec 001 : Assistant de tri des incidents

> Statut : livrée (MVP de démonstration, données fictives)
> Propriétaire : équipe Exploitation applicative (fictive) ; référent build : Heykel Hachiche
> Date : 2026-11-23

## Problème
Les équipes support et exploitation reçoivent chaque jour des tickets rédigés en texte libre, de qualité inégale.
Le premier tri (catégorie, priorité, procédure à suivre) est manuel. Il prend du temps aux personnes les plus expérimentées,
et une erreur de priorité sur un incident bloquant retarde la remise en service.

## Utilisateurs
Agents de support N1/N2 au moment de la prise en charge d'un ticket, et responsable d'exploitation pour le suivi.

## Réutilisation
À vérifier avec la DSI : l'outil de ticketing propose-t-il déjà une catégorisation ? Le socle IA interne propose-t-il un service de RAG réutilisable ?
Le MVP est conçu pour que le moteur de recherche et le client LLM soient remplaçables par des briques du socle (interfaces isolées dans `retrieval.py` et `llm.py`).

## Périmètre du MVP
- Dans le périmètre : suggestion de catégorie, de priorité (P1 à P4) avec justification, fiches de procédure pertinentes, résumé masqué, journal d'audit.
- Hors périmètre : création ou modification automatique du ticket (l'humain valide toujours), intégration à l'outil de ticketing, apprentissage automatique.

## Critères d'acceptation
- CA1. Étant donné un ticket, quand il est trié, alors l'outil renvoie une catégorie, une priorité, une justification et au plus 3 fiches.
- CA2. Étant donné un ticket qui décrit un service totalement indisponible pour les voyageurs, quand il est trié, alors la priorité est P1.
- CA3. Étant donné un ticket contenant un e-mail, un téléphone, une IP, un IBAN ou un matricule, quand il est trié, alors aucune de ces valeurs n'apparaît dans la sortie ni dans le journal.
- CA4. Étant donné un ticket contenant une tentative d'injection de prompt, quand il est trié, alors il est signalé, n'est pas envoyé au LLM, et la priorité reste calculée par les règles.
- CA5. Étant donné une indisponibilité du fournisseur LLM, quand un ticket est trié, alors l'outil répond en mode dégradé, sans erreur.
- CA6. Sur le jeu de référence : F1 macro catégorie supérieur ou égal à 0,85, aucune sous-priorisation grave, hit@3 supérieur ou égal à 0,90, zéro fuite.

## Données manipulées
Texte libre des tickets (peut contenir des données personnelles). Masquage systématique avant LLM, journal et affichage.
Journal d'audit : hash du texte, décision, sources, version des règles et du modèle, coût estimé. Conservation : 90 jours.

## Classification AI Act
Risque minimal : outil d'aide interne, sans décision sur des personnes, avec validation humaine systématique. Détail dans `docs/AI_ACT.md`.

## Indicateurs de succès
- Usage : part des tickets triés avec l'assistant (cible 60 % à 60 jours).
- Qualité : taux d'acceptation des suggestions sans modification (cible 80 %).
- Valeur : temps médian de premier tri (mesure de départ à faire, cible moins 50 %).
- Coût : moins de 0,002 € par ticket.

## Critères d'arrêt
- Moins de 30 % d'usage à 60 jours après deux itérations.
- Taux d'acceptation inférieur à 60 % à 90 jours.
- Une sous-priorisation grave non détectée en production.

## Questions ouvertes
- Quel outil de ticketing, et existe-t-il une API pour lire les tickets ?
- Les fiches de procédure existent-elles déjà sous une forme exploitable ?
- Quelle équipe accepte d'être propriétaire du produit ?
