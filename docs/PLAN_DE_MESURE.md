# Plan de mesure

On ne garde un outil que s'il est utilisé et utile. Les indicateurs sont définis avant le déploiement, avec une mesure de départ.

| Indicateur | Définition | Source | Départ | Cible |
|---|---|---|---|---|
| Usage | Part des tickets triés avec l'assistant | Journal d'audit / outil de ticketing | 0 % | 60 % à 60 jours |
| Acceptation | Part des suggestions acceptées sans modification | Retour de l'agent (accepter / corriger) | à mesurer | 80 % |
| Temps de premier tri | Médiane entre création du ticket et première qualification | Outil de ticketing | à mesurer sur 2 semaines avant déploiement | moins 50 % |
| Sous-priorisations graves | P1 ou P2 proposés en P3 ou P4 | Corrections des agents | | 0 |
| Qualité hors ligne | F1 macro, hit@3, fuites | `eval/run_eval.py` en CI | voir `eval/RAPPORT.md` | seuils de `eval/seuils.json` |
| Coût | Coût moyen par ticket et coût mensuel | Journal d'audit (`cout_usd`) | | < 0,002 USD par ticket |

## Boucle d'amélioration
Chaque correction faite par un agent devient un cas du jeu de référence. La CI empêche toute régression sur ces cas.

## Revue
À 30, 60 et 90 jours avec l'équipe propriétaire. Application des critères d'arrêt de la spec 001 : on arrête ce qui ne prend pas.
