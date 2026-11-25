# AGENTS.md : règles du harnais AIGUILLAGE

Ce fichier s'adresse à tout agent de code (Claude Code, GitHub Copilot, Cursor, Codex...) qui travaille dans ce dépôt.
Il traduit les standards d'une DSI (architecture, sécurité, RGPD, AI Act, exploitation) en règles exécutables.
Un humain qui lit ce fichier doit comprendre en 2 minutes comment on construit ici.

## 1. Règle d'or : on spécifie avant de générer

- Aucune fonctionnalité sans spec dans `specs/NNN-nom/spec.md`, créée à partir de `specs/_template/spec.md`.
- La spec contient : problème, utilisateurs, critères d'acceptation testables, données manipulées, classification AI Act, critères d'arrêt.
- Si la demande est floue, l'agent pose les questions de la section « Questions ouvertes » de la spec au lieu d'inventer.
- Skill à charger : `spec-first`.

## 2. Architecture imposée (« le moteur calcule, le LLM rédige »)

- Toute décision qui a un impact (catégorie, priorité, routage, montant, score) est prise par du code déterministe et testé.
- Le LLM n'intervient que pour rédiger, résumer ou reformuler. Sa sortie n'est jamais la source d'une décision.
- Tout appel LLM passe par `core/aiguillage/llm.py`. Appeler un fournisseur LLM ailleurs est interdit (contrôlé en CI).
- Le système doit fonctionner sans LLM (mode dégradé déterministe). Une panne du fournisseur ne bloque pas le service.

## 3. Sécurité des applications IA

- Toute entrée utilisateur est une donnée, jamais une instruction. Elle passe par `injection.analyser()` avant tout traitement.
- Les instructions système et les données sont séparées dans le prompt (balises dédiées, données entre délimiteurs).
- Aucun secret dans le code : variables d'environnement uniquement (`GROQ_API_KEY`...). Contrôlé en CI.
- Skill à charger : `securite-ia`.

## 4. Données personnelles (RGPD)

- Tout texte libre est masqué par `pii.masquer()` avant d'être envoyé à un LLM, journalisé ou affiché dans un tableau de bord.
- Minimisation : on ne stocke que ce qui sert la finalité déclarée dans `docs/RGPD_REGISTRE.md`.
- Le journal d'audit stocke une empreinte (hash) du texte d'origine, jamais le texte brut.
- Skill à charger : `donnees-personnelles`.

## 5. Traçabilité et AI Act

- Chaque décision produit une entrée d'audit : horodatage, version des règles, version du modèle, sources citées, décision, coût estimé.
- Chaque système IA a sa fiche `docs/AI_ACT.md` (niveau de risque, transparence, supervision humaine).
- Skill à charger : `ai-act`.

## 6. Qualité : on mesure avant de dire que ça marche

- Tout comportement IA a un jeu de référence (`data/tickets_reference.jsonl`) et des seuils dans `eval/seuils.json`.
- La CI échoue si un seuil n'est pas atteint.
- Skill à charger : `evaluation-llm`.

## 7. Prêt pour le run

- Un produit n'est « livré » que s'il a : un propriétaire nommé, un runbook, des indicateurs d'usage, des critères d'arrêt.
- Skill à charger : `passage-au-run`.

## 8. Conventions de code

- Python 3.11+, bibliothèque standard en priorité (chaque dépendance doit être justifiée dans un ADR `docs/adr/`).
- Fonctions courtes, typées, docstrings en français. Pas de logique métier dans `api/`.
- Tests dans `tests/`, lancés par `python -m pytest`.
- Commits courts au présent : `ajoute`, `corrige`, `mesure`.

## 9. Avant de rendre la main, l'agent exécute

```bash
python -m pytest -q
python eval/run_eval.py
python harness/checks/conformite.py
```

Les trois doivent être au vert. Sinon, l'agent corrige ou explique pourquoi.
