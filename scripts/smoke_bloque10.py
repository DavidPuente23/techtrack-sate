"""Prueba de extremo a extremo del Bloque 10.

Cubre las alertas de mantenimientos próximos (7 días), el filtro de
vencimiento, el reporte de inventario en PDF con alcance por rol y la página
pública de cumplimiento del PIA.

Crea un activo y dos mantenimientos temporales y los elimina al final.
"""
import sys
import time
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector

from config import Config
from app import app

MARCA = str(int(time.time()))
IDENTIFICADOR = f"TST-B10-{MARCA[-7:]}"
NOMBRE_ACTIVO = f"Equipo Prueba Bloque 10 {MARCA}"
DESC_PROXIMO = f"Mantenimiento próximo Bloque 10 {MARCA}"
DESC_VENCIDO = f"Mantenimiento vencido Bloque 10 {MARCA}"

fallos = []
activo_id = None
mant_proximo_id = None
mant_vencido_id = None
base_activos = 0
base_dept3 = 0


def conectar():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        autocommit=False,
    )


def comprobar(condicion, mensaje):
    print(f"{'OK ' if condicion else 'FALLO'} {mensaje}")
    if not condicion:
        fallos.append(mensaje)


def ejecutar(sql, params=()):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()


def sesion(cliente, rol, usuario_id=1, nombre="Prueba Bloque 10", departamento_id=1):
    with cliente.session_transaction() as sesion_actual:
        sesion_actual.clear()
        sesion_actual["usuario_id"] = usuario_id
        sesion_actual["nombre"] = nombre
        sesion_actual["rol"] = rol
        sesion_actual["departamento_id"] = departamento_id
        sesion_actual["tema"] = "blue"
        sesion_actual["_csrf_token"] = "token-bloque10"


def limpiar():
    if mant_proximo_id is not None:
        ejecutar("DELETE FROM mantenimientos WHERE id = %s", (mant_proximo_id,))
    if mant_vencido_id is not None:
        ejecutar("DELETE FROM mantenimientos WHERE id = %s", (mant_vencido_id,))
    if activo_id is not None:
        ejecutar("DELETE FROM historial_activos WHERE activo_id = %s", (activo_id,))
        ejecutar("DELETE FROM auditoria WHERE entidad = 'Activo' AND entidad_id = %s", (activo_id,))
        ejecutar("DELETE FROM activos WHERE id = %s", (activo_id,))


try:
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS total FROM activos")
    base_activos = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM activos WHERE departamento_id = 3")
    base_dept3 = cursor.fetchone()["total"]

    cursor.execute(
        """
        INSERT INTO activos
            (identificador, nombre, tipo, marca, modelo, numero_serie,
             ubicacion, responsable, departamento_id, estado)
        VALUES (%s, %s, 'Laptop', 'MarcaB10', 'ModeloB10', %s,
                'Aula 10', 'Responsable B10', 3, 'Operativo')
        """,
        (IDENTIFICADOR, NOMBRE_ACTIVO, f"SERIE-B10-{MARCA}"),
    )
    activo_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO mantenimientos
            (activo_id, tipo, descripcion, fecha_programada, responsable, estado)
        VALUES (%s, 'Preventivo', %s, %s, 'Soporte B10', 'Pendiente')
        """,
        (activo_id, DESC_PROXIMO, date.today() + timedelta(days=3)),
    )
    mant_proximo_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO mantenimientos
            (activo_id, tipo, descripcion, fecha_programada, responsable, estado)
        VALUES (%s, 'Correctivo', %s, %s, 'Soporte B10', 'Pendiente')
        """,
        (activo_id, DESC_VENCIDO, date.today() - timedelta(days=2)),
    )
    mant_vencido_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()

    # ---------------------------------------------------------
    # 1. Panel: alerta de mantenimientos próximos
    # ---------------------------------------------------------
    with app.test_client() as admin:
        sesion(admin, "Administrador General")
        respuesta = admin.get("/app/dashboard")
        cuerpo = respuesta.get_data(as_text=True)

        comprobar(respuesta.status_code == 200, "el panel del administrador responde")
        comprobar(
            "por vencer en los próximos 7 días" in cuerpo,
            "el panel alerta de mantenimientos que vencen en 7 días",
        )
        comprobar(
            "vencimiento=7" in cuerpo,
            "la alerta enlaza al filtro de próximos 7 días",
        )
        comprobar(
            "vencimiento=vencidos" in cuerpo,
            "la alerta de vencidos enlaza a su filtro",
        )

        # -----------------------------------------------------
        # 2. Filtros de vencimiento en mantenimientos
        # -----------------------------------------------------
        respuesta = admin.get("/app/mantenimientos?vencimiento=7")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(respuesta.status_code == 200, "el filtro de próximos 7 días responde")
        comprobar(
            f"/app/mantenimientos/{mant_proximo_id}" in cuerpo,
            "el filtro de próximos 7 días incluye el mantenimiento temporal",
        )
        comprobar(
            f"/app/mantenimientos/{mant_vencido_id}" not in cuerpo,
            "el filtro de próximos 7 días excluye el mantenimiento vencido",
        )
        comprobar(
            "Próximos 7 días" in cuerpo,
            "la vista muestra el chip del filtro de vencimiento",
        )

        respuesta = admin.get("/app/mantenimientos?vencimiento=vencidos")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(respuesta.status_code == 200, "el filtro de vencidos responde")
        comprobar(
            f"/app/mantenimientos/{mant_vencido_id}" in cuerpo,
            "el filtro de vencidos incluye el mantenimiento temporal",
        )
        comprobar(
            f"/app/mantenimientos/{mant_proximo_id}" not in cuerpo,
            "el filtro de vencidos excluye el mantenimiento próximo",
        )

        # -----------------------------------------------------
        # 3. Reporte de inventario en PDF
        # -----------------------------------------------------
        respuesta = admin.get("/app/activos/reporte")
        comprobar(respuesta.status_code == 200, "el reporte de inventario responde")
        comprobar(
            respuesta.headers.get("Content-Type", "").startswith("application/pdf"),
            "el reporte se entrega como PDF",
        )
        comprobar(respuesta.data.startswith(b"%PDF"), "el archivo tiene cabecera PDF")
        comprobar(len(respuesta.data) > 1500, "el PDF tiene contenido")
        comprobar(
            respuesta.headers.get("X-Activos-Reporte") == str(base_activos + 1),
            "el reporte del administrador incluye todos los activos",
        )

        respuesta = admin.get("/app/activos/reporte?departamento_id=3")
        comprobar(
            respuesta.headers.get("X-Activos-Reporte") == str(base_dept3 + 1),
            "el reporte filtrado por departamento limita los activos",
        )

        respuesta = admin.get("/app/activos")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar("Reporte PDF" in cuerpo, "el inventario muestra el botón de reporte")
        comprobar(
            "/app/activos/reporte" in cuerpo,
            "el botón de reporte apunta a la ruta correcta",
        )

    # ---------------------------------------------------------
    # 4. Alcance del reporte para el Usuario Solicitante
    # ---------------------------------------------------------
    with app.test_client() as solicitante:
        sesion(
            solicitante,
            "Usuario Solicitante",
            usuario_id=1,
            nombre="Solicitante Bloque 10",
            departamento_id=3,
        )
        respuesta = solicitante.get("/app/activos/reporte")
        comprobar(respuesta.status_code == 200, "el solicitante puede generar su reporte")
        comprobar(
            respuesta.headers.get("X-Activos-Reporte") == str(base_dept3 + 1),
            "el reporte del solicitante solo incluye su departamento",
        )

    # ---------------------------------------------------------
    # 5. Dirección General: consulta sin altas
    # ---------------------------------------------------------
    with app.test_client() as direccion:
        sesion(direccion, "Dirección General")
        respuesta = direccion.get("/app/activos/reporte")
        comprobar(respuesta.status_code == 200, "Dirección General puede generar el reporte")

    # ---------------------------------------------------------
    # 6. Página pública de cumplimiento del PIA
    # ---------------------------------------------------------
    with app.test_client() as publico:
        respuesta = publico.get("/cumplimiento-pia")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(respuesta.status_code == 200, "la página de cumplimiento responde")
        for texto in (
            "Cumplimiento del PIA",
            "Matriz de evidencia",
            "Organigrama",
            "Políticas generales",
            "Reporte de inventario en PDF",
            "próximos 7 días",
            "Implementado",
            "Publicado",
        ):
            comprobar(texto in cuerpo, f"la página de cumplimiento incluye {texto!r}")

    # ---------------------------------------------------------
    # 7. Una sesión de una cuenta eliminada no bloquea el sitio público
    # ---------------------------------------------------------
    with app.test_client() as fantasma:
        with fantasma.session_transaction() as sesion_actual:
            sesion_actual["usuario_id"] = 999999
            sesion_actual["nombre"] = "Cuenta eliminada"
            sesion_actual["rol"] = "Administrador General"
            sesion_actual["_csrf_token"] = "token-bloque10"
        respuesta = fantasma.get("/")
        comprobar(respuesta.status_code == 200, "el sitio público sigue visible sin cuenta válida")
        comprobar(
            "TechTrack Solutions" in respuesta.get_data(as_text=True),
            "el inicio público se renderiza aunque la sesión sea inválida",
        )
        respuesta = fantasma.get("/app/dashboard")
        comprobar(respuesta.status_code == 302, "una ruta privada redirige al login")
        comprobar(
            "/login" in respuesta.headers.get("Location", ""),
            "la redirección privada apunta al login",
        )

    print()
    if fallos:
        print(f"FALLOS: {len(fallos)}")
        raise SystemExit(1)
    print("BLOQUE 10 OK")
finally:
    limpiar()
