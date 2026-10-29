"""Prueba de extremo a extremo del Bloque 7.

Cubre los filtros del inventario (texto, estado, tipo, departamento y
combinaciones), el respeto del alcance por departamento y el historial
real de cambios: sin cambios no se registra nada y con cambios se guarda
el detalle antes/después junto al usuario que los realizó.

Crea un activo y un usuario temporales y los elimina al final.
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
NOMBRE_ACTIVO = f"Monitor Prueba Bloque 7 {MARCA}"
IDENTIFICADOR = f"MON-T7-{MARCA[-8:]}"
MARCA_TEXTO = f"MarcaPrueba{MARCA}"
EMAIL = f"prueba.bloque7.{MARCA}@techtrack.com"

fallos = []
activo_id = None
usuario_id = None


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
        sesion["nombre"] = "Solicitante Bloque 7"
        sesion["rol"] = "Usuario Solicitante"
        sesion["departamento_id"] = 2
        sesion["tema"] = "blue"
        sesion["_csrf_token"] = "token-solicitante"


def contar_historial():
    return consultar(
        "SELECT COUNT(*) AS total FROM historial_activos WHERE activo_id = %s",
        (activo_id,),
    )[0]["total"]


def limpiar():
    if activo_id is not None:
        ejecutar("DELETE FROM auditoria WHERE entidad = 'Activo' AND entidad_id = %s", (activo_id,))
        ejecutar("DELETE FROM activos WHERE id = %s", (activo_id,))
    if usuario_id is not None:
        ejecutar("DELETE FROM auditoria WHERE entidad = 'Usuario' AND entidad_id = %s", (usuario_id,))
        ejecutar("DELETE FROM usuarios WHERE id = %s", (usuario_id,))


try:
    # ---------------------------------------------------------
    # Datos temporales
    # ---------------------------------------------------------
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO activos
            (identificador, nombre, tipo, marca, modelo, numero_serie,
             ubicacion, responsable, departamento_id, estado)
        VALUES (%s, %s, 'Monitor', %s, 'ModeloPrueba', %s,
                'Laboratorio de pruebas', 'Responsable Original', 4, 'Con Falla')
        """,
        (IDENTIFICADOR, NOMBRE_ACTIVO, MARCA_TEXTO, f"SERIE-{MARCA}"),
    )
    activo_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO usuarios
            (nombre, email, password, departamento_id, rol_id, activo, debe_cambiar_password)
        VALUES (%s, %s, %s, 2, 4, TRUE, FALSE)
        """,
        ("Solicitante Bloque 7", EMAIL, generate_password_hash("Temporal123!")),
    )
    usuario_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()

    comprobar(contar_historial() == 0, "el activo temporal nace sin historial")

    # ---------------------------------------------------------
    # 1. Filtros del inventario
    # ---------------------------------------------------------
    with app.test_client() as admin:
        sesion_admin(admin)

        respuesta = admin.get(f"/app/activos?q={MARCA_TEXTO}")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(respuesta.status_code == 200, "el inventario responde con filtro de texto")
        comprobar(NOMBRE_ACTIVO in cuerpo, "la búsqueda por marca encuentra el activo")
        comprobar("HP DESARROLLO" not in cuerpo, "la búsqueda excluye los equipos que no coinciden")

        respuesta = admin.get("/app/activos?q=HP%20DESARROLLO")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar("HP DESARROLLO" in cuerpo, "la búsqueda por nombre funciona")
        comprobar(NOMBRE_ACTIVO not in cuerpo, "la búsqueda por nombre no arrastra otros equipos")

        respuesta = admin.get("/app/activos?estado=Con+Falla")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(NOMBRE_ACTIVO in cuerpo, "el filtro por estado encuentra el activo con falla")
        comprobar("HP DESARROLLO" not in cuerpo, "el filtro por estado descarta los operativos")
        comprobar(
            'value="Con Falla" selected' in cuerpo,
            "el formulario conserva el estado seleccionado",
        )
        comprobar("Filtros aplicados" in cuerpo, "el resumen avisa de los filtros activos")

        respuesta = admin.get("/app/activos?tipo=Monitor")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(NOMBRE_ACTIVO in cuerpo, "el filtro por tipo funciona")
        comprobar("HP DESARROLLO" not in cuerpo, "el filtro por tipo descarta las laptops")

        respuesta = admin.get("/app/activos?departamento_id=4")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(NOMBRE_ACTIVO in cuerpo, "el filtro por departamento funciona")
        comprobar("IMPRESORA" not in cuerpo, "el filtro por departamento descarta otros equipos")
        comprobar(
            'value="4" selected' in cuerpo,
            "el formulario conserva el departamento seleccionado",
        )

        respuesta = admin.get("/app/activos")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar("Filtros aplicados" not in cuerpo, "sin filtros no se muestra la marca de filtros")

        consulta = (
            f"/app/activos?q={MARCA_TEXTO}&estado=Con+Falla"
            "&tipo=Monitor&departamento_id=4"
        )
        respuesta = admin.get(consulta)
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(NOMBRE_ACTIVO in cuerpo, "los filtros combinados devuelven el activo")

        respuesta = admin.get(f"/app/activos?q={MARCA_TEXTO}&estado=Operativo")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(
            NOMBRE_ACTIVO not in cuerpo,
            "una combinación incompatible no devuelve resultados",
        )
        comprobar(
            "No hay activos que coincidan" in cuerpo,
            "el inventario muestra el estado vacío de los filtros",
        )

        respuesta = admin.get("/app/activos?estado=Inexistente&tipo=Invalido")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(
            NOMBRE_ACTIVO in cuerpo,
            "los filtros inválidos se ignoran sin romper el listado",
        )

        respuesta = admin.get("/app/activos?departamento_id=abc")
        comprobar(
            respuesta.status_code == 200,
            "un departamento no numérico no rompe el inventario",
        )

    # ---------------------------------------------------------
    # 2. Alcance del Usuario Solicitante en los filtros
    # ---------------------------------------------------------
    with app.test_client() as solicitante:
        sesion_solicitante(solicitante)

        respuesta = solicitante.get(f"/app/activos?q={MARCA_TEXTO}")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(
            NOMBRE_ACTIVO not in cuerpo,
            "el solicitante no ve por búsqueda un activo de otro departamento",
        )

        respuesta = solicitante.get("/app/activos?departamento_id=4")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(
            NOMBRE_ACTIVO not in cuerpo,
            "el solicitante no puede saltarse el alcance con el filtro de departamento",
        )

        respuesta = solicitante.get("/app/activos?q=HP%20DESARROLLO")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(
            "HP DESARROLLO" in cuerpo,
            "el solicitante sigue viendo los activos de su departamento",
        )

    # ---------------------------------------------------------
    # 3. Historial real de cambios
    # ---------------------------------------------------------
    with app.test_client() as admin:
        sesion_admin(admin)

        datos_originales = {
            "nombre": NOMBRE_ACTIVO,
            "ubicacion": "Laboratorio de pruebas",
            "responsable": "Responsable Original",
            "departamento_id": "4",
            "estado": "Con Falla",
            "_csrf_token": "token-admin",
        }
        respuesta = admin.post(
            f"/app/activos/{activo_id}/editar",
            data=datos_originales,
            follow_redirects=False,
        )
        comprobar(respuesta.status_code == 302, "se procesa una edición sin cambios")
        comprobar(
            contar_historial() == 0,
            "una edición sin cambios no escribe historial",
        )

        datos_nuevos = dict(datos_originales)
        datos_nuevos["responsable"] = "Responsable Nuevo"
        datos_nuevos["ubicacion"] = "Sala de redes"
        respuesta = admin.post(
            f"/app/activos/{activo_id}/editar",
            data=datos_nuevos,
            follow_redirects=False,
        )
        comprobar(respuesta.status_code == 302, "se procesa una edición con cambios")
        comprobar(contar_historial() == 1, "la edición con cambios registra un movimiento")

        filas = consultar(
            "SELECT tipo_movimiento, detalle, usuario_id FROM historial_activos"
            " WHERE activo_id = %s ORDER BY id DESC LIMIT 1",
            (activo_id,),
        )
        comprobar(len(filas) == 1, "el movimiento de edición existe")
        if filas:
            registro = filas[0]
            comprobar(
                registro["tipo_movimiento"] == "Actualización de datos",
                "el movimiento se clasifica como actualización de datos",
            )
            comprobar(
                "Responsable Original" in registro["detalle"]
                and "Responsable Nuevo" in registro["detalle"],
                "el detalle guarda el valor anterior y el nuevo del responsable",
            )
            comprobar(
                "Sala de redes" in registro["detalle"],
                "el detalle guarda la nueva ubicación",
            )
            comprobar(
                registro["usuario_id"] == 1,
                "el movimiento queda asociado al usuario que editó",
            )

        respuesta = admin.get(f"/app/activos/{activo_id}")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(respuesta.status_code == 200, "la ficha del activo responde")
        comprobar("Historial de movimientos" in cuerpo, "la ficha muestra el historial")
        comprobar("Responsable Nuevo" in cuerpo, "la ficha refleja el cambio")
        comprobar("1 movimiento(s) registrado(s)" in cuerpo, "la ficha cuenta los movimientos")
        comprobar("Administrador" in cuerpo, "el historial muestra el usuario que registró")
        comprobar(
            "history-timeline" in cuerpo,
            "el historial se presenta como línea de tiempo",
        )

        # Restaurar los valores del activo antes de borrarlo (deja otro movimiento).
        respuesta = admin.post(
            f"/app/activos/{activo_id}/editar",
            data=datos_originales,
            follow_redirects=False,
        )
        comprobar(respuesta.status_code == 302, "se restauran los datos originales")
        comprobar(contar_historial() == 2, "la restauración registra su propio movimiento")

    print()
    if fallos:
        print(f"FALLOS: {len(fallos)}")
        raise SystemExit(1)
    print("BLOQUE 7 OK")
finally:
    limpiar()
