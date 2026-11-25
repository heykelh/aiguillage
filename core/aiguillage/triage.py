"""Orchestration du tri d'un ticket.

Ordre imposé par le harnais :
1. analyse de sécurité sur le texte brut,
2. masquage des données personnelles,
3. décisions déterministes (catégorie, priorité),
4. recherche des fiches,
5. rédaction du résumé (LLM seulement si le ticket n'est pas suspect),
6. journal d'audit.
"""

from dataclasses import asdict

from . import audit, classement, injection, llm, pii, recherche, regles
from .version import VERSION_REGLES


def trier(texte: str, autoriser_llm: bool = True, journaliser: bool = True) -> dict:
    """Trie un ticket et renvoie une suggestion explicable, à valider par un humain."""
    texte = (texte or "").strip()[:5000]

    securite = injection.analyser(texte)
    texte_masque, pii_detectees = pii.masquer(texte)

    # Les décisions se prennent sur le texte débarrassé des phrases d'injection.
    texte_decision = injection.neutraliser(texte_masque) if securite.suspect else texte_masque
    categorie = classement.classer(texte_decision)
    priorite = regles.prioriser(texte_decision)
    fiches = recherche.rechercher(
        texte_decision, None if categorie.a_qualifier else categorie.code, k=3
    )

    redaction = llm.rediger_resume(texte_decision, autoriser_llm=autoriser_llm and not securite.suspect)
    resume, _ = pii.masquer(redaction.texte)  # la sortie du LLM repasse au masquage
    if redaction.source == "deterministe":
        resume = f"{categorie.libelle}, {priorite.niveau}. {resume}" if resume else f"{categorie.libelle}, {priorite.niveau}."

    resultat = {
        "texte_masque": texte_masque,
        "texte_decision": texte_decision,
        "transmis_au_llm": redaction.source == "llm",
        "donnees_personnelles_masquees": pii_detectees,
        "securite": asdict(securite),
        "categorie": {
            "code": categorie.code,
            "libelle": categorie.libelle,
            "score": categorie.score,
            "indices": categorie.indices,
            "a_qualifier": categorie.a_qualifier,
        },
        "priorite": asdict(priorite),
        "fiches": [asdict(f) for f in fiches],
        "resume": {"texte": resume, "source": redaction.source, "erreur": redaction.erreur},
        "cout_estime_usd": redaction.cout_usd,
        "versions": {"regles": VERSION_REGLES, "modele": redaction.modele},
        "validation_humaine_requise": True,
    }

    entree = {
        "empreinte_ticket": audit.empreinte(texte),
        "categorie": categorie.code,
        "priorite": priorite.niveau,
        "fiches": [f.id for f in fiches],
        "suspect": securite.suspect,
        "motifs_securite": securite.motifs,
        "types_pii_masques": sorted(pii_detectees),
        "source_resume": redaction.source,
        "modele": redaction.modele,
        "version_regles": VERSION_REGLES,
        "cout_usd": redaction.cout_usd,
    }
    resultat["audit"] = audit.journaliser(entree) if journaliser else entree
    return resultat
