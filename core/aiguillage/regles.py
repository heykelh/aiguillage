"""Moteur de règles déterministe : catégorie et priorité.

Principe du harnais : « le moteur calcule, le LLM rédige ».
Chaque décision est explicable : on renvoie les indices qui l'ont déclenchée.
"""

import re
from dataclasses import dataclass, field
from functools import lru_cache

from .texte import normaliser

CATEGORIES: dict[str, dict] = {
    "VENTE": {
        "libelle": "Vente et réservation",
        "indices": {
            "reservation": 3, "reserver": 3, "billet": 3, "billets": 3, "e-billet": 3, "vente": 3,
            "panier": 2, "commande": 2, "tarif": 2, "echange": 2, "annulation": 2, "place": 1, "places": 1,
            "guichet": 2, "borne de vente": 3, "carte avantage": 2, "abonnement": 2, "dossier voyage": 3,
            "remboursement": 1, "plan de salle": 2,
        },
    },
    "PAIEMENT": {
        "libelle": "Paiement",
        "indices": {
            "paiement": 4, "payer": 3, "carte bancaire": 4, "3d secure": 4, "3ds": 3, "transaction": 3,
            "debit": 3, "debite": 3, "prestataire de paiement": 4, "psp": 3, "refuse": 1, "terminal de paiement": 4, "tpe": 3,
            "encaissement": 3, "double debit": 4,
        },
    },
    "INFO_VOYAGEURS": {
        "libelle": "Information voyageurs",
        "indices": {
            "affichage": 3, "ecran": 2, "ecrans": 2, "afficheur": 3, "afficheurs": 3, "horaires": 2, "temps reel": 3,
            "voie": 1, "quai": 2, "annonce sonore": 3, "annonces": 2, "retard affiche": 3, "info trafic": 3,
            "information voyageurs": 4, "panneau": 2, "notification push": 3, "notifications push": 3, "alerte trafic": 3, "depart": 1,
        },
    },
    "DONNEES": {
        "libelle": "Traitements et flux de données",
        "indices": {
            "batch": 4, "traitement de nuit": 4, "traitements de nuit": 4, "colonne": 2, "flux": 3, "etl": 4, "export": 2, "import": 2, "fichier": 1,
            "csv": 2, "chargement": 2, "pipeline": 3, "job": 3, "ordonnanceur": 4, "dataset": 3,
            "rapport": 1, "tableau de bord": 2, "donnees manquantes": 4, "doublons": 3, "power bi": 3,
        },
    },
    "ACCES": {
        "libelle": "Accès et comptes",
        "indices": {
            "mot de passe": 4, "compte": 2, "acces": 2, "authentification": 4, "connexion": 1, "sso": 4,
            "habilitation": 3, "droits": 3, "verrouille": 3, "bloque": 1, "identifiant": 2, "mfa": 4,
            "double authentification": 4, "profil": 2, "badge": 2,
        },
    },
    "INFRA": {
        "libelle": "Infrastructure et réseau",
        "indices": {
            "serveur": 3, "reseau": 3, "vpn": 4, "base de donnees": 3, "stockage": 3, "disque": 3, "cpu": 3,
            "memoire": 2, "latence": 2, "certificat": 3, "dns": 4, "load balancer": 4, "kubernetes": 4, "pod": 3,
            "cluster": 3, "sauvegarde": 3, "datacenter": 4, "pare-feu": 4, "firewall": 4, "api": 2, "timeout": 2,
            "erreur 500": 3, "erreur 502": 3, "erreur 503": 3, "supervision": 2,
        },
    },
    "POSTE": {
        "libelle": "Poste de travail",
        "indices": {
            "pc": 3, "ordinateur": 3, "portable": 2, "imprimante": 4, "ecran externe": 3, "clavier": 3, "souris": 3,
            "outlook": 4, "messagerie": 3, "teams": 3, "casque": 3, "station d'accueil": 3, "windows": 2,
            "logiciel": 2, "installation": 2, "lent au demarrage": 3, "webcam": 3,
        },
    },
}

SEUIL_CONFIANCE = 3  # en dessous, on demande une qualification humaine.

# Impact générique : quantificateurs universels ou partiels, quel que soit le nom qui suit.
IMPACT_FORT_MOTIFS = [r"\b(tous|toutes) les \w+", r"\btoute la \w+", r"\btout le \w+"]
IMPACT_MOYEN_MOTIFS = [r"\bplusieurs \w+", r"\b(certains|certaines) \w+", r"\b\d{1,3} ?%"]

# Impact : combien de personnes ou de voyageurs sont touchés.
IMPACT_FORT = [
    "tous les voyageurs", "tous les clients", "toutes les gares", "national", "nationale", "ensemble du reseau",
    "toute la france", "tous les sites", "toutes les ventes", "tous les paiements", "plus personne",
    "aucun client", "aucun voyageur", "aucune vente", "aucun paiement", "toutes les agences",
    "en masse", "massivement", "tous les agents", "tout le reseau", "du reseau", "toutes les bornes", "tous les utilisateurs", "des milliers", "tous les trains", "toutes les lignes",
]
IMPACT_MOYEN = [
    "une gare", "plusieurs gares", "un site", "une equipe", "le service", "plusieurs agents", "plusieurs utilisateurs",
    "une region", "une ligne", "plusieurs clients", "des clients", "des voyageurs", "l'equipe", "le plateau",
    "plusieurs collegues", "une agence", "certains clients", "certains voyageurs", "une partie", "la gare", "en gare", "les voyageurs", "tous les traitements", "tous les jobs", "rapport mensuel", "tableau de bord", "les rapports",
]
# Urgence : à quel point le service est arrêté.
URGENCE_HAUTE = [
    "bloque", "bloquant", "bloquee", "impossible", "indisponible", "hors service", "panne", "en panne", "plante",
    "ne fonctionne plus", "ne marche plus", "a l'arret", "arret total", "down", "inaccessible", "erreur 500",
    "erreur 502", "erreur 503", "crash", "tombe", "coupure", "aucune reponse", "fuite de donnees", "faille", "fige", "echoue", "echouent", "en echec", "a echoue", "hors ligne",
    "ne marche pas", "ne fonctionne pas", "does not work", "not working", "ne passe",
]
URGENCE_MOYENNE = [
    "lent", "lenteur", "lenteurs", "degrade", "intermittent", "parfois", "de temps en temps", "erreur", "echec",
    "incorrect", "incorrecte", "faux", "fausse", "decalage", "retard", "manquant", "manquantes", "ne s'affiche pas",
    "ne se lance pas", "refuse",
]
URGENCE_BASSE = [
    "question", "demande", "souhaiterais", "voudrais", "amelioration", "evolution", "quand vous pourrez",
    "pas urgent", "information", "comment faire", "besoin de", "installer", "nouveau",
]

# Matrice impact x urgence de type ITIL. 1 = fort / haute, 3 = faible / basse.
MATRICE = {
    (1, 1): "P1", (1, 2): "P2", (1, 3): "P3",
    (2, 1): "P2", (2, 2): "P3", (2, 3): "P4",
    (3, 1): "P3", (3, 2): "P4", (3, 3): "P4",
}


@dataclass
class Decision:
    code: str
    libelle: str
    score: int
    indices: list[str] = field(default_factory=list)
    a_qualifier: bool = False


@dataclass
class Priorite:
    niveau: str
    impact: int
    urgence: int
    justification: list[str] = field(default_factory=list)


# Expressions régulières supplémentaires d'urgence haute (« ne ... plus », « plus aucun »).
URGENCE_HAUTE_MOTIFS = [r"\bne \w+ plus\b", r"\bne se \w+ plus\b", r"\bn \w+ plus\b", r"\bplus aucune?\b"]


@lru_cache(maxsize=None)
def _motif(expression: str) -> re.Pattern:
    """Expression sur frontières de mots, tolérante au pluriel et à l'accord (s, x, e, es, ee, ees)."""
    expr = _ponctuer(expression)
    return re.compile(r"(?<![a-z0-9])" + re.escape(expr) + r"(?:s|x|e|es|ee|ees)?(?![a-z0-9])")


def _contient(texte_normalise: str, expression: str) -> bool:
    return bool(_motif(expression).search(texte_normalise))


def _ponctuer(texte: str) -> str:
    """Normalise et remplace la ponctuation (apostrophes comprises) par des espaces."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 -]", " ", normaliser(texte))).strip()


def classer(texte: str) -> Decision:
    """Calcule la catégorie la plus probable à partir d'indices pondérés."""
    t = _ponctuer(texte)
    meilleur: Decision | None = None
    for code, definition in CATEGORIES.items():
        trouves = [mot for mot in definition["indices"] if _contient(t, mot)]
        score = sum(definition["indices"][mot] for mot in trouves)
        if meilleur is None or score > meilleur.score:
            meilleur = Decision(code, definition["libelle"], score, trouves)
    assert meilleur is not None
    if meilleur.score < SEUIL_CONFIANCE:
        return Decision("A_QUALIFIER", "À qualifier par un humain", meilleur.score, meilleur.indices, True)
    return meilleur


def _premier(t: str, expressions: list[str]) -> str | None:
    return next((e for e in expressions if _contient(t, e)), None)


def prioriser(texte: str) -> Priorite:
    """Calcule la priorité P1 à P4 par la matrice impact x urgence."""
    t = _ponctuer(texte)
    justification: list[str] = []

    def _motifs(motifs: list[str], cible: str) -> str | None:
        return next((m.group(0) for r in motifs if (m := re.search(r, cible))), None)

    if (e := _premier(t, IMPACT_FORT) or _motifs(IMPACT_FORT_MOTIFS, t)):
        impact = 1
        justification.append(f"impact fort (« {e} »)")
    elif (e := _premier(t, IMPACT_MOYEN) or _motifs(IMPACT_MOYEN_MOTIFS, texte)):
        impact = 2
        justification.append(f"impact moyen (« {e} »)")
    else:
        impact = 3
        justification.append("impact individuel (aucun indice de portée collective)")

    motif_haut = next((m.group(0) for r in URGENCE_HAUTE_MOTIFS if (m := re.search(r, t))), None)
    if (e := _premier(t, URGENCE_HAUTE) or motif_haut):
        urgence = 1
        justification.append(f"urgence haute (« {e} »)")
    elif (e := _premier(t, URGENCE_MOYENNE)):
        urgence = 2
        justification.append(f"urgence moyenne (« {e} »)")
    elif (e := _premier(t, URGENCE_BASSE)):
        urgence = 3
        justification.append(f"urgence basse (« {e} »)")
    else:
        urgence = 2
        justification.append("urgence moyenne par défaut (aucun indice)")

    niveau = MATRICE[(impact, urgence)]
    justification.append(f"matrice impact {impact} x urgence {urgence} = {niveau}")
    return Priorite(niveau, impact, urgence, justification)
