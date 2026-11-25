---
name: passage-au-run
description: À utiliser avant de déclarer un produit livré. Vérifie qu'une équipe peut l'exploiter sans son créateur, et que son usage est mesuré.
---

# Passage du build au run

## Un produit est livré seulement si
1. **Propriétaire** : une équipe et une personne nommées dans `docs/PASSATION.md`.
2. **Runbook** : `docs/RUNBOOK.md` répond à « ça ne marche plus, je fais quoi ? » (symptômes, diagnostic, actions, escalade).
3. **Mesure** : les indicateurs d'usage et de valeur sont définis dans `docs/PLAN_DE_MESURE.md` et instrumentés dans le code (journal d'audit).
4. **Critères d'arrêt** : écrits dans la spec. Revue à 30, 60 et 90 jours.
5. **Coûts** : coût par requête et budget mensuel estimés, avec un plafond.
6. **Transfert de compétences** : au moins une session de construction en binôme avec l'équipe propriétaire, tracée dans `docs/PASSATION.md`.

## Checklist de revue
- [ ] La CI est verte (tests, évaluation, conformité).
- [ ] Le mode dégradé sans LLM a été testé.
- [ ] Les secrets sont dans le coffre de l'équipe propriétaire.
- [ ] L'équipe propriétaire a fait une modification seule, sans aide.
