# ADR 0002 : zéro dépendance d'exécution

## Contexte
Un outil interne doit passer les revues sécurité et être maintenu par une équipe qui ne l'a pas écrit.

## Décision
Le cœur n'utilise que la bibliothèque standard Python (BM25 et client HTTP écrits à la main, en moins de 100 lignes chacun).
Seul `pytest` est utilisé, pour les tests.

## Conséquences
- Aucune vulnérabilité de dépendance à suivre, déploiement trivial.
- Les briques (recherche, client LLM) sont isolées derrière une interface simple et remplaçables par celles du socle IA de l'entreprise.
