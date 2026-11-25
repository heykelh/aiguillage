"""CA3 : aucune donnée personnelle dans la sortie ni dans le journal."""

import json

import pytest

from aiguillage import pii, trier

CAS = [
    ("Contact : marie.curie@exemple.fr", "EMAIL", "marie.curie@exemple.fr"),
    ("Rappeler au 06 12 34 56 78", "TEL", "06 12 34 56 78"),
    ("Rappeler au +33 6 12 34 56 78", "TEL", "+33 6 12 34 56 78"),
    ("Poste 10.0.12.254 injoignable", "IP", "10.0.12.254"),
    ("IBAN FR76 3000 6000 0112 3456 7890 189", "IBAN", "FR76 3000 6000 0112 3456 7890 189"),
    ("Matricule 1234567A bloqué", "MATRICULE", "1234567A"),
    ("Carte 4970 1012 3456 7890 refusée", "CARTE", "4970 1012 3456 7890"),
    ("Demande de Mme Lefebvre", "NOM", "Lefebvre"),
]


@pytest.mark.parametrize("texte,type_attendu,valeur", CAS)
def test_masquage_par_type(texte, type_attendu, valeur):
    masque, compte = pii.masquer(texte)
    assert valeur not in masque
    assert compte.get(type_attendu, 0) >= 1


def test_zero_fuite_dans_sortie_et_audit(tmp_path, monkeypatch):
    monkeypatch.setattr("aiguillage.audit.CHEMIN", tmp_path / "audit.jsonl")
    texte = "Paiement refusé pour M. Garnier, jean.garnier@exemple.fr, 06 98 76 54 32"
    resultat = trier(texte, autoriser_llm=False)
    sortie = json.dumps(resultat, ensure_ascii=False)
    journal = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    for valeur in ["Garnier", "jean.garnier@exemple.fr", "06 98 76 54 32"]:
        assert valeur not in sortie
        assert valeur not in journal


def test_journal_ne_contient_pas_le_texte(tmp_path, monkeypatch):
    monkeypatch.setattr("aiguillage.audit.CHEMIN", tmp_path / "audit.jsonl")
    trier("Mon imprimante est hors ligne depuis ce matin", autoriser_llm=False)
    entree = json.loads((tmp_path / "audit.jsonl").read_text(encoding="utf-8"))
    assert "imprimante" not in json.dumps(entree)
    assert len(entree["empreinte_ticket"]) == 16
