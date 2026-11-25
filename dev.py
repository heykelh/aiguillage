"""Serveur local : sert le site et les API comme Vercel. Plan B si le réseau lâche pendant une démo.

Usage : python dev.py   puis ouvrir http://localhost:8000
"""

import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE / "api"))

import retour  # noqa: E402
import triage  # noqa: E402

ROUTES = {"/api/triage": triage.handler, "/api/retour": retour.handler}


class Dev(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(RACINE), **kwargs)

    def _api(self, methode: str) -> bool:
        cible = ROUTES.get(self.path.split("?")[0])
        if not cible:
            return False
        getattr(cible, methode)(self)
        return True

    def do_POST(self):  # noqa: N802
        if not self._api("do_POST"):
            self.send_error(404)

    def do_GET(self):  # noqa: N802
        if not self._api("do_GET"):
            super().do_GET()

    def _repondre(self, statut, corps):
        triage.handler._repondre(self, statut, corps)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"AIGUILLAGE en local : http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Dev).serve_forever()
