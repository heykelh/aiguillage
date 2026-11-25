# Rapport d'évaluation

Version des règles : `2026.11.2` ; 62 tickets fictifs annotés.

| Métrique | Valeur |
|---|---|
| f1_macro_categorie | 0.987 |
| exactitude_categorie | 0.984 |
| exactitude_priorite | 0.935 |
| sous_priorisations_graves | 0 |
| hit_at_3_fiches | 1.0 |
| rappel_injection | 1.0 |
| faux_positifs_injection | 0 |
| fuites_donnees_personnelles | 0 |
| latence_moyenne_ms | 0.88 |

## Par catégorie

| Catégorie | Précision | Rappel | F1 | Support |
|---|---|---|---|---|
| ACCES | 1.0 | 1.0 | 1.0 | 9 |
| A_QUALIFIER | 1.0 | 1.0 | 1.0 | 1 |
| DONNEES | 1.0 | 1.0 | 1.0 | 9 |
| INFO_VOYAGEURS | 1.0 | 1.0 | 1.0 | 8 |
| INFRA | 1.0 | 0.889 | 0.941 | 9 |
| PAIEMENT | 1.0 | 1.0 | 1.0 | 9 |
| POSTE | 1.0 | 1.0 | 1.0 | 7 |
| VENTE | 0.909 | 1.0 | 0.952 | 10 |

## Erreurs restantes (à analyser, pas à cacher)

- T003 : catégorie PAIEMENT -> PAIEMENT, priorité P3 -> P2 : « Le terminal de paiement du guichet 3 de la gare est en panne, impossible d'encaisser. »
- T006 : catégorie PAIEMENT -> PAIEMENT, priorité P4 -> P3 : « Transaction en échec pour Mme Durand, merci de la rappeler au 06 12 34 56 78. »
- T029 : catégorie DONNEES -> DONNEES, priorité P2 -> P1 : « Tous les traitements de nuit sont en échec, aucun fichier produit pour la production ce ma »
- T042 : catégorie INFRA -> VENTE, priorité P1 -> P1 : « Erreur 503 sur l'API de réservation en production, tous les clients sont touchés. »
- T055 : catégorie POSTE -> POSTE, priorité P4 -> P3 : « Ma webcam et mon casque ne sont plus reconnus sur la station d'accueil. »

## Jeu de validation (rédigé après le gel des règles, jamais utilisé pour les régler)

| Métrique | Valeur |
|---|---|
| f1_macro_categorie | 1.0 |
| exactitude_categorie | 1.0 |
| exactitude_priorite | 0.812 |
| sous_priorisations_graves | 0 |
| hit_at_3_fiches | 0.938 |
| rappel_injection | 1.0 |
| faux_positifs_injection | 0 |
| fuites_donnees_personnelles | 0 |
| latence_moyenne_ms | 0.49 |

- V001 : catégorie VENTE -> VENTE, priorité P2 -> P3 : « Les clients ne peuvent plus télécharger leur billet depuis l'application, erreur à l'ouver »
- V007 : catégorie POSTE -> POSTE, priorité P3 -> P4 : « Mon écran externe ne s'allume plus. »
- V012 : catégorie DONNEES -> DONNEES, priorité P2 -> P1 : « Le rapport Power BI des ventes ne se rafraîchit plus depuis lundi pour toute la direction. »

## Seuils (appliqués au jeu de référence)

Tous les seuils sont atteints.
