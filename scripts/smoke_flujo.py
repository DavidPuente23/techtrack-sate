"""Flujo completo de activo -> mantenimiento -> incidencia -> cierre.

Crea un activo temporal y lo elimina al final.
"""
import sys
import time
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from config import Config
from app import app

marca = f"TST-{int(time.time())}"
fallos = []


def conectar():
    return mysql.connector.connect(
        host=Config.DB_HOST, port=Config.DB_PORT, user=Config.DB_USER,
        password=Config.DB_PASSWORD, database=Config.DB_NAME,
    )


conn = conectar()
cursor = conn.cursor()
cursor.execute("SELECT id FROM departamentos ORDER BY id LIMIT 1")
departamento_id = cursor.fetchone()[0]
cursor.execute(
    """
    INSERT INTO activos
        (identificador, nombre, tipo, marca, modelo, numero_serie,
         ubicacion, responsable, departamento_id, estado)
    VALUES (%s, %s, 'Laptop', 'QA', 'Smoke', %s, 'QA', 'Prueba', %s, 'Operativo')
    """,
    (marca, "Activo de prueba", marca, departamento_id),
)
activo_id = cursor.lastrowid
conn.commit()
cursor.close()
conn.close()
print(f"Activo temporal id={activo_id} ({marca})")


def token_de(cliente, ruta):
    cliente.get(ruta)
    with cliente.session_transaction() as sesion:
        return sesion.get("_csrf_token")


with app.test_client() as cliente:
    with cliente.session_transaction() as sesion:
        sesion["usuario_id"] = 1
        sesion["nombre"] = "Administrador"
        sesion["rol"] = "Administrador General"
        sesion["tema"] = "blue"
        sesion["_csrf_token"] = "token-flujo"

    # Crear mantenimiento
    respuesta = cliente.post(
        "/app/mantenimientos/nuevo",
        data={
            "_csrf_token": "token-flujo",
            "activo_id": str(activo_id),
            "tipo": "Preventivo",
            "descripcion": "Mantenimiento de prueba",
            "fecha_programada": date.today().isoformat(),
            "responsable": "Soporte QA",
        },
    )
    ok = respuesta.status_code == 302
    print(f"{'OK ' if ok else 'FALLO'} POST mantenimiento -> {respuesta.status_code}")
    if not ok:
        fallos.append("mantenimiento")

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, estado FROM mantenimientos WHERE activo_id = %s", (activo_id,))
    mantenimiento = cursor.fetchone()
    cursor.execute("SELECT estado FROM activos WHERE id = %s", (activo_id,))
    estado_activo = cursor.fetchone()["estado"]
    cursor.close()
    conn.close()
    ok = mantenimiento is not None and estado_activo == "En Mantenimiento"
    print(f"{'OK ' if ok else 'FALLO'} activo en mantenimiento (estado={estado_activo})")
    if not ok:
        fallos.append("estado_mantenimiento")

    # Crear incidencia
    respuesta = cliente.post(
        "/app/incidencias/nueva",
        data={
            "_csrf_token": "token-flujo",
            "activo_id": str(activo_id),
            "descripcion": "Falla de prueba",
            "prioridad": "Alta",
            "responsable": "Soporte QA",
        },
    )
    ok = respuesta.status_code == 302
    print(f"{'OK ' if ok else 'FALLO'} POST incidencia -> {respuesta.status_code}")
    if not ok:
        fallos.append("incidencia")

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, estado FROM incidencias WHERE activo_id = %s", (activo_id,))
    incidencia = cursor.fetchone()
    cursor.close()
    conn.close()
    ok = incidencia is not None and incidencia["estado"] == "Nueva"
    print(f"{'OK ' if ok else 'FALLO'} incidencia creada (estado={incidencia and incidencia['estado']})")
    if not ok:
        fallos.append("incidencia_bd")

    # Resolver incidencia
    respuesta = cliente.post(
        f"/app/incidencias/{incidencia['id']}/editar",
        data={
            "_csrf_token": "token-flujo",
            "estado": "Resuelta",
            "diagnostico": "Falla reproducida y confirmada en prueba automatizada.",
            "resolucion": "Resuelta en prueba automatizada.",
        },
    )
    ok = respuesta.status_code == 302
    print(f"{'OK ' if ok else 'FALLO'} POST resolver incidencia -> {respuesta.status_code}")
    if not ok:
        fallos.append("resolver_incidencia")

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT estado, fecha_cierre, diagnostico FROM incidencias WHERE id = %s", (incidencia["id"],))
    fila = cursor.fetchone()
    cursor.close()
    conn.close()
    ok = fila["estado"] == "Resuelta" and fila["fecha_cierre"] is not None
    print(f"{'OK ' if ok else 'FALLO'} incidencia resuelta con fecha_cierre")
    if not ok:
        fallos.append("fecha_cierre")

    ok = "prueba automatizada" in (fila["diagnostico"] or "")
    print(f"{'OK ' if ok else 'FALLO'} diagnóstico técnico guardado")
    if not ok:
        fallos.append("diagnostico_incidencia")

    # Finalizar mantenimiento
    respuesta = cliente.post(
        f"/app/mantenimientos/{mantenimiento['id']}/editar",
        data={
            "_csrf_token": "token-flujo",
            "estado": "Finalizado",
            "observaciones": "Finalizado en prueba automatizada.",
        },
    )
    ok = respuesta.status_code == 302
    print(f"{'OK ' if ok else 'FALLO'} POST finalizar mantenimiento -> {respuesta.status_code}")
    if not ok:
        fallos.append("finalizar_mantenimiento")

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT estado, fecha_finalizacion FROM mantenimientos WHERE id = %s",
        (mantenimiento["id"],),
    )
    fila = cursor.fetchone()
    cursor.execute("SELECT estado FROM activos WHERE id = %s", (activo_id,))
    estado_final = cursor.fetchone()["estado"]
    cursor.close()
    conn.close()
    ok = fila["estado"] == "Finalizado" and fila["fecha_finalizacion"] is not None
    print(f"{'OK ' if ok else 'FALLO'} mantenimiento finalizado con fecha_finalizacion")
    if not ok:
        fallos.append("fecha_finalizacion")
    ok = estado_final == "Operativo"
    print(f"{'OK ' if ok else 'FALLO'} activo vuelve a Operativo (estado={estado_final})")
    if not ok:
        fallos.append("estado_final")

# Limpieza
conn = conectar()
cursor = conn.cursor()
cursor.execute("DELETE FROM incidencias WHERE activo_id = %s", (activo_id,))
cursor.execute("DELETE FROM mantenimientos WHERE activo_id = %s", (activo_id,))
cursor.execute("DELETE FROM historial_activos WHERE activo_id = %s", (activo_id,))
cursor.execute(
    "DELETE FROM auditoria WHERE (entidad = 'Activo' AND entidad_id = %s)"
    " OR (entidad = 'Incidencia' AND entidad_id = %s)"
    " OR (entidad = 'Mantenimiento' AND entidad_id = %s)",
    (activo_id, incidencia["id"] if incidencia else 0, mantenimiento["id"] if mantenimiento else 0),
)
cursor.execute("DELETE FROM activos WHERE id = %s", (activo_id,))
conn.commit()
cursor.close()
conn.close()
print("Datos de prueba eliminados.")

print()
if fallos:
    print("FALLOS:", fallos)
    raise SystemExit(1)
print("FLUJO DE MANTENIMIENTO E INCIDENCIAS OK")
