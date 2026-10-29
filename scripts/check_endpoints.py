"""Comprueba que todos los url_for() de las plantillas apunten a rutas reales."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app

PATRON = re.compile(r"""url_for\(\s*['"]([^'"]+)""")
endpoints = set(app.url_map._rules_by_endpoint)
usados = set()

for plantilla in Path("templates").rglob("*.html"):
    usados.update(PATRON.findall(plantilla.read_text(encoding="utf-8")))

faltantes = sorted(u for u in usados if u not in endpoints and u != "static")

print("Endpoints usados:", len(usados))
if faltantes:
    print("FALTANTES:", faltantes)
    raise SystemExit(1)
print("Todos los url_for() son válidos.")
