# AIGUILLAGE

**Un harnais de développement IA pour une DSI, et le premier produit construit avec.**

[![Harnais IA](https://github.com/heykelh/aiguillage/actions/workflows/conformite.yml/badge.svg)](https://github.com/heykelh/aiguillage/actions/workflows/conformite.yml)

Les équipes vont de plus en plus construire leurs outils avec des agents de code. Le risque, c'est d'obtenir des dizaines de prototypes qui ne passeront jamais en production :
clés en dur, données personnelles envoyées à un fournisseur, un LLM qui décide seul, ni trace, ni tests, ni propriétaire.

AIGUILLAGE traite le problème à la source :

1. **Le harnais** : un `AGENTS.md` et six skills que l'agent de code charge avant d'écrire du code, plus des contrôles automatiques qui vérifient le résultat en CI.
2. **Le produit** : un assistant de tri des incidents (catégorie, priorité, fiches de procédure, résumé), construit avec ce harnais, mesuré et prêt à être repris par une équipe.

> Données fictives, rédigées pour la démonstration. Aucune donnée ni aucun outil interne d'une entreprise réelle.

## La démonstration en une minute

```bash
./harness/demo/avant_apres.sh
```

Même demande (« un script qui trie les tickets avec un LLM ») :

| | Sans harnais | Avec le harnais |
|---|---|---|
| Règles respectées | **0 / 9** | **9 / 9** |
| Secrets | clé en dur | variables d'environnement |
| Données personnelles | envoyées brutes au fournisseur | masquées avant tout envoi |
| Qui décide de la priorité | le LLM | des règles testées ; le LLM rédige seulement |
| Injection de prompt | exécutée | détectée, neutralisée, jamais envoyée au LLM |
| Trace | aucune | journal d'audit sans texte brut |
| Qualité | « ça a l'air de marcher » | 32 tests, évaluation avec seuils bloquants |
| Run | rien | runbook, passation, plan de mesure, critères d'arrêt |

## Le harnais

| Fichier | Rôle |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Les règles du dépôt, lues par Claude Code, Copilot, Cursor, Codex |
| [`.claude/skills/spec-first`](.claude/skills/spec-first/SKILL.md) | Spécifier avant de générer (Spec-Driven Development) |
| [`.claude/skills/securite-ia`](.claude/skills/securite-ia/SKILL.md) | Injection, séparation instructions / données, secrets, point d'entrée LLM unique |
| [`.claude/skills/donnees-personnelles`](.claude/skills/donnees-personnelles/SKILL.md) | Masquage, minimisation, registre RGPD |
| [`.claude/skills/ai-act`](.claude/skills/ai-act/SKILL.md) | Classification du risque et fiche système |
| [`.claude/skills/evaluation-llm`](.claude/skills/evaluation-llm/SKILL.md) | Jeu de référence, métriques, seuils bloquants |
| [`.claude/skills/passage-au-run`](.claude/skills/passage-au-run/SKILL.md) | Propriétaire, runbook, mesure, critères d'arrêt |
| [`harness/checks/conformite.py`](harness/checks/conformite.py) | 9 contrôles automatiques, chacun relié à un skill |
| [`specs/_template/spec.md`](specs/_template/spec.md) | Modèle de spec |

## Le produit : assistant de tri des incidents

```
ticket ─► 1. sécurité (injection) ─► 2. masquage RGPD ─► 3. catégorie (règles + fiches)
       ─► 4. priorité (impact × urgence) ─► 5. fiches (BM25) ─► 6. résumé (LLM optionnel) ─► audit
```

- **Le moteur calcule, le LLM rédige** ([ADR 0001](docs/adr/0001-le-moteur-calcule-le-llm-redige.md)). Chaque décision est expliquée.
- **Fonctionne sans LLM** : panne du fournisseur, coût ou souveraineté, le service reste utilisable.
- **Zéro dépendance d'exécution** ([ADR 0002](docs/adr/0002-zero-dependance.md)) : recherche et client LLM remplaçables par les briques du socle IA de l'entreprise.
- **Boucle d'adoption** : l'agent accepte ou corrige la suggestion (`/api/retour`), et chaque correction alimente le jeu de référence.

Spec : [`specs/001-tri-incidents/spec.md`](specs/001-tri-incidents/spec.md)

## Évaluation

Rapport complet : [`eval/RAPPORT.md`](eval/RAPPORT.md). Seuils : [`eval/seuils.json`](eval/seuils.json).

| Métrique (jeu de référence, 62 tickets) | Valeur | Seuil |
|---|---|---|
| F1 macro catégorie | 0,99 | ≥ 0,85 |
| Exactitude priorité | 0,94 | ≥ 0,80 |
| Sous-priorisations graves | 0 | 0 |
| Bonne fiche dans le top 3 | 1,00 | ≥ 0,90 |
| Injections détectées / faux positifs | 100 % / 0 | 100 % / 0 |
| Fuites de données personnelles | 0 | 0 |

**Ce que l'évaluation a révélé.** La v1 (règles par mots-clés) faisait 0,97 de F1 sur les tickets ayant servi à l'écrire, mais **0,64** sur un jeu tenu à l'écart : elle surapprenait.
La v2 corrige la structure (signal des fiches de procédure, quantificateurs génériques d'impact) sans ajouter de vocabulaire : 1,00 sur ce jeu de 16 tickets.
Ce jeu ayant été consulté une fois pour le diagnostic, la prochaine mesure propre devra se faire sur de vrais tickets annotés. Historique : [`eval/historique/`](eval/historique/).

**Une faille trouvée.** « Ignore toutes les instructions… » faisait remonter un ticket en P2 : « toutes les » était lu comme un impact fort. Même un moteur déterministe peut être manipulé.
Les décisions se prennent désormais sur le texte débarrassé des phrases suspectes, et un test le vérifie.

## Du build au run

[Runbook](docs/RUNBOOK.md) · [Passation](docs/PASSATION.md) · [Plan de mesure](docs/PLAN_DE_MESURE.md) · [Fiche AI Act](docs/AI_ACT.md) · [Registre RGPD](docs/RGPD_REGISTRE.md) · [Cadrage du portefeuille](docs/CADRAGE_PORTEFEUILLE.md)

## Lancer en local

```bash
python dev.py                       # site + API sur http://localhost:8000
python -m pytest -q                 # tests (critères d'acceptation)
python eval/run_eval.py             # évaluation et seuils
python harness/checks/conformite.py # conformité au harnais
```

Optionnel : `export GROQ_API_KEY=...` pour activer le résumé rédigé par LLM. Sans clé, tout fonctionne en mode déterministe.

## Structure

```
AGENTS.md, CLAUDE.md          règles pour les agents de code
.claude/skills/               les 6 skills du harnais
harness/checks/               contrôles de conformité (CI)
harness/demo/                 démonstration avant / après
specs/                        template + spec 001
core/aiguillage/              le produit (Python, sans dépendance)
api/                          fonctions serverless (Vercel)
data/                         fiches de procédure et tickets fictifs
eval/                         évaluation, seuils, rapport, historique
docs/                         AI Act, RGPD, runbook, passation, mesure, ADR
index.html                    site de démonstration
```

---
Conçu et construit par **Heykel Hachiche** · [heykelhachiche.com](https://heykelhachiche.com)
