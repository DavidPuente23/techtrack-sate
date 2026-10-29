"""Pruebas de humo de vistas de detalle/edición con IDs reales."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from config import Config
from app import app


def primer_id(tabla):
    conn = mysql.connector.connect(
        host=Config.DB_HOST, port=Config.DB_PORT, user=Config.DB_USER,
        password=Config.DB_PASSWORD, database=Config.DB_NAME,
    )
    cursor = conn.cursor()
    cursor.execute(f"SELECT MIN(id) FROM {tabla}")
    valor = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return valor


ids = {
    "activos": primer_id("activos"),
    "mantenimientos": primer_id("mantenimientos"),
    "incidencias": primer_id("incidencias"),
}

RUTAS = []
if ids["activos"]:
    RUTAS += [
        f"/app/activos/{ids['activos']}",
        f"/app/activos/{ids['activos']}/editar",
        f"/app/activos/{ids['activos']}/resguardo",
    ]
if ids["mantenimientos"]:
    RUTAS += [
        f"/app/mantenimientos/{ids['mantenimientos']}/editar",
        f"/app/mantenimientos/{ids['mantenimientos']}/orden",
    ]
if ids["incidencias"]:
    RUTAS.append(f"/app/incidencias/{ids['incidencias']}/editar")

fallos = []

with app.test_client() as cliente:
    with cliente.session_transaction() as sesion:
        sesion["usuario_id"] = 1
        sesion["nombre"] = "Administrador"
        sesion["rol"] = "Administrador General"
        sesion["tema"] = "blue"
        sesion["_csrf_token"] = "token-de-prueba"

    for ruta in RUTAS:
        respuesta = cliente.get(ruta)
        ok = respuesta.status_code in (200, 302)
        print(f"{'OK ' if ok else 'FALLO'} GET {ruta} -> {respuesta.status_code}")
        if not ok:
            fallos.append((ruta, respuesta.status_code))

print()
if fallos:
    print("FALLOS:", fallos)
    raise SystemExit(1)
print("DETALLES Y EDICIÓN OK")
