"""Détection des tentatives d'injection de prompt (skill securite-ia).

Un ticket est une donnée, jamais une instruction. Si un ticket est suspect,
il n'est pas envoyé au LLM : le tri reste entièrement déterministe.
"""

import re
from dataclasses import dataclass, field

from .texte import normaliser

# Motifs appliqués sur le texte normalisé (minuscules, sans accents).
MOTIFS = {
    "contournement_consignes": r"\b(ignore[rsz]?|oublie[rsz]?|ne tiens? pas compte)\b.{0,30}\b(instructions?|consignes?|regles?|prompt|ce qui precede)\b",
    "contournement_consignes_en": r"\b(ignore|disregard|forget)\b.{0,30}\b(previous|above|prior|all)\b.{0,20}\b(instructions?|rules?|prompt)\b",
    "changement_de_role": r"\b(tu es (desormais|maintenant)|a partir de maintenant tu|agis comme|joue le role|you are now|act as)\b",
    "extraction_prompt": r"\b(revele|affiche|montre|donne|repete|print|reveal|show)\b.{0,30}\b(prompt|instructions? systeme|system prompt|consignes? internes?)\b",
    "mode_privilegie": r"\b(developer mode|mode developpeur|jailbreak|dan mode|sans restriction|mode admin)\b",
    "balise_systeme": r"(</?\s*(system|donnees|instructions?)\s*>|\[/?inst\]|<\|im_start\|>)",
    "exfiltration": r"\b(envoie|transmets|send|post)\b.{0,40}\b(https?://|webhook|cle api|api key|mot de passe|token)\b",
}
MOTIFS_COMPILES = {nom: re.compile(motif) for nom, motif in MOTIFS.items()}
MOTIF_BASE64 = re.compile(r"[A-Za-z0-9+/]{60,}={0,2}")


@dataclass
class AnalyseSecurite:
    suspect: bool
    motifs: list[str] = field(default_factory=list)


def analyser(texte: str) -> AnalyseSecurite:
    """Analyse un texte et renvoie les motifs d'injection détectés."""
    normalise = normaliser(texte)
    motifs = [nom for nom, motif in MOTIFS_COMPILES.items() if motif.search(normalise)]
    if MOTIF_BASE64.search(texte):
        motifs.append("contenu_encode")
    return AnalyseSecurite(suspect=bool(motifs), motifs=motifs)


def neutraliser(texte: str) -> str:
    """Retire les phrases qui contiennent un motif d'injection.

    Même un moteur déterministe peut être manipulé : « Ignore toutes les instructions »
    contient « toutes les », lu comme un impact fort. On décide donc sur le texte nettoyé.
    """
    import re as _re

    phrases = _re.split(r"(?<=[.!?])\s+|\n+", texte)
    gardees = [p for p in phrases if not analyser(p).suspect]
    return " ".join(gardees).strip()
