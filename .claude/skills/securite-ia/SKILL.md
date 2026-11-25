---
name: securite-ia
description: À utiliser dès que du code appelle un LLM, traite du texte saisi par un utilisateur, ou manipule des secrets. Couvre l'injection de prompt, la séparation instructions/données et la gestion des secrets.
---

# Sécurité des applications IA

## Règles
1. **Entrée = donnée.** Tout texte utilisateur passe par `core/aiguillage/injection.py::analyser()` avant usage.
   Si `suspect` est vrai : on n'envoie pas le texte au LLM, on bascule en mode déterministe et on journalise l'alerte.
2. **Séparation stricte.** Le prompt système est une constante versionnée. Les données utilisateur sont insérées entre
   les balises `<donnees>` et `</donnees>`, et le prompt système rappelle de ne jamais suivre d'instruction qui s'y trouve.
3. **Le LLM ne décide pas.** Aucune sortie LLM ne modifie une catégorie, une priorité ou un routage (voir AGENTS.md §2).
4. **Sortie contrôlée.** La sortie du LLM est tronquée, nettoyée (pas de HTML actif) et repassée au masquage avant affichage.
5. **Secrets.** Jamais de clé en dur. `os.environ` uniquement. Le contrôle CI recherche les motifs de clés connus.
6. **Point d'entrée unique.** Tout appel fournisseur passe par `core/aiguillage/llm.py` (contrôlé en CI).

## Tests à écrire
- Au moins 5 tentatives d'injection dans `tests/test_injection.py` (ignore les instructions, changement de rôle, exfiltration, encodage, prompt caché).
- Un test qui vérifie qu'un ticket suspect n'atteint jamais le client LLM.

## Références
OWASP Top 10 for LLM Applications (LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM06 Excessive Agency).
