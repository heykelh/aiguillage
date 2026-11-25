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


def test_raison_explicite_sans_cle(monkeypatch, tmp_path):
    monkeypatch.setattr("aiguillage.audit.CHEMIN", tmp_path / "audit.jsonl")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    r = trier("Mon imprimante est hors ligne")
    assert r["resume"]["erreur"] == "cle_absente"
    assert llm.etat()["cle_configuree"] is False


def test_erreur_http_detaillee_et_identifiant_envoye(monkeypatch, tmp_path):
    import io

    monkeypatch.setattr("aiguillage.audit.CHEMIN", tmp_path / "audit.jsonl")
    monkeypatch.setenv("GROQ_API_KEY", "cle-de-test")
    vus = {}

    def refus(requete, timeout=None):
        vus["ua"] = requete.get_header("User-agent")
        raise urllib.error.HTTPError(requete.full_url, 403, "Forbidden", {}, io.BytesIO(b"error code: 1010"))

    monkeypatch.setattr("urllib.request.urlopen", refus)
    r = trier("Mon imprimante est hors ligne")
    assert r["resume"]["source"] == "deterministe"
    assert r["resume"]["erreur"] == "HTTP 403 : error code: 1010"
    assert vus["ua"].startswith("aiguillage/")


def test_bascule_sur_le_modele_de_secours(monkeypatch, tmp_path):
    import io
    import json as _json

    monkeypatch.setattr("aiguillage.audit.CHEMIN", tmp_path / "audit.jsonl")
    monkeypatch.setenv("GROQ_API_KEY", "cle-de-test")
    appels = []

    class Reponse(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def fournisseur(requete, timeout=None):
        modele = _json.loads(requete.data)["model"]
        appels.append(modele)
        if modele == llm.MODELE:
            corps = b'{"error":{"message":"The model does not exist","code":"model_not_found"}}'
            raise urllib.error.HTTPError(requete.full_url, 404, "Not Found", {}, io.BytesIO(corps))
        contenu = {"choices": [{"message": {"content": "Imprimante hors ligne."}}], "usage": {"prompt_tokens": 50, "completion_tokens": 5}}
        return Reponse(_json.dumps(contenu).encode())

    monkeypatch.setattr("urllib.request.urlopen", fournisseur)
    r = trier("Mon imprimante est hors ligne")
    assert appels == [llm.MODELE, llm.SECOURS[0]]
    assert r["resume"]["source"] == "llm"
    assert r["versions"]["modele"] == llm.SECOURS[0]
