"""Recherche des fiches de procédure : BM25 lexical + bonus métier.

Interface volontairement minimale (rechercher) pour pouvoir être remplacée
par un service de RAG du socle IA de l'entreprise sans toucher au reste.
"""

import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .texte import jetons

DOSSIER_FICHES = Path(__file__).resolve().parents[2] / "data" / "fiches"
MOTS_VIDES = set(
    "le la les un une des de du et en a au aux pour par sur dans est sont pas ne plus que qui quoi ce cet cette "
    "ces il elle ils elles on nous vous je tu se sa son ses leur leurs avec sans ou mais donc car si y d l s "
    "qu c n j m t etre avoir fait faire tout tous toute toutes tres bien depuis".split()
)
K1, B = 1.5, 0.75
BONUS_CATEGORIE = 1.5
SEUIL_RELATIF = 0.35


@dataclass
class Fiche:
    id: str
    titre: str
    categorie: str
    contenu: str


@dataclass
class Resultat:
    id: str
    titre: str
    categorie: str
    score: float
    extrait: str


def _lire_fiche(chemin: Path) -> Fiche:
    texte = chemin.read_text(encoding="utf-8")
    entete, _, corps = texte.partition("\n---\n")
    meta = dict(
        ligne.split(":", 1) for ligne in entete.strip("-\n").splitlines() if ":" in ligne
    )
    return Fiche(
        id=meta["id"].strip(),
        titre=meta["titre"].strip(),
        categorie=meta["categorie"].strip(),
        contenu=corps.strip(),
    )


def _termes(texte: str) -> list[str]:
    return [m for m in jetons(texte) if m not in MOTS_VIDES]


@lru_cache(maxsize=1)
def _index() -> tuple[list[Fiche], list[list[str]], dict[str, float], float]:
    fiches = [_lire_fiche(p) for p in sorted(DOSSIER_FICHES.glob("*.md"))]
    docs = [_termes(f.titre + " " + f.titre + " " + f.contenu) for f in fiches]
    n = len(docs)
    df: dict[str, int] = {}
    for doc in docs:
        for terme in set(doc):
            df[terme] = df.get(terme, 0) + 1
    idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}
    longueur_moyenne = sum(len(d) for d in docs) / max(n, 1)
    return fiches, docs, idf, longueur_moyenne


def _extrait(contenu: str) -> str:
    premiere = next((l for l in contenu.splitlines() if l.strip() and not l.startswith("#")), "")
    return re.sub(r"\s+", " ", premiere)[:180]


def rechercher_brut(requete: str) -> list[Resultat]:
    """Scores BM25 de toutes les fiches, sans filtre (utilisé par le classement)."""
    return _scorer(requete, None)


def rechercher(requete: str, categorie: str | None = None, k: int = 3) -> list[Resultat]:
    """Renvoie les k fiches les plus pertinentes pour la requête."""
    resultats = _scorer(requete, categorie)
    if resultats:  # on écarte les fiches trop éloignées de la meilleure
        seuil = resultats[0].score * SEUIL_RELATIF
        resultats = [r for r in resultats if r.score >= seuil]
    return resultats[:k]


def _scorer(requete: str, categorie: str | None) -> list[Resultat]:
    fiches, docs, idf, lm = _index()
    q = _termes(requete)
    resultats: list[Resultat] = []
    for fiche, doc in zip(fiches, docs):
        score = 0.0
        for terme in set(q):
            tf = doc.count(terme)
            if tf:
                score += idf.get(terme, 0) * tf * (K1 + 1) / (tf + K1 * (1 - B + B * len(doc) / lm))
        if categorie and fiche.categorie == categorie and score > 0:
            score += BONUS_CATEGORIE
        if score > 0:
            resultats.append(Resultat(fiche.id, fiche.titre, fiche.categorie, round(score, 2), _extrait(fiche.contenu)))
    resultats.sort(key=lambda r: r.score, reverse=True)
    return resultats


def toutes_les_fiches() -> list[Fiche]:
    return list(_index()[0])
