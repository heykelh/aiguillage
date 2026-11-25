"""Retour de l'agent sur une suggestion (accepter / corriger) : base de l'indicateur d'acceptation."""

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))

from aiguillage import audit  # noqa: E402

PRIORITES = {"P1", "P2", "P3", "P4"}


class handler(BaseHTTPRequestHandler):  # noqa: N801
    def _repondre(self, statut: int, corps: dict) -> None:
        donnees = json.dumps(corps, ensure_ascii=False).encode("utf-8")
        self.send_response(statut)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(donnees)

    def do_POST(self) -> None:  # noqa: N802
        try:
            corps = json.loads(self.rfile.read(min(int(self.headers.get("Content-Length") or 0), 2000)))
            empreinte = str(corps["empreinte_ticket"])[:16]
            accepte = bool(corps["accepte"])
            correction = corps.get("priorite_corrigee")
            if correction is not None and correction not in PRIORITES:
                raise ValueError
        except (ValueError, KeyError, TypeError):
            return self._repondre(400, {"erreur": "attendu {empreinte_ticket, accepte, priorite_corrigee?}"})
        entree = audit.journaliser({
            "type": "retour_agent", "empreinte_ticket": empreinte, "accepte": accepte, "priorite_corrigee": correction,
        })
        self._repondre(200, {"enregistre": True, "audit": entree})
