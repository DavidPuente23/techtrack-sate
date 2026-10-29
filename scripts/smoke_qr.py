"""Prueba de la identificación por QR de los activos.

Cubre la ruta del código QR, la etiqueta imprimible, la presencia de ambos en la
ficha del activo y el alcance por departamento. Crea un activo temporal y lo
elimina al final.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector

from config import Config
from app import app

MARCA = str(int(time.time()))
IDENTIFICADOR = f"TST-QR-{MARCA[-7:]}"
NOMBRE_ACTIVO = f"Equipo Prueba QR {MARCA}"

fallos = []
activo_id = None


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


def sesion(cliente, rol, usuario_id=1, nombre="Prueba QR", departamento_id=3):
    with cliente.session_transaction() as sesion_actual:
        sesion_actual.clear()
        sesion_actual["usuario_id"] = usuario_id
        sesion_actual["nombre"] = nombre
        sesion_actual["rol"] = rol
        sesion_actual["departamento_id"] = departamento_id
        sesion_actual["tema"] = "blue"
        sesion_actual["_csrf_token"] = "token-qr"


def limpiar():
    if activo_id is not None:
        ejecutar("DELETE FROM historial_activos WHERE activo_id = %s", (activo_id,))
        ejecutar(
            "DELETE FROM auditoria WHERE entidad = 'Activo' AND entidad_id = %s",
            (activo_id,),
        )
        ejecutar("DELETE FROM activos WHERE id = %s", (activo_id,))


try:
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO activos
            (identificador, nombre, tipo, marca, modelo, numero_serie,
             ubicacion, responsable, departamento_id, estado)
        VALUES (%s, %s, 'Laptop', 'MarcaQR', 'ModeloQR', %s,
                'Aula QR', 'Responsable QR', 3, 'Operativo')
        """,
        (IDENTIFICADOR, NOMBRE_ACTIVO, f"SERIE-QR-{MARCA}"),
    )
    activo_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()

    with app.test_client() as admin:
        sesion(admin, "Administrador General")

        # -----------------------------------------------------
        # 1. La ficha del activo ofrece el QR y la etiqueta
        # -----------------------------------------------------
        respuesta = admin.get(f"/app/activos/{activo_id}")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(respuesta.status_code == 200, "la ficha del activo responde")
        comprobar("Identificación del activo" in cuerpo, "la ficha incluye la sección de QR")
        comprobar(
            f"/app/activos/{activo_id}/qr.svg" in cuerpo,
            "la ficha enlaza el código QR del activo",
        )
        comprobar(
            f"/app/activos/{activo_id}/etiqueta" in cuerpo,
            "la ficha enlaza la etiqueta imprimible",
        )

        # -----------------------------------------------------
        # 2. El código QR se entrega como SVG
        # -----------------------------------------------------
        respuesta = admin.get(f"/app/activos/{activo_id}/qr.svg")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(respuesta.status_code == 200, "el código QR responde")
        comprobar(
            respuesta.headers.get("Content-Type", "").startswith("image/svg+xml"),
            "el código QR se entrega como SVG",
        )
        comprobar("<svg" in cuerpo and "</svg>" in cuerpo, "el SVG está bien formado")
        comprobar(len(cuerpo) > 500, "el SVG tiene contenido")
        comprobar(
            "private" in respuesta.headers.get("Cache-Control", ""),
            "el QR se marca como privado en caché",
        )

        # Dos activos distintos generan códigos distintos
        respuesta_otro = admin.get("/app/activos/1/qr.svg")
        comprobar(respuesta_otro.status_code == 200, "el QR de otro activo responde")
        comprobar(
            respuesta_otro.get_data() != respuesta.get_data(),
            "cada activo genera un código distinto",
        )

        # -----------------------------------------------------
        # 3. Etiqueta imprimible
        # -----------------------------------------------------
        respuesta = admin.get(f"/app/activos/{activo_id}/etiqueta")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(respuesta.status_code == 200, "la etiqueta imprimible responde")
        comprobar(IDENTIFICADOR in cuerpo, "la etiqueta muestra el identificador")
        comprobar(NOMBRE_ACTIVO in cuerpo, "la etiqueta muestra el nombre del activo")
        comprobar("window.print()" in cuerpo, "la etiqueta ofrece el botón de impresión")
        comprobar(
            f"/app/activos/{activo_id}/qr.svg" in cuerpo,
            "la etiqueta incrusta el código QR",
        )
        comprobar("@media print" in cuerpo, "la etiqueta define estilos de impresión")

    # ---------------------------------------------------------
    # 4. Alcance por departamento
    # ---------------------------------------------------------
    with app.test_client() as ajeno:
        sesion(
            ajeno,
            "Usuario Solicitante",
            usuario_id=1,
            nombre="Solicitante de otro departamento",
            departamento_id=1,
        )
        comprobar(
            ajeno.get(f"/app/activos/{activo_id}/qr.svg").status_code == 403,
            "un solicitante de otro departamento no obtiene el QR",
        )
        comprobar(
            ajeno.get(f"/app/activos/{activo_id}/etiqueta").status_code == 403,
            "un solicitante de otro departamento no obtiene la etiqueta",
        )

    with app.test_client() as propio:
        sesion(
            propio,
            "Usuario Solicitante",
            usuario_id=1,
            nombre="Solicitante del departamento",
            departamento_id=3,
        )
        comprobar(
            propio.get(f"/app/activos/{activo_id}/qr.svg").status_code == 200,
            "un solicitante del departamento sí obtiene el QR",
        )
        comprobar(
            propio.get(f"/app/activos/{activo_id}/etiqueta").status_code == 200,
            "un solicitante del departamento sí obtiene la etiqueta",
        )

    # ---------------------------------------------------------
    # 5. Sin sesión no se exponen el QR ni la etiqueta
    # ---------------------------------------------------------
    with app.test_client() as anonimo:
        for ruta in (f"/app/activos/{activo_id}/qr.svg", f"/app/activos/{activo_id}/etiqueta"):
            respuesta = anonimo.get(ruta)
            comprobar(respuesta.status_code == 302, f"sin sesión {ruta} redirige al login")
            comprobar(
                "/login" in respuesta.headers.get("Location", ""),
                f"sin sesión {ruta} apunta al login",
            )

    print()
    if fallos:
        print(f"FALLOS: {len(fallos)}")
        raise SystemExit(1)
    print("QR DE ACTIVOS OK")
finally:
    limpiar()
