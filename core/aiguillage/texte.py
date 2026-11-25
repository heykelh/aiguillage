"""Normalisation de texte partagée par les modules."""

import re
import unicodedata


def normaliser(texte: str) -> str:
    """Met en minuscules, retire les accents et compacte les espaces."""
    sans_accents = unicodedata.normalize("NFKD", texte)
    sans_accents = "".join(c for c in sans_accents if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sans_accents.lower()).strip()


def jetons(texte: str) -> list[str]:
    """Découpe un texte normalisé en mots d'au moins 2 caractères."""
    return [m for m in re.findall(r"[a-z0-9]+", normaliser(texte)) if len(m) > 1]
