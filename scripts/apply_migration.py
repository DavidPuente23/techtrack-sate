"""Aplica database/migrate_p0.sql a la base configurada en .env.

Solo agrega columnas e índices que falten. No borra datos.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from config import Config

sql = Path("database/migrate_p0.sql").read_text(encoding="utf-8")

conn = mysql.connector.connect(
    host=Config.DB_HOST, port=Config.DB_PORT,
    user=Config.DB_USER, password=Config.DB_PASSWORD,
    database=Config.DB_NAME,
)
cursor = conn.cursor()

cursor.execute("DROP PROCEDURE IF EXISTS sate_add_column")
procedimiento = re.search(r"CREATE PROCEDURE[\s\S]*?END\$\$", sql)
if not procedimiento:
    raise SystemExit("No se encontró el procedimiento en migrate_p0.sql")
cursor.execute(procedimiento.group(0).replace("$$", ""))

for tabla, columna, definicion in re.findall(
    r"CALL sate_add_column\('(\w+)', '(\w+)', '([^']+)'\)", sql
):
    cursor.execute("CALL sate_add_column(%s, %s, %s)", (tabla, columna, definicion))
    print(f"OK {tabla}.{columna}")

for tabla, columna in [("incidencias", "estado"), ("auditoria", "fecha")]:
    indice = f"idx_{tabla}_{columna}"
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND INDEX_NAME = %s
        """,
        (Config.DB_NAME, tabla, indice),
    )
    if cursor.fetchone()[0] == 0:
        cursor.execute(f"CREATE INDEX {indice} ON {tabla} ({columna})")
        print(f"OK índice {indice}")

cursor.execute("DROP PROCEDURE IF EXISTS sate_add_column")
conn.commit()
cursor.close()
conn.close()
print("Migración aplicada.")
