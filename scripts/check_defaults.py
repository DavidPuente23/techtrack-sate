import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from config import Config

conn = mysql.connector.connect(
    host=Config.DB_HOST, port=Config.DB_PORT, user=Config.DB_USER,
    password=Config.DB_PASSWORD, database=Config.DB_NAME,
)
cursor = conn.cursor(dictionary=True)
cursor.execute(
    """
    SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, COLUMN_DEFAULT
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = %s
      AND COLUMN_NAME IN ('estado', 'tema', 'activo', 'atendido')
    ORDER BY TABLE_NAME, COLUMN_NAME
    """,
    (Config.DB_NAME,),
)
for fila in cursor.fetchall():
    print(fila)
cursor.close()
conn.close()
