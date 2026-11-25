"""Masquage des données personnelles (skill donnees-personnelles).

Règle : tout texte libre passe par masquer() avant un LLM, un journal ou un affichage.
Approche déterministe par motifs : explicable, testable, sans envoi de données à un tiers.
"""

import re
from collections import Counter

# L'ordre compte : les motifs les plus spécifiques passent en premier.
MOTIFS: list[tuple[str, re.Pattern]] = [
    ("EMAIL", re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")),
    ("IBAN", re.compile(r"\bFR\d{2}(?:\s?[A-Z0-9]{4}){5}\s?[A-Z0-9]{3}\b", re.IGNORECASE)),
    ("CARTE", re.compile(r"\b(?:\d{4}[\s-]?){3}\d{4}\b")),
    ("TEL", re.compile(r"(?<!\d)(?:\+33\s?|0)[1-9](?:[\s.-]?\d{2}){4}(?!\d)")),
    ("IP", re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")),
    ("MATRICULE", re.compile(r"\b(?:matricule|id agent|cp)\s*:?\s*[A-Z0-9]{5,10}\b", re.IGNORECASE)),
    ("MATRICULE", re.compile(r"\b\d{7}[A-Z]\b")),
    (
        "NOM",
        re.compile(
            r"\b(?:M\.|Mme|Mlle|Monsieur|Madame)\s+[A-ZÉÈÀÂÎÔÛÇ][\w'-]+(?:\s+[A-ZÉÈÀÂÎÔÛÇ][\w'-]+)?"
        ),
    ),
]


def masquer(texte: str) -> tuple[str, dict[str, int]]:
    """Remplace les données personnelles par des jetons typés.

    Renvoie le texte masqué et le nombre de remplacements par type.
    """
    compteur: Counter = Counter()
    resultat = texte
    for type_donnee, motif in MOTIFS:
        resultat, n = motif.subn(f"[{type_donnee}]", resultat)
        if n:
            compteur[type_donnee] += n
    return resultat, dict(compteur)


def contient_donnees_personnelles(texte: str) -> bool:
    """Vrai si au moins un motif de donnée personnelle est présent."""
    return any(motif.search(texte) for _, motif in MOTIFS)
