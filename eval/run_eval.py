"""Évaluation de l'assistant de tri sur le jeu de référence (skill evaluation-llm).

Usage : python eval/run_eval.py
Produit eval/resultats.json et eval/RAPPORT.md. Code de sortie 1 si un seuil n'est pas atteint.
"""

import json
import sys
import time
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "core"))

from aiguillage import trier  # noqa: E402
from aiguillage.version import VERSION_REGLES  # noqa: E402

NIVEAUX = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}


def charger(nom: str = "tickets_reference.jsonl") -> list[dict]:
    chemin = RACINE / "data" / nom
    return [json.loads(l) for l in chemin.read_text(encoding="utf-8").splitlines() if l.strip()]


def f1_par_classe(attendus: list[str], predits: list[str]) -> dict[str, dict]:
    classes = sorted(set(attendus) | set(predits))
    res = {}
    for c in classes:
        vp = sum(1 for a, p in zip(attendus, predits) if a == c and p == c)
        fp = sum(1 for a, p in zip(attendus, predits) if a != c and p == c)
        fn = sum(1 for a, p in zip(attendus, predits) if a == c and p != c)
        precision = vp / (vp + fp) if vp + fp else 0.0
        rappel = vp / (vp + fn) if vp + fn else 0.0
        f1 = 2 * precision * rappel / (precision + rappel) if precision + rappel else 0.0
        res[c] = {"precision": round(precision, 3), "rappel": round(rappel, 3), "f1": round(f1, 3), "support": vp + fn}
    return res


def evaluer(nom: str = "tickets_reference.jsonl") -> dict:
    tickets = charger(nom)
    attendus_cat, predits_cat, erreurs, matrice_prio = [], [], [], Counter()
    prio_ok = sous_graves = hits = avec_fiche = 0
    inj_vp = inj_fn = inj_fp = fuites = 0
    debut = time.perf_counter()

    for t in tickets:
        r = trier(t["texte"], autoriser_llm=False, journaliser=False)
        cat, prio = r["categorie"]["code"], r["priorite"]["niveau"]
        attendus_cat.append(t["categorie"])
        predits_cat.append(cat)
        matrice_prio[(t["priorite"], prio)] += 1

        if prio == t["priorite"]:
            prio_ok += 1
        if NIVEAUX[prio] - NIVEAUX[t["priorite"]] >= 2:
            sous_graves += 1

        if t["fiche_attendue"]:
            avec_fiche += 1
            if t["fiche_attendue"] in [f["id"] for f in r["fiches"]]:
                hits += 1

        suspect = r["securite"]["suspect"]
        inj_vp += t["injection"] and suspect
        inj_fn += t["injection"] and not suspect
        inj_fp += (not t["injection"]) and suspect

        sortie = json.dumps({k: v for k, v in r.items()}, ensure_ascii=False)
        fuite = [v for v in t["pii_a_masquer"] if v in sortie]
        fuites += len(fuite)

        if cat != t["categorie"] or prio != t["priorite"] or fuite:
            erreurs.append({
                "id": t["id"], "texte": t["texte"][:90], "categorie": [t["categorie"], cat],
                "priorite": [t["priorite"], prio], "fuites": fuite,
            })

    duree_ms = (time.perf_counter() - debut) * 1000 / len(tickets)
    par_classe = f1_par_classe(attendus_cat, predits_cat)
    f1_macro = sum(v["f1"] for v in par_classe.values()) / len(par_classe)

    return {
        "version_regles": VERSION_REGLES,
        "nb_tickets": len(tickets),
        "metriques": {
            "f1_macro_categorie": round(f1_macro, 3),
            "exactitude_categorie": round(sum(a == p for a, p in zip(attendus_cat, predits_cat)) / len(tickets), 3),
            "exactitude_priorite": round(prio_ok / len(tickets), 3),
            "sous_priorisations_graves": sous_graves,
            "hit_at_3_fiches": round(hits / avec_fiche, 3),
            "rappel_injection": round(inj_vp / (inj_vp + inj_fn), 3) if inj_vp + inj_fn else 1.0,
            "faux_positifs_injection": inj_fp,
            "fuites_donnees_personnelles": fuites,
            "latence_moyenne_ms": round(duree_ms, 2),
        },
        "par_categorie": par_classe,
        "matrice_priorite": {f"{a}->{p}": n for (a, p), n in sorted(matrice_prio.items())},
        "erreurs": erreurs,
    }


def verifier_seuils(metriques: dict) -> list[str]:
    seuils = json.loads((RACINE / "eval" / "seuils.json").read_text(encoding="utf-8"))
    echecs = []
    for nom, regle in seuils.items():
        valeur = metriques[nom]
        if "min" in regle and valeur < regle["min"]:
            echecs.append(f"{nom} = {valeur} < {regle['min']}")
        if "max" in regle and valeur > regle["max"]:
            echecs.append(f"{nom} = {valeur} > {regle['max']}")
    return echecs


def rapport(res: dict, echecs: list[str]) -> str:
    m = res["metriques"]
    lignes = [
        "# Rapport d'évaluation",
        "",
        f"Version des règles : `{res['version_regles']}` ; {res['nb_tickets']} tickets fictifs annotés.",
        "",
        "| Métrique | Valeur |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in m.items()],
        "",
        "## Par catégorie",
        "",
        "| Catégorie | Précision | Rappel | F1 | Support |",
        "|---|---|---|---|---|",
        *[f"| {c} | {v['precision']} | {v['rappel']} | {v['f1']} | {v['support']} |" for c, v in res["par_categorie"].items()],
        "",
        "## Erreurs restantes (à analyser, pas à cacher)",
        "",
        *([f"- {e['id']} : catégorie {e['categorie'][0]} -> {e['categorie'][1]}, priorité {e['priorite'][0]} -> {e['priorite'][1]} : « {e['texte']} »" for e in res["erreurs"]] or ["Aucune."]),
        "",
        "## Jeu de validation (rédigé après le gel des règles, jamais utilisé pour les régler)",
        "",
        "| Métrique | Valeur |",
        "|---|---|",
        *[f"| {k} | {v} |" for k, v in res["validation"]["metriques"].items()],
        "",
        *[f"- {e['id']} : catégorie {e['categorie'][0]} -> {e['categorie'][1]}, priorité {e['priorite'][0]} -> {e['priorite'][1]} : « {e['texte']} »" for e in res["validation"]["erreurs"]],
        "",
        "## Seuils (appliqués au jeu de référence)",
        "",
        "Tous les seuils sont atteints." if not echecs else "\n".join(f"- ÉCHEC : {e}" for e in echecs),
        "",
    ]
    return "\n".join(lignes)


if __name__ == "__main__":
    resultats = evaluer()
    validation = evaluer("tickets_validation.jsonl")
    resultats["validation"] = {"nb_tickets": validation["nb_tickets"], "metriques": validation["metriques"], "erreurs": validation["erreurs"]}
    echecs = verifier_seuils(resultats["metriques"])
    resultats["seuils_atteints"] = not echecs
    (RACINE / "eval" / "resultats.json").write_text(json.dumps(resultats, ensure_ascii=False, indent=2), encoding="utf-8")
    (RACINE / "eval" / "RAPPORT.md").write_text(rapport(resultats, echecs), encoding="utf-8")
    for k, v in resultats["metriques"].items():
        print(f"{k:32} {v}")
    print("\nValidation (jeu tenu à l'écart) :")
    for k, v in validation["metriques"].items():
        print(f"  {k:30} {v}")
    if echecs:
        print("\nSEUILS NON ATTEINTS :\n- " + "\n- ".join(echecs))
        sys.exit(1)
    print("\nTous les seuils sont atteints.")
