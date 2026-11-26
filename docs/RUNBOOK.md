# Runbook : assistant de tri des incidents

## Architecture en une phrase
Une fonction Python sans dépendance (`core/aiguillage`) exposée par une API (`api/triage.py`). Le LLM est optionnel : sans lui, tout fonctionne en mode déterministe.

## Symptômes et actions

| Symptôme | Diagnostic | Action |
|---|---|---|
| Le résumé est toujours « déterministe » | Lire `resume.erreur`, puis ouvrir `/api/triage?diagnostic` : clé lue ou non, modèles accessibles avec la clé | Clé absente : `LLM_API_KEY` ou `GROQ_API_KEY`. Modèle refusé : choisir un identifiant de la liste dans `LLM_MODELE`. Le service reste utilisable en mode dégradé. |
| Beaucoup de tickets « À qualifier » | Vocabulaire nouveau, ou fiches de procédure absentes pour ce sujet | Ajouter ou enrichir une fiche dans `data/fiches/`, ajouter des cas au jeu de référence, relancer l'évaluation |
| Une priorité est jugée fausse par les agents | Lire `priorite.justification` dans la réponse | Ajouter le cas au jeu de référence, ajuster les listes de `regles.py`, vérifier que la CI reste verte |
| Alerte « suspect » sur un ticket légitime | Lire `securite.motifs` | Ajouter le cas aux tests `LEGITIMES` de `tests/test_injection.py`, affiner le motif |
| Coût en hausse | Somme de `cout_usd` dans le journal | Vérifier le volume, le modèle (`LLM_MODELE`) et la longueur des tickets |
| La CI est rouge | Lire le contrôle en échec et le skill associé | Corriger avant toute mise en production |

## Commandes utiles
```bash
python -m pytest -q                      # tests
python eval/run_eval.py                  # évaluation et seuils
python harness/checks/conformite.py      # conformité au harnais
```

## Escalade
1. Équipe propriétaire (voir `docs/PASSATION.md`).
2. Référent build IA.
3. Référent IA / SSI si suspicion de fuite de données ou d'attaque.
