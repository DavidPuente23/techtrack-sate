"""Prueba de extremo a extremo del Bloque 8.

Cubre los filtros y las fichas de detalle de mantenimientos e incidencias,
incluido el alcance del rol Usuario Solicitante sobre sus propias incidencias.

Crea un activo, un usuario, un mantenimiento y una incidencia temporales y los
elimina al final.
"""
import sys
import time
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from werkzeug.security import generate_password_hash

from config import Config
from app import app

MARCA = str(int(time.time()))
IDENTIFICADOR = f"TST-B8-{MARCA[-8:]}"
NOMBRE_ACTIVO = f"Equipo Prueba Bloque 8 {MARCA}"
EMAIL = f"prueba.bloque8.{MARCA}@techtrack.com"
DESCRIPCION_MANT = f"Limpieza preventiva de prueba {MARCA}"
DESCRIPCION_INC = f"Falla de prueba de incidencias {MARCA}"
DIAGNOSTICO = f"Diagnóstico de prueba {MARCA}"
RESOLUCION = f"Resolución de prueba {MARCA}"

fallos = []
activo_id = None
usuario_id = None
mantenimiento_id = None
incidencia_id = None


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


def consultar(sql, params=()):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params)
    filas = cursor.fetchall()
    cursor.close()
    conn.close()
    return filas


def ejecutar(sql, params=()):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()
    conn.close()


def sesion_admin(cliente):
    with cliente.session_transaction() as sesion:
        sesion.clear()
        sesion["usuario_id"] = 1
        sesion["nombre"] = "Administrador"
        sesion["rol"] = "Administrador General"
        sesion["departamento_id"] = 1
        sesion["tema"] = "blue"
        sesion["_csrf_token"] = "token-admin"


def sesion_solicitante(cliente):
    with cliente.session_transaction() as sesion:
        sesion.clear()
        sesion["usuario_id"] = usuario_id
        sesion["nombre"] = "Solicitante Bloque 8"
        sesion["rol"] = "Usuario Solicitante"
        sesion["departamento_id"] = 3
        sesion["tema"] = "blue"
        sesion["_csrf_token"] = "token-solicitante"


def limpiar():
    if incidencia_id is not None:
        ejecutar("DELETE FROM incidencias WHERE id = %s", (incidencia_id,))
        ejecutar(
            "DELETE FROM auditoria WHERE entidad = 'Incidencia' AND entidad_id = %s",
            (incidencia_id,),
        )
    if mantenimiento_id is not None:
        ejecutar("DELETE FROM mantenimientos WHERE id = %s", (mantenimiento_id,))
    if activo_id is not None:
        ejecutar("DELETE FROM auditoria WHERE entidad = 'Activo' AND entidad_id = %s", (activo_id,))
        ejecutar("DELETE FROM activos WHERE id = %s", (activo_id,))
    if usuario_id is not None:
        ejecutar("DELETE FROM auditoria WHERE entidad = 'Usuario' AND entidad_id = %s", (usuario_id,))
        ejecutar("DELETE FROM usuarios WHERE id = %s", (usuario_id,))


try:
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO activos
            (identificador, nombre, tipo, marca, modelo, numero_serie,
             ubicacion, responsable, departamento_id, estado)
        VALUES (%s, %s, 'Laptop', 'MarcaB8', 'ModeloB8', %s,
                'Aula 8', 'Responsable B8', 3, 'Operativo')
        """,
        (IDENTIFICADOR, NOMBRE_ACTIVO, f"SERIE-{MARCA}"),
    )
    activo_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO usuarios
            (nombre, email, password, departamento_id, rol_id, activo, debe_cambiar_password)
        VALUES (%s, %s, %s, 3, 4, TRUE, FALSE)
        """,
        ("Solicitante Bloque 8", EMAIL, generate_password_hash("Temporal123!")),
    )
    usuario_id = cursor.lastrowid

    fecha_futura = date.today() + timedelta(days=5)
    cursor.execute(
        """
        INSERT INTO mantenimientos
            (activo_id, tipo, descripcion, fecha_programada, responsable, estado)
        VALUES (%s, 'Preventivo', %s, %s, 'Técnico B8', 'Pendiente')
        """,
        (activo_id, DESCRIPCION_MANT, fecha_futura),
    )
    mantenimiento_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO incidencias
            (activo_id, descripcion, prioridad, responsable, estado,
             diagnostico, resolucion, solicitante_id)
        VALUES (%s, %s, 'Alta', 'Soporte B8', 'Resuelta', %s, %s, %s)
        """,
        (activo_id, DESCRIPCION_INC, DIAGNOSTICO, RESOLUCION, usuario_id),
    )
    incidencia_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()

    # ---------------------------------------------------------
    # 1. Mantenimientos: filtros y ficha
    # ---------------------------------------------------------
    with app.test_client() as admin:
        sesion_admin(admin)

        respuesta = admin.get(f"/app/mantenimientos?q={MARCA}")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(respuesta.status_code == 200, "el listado de mantenimientos responde")
        comprobar(NOMBRE_ACTIVO in cuerpo, "la búsqueda encuentra el mantenimiento por equipo")
        comprobar(f"#{mantenimiento_id}" in cuerpo, "el mantenimiento temporal aparece en la tabla")

        respuesta = admin.get("/app/mantenimientos?estado=Pendiente")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(f"#{mantenimiento_id}" in cuerpo, "el filtro por estado encuentra el pendiente")
        comprobar(
            'value="Pendiente" selected' in cuerpo,
            "el formulario conserva el estado de mantenimiento",
        )

        respuesta = admin.get("/app/mantenimientos?tipo=Correctivo")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(
            DESCRIPCION_MANT not in cuerpo,
            "el filtro por tipo descarta los preventivos",
        )

        respuesta = admin.get(f"/app/mantenimientos?q={MARCA}&estado=Pendiente&tipo=Preventivo")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(f"#{mantenimiento_id}" in cuerpo, "los filtros combinados devuelven el mantenimiento")

        respuesta = admin.get(f"/app/mantenimientos/{mantenimiento_id}")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(respuesta.status_code == 200, "la ficha del mantenimiento responde")
        comprobar(DESCRIPCION_MANT in cuerpo, "la ficha muestra la descripción")
        comprobar("Técnico B8" in cuerpo, "la ficha muestra el responsable")
        comprobar(NOMBRE_ACTIVO in cuerpo, "la ficha muestra el equipo intervenido")

        respuesta = admin.get("/app/mantenimientos/999999")
        comprobar(respuesta.status_code == 404, "un mantenimiento inexistente devuelve 404")

        # -----------------------------------------------------
        # 2. Incidencias: filtros y ficha
        # -----------------------------------------------------
        respuesta = admin.get(f"/app/incidencias?q={MARCA}")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(respuesta.status_code == 200, "el listado de incidencias responde")
        comprobar(DESCRIPCION_INC in cuerpo, "la búsqueda encuentra la incidencia")

        respuesta = admin.get("/app/incidencias?prioridad=Alta")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(DESCRIPCION_INC in cuerpo, "el filtro por prioridad encuentra la incidencia")
        comprobar(
            'value="Alta" selected' in cuerpo,
            "el formulario conserva la prioridad seleccionada",
        )

        respuesta = admin.get("/app/incidencias?estado=Nueva")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(
            DESCRIPCION_INC not in cuerpo,
            "el filtro por estado descarta las incidencias resueltas",
        )

        respuesta = admin.get(f"/app/incidencias/{incidencia_id}")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(respuesta.status_code == 200, "la ficha de la incidencia responde")
        comprobar(DESCRIPCION_INC in cuerpo, "la ficha muestra la descripción de la falla")
        comprobar(DIAGNOSTICO in cuerpo, "la ficha muestra el diagnóstico")
        comprobar(RESOLUCION in cuerpo, "la ficha muestra la resolución")
        comprobar("Solicitante Bloque 8" in cuerpo, "la ficha muestra al solicitante")

        respuesta = admin.get("/app/incidencias/999999")
        comprobar(respuesta.status_code == 404, "una incidencia inexistente devuelve 404")

    # ---------------------------------------------------------
    # 3. Alcance del Usuario Solicitante
    # ---------------------------------------------------------
    with app.test_client() as solicitante:
        sesion_solicitante(solicitante)

        respuesta = solicitante.get("/app/incidencias")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(DESCRIPCION_INC in cuerpo, "el solicitante ve su propia incidencia")

        respuesta = solicitante.get(f"/app/incidencias/{incidencia_id}")
        comprobar(respuesta.status_code == 200, "el solicitante abre el detalle de su incidencia")

        respuesta = solicitante.get("/app/incidencias/1")
        comprobar(
            respuesta.status_code == 403,
            "el solicitante no abre incidencias de otras personas",
        )

        respuesta = solicitante.get(f"/app/mantenimientos/{mantenimiento_id}")
        comprobar(
            respuesta.status_code == 403,
            "el solicitante no accede a la ficha de mantenimientos",
        )

    print()
    if fallos:
        print(f"FALLOS: {len(fallos)}")
        raise SystemExit(1)
    print("BLOQUE 8 OK")
finally:
    limpiar()
