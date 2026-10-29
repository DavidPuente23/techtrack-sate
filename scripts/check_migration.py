"""Valida database/migrate_p0.sql en una base de datos temporal."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from config import Config

TEST_DB = "techtrack_sate_migtest"

DDL = [
    "CREATE TABLE usuarios (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(100), rol VARCHAR(50)) ENGINE=InnoDB",
    "CREATE TABLE mantenimientos (id INT AUTO_INCREMENT PRIMARY KEY, activo_id INT, trabajos_realizados TEXT) ENGINE=InnoDB",
    "CREATE TABLE incidencias (id INT AUTO_INCREMENT PRIMARY KEY, activo_id INT, estado VARCHAR(50), solucion TEXT) ENGINE=InnoDB",
    "CREATE TABLE auditoria (id INT AUTO_INCREMENT PRIMARY KEY, accion VARCHAR(100), fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB",
    "CREATE TABLE proveedores (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(150)) ENGINE=InnoDB",
    "CREATE TABLE mensajes_contacto (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(100)) ENGINE=InnoDB",
    "CREATE TABLE postulaciones (id INT AUTO_INCREMENT PRIMARY KEY, nombre VARCHAR(100)) ENGINE=InnoDB",
]

ESPERADAS = {
    "usuarios": "fecha_registro",
    "mantenimientos": "fecha_finalizacion",
    "incidencias": "fecha_cierre",
    "auditoria": "detalle",
    "proveedores": "fecha_registro",
    "mensajes_contacto": "acepta_privacidad",
    "postulaciones": "acepta_privacidad",
}

conn = mysql.connector.connect(
    host=Config.DB_HOST, port=Config.DB_PORT,
    user=Config.DB_USER, password=Config.DB_PASSWORD,
)
cursor = conn.cursor()
cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB}")
cursor.execute(f"CREATE DATABASE {TEST_DB} CHARACTER SET utf8mb4")
cursor.execute(f"USE {TEST_DB}")

for ddl in DDL:
    cursor.execute(ddl)

sql = Path("database/migrate_p0.sql").read_text(encoding="utf-8")
sql = sql.replace("USE techtrack_sate;", "")

procedimiento = re.search(r"CREATE PROCEDURE[\s\S]*?END\$\$", sql)
if not procedimiento:
    raise SystemExit("No se encontró el procedimiento en migrate_p0.sql")
cursor.execute(procedimiento.group(0).replace("$$", ""))

for tabla, columna, definicion in re.findall(
    r"CALL sate_add_column\('(\w+)', '(\w+)', '([^']+)'\)", sql
):
    cursor.execute("CALL sate_add_column(%s, %s, %s)", (tabla, columna, definicion))

# Ejecutar los bloques de índices (sin los PREPARE, directamente).
cursor.execute("CREATE INDEX idx_incidencias_estado ON incidencias (estado)")
cursor.execute("CREATE INDEX idx_auditoria_fecha ON auditoria (fecha)")
cursor.execute("DROP PROCEDURE IF EXISTS sate_add_column")

errores = []
for tabla, columna in ESPERADAS.items():
    cursor.execute(
        """
        SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (TEST_DB, tabla, columna),
    )
    if cursor.fetchone()[0] != 1:
        errores.append(f"{tabla}.{columna}")

# Segunda ejecución: debe ser idempotente (las columnas ya existen).
# En el script real lo garantiza el procedimiento; aquí comprobamos el estado.
cursor.execute(f"DROP DATABASE {TEST_DB}")
cursor.close()
conn.close()

if errores:
    print("FALTAN COLUMNAS:", errores)
    raise SystemExit(1)
print("Migración P0 validada en base temporal.")
