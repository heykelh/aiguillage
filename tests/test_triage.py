"""CA1, CA2, CA5 : contrat de sortie, P1 sur indisponibilité totale, mode dégradé."""

import urllib.error

from aiguillage import llm, regles, trier


def test_contrat_de_sortie(tmp_path, monkeypatch):
    monkeypatch.setattr("aiguillage.audit.CHEMIN", tmp_path / "audit.jsonl")
    r = trier("Le VPN ne se connecte plus pour plusieurs collègues", autoriser_llm=False)
    assert r["categorie"]["code"] == "INFRA"
    assert r["priorite"]["niveau"] in {"P1", "P2", "P3", "P4"}
    assert r["priorite"]["justification"]
    assert 1 <= len(r["fiches"]) <= 3
    assert r["validation_humaine_requise"] is True
    assert r["audit"]["version_regles"]


def test_indisponibilite_totale_est_p1():
    p = regles.prioriser("Le site de vente est indisponible pour tous les clients")
    assert p.niveau == "P1"


def test_demande_simple_est_p4():
    assert regles.prioriser("Besoin d'installer un logiciel, pas urgent").niveau == "P4"


def test_ticket_vide_a_qualifier(tmp_path, monkeypatch):
    monkeypatch.setattr("aiguillage.audit.CHEMIN", tmp_path / "audit.jsonl")
    r = trier("Bonjour, ça ne marche pas.", autoriser_llm=False)
    assert r["categorie"]["a_qualifier"]


def test_mode_degrade_si_fournisseur_en_panne(monkeypatch, tmp_path):
    monkeypatch.setattr("aiguillage.audit.CHEMIN", tmp_path / "audit.jsonl")
    monkeypatch.setenv("GROQ_API_KEY", "cle-de-test")

    def panne(*args, **kwargs):
        raise urllib.error.URLError("fournisseur indisponible")

    monkeypatch.setattr("urllib.request.urlopen", panne)
    r = trier("Mon imprimante est hors ligne")
    assert r["resume"]["source"] == "deterministe"
    assert r["resume"]["erreur"] == "URLError"
    assert r["priorite"]["niveau"]


def test_resume_llm_repasse_au_masquage(monkeypatch, tmp_path):
    monkeypatch.setattr("aiguillage.audit.CHEMIN", tmp_path / "audit.jsonl")
    monkeypatch.setattr(
        llm, "rediger_resume",
        lambda texte, autoriser_llm=True: llm.Redaction("Rappeler a.b@exemple.fr", "llm", "test", 10, 5, 0.0),
    )
    r = trier("Mon imprimante est hors ligne")
    assert "a.b@exemple.fr" not in r["resume"]["texte"]


def test_cout_estime():
    assert llm.cout(1_000_000, 0) == llm.PRIX_ENTREE
