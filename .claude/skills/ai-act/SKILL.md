---
name: ai-act
description: À utiliser à la création ou à la modification substantielle d'un système d'IA. Classe le système selon le règlement européen sur l'IA et produit sa fiche de conformité.
---

# AI Act : classification et fiche système

## Étapes
1. **Est-ce un système d'IA ?** Si le composant infère des sorties (prédiction, contenu, recommandation, décision) à partir d'entrées, oui.
2. **Pratique interdite (art. 5) ?** Notation sociale, manipulation, reconnaissance des émotions au travail... Si oui : on arrête.
3. **Haut risque (annexe III) ?** Points d'attention pour une DSI : gestion des travailleurs (recrutement, évaluation, attribution de tâches à des personnes),
   composants de sécurité d'infrastructures critiques. Si oui : on remonte au référent IA avant de continuer.
4. **Obligations de transparence (art. 50) ?** Chatbot face à des personnes, contenu généré : on informe l'utilisateur qu'il interagit avec une IA.
5. **Sinon : risque minimal.** On applique quand même les bonnes pratiques : supervision humaine, traçabilité, documentation.

## Livrable
Mettre à jour `docs/AI_ACT.md` avec : finalité, niveau de risque et justification, rôle (fournisseur ou déployeur), supervision humaine,
journalisation, données d'entraînement ou de contexte, limites connues, date de revue.

## Contrôle
`harness/checks/conformite.py` échoue si `docs/AI_ACT.md` est absent ou s'il manque une section obligatoire.
