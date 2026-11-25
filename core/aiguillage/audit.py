"""Journal d'audit (skills ai-act et donnees-personnelles).

Une ligne JSON par décision. On stocke une empreinte du texte, jamais le texte brut.
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

CHEMIN = Path(os.environ.get("AUDIT_PATH", "/tmp/aiguillage_audit.jsonl"))
RETENTION_JOURS = int(os.environ.get("AUDIT_RETENTION_JOURS", "90"))


def empreinte(texte: str) -> str:
    return hashlib.sha256(texte.encode("utf-8")).hexdigest()[:16]


def journaliser(entree: dict) -> dict:
    """Ajoute l'horodatage et écrit l'entrée. Ne lève jamais d'exception (le tri ne doit pas échouer)."""
    entree = {"horodatage": datetime.now(timezone.utc).isoformat(timespec="seconds"), **entree}
    try:
        CHEMIN.parent.mkdir(parents=True, exist_ok=True)
        with CHEMIN.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entree, ensure_ascii=False) + "\n")
    except OSError:
        entree["journal"] = "indisponible"
    return entree
