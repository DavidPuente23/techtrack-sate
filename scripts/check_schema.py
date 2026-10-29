"""Compara las columnas del schema.sql con la base de datos local."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from config import Config

sql = Path("database/schema.sql").read_text(encoding="utf-8")

tablas_schema = {}
for match in re.finditer(r"CREATE TABLE\s+(\w+)\s*\((.*?)\)\s*ENGINE", sql, re.S | re.I):
    tabla, cuerpo = match.group(1), match.group(2)
    columnas = []
    for linea in cuerpo.splitlines():
        linea = linea.strip().rstrip(",")
        if not linea:
            continue
        if re.match(r"(CONSTRAINT|PRIMARY|UNIQUE|INDEX|KEY|FOREIGN|CHECK|ON|NOT|DEFAULT)\b", linea, re.I):
            continue
        columnas.append(linea.split()[0].strip("`"))
    tablas_schema[tabla] = set(columnas)

conn = mysql.connector.connect(
    host=Config.DB_HOST, port=Config.DB_PORT, user=Config.DB_USER,
    password=Config.DB_PASSWORD, database=Config.DB_NAME,
)
cursor = conn.cursor()
problemas = []
for tabla, columnas in tablas_schema.items():
    cursor.execute(f"SHOW COLUMNS FROM {tabla}")
    reales = {fila[0] for fila in cursor.fetchall()}
    faltan_en_schema = reales - columnas
    faltan_en_bd = columnas - reales
    if faltan_en_schema or faltan_en_bd:
        problemas.append((tabla, sorted(faltan_en_schema), sorted(faltan_en_bd)))

cursor.close()
conn.close()

faltantes_bd = [(t, c) for t, _, c in problemas if c]
if problemas:
    for tabla, extra_bd, extra_schema in problemas:
        print(f"{tabla}:")
        if extra_bd:
            print("  en la BD pero no en schema.sql (legado, no bloquea):", extra_bd)
        if extra_schema:
            print("  en schema.sql pero no en la BD (ejecuta migrate_p0.sql):", extra_schema)

if faltantes_bd:
    raise SystemExit(1)

print(f"Schema y BD coinciden en {len(tablas_schema)} tablas.")
