# Cadrage d'un portefeuille d'irritants DSI (exemple)

Méthode : partir des irritants, qualifier la valeur, vérifier l'existant, découper en MVP, et savoir dire non.
Les irritants ci-dessous sont des hypothèses à confronter aux équipes, pas une liste validée.

Note sur 5 : Valeur (V), Effort (E, 5 = faible effort), Risque AI Act et données (R, 5 = faible risque), Réutilisation possible (U).
Score = V x 2 + E + R + U.

| Irritant (hypothèse) | Équipe | V | E | R | U | Score | Décision |
|---|---|---|---|---|---|---|---|
| Premier tri des tickets long et inégal | Support / exploitation | 4 | 4 | 5 | 3 | 20 | **MVP construit (spec 001)** |
| Écriture des cas de recette à partir des spécifications | Recette | 5 | 3 | 5 | 3 | 21 | Prochain MVP |
| Analyse des journaux après incident (chronologie, cause probable) | Exploitation | 4 | 2 | 4 | 3 | 17 | À cadrer avec la plateforme data |
| Recherche dans la documentation technique éparpillée | Développement | 3 | 4 | 5 | 5 | 20 | Vérifier d'abord l'outil IA interne existant |
| Rédaction des comptes rendus de comité | Tous | 2 | 5 | 4 | 5 | 18 | **Non** : couvert par les outils bureautiques existants |
| Évaluation automatique de la performance des agents | Management | 2 | 3 | 1 | 1 | 9 | **Non** : haut risque AI Act, pas de valeur suffisante |

## Découpage du MVP retenu
1. Jour 1 : spec, critères d'acceptation, jeu de référence.
2. Jour 2 : moteur déterministe, masquage, injection, recherche des fiches.
3. Jour 3 : évaluation, CI, journal d'audit.
4. Jour 4 : interface, passation, plan de mesure.
