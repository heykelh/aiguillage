"""API HTTP (fonction serverless Vercel). Aucune logique métier ici : tout est dans core/aiguillage."""

import json
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))

from aiguillage import llm, trier  # noqa: E402

TAILLE_MAX = 5000


class handler(BaseHTTPRequestHandler):  # noqa: N801 (nom imposé par Vercel)
    def _repondre(self, statut: int, corps: dict) -> None:
        donnees = json.dumps(corps, ensure_ascii=False).encode("utf-8")
        self.send_response(statut)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(donnees)

    def do_POST(self) -> None:  # noqa: N802
        longueur = int(self.headers.get("Content-Length") or 0)
        if longueur <= 0 or longueur > TAILLE_MAX * 4:
            return self._repondre(400, {"erreur": "corps vide ou trop long"})
        try:
            texte = json.loads(self.rfile.read(longueur)).get("ticket", "")
        except (ValueError, AttributeError):
            return self._repondre(400, {"erreur": "JSON invalide, attendu {\"ticket\": \"...\"}"})
        if not isinstance(texte, str) or not texte.strip():
            return self._repondre(400, {"erreur": "le champ ticket est vide"})
        self._repondre(200, trier(texte[:TAILLE_MAX]))

    def do_GET(self) -> None:  # noqa: N802
        self._repondre(200, {"service": "aiguillage", "usage": "POST {\"ticket\": \"...\"}", "llm": llm.etat()})
