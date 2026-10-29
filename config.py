"""
Configuración central de TechTrack SATE.

Las variables se leen desde el archivo .env (si existe) y luego desde
el entorno del sistema. Las variables de entorno reales tienen prioridad.
"""

from datetime import timedelta
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent


def load_env(path: str | Path | None = None) -> None:
    """Carga un archivo .env sencillo sin dependencias externas."""
    env_path = Path(path) if path else BASE_DIR / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


load_env()


def _bool_env(name: str, default: bool = False) -> bool:
    return os.getenv(name, "1" if default else "0").strip().lower() in {
        "1", "true", "yes", "si", "sí", "on"
    }


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    DEBUG = _bool_env("FLASK_DEBUG", False)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _bool_env("SESSION_COOKIE_SECURE", False)
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.getenv("SESSION_LIFETIME_HOURS", "8"))
    )
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH_MB", "16")) * 1024 * 1024

    # Base de datos
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "techtrack_sate")
    DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

    # Aplicación
    APP_NAME = os.getenv("APP_NAME", "TechTrack Solutions")
    APP_DEBUG_SQL = _bool_env("APP_DEBUG_SQL", False)
