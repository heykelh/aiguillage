# Passation du build au run

| Élément | Statut |
|---|---|
| Équipe propriétaire | À désigner (proposition : équipe Exploitation applicative) |
| Personne référente côté équipe | À désigner |
| Référent build | Heykel Hachiche |
| Session de construction en binôme | À planifier : l'équipe ajoute elle-même une fiche et une règle, CI comprise |
| Première modification faite seule par l'équipe | À faire |
| Secrets transférés dans le coffre de l'équipe | À faire |
| Revue 30 / 60 / 90 jours | Voir critères d'arrêt dans la spec 001 |

## Ce que l'équipe doit savoir faire seule
1. Ajouter une fiche de procédure (`data/fiches/Fxx.md`) et vérifier qu'elle remonte (évaluation, hit@3).
2. Ajouter un cas au jeu de référence quand un agent signale une erreur.
3. Ajuster une règle de priorité et vérifier qu'aucune sous-priorisation grave n'apparaît.
4. Lire le journal d'audit pour répondre à « pourquoi l'outil a proposé ça ? ».

## Comment l'équipe construit ensuite ses propres outils
Avec le même harnais : `AGENTS.md` et les skills de `.claude/skills/` guident leur agent de code, et `harness/checks/conformite.py` vérifie le résultat.
