"""Contrôles de conformité du harnais, exécutés en CI et par les agents de code.

Usage :
    python harness/checks/conformite.py            # contrôle le dépôt
    python harness/checks/conformite.py <dossier>  # contrôle un autre projet (ex. la démo sans harnais)

Chaque règle renvoie au skill qui l'explique. Code de sortie 1 si une règle échoue.
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

RACINE_DEPOT = Path(__file__).resolve().parents[2]
EXCLUS = {"harness/demo", "tests", ".git", "node_modules", "__pycache__", ".venv"}

MOTIFS_SECRETS = [
    re.compile(r"\b(?:gsk|sk|pk|rk)_[A-Za-z0-9]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
    re.compile(r"""(?i)\b\w*(?:api_?key|secret|token|password|mot_de_passe)\w*\s*=\s*["'][^"'\s]{8,}["']"""),
]
APPELS_LLM = re.compile(r"api\.groq\.com|api\.openai\.com|api\.anthropic\.com|chat/completions|from openai import|import anthropic")
SECTIONS_SPEC = ["## Problème", "## Réutilisation", "## Critères d'acceptation", "## Données manipulées", "## Classification AI Act", "## Critères d'arrêt"]
SECTIONS_AI_ACT = ["## Finalité", "## Niveau de risque", "## Supervision humaine", "## Journalisation", "## Limites connues"]
DOCS_RUN = ["docs/RUNBOOK.md", "docs/PASSATION.md", "docs/PLAN_DE_MESURE.md", "docs/RGPD_REGISTRE.md"]


@dataclass
class Resultat:
    regle: str
    skill: str
    ok: bool
    details: list[str] = field(default_factory=list)


def _fichiers(racine: Path, suffixes: tuple[str, ...]) -> list[Path]:
    fichiers = []
    for p in racine.rglob("*"):
        rel = p.relative_to(racine).as_posix()
        if p.is_file() and p.suffix in suffixes and not any(rel == e or rel.startswith(e + "/") or f"/{e}/" in f"/{rel}" for e in EXCLUS):
            fichiers.append(p)
    return fichiers


def controler(racine: Path) -> list[Resultat]:
    code = _fichiers(racine, (".py", ".ts", ".js"))
    tout = _fichiers(racine, (".py", ".ts", ".js", ".json", ".md", ".yml", ".yaml", ".env", ".toml"))
    rel = lambda p: p.relative_to(racine).as_posix()  # noqa: E731
    resultats: list[Resultat] = []

    # 1. Secrets
    fuites = [f"{rel(p)}:{n}" for p in tout for n, l in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1)
              if any(m.search(l) for m in MOTIFS_SECRETS)]
    resultats.append(Resultat("Aucun secret dans le code", "securite-ia", not fuites, fuites))

    # 2. Point d'entrée LLM unique
    appels = [rel(p) for p in code if APPELS_LLM.search(p.read_text(encoding="utf-8", errors="ignore"))]
    autorises = {"core/aiguillage/llm.py", "harness/checks/conformite.py"}  # le contrôleur contient les motifs
    hors_passerelle = [a for a in appels if a not in autorises]
    resultats.append(Resultat("Appels LLM uniquement via core/aiguillage/llm.py", "securite-ia", not hors_passerelle, hors_passerelle))

    # 3. Masquage des données personnelles avant le LLM
    utilisateurs_llm = [p for p in code if "rediger_resume(" in p.read_text(encoding="utf-8") and not p.name == "llm.py"] or \
                       [p for p in code if APPELS_LLM.search(p.read_text(encoding="utf-8", errors="ignore"))]
    sans_masquage = [rel(p) for p in utilisateurs_llm if "masquer(" not in p.read_text(encoding="utf-8") and p.name != "llm.py"]
    if not utilisateurs_llm:
        sans_masquage = []
    if any(rel(p) == "core/aiguillage/llm.py" for p in utilisateurs_llm) and not (racine / "core/aiguillage/triage.py").exists():
        sans_masquage.append("aucun orchestrateur ne masque les données avant le LLM")
    resultats.append(Resultat("Données personnelles masquées avant tout appel LLM", "donnees-personnelles", not sans_masquage, sans_masquage))

    # 4. Journal d'audit
    sans_audit = [rel(p) for p in utilisateurs_llm if p.name != "llm.py" and "journaliser" not in p.read_text(encoding="utf-8")]
    resultats.append(Resultat("Chaque décision est journalisée", "ai-act", not sans_audit, sans_audit))

    # 5. Le LLM ne décide pas
    decide = [rel(p) for p in code if re.search(r"(priorit\w*|categor\w*)\s*=\s*\w*(reponse|response|completion|choices)", p.read_text(encoding="utf-8", errors="ignore"), re.I)]
    resultats.append(Resultat("Le LLM ne fixe ni catégorie ni priorité", "securite-ia", not decide, decide))

    # 6. Spec avant code
    specs = sorted((racine / "specs").glob("[0-9][0-9][0-9]-*/spec.md")) if (racine / "specs").exists() else []
    manquantes = [f"{rel(s)} : {sec}" for s in specs for sec in SECTIONS_SPEC if sec not in s.read_text(encoding="utf-8")]
    if not specs:
        manquantes = ["aucune spec dans specs/NNN-*/spec.md"]
    resultats.append(Resultat("Une spec complète par fonctionnalité", "spec-first", not manquantes, manquantes))

    # 7. Fiche AI Act
    fiche = racine / "docs" / "AI_ACT.md"
    absents = ["docs/AI_ACT.md absent"] if not fiche.exists() else [s for s in SECTIONS_AI_ACT if s not in fiche.read_text(encoding="utf-8")]
    resultats.append(Resultat("Fiche AI Act complète", "ai-act", not absents, absents))

    # 8. Prêt pour le run
    docs_absents = [d for d in DOCS_RUN if not (racine / d).exists()]
    resultats.append(Resultat("Runbook, passation, plan de mesure, registre RGPD", "passage-au-run", not docs_absents, docs_absents))

    # 9. Tests et évaluation
    seuils = racine / "eval" / "seuils.json"
    tests = list((racine / "tests").glob("test_*.py")) if (racine / "tests").exists() else []
    probs = ([] if tests else ["aucun test"]) + ([] if seuils.exists() else ["aucun seuil d'évaluation"])
    resultats.append(Resultat("Tests et seuils d'évaluation présents", "evaluation-llm", not probs, probs))

    return resultats


def afficher(resultats: list[Resultat], cible: str) -> None:
    vert, rouge, gris, fin = "\033[32m", "\033[31m", "\033[90m", "\033[0m"
    print(f"\nContrôles du harnais AIGUILLAGE sur : {cible}\n")
    for r in resultats:
        marque = f"{vert}✔{fin}" if r.ok else f"{rouge}✘{fin}"
        print(f"  {marque} {r.regle} {gris}(skill {r.skill}){fin}")
        for d in r.details[:5]:
            print(f"      {gris}- {d}{fin}")
    n_ok = sum(r.ok for r in resultats)
    couleur = vert if n_ok == len(resultats) else rouge
    print(f"\n  {couleur}{n_ok}/{len(resultats)} règles respectées{fin}\n")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # ✔ et ✘ lisibles aussi sous Windows
    cible = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else RACINE_DEPOT
    if cible != RACINE_DEPOT:
        EXCLUS.discard("harness/demo")
    resultats = controler(cible)
    afficher(resultats, cible.relative_to(RACINE_DEPOT).as_posix() if cible != RACINE_DEPOT and RACINE_DEPOT in cible.parents else str(cible.name))
    sortie = RACINE_DEPOT / "eval" / ("conformite.json" if cible == RACINE_DEPOT else "conformite_demo.json")
    sortie.write_text(json.dumps([r.__dict__ for r in resultats], ensure_ascii=False, indent=2), encoding="utf-8")
    sys.exit(0 if all(r.ok for r in resultats) else 1)
