---
name: spec-first
description: À utiliser avant toute nouvelle fonctionnalité ou tout nouvel outil IA. Produit une spec testable à partir du template avant d'écrire la moindre ligne de code.
---

# Spec-first (Spec-Driven Development)

## Quand
Dès qu'on te demande de construire, refondre ou étendre un outil. Pas de code avant que la spec soit validée par un humain.

## Étapes
1. Copie `specs/_template/spec.md` vers `specs/NNN-nom-court/spec.md` (NNN = numéro suivant).
2. Remplis chaque section. Si une information manque, écris-la dans « Questions ouvertes » et pose-la à l'humain. N'invente pas.
3. Écris les critères d'acceptation au format « Étant donné / Quand / Alors », chacun vérifiable par un test.
4. Remplis « Réutilisation » : un outil IA interne existant couvre-t-il déjà le besoin ? Si oui, on s'arrête là et on le documente.
5. Remplis « Critères d'arrêt » : à quelles conditions on arrête le produit (adoption, qualité, coût).
6. Fais valider la spec. Ensuite seulement, génère le code, critère par critère, avec un test par critère.

## Contrôles
- `harness/checks/conformite.py` vérifie que chaque dossier `specs/NNN-*` contient les sections obligatoires.
- Un critère d'acceptation sans test associé est signalé dans la revue.

## Anti-patterns
- Générer tout le code d'un coup « pour voir ».
- Une spec qui décrit la solution technique au lieu du problème.
- Des critères non mesurables (« rapide », « intuitif »).
