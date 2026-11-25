---
name: evaluation-llm
description: À utiliser pour tout comportement IA (classification, RAG, agent, génération). Définit le jeu de référence, les métriques et les seuils qui bloquent la CI.
---

# Évaluation d'un comportement IA

## Principe
On ne dit pas « ça marche » : on montre un chiffre, mesuré sur un jeu de référence, comparé à un seuil.

## Étapes
1. **Jeu de référence** au format JSONL dans `data/`, avec la réponse attendue pour chaque cas. Viser au moins 50 cas, dont des cas pièges (injection, données personnelles, ambiguïtés).
2. **Métriques adaptées :**
   - classification : précision, rappel, F1 par classe, et F1 macro ;
   - priorité : exactitude, et surtout « sous-priorisations graves » (un P1 classé P3 ou P4), qui doivent être à 0 ;
   - recherche (RAG) : la bonne fiche est-elle dans les 3 premières (hit@3) ;
   - sécurité : taux de détection des injections, nombre de fuites de données personnelles (doit être 0) ;
   - coût : coût moyen estimé par requête.
3. **Seuils** dans `eval/seuils.json`. La CI échoue si un seuil n'est pas atteint.
4. **Rapport** généré dans `eval/RAPPORT.md` et `eval/resultats.json`, lu par le tableau de bord.
5. **En production :** on échantillonne des cas réels (masqués), on les fait annoter, on les ajoute au jeu de référence. Le jeu vit.

## Anti-patterns
- Évaluer sur les exemples qui ont servi à écrire les règles, sans cas nouveaux.
- Un seul chiffre global qui cache une classe ratée.
- LLM-as-judge sans calibration sur un échantillon annoté par un humain.
