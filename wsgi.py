"""
Punto de entrada WSGI para hosting compartido (alwaysdata, PythonAnywhere, etc.).

Los servidores WSGI buscan un objeto llamado ``application``. Aquí solo se
expone la aplicación Flask que ya vive en ``app.py``.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import app as application  # noqa: E402


if __name__ == "__main__":
    application.run()
