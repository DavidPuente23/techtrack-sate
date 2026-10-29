import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from config import Config

conn = mysql.connector.connect(
    host=Config.DB_HOST, port=Config.DB_PORT, user=Config.DB_USER,
    password=Config.DB_PASSWORD, database=Config.DB_NAME,
)
cursor = conn.cursor()
for tabla, columna in [
    ("incidencias", "estado"),
    ("activos", "estado"),
    ("mantenimientos", "estado"),
    ("postulaciones", "estado"),
    ("cambios", "estado"),
    ("problemas", "estado"),
]:
    cursor.execute(f"SELECT {columna}, COUNT(*) FROM {tabla} GROUP BY {columna}")
    print(tabla, cursor.fetchall())
cursor.close()
conn.close()
