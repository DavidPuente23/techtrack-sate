"""Aplica database/migrate_bloque6.sql a la base configurada en .env.

El script no borra datos. Puede ejecutarse varias veces.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from config import Config

sql = Path("database/migrate_bloque6.sql").read_text(encoding="utf-8")
lineas = [linea for linea in sql.splitlines() if not linea.strip().startswith("--")]
sentencias = [s.strip() for s in "\n".join(lineas).split(";") if s.strip()]

conn = mysql.connector.connect(
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME,
)
cursor = conn.cursor()

for sentencia in sentencias:
    cursor.execute(sentencia)

conn.commit()
cursor.close()
conn.close()
print(f"Migración Bloque 6 aplicada ({len(sentencias)} sentencias).")
