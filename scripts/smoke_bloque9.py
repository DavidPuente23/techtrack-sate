"""Prueba de extremo a extremo del Bloque 9.

Cubre la coherencia del panel principal según el rol (métricas, accesos
rápidos y actividad reciente con alcance) y el marcado de la navegación
móvil de SATE.

Crea un activo, dos usuarios y dos incidencias temporales, y los elimina
al final.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from werkzeug.security import generate_password_hash

from config import Config
from app import app

MARCA = str(int(time.time()))
IDENTIFICADOR = f"TST-B9-{MARCA[-8:]}"
NOMBRE_ACTIVO = f"Equipo Prueba Bloque 9 {MARCA}"
EMAIL_SOLICITANTE = f"prueba.bloque9.solicitante.{MARCA}@techtrack.com"
EMAIL_OTRO = f"prueba.bloque9.otro.{MARCA}@techtrack.com"
DESC_PROPIA = f"Incidencia propia Bloque 9 {MARCA}"
DESC_AJENA = f"Incidencia ajena Bloque 9 {MARCA}"

fallos = []
activo_id = None
solicitante_id = None
otro_id = None
incidencia_propia_id = None
incidencia_ajena_id = None


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


def sesion(cliente, rol, usuario_id=1, nombre="Prueba Bloque 9", departamento_id=1):
    with cliente.session_transaction() as sesion_actual:
        sesion_actual.clear()
        sesion_actual["usuario_id"] = usuario_id
        sesion_actual["nombre"] = nombre
        sesion_actual["rol"] = rol
        sesion_actual["departamento_id"] = departamento_id
        sesion_actual["tema"] = "blue"
        sesion_actual["_csrf_token"] = "token-bloque9"


def limpiar():
    if incidencia_propia_id is not None:
        ejecutar("DELETE FROM incidencias WHERE id = %s", (incidencia_propia_id,))
        ejecutar(
            "DELETE FROM auditoria WHERE entidad = 'Incidencia' AND entidad_id = %s",
            (incidencia_propia_id,),
        )
    if incidencia_ajena_id is not None:
        ejecutar("DELETE FROM incidencias WHERE id = %s", (incidencia_ajena_id,))
        ejecutar(
            "DELETE FROM auditoria WHERE entidad = 'Incidencia' AND entidad_id = %s",
            (incidencia_ajena_id,),
        )
    if activo_id is not None:
        ejecutar("DELETE FROM auditoria WHERE entidad = 'Activo' AND entidad_id = %s", (activo_id,))
        ejecutar("DELETE FROM activos WHERE id = %s", (activo_id,))
    for usuario in (solicitante_id, otro_id):
        if usuario is not None:
            ejecutar("DELETE FROM auditoria WHERE entidad = 'Usuario' AND entidad_id = %s", (usuario,))
            ejecutar("DELETE FROM usuarios WHERE id = %s", (usuario,))


try:
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO activos
            (identificador, nombre, tipo, marca, modelo, numero_serie,
             ubicacion, responsable, departamento_id, estado)
        VALUES (%s, %s, 'Laptop', 'MarcaB9', 'ModeloB9', %s,
                'Aula 9', 'Responsable B9', 3, 'Operativo')
        """,
        (IDENTIFICADOR, NOMBRE_ACTIVO, f"SERIE-B9-{MARCA}"),
    )
    activo_id = cursor.lastrowid

    for nombre, email in (
        ("Solicitante Bloque 9", EMAIL_SOLICITANTE),
        ("Otro Solicitante Bloque 9", EMAIL_OTRO),
    ):
        cursor.execute(
            """
            INSERT INTO usuarios
                (nombre, email, password, departamento_id, rol_id, activo, debe_cambiar_password)
            VALUES (%s, %s, %s, 3, 4, TRUE, FALSE)
            """,
            (nombre, email, generate_password_hash("Temporal123!")),
        )
        if nombre.startswith("Solicitante"):
            solicitante_id = cursor.lastrowid
        else:
            otro_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO incidencias
            (activo_id, descripcion, prioridad, responsable, estado, solicitante_id)
        VALUES (%s, %s, 'Alta', 'Soporte B9', 'Nueva', %s)
        """,
        (activo_id, DESC_PROPIA, solicitante_id),
    )
    incidencia_propia_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO incidencias
            (activo_id, descripcion, prioridad, responsable, estado, solicitante_id)
        VALUES (%s, %s, 'Baja', 'Soporte B9', 'Nueva', %s)
        """,
        (activo_id, DESC_AJENA, otro_id),
    )
    incidencia_ajena_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()

    # ---------------------------------------------------------
    # 1. Administrador: panel completo y menú móvil
    # ---------------------------------------------------------
    with app.test_client() as admin:
        sesion(admin, "Administrador General")
        respuesta = admin.get("/app/dashboard")
        cuerpo = respuesta.get_data(as_text=True)

        comprobar(respuesta.status_code == 200, "el panel del administrador responde")
        comprobar("Actividad reciente" in cuerpo, "el panel muestra la actividad reciente")
        comprobar("Usuarios activos" in cuerpo, "el administrador ve la métrica de usuarios")
        comprobar("Gestionar usuarios" in cuerpo, "el administrador ve el acceso a usuarios")
        comprobar("Registrar activo" in cuerpo, "el administrador ve el alta de activos")
        comprobar("Programar mantenimiento" in cuerpo, "el administrador ve el alta de mantenimientos")
        comprobar("Reportar incidencia" in cuerpo, "el administrador ve el alta de incidencias")
        comprobar("Mantenimientos próximos" in cuerpo, "el administrador ve mantenimientos próximos")
        comprobar("Incidencias por estado" in cuerpo, "el administrador ve la gráfica de incidencias")
        comprobar(DESC_PROPIA in cuerpo, "el administrador ve la incidencia propia temporal")
        comprobar(DESC_AJENA in cuerpo, "el administrador ve la incidencia ajena temporal")

        comprobar('id="menu-toggle"' in cuerpo, "el layout incluye el botón de menú móvil")
        comprobar('aria-controls="sidebar-sate"' in cuerpo, "el botón de menú apunta al sidebar")
        comprobar('aria-expanded="false"' in cuerpo, "el botón de menú declara su estado inicial")
        comprobar('id="sidebar-overlay"' in cuerpo, "el layout incluye el overlay del menú")
        comprobar('id="sidebar-sate"' in cuerpo, "el sidebar tiene identificador para el menú móvil")
        comprobar("js/sate_nav.js" in cuerpo, "el layout carga el script de navegación móvil")

    # ---------------------------------------------------------
    # 2. Dirección General: consulta, sin altas ni administración
    # ---------------------------------------------------------
    with app.test_client() as direccion:
        sesion(direccion, "Dirección General")
        respuesta = direccion.get("/app/dashboard")
        cuerpo = respuesta.get_data(as_text=True)

        comprobar(respuesta.status_code == 200, "el panel de Dirección General responde")
        comprobar("Ver inventario" in cuerpo, "Dirección ve el acceso de consulta al inventario")
        comprobar("Ver mantenimientos" in cuerpo, "Dirección ve el acceso de consulta a mantenimientos")
        comprobar("Ver incidencias" in cuerpo, "Dirección ve el acceso de consulta a incidencias")
        comprobar("Registrar activo" not in cuerpo, "Dirección no ve el alta de activos")
        comprobar("Programar mantenimiento" not in cuerpo, "Dirección no ve el alta de mantenimientos")
        comprobar("Reportar incidencia" not in cuerpo, "Dirección no ve el alta de incidencias")
        comprobar("Gestionar usuarios" not in cuerpo, "Dirección no ve la gestión de usuarios")
        comprobar("Usuarios activos" not in cuerpo, "Dirección no ve la métrica de usuarios")
        comprobar("Mantenimientos próximos" in cuerpo, "Dirección ve mantenimientos próximos")
        comprobar("Incidencias por estado" in cuerpo, "Dirección ve la gráfica de incidencias")

    # ---------------------------------------------------------
    # 3. Usuario Solicitante: alcance de departamento e incidencias propias
    # ---------------------------------------------------------
    with app.test_client() as solicitante:
        sesion(
            solicitante,
            "Usuario Solicitante",
            usuario_id=solicitante_id,
            nombre="Solicitante Bloque 9",
            departamento_id=3,
        )
        respuesta = solicitante.get("/app/dashboard")
        cuerpo = respuesta.get_data(as_text=True)

        comprobar(respuesta.status_code == 200, "el panel del Usuario Solicitante responde")
        comprobar("Activos de mi área" in cuerpo, "el solicitante ve la métrica de su área")
        comprobar("Mis incidencias abiertas" in cuerpo, "el solicitante ve sus incidencias abiertas")
        comprobar("Alcance de tu cuenta" in cuerpo, "el solicitante ve la nota de alcance")
        comprobar("Desarrollo" in cuerpo, "la nota de alcance nombra su departamento")
        comprobar("Reportar incidencia" in cuerpo, "el solicitante puede reportar incidencias")
        comprobar("Ver inventario" in cuerpo, "el solicitante ve el acceso a su inventario")
        comprobar("Ver incidencias" in cuerpo, "el solicitante ve el acceso a sus incidencias")
        comprobar("Programar mantenimiento" not in cuerpo, "el solicitante no ve el alta de mantenimientos")
        comprobar("Ver mantenimientos" not in cuerpo, "el solicitante no ve el módulo de mantenimientos")
        comprobar("Mantenimientos próximos" not in cuerpo, "el solicitante no ve mantenimientos próximos")
        comprobar("Gestionar usuarios" not in cuerpo, "el solicitante no ve la gestión de usuarios")
        comprobar("Usuarios activos" not in cuerpo, "el solicitante no ve la métrica de usuarios")
        comprobar(DESC_PROPIA in cuerpo, "el solicitante ve su incidencia temporal")
        comprobar(DESC_AJENA not in cuerpo, "el solicitante no ve la incidencia de otra persona")

    # ---------------------------------------------------------
    # 4. Los siete roles renderizan el panel sin errores
    # ---------------------------------------------------------
    for rol in (
        "Administrador General",
        "Dirección General",
        "Administrador de Activos",
        "Administrador de Redes",
        "Desarrollador",
        "Técnico de Soporte",
        "Usuario Solicitante",
    ):
        with app.test_client() as cliente:
            sesion(cliente, rol)
            respuesta = cliente.get("/app/dashboard")
            comprobar(respuesta.status_code == 200, f"el panel responde para {rol}")

    print()
    if fallos:
        print(f"FALLOS: {len(fallos)}")
        raise SystemExit(1)
    print("BLOQUE 9 OK")
finally:
    limpiar()
