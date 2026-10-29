"""Comprueba que todas las plantillas Jinja se puedan compilar."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app

errores = []
for ruta in sorted(Path("templates").rglob("*.html")):
    nombre = ruta.relative_to("templates").as_posix()
    try:
        app.jinja_env.get_template(nombre)
    except Exception as exc:  # noqa: BLE001
        errores.append((nombre, str(exc)))

if errores:
    for nombre, error in errores:
        print(f"FALLO {nombre}: {error}")
    raise SystemExit(1)
print("Todas las plantillas Jinja compilan correctamente.")
