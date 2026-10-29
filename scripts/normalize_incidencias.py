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
cursor.execute("UPDATE incidencias SET estado = 'Nueva' WHERE estado = 'Pendiente'")
print("Filas normalizadas:", cursor.rowcount)
cursor.execute("ALTER TABLE incidencias ALTER COLUMN estado SET DEFAULT 'Nueva'")
conn.commit()
cursor.close()
conn.close()
print("Estado por defecto de incidencias actualizado a 'Nueva'.")
