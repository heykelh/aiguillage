# ADR 0001 : le moteur calcule, le LLM rédige

## Contexte
Une priorité d'incident fausse a un coût opérationnel. Un LLM est non déterministe, difficile à auditer, et manipulable par injection.

## Décision
Catégorie et priorité sont calculées par du code déterministe et testé (règles, matrice impact x urgence, signal des fiches).
Le LLM ne rédige qu'un résumé, sur un texte déjà masqué, et sa sortie repasse au masquage.

## Conséquences
- Chaque décision est explicable (justification renvoyée) et reproductible.
- Le service fonctionne sans LLM (panne, coût, souveraineté).
- Limite : le moteur généralise moins bien qu'un modèle. Mesuré : voir `eval/historique/` (v1 surapprenait, v2 corrigée).
- Évolution possible : un classifieur appris ou un LLM qui *propose* une catégorie, avec un plancher de priorité imposé par les règles.
