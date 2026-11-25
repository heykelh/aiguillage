"""Classement hybride (v2) : règles + signal des fiches de procédure.

Constat de la v1 (eval/historique/v1.json) : les règles seules atteignent 0,97 de F1 sur le jeu
qui a servi à les écrire, mais 0,64 sur un jeu tenu à l'écart. Elles ne généralisent pas.

Correction structurelle, sans ajout de vocabulaire : les fiches de procédure décrivent chaque
catégorie avec un vocabulaire riche. On ajoute au score des règles le score BM25 des fiches de
chaque catégorie. Le résultat reste déterministe et explicable.
"""

from collections import defaultdict

from . import recherche, regles

POIDS_FICHES = 1.0
SEUIL_HYBRIDE = 3.0


def classer(texte: str) -> regles.Decision:
    """Combine le score des règles et le meilleur score de fiche par catégorie."""
    scores: dict[str, float] = defaultdict(float)
    indices: dict[str, list[str]] = defaultdict(list)

    t = regles._ponctuer(texte)
    for code, definition in regles.CATEGORIES.items():
        trouves = [mot for mot in definition["indices"] if regles._contient(t, mot)]
        scores[code] += sum(definition["indices"][mot] for mot in trouves)
        indices[code].extend(trouves)

    for resultat in recherche.rechercher_brut(texte):
        signal = POIDS_FICHES * resultat.score
        if signal > scores.get(f"_fiche_{resultat.categorie}", 0):
            scores[f"_fiche_{resultat.categorie}"] = signal

    totaux = {
        code: scores[code] + scores.get(f"_fiche_{code}", 0.0) for code in regles.CATEGORIES
    }
    meilleur = max(totaux, key=lambda c: totaux[c])
    score = round(totaux[meilleur], 2)
    preuves = indices[meilleur] + ([f"fiche {meilleur.lower()} (+{scores[f'_fiche_{meilleur}']:.1f})"] if scores.get(f"_fiche_{meilleur}") else [])

    if score < SEUIL_HYBRIDE:
        return regles.Decision("A_QUALIFIER", "À qualifier par un humain", score, preuves, True)
    return regles.Decision(meilleur, regles.CATEGORIES[meilleur]["libelle"], score, preuves)
