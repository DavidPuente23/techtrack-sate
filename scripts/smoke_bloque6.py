"""Prueba de extremo a extremo del Bloque 6.

Cubre el alta de usuarios, la contraseña temporal, el alcance del rol
Usuario Solicitante, el restablecimiento de contraseña, la desactivación
de cuentas y las protecciones del último administrador.

Crea un usuario y una incidencia temporales y los elimina al final.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from config import Config
from app import app

MARCA = str(int(time.time()))
EMAIL = f"prueba.bloque6.{MARCA}@techtrack.com"
PASSWORD_TEMP = "Temporal123!"
PASSWORD_NUEVA = "Definitiva123!"
PASSWORD_RESET = "Restablecida123!"
PASSWORD_FINAL = "Final12345!"

fallos = []
usuario_id = None
incidencia_id = None
estado_original_activo = None


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


def token(cliente):
    cliente.get("/login")
    with cliente.session_transaction() as sesion:
        return sesion["_csrf_token"]


def sesion_admin(cliente):
    with cliente.session_transaction() as sesion:
        sesion.clear()
        sesion["usuario_id"] = 1
        sesion["nombre"] = "Administrador"
        sesion["rol"] = "Administrador General"
        sesion["departamento_id"] = 1
        sesion["tema"] = "blue"
        sesion["_csrf_token"] = "token-admin"


def login(cliente, email, password):
    with cliente.session_transaction() as sesion:
        sesion.clear()
    cliente.get("/login")
    with cliente.session_transaction() as sesion:
        csrf = sesion["_csrf_token"]
    respuesta = cliente.post(
        "/login",
        data={"email": email, "password": password, "_csrf_token": csrf},
        follow_redirects=False,
    )
    return respuesta


def limpiar():
    if usuario_id is None:
        return
    if incidencia_id is not None:
        ejecutar("DELETE FROM incidencias WHERE id = %s", (incidencia_id,))
        ejecutar(
            "DELETE FROM auditoria WHERE entidad = 'Incidencia' AND entidad_id = %s",
            (incidencia_id,),
        )
    ejecutar(
        "DELETE FROM historial_activos WHERE detalle LIKE %s",
        (f"%Falla de prueba {MARCA}%",),
    )
    ejecutar("DELETE FROM auditoria WHERE entidad = 'Usuario' AND entidad_id = %s", (usuario_id,))
    ejecutar("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
    if estado_original_activo:
        ejecutar(
            "UPDATE activos SET estado = %s WHERE nombre = 'HP DESARROLLO'",
            (estado_original_activo,),
        )


try:
    activo_propio = consultar(
        "SELECT id, estado FROM activos WHERE nombre = 'HP DESARROLLO' LIMIT 1"
    )[0]
    activo_ajeno = consultar(
        "SELECT id FROM activos WHERE nombre = 'IMPRESORA' LIMIT 1"
    )[0]
    estado_original_activo = activo_propio["estado"]

    # ---------------------------------------------------------
    # 1. Alta de usuario desde el módulo de usuarios
    # ---------------------------------------------------------
    with app.test_client() as admin:
        sesion_admin(admin)
        respuesta = admin.get("/app/usuarios")
        comprobar(respuesta.status_code == 200, "el administrador ve el listado de usuarios")

        respuesta = admin.post(
            "/app/usuarios/nuevo",
            data={
                "nombre": "Usuario Prueba Bloque 6",
                "email": EMAIL,
                "password": PASSWORD_TEMP,
                "departamento_id": 2,
                "rol_id": 4,
                "_csrf_token": "token-admin",
            },
            follow_redirects=False,
        )
        comprobar(respuesta.status_code == 302, "el administrador crea un usuario")

    filas = consultar("SELECT * FROM usuarios WHERE email = %s", (EMAIL,))
    comprobar(len(filas) == 1, "el usuario temporal existe en la base de datos")
    usuario = filas[0]
    usuario_id = usuario["id"]
    comprobar(bool(usuario["debe_cambiar_password"]), "la cuenta nueva nace con contraseña temporal")
    comprobar(usuario["departamento_id"] == 2, "la cuenta queda en el departamento Redes")

    # ---------------------------------------------------------
    # 2. Primer acceso: contraseña temporal obligatoria
    # ---------------------------------------------------------
    with app.test_client() as usuario_cliente:
        respuesta = login(usuario_cliente, EMAIL, PASSWORD_TEMP)
        comprobar(
            respuesta.headers.get("Location", "").endswith("/app/perfil"),
            "el primer acceso redirige a Mi Perfil",
        )

        respuesta = usuario_cliente.get("/app/dashboard", follow_redirects=False)
        comprobar(
            respuesta.status_code == 302
            and respuesta.headers.get("Location", "").endswith("/app/perfil"),
            "sin cambiar la contraseña no se puede entrar al panel",
        )

        usuario_cliente.get("/app/perfil")
        with usuario_cliente.session_transaction() as sesion:
            csrf = sesion["_csrf_token"]

        respuesta = usuario_cliente.post(
            "/app/perfil",
            data={
                "password_actual": "incorrecta",
                "password": PASSWORD_NUEVA,
                "tema": "blue",
                "_csrf_token": csrf,
            },
            follow_redirects=False,
        )
        comprobar(respuesta.status_code == 302, "se rechaza una contraseña actual incorrecta")
        with usuario_cliente.session_transaction() as sesion:
            comprobar(
                bool(sesion.get("debe_cambiar_password")),
                "la marca de contraseña temporal sigue activa tras el error",
            )

        respuesta = usuario_cliente.post(
            "/app/perfil",
            data={
                "password_actual": PASSWORD_TEMP,
                "password": PASSWORD_NUEVA,
                "tema": "blue",
                "_csrf_token": csrf,
            },
            follow_redirects=False,
        )
        comprobar(respuesta.status_code == 302, "el usuario cambia su contraseña temporal")
        with usuario_cliente.session_transaction() as sesion:
            comprobar(
                not sesion.get("debe_cambiar_password"),
                "la marca de contraseña temporal desaparece de la sesión",
            )

        respuesta = usuario_cliente.get("/app/dashboard")
        comprobar(respuesta.status_code == 200, "tras el cambio ya puede entrar al panel")

        # -----------------------------------------------------
        # 3. Alcance del rol Usuario Solicitante
        # -----------------------------------------------------
        respuesta = usuario_cliente.get("/app/activos")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(respuesta.status_code == 200, "el solicitante consulta activos")
        comprobar("HP DESARROLLO" in cuerpo, "ve el activo de su departamento")
        comprobar("IMPRESORA" not in cuerpo, "no ve activos de otro departamento")

        respuesta = usuario_cliente.get("/app/incidencias")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(
            "No hay incidencias que coincidan con los filtros" in cuerpo,
            "al principio solo ve sus propias incidencias (ninguna)",
        )

        respuesta = usuario_cliente.get("/app/mantenimientos", follow_redirects=False)
        comprobar(respuesta.status_code == 403, "el solicitante no accede a mantenimientos")

        respuesta = usuario_cliente.get("/app/usuarios", follow_redirects=False)
        comprobar(respuesta.status_code == 403, "el solicitante no accede a usuarios")

        with usuario_cliente.session_transaction() as sesion:
            csrf = sesion["_csrf_token"]

        # Intento de reportar una falla sobre un activo de otro departamento.
        respuesta = usuario_cliente.post(
            "/app/incidencias/nueva",
            data={
                "activo_id": activo_ajeno["id"],
                "descripcion": "Intento fuera de alcance",
                "prioridad": "Media",
                "responsable": "Soporte",
                "_csrf_token": csrf,
            },
            follow_redirects=False,
        )
        comprobar(respuesta.status_code == 302, "se procesa el intento fuera de alcance")
        filas = consultar(
            "SELECT id FROM incidencias WHERE descripcion = %s",
            ("Intento fuera de alcance",),
        )
        comprobar(not filas, "no se crea una incidencia sobre un activo ajeno")

        # Falla válida sobre su propio activo.
        respuesta = usuario_cliente.post(
            "/app/incidencias/nueva",
            data={
                "activo_id": activo_propio["id"],
                "descripcion": f"Falla de prueba {MARCA}",
                "prioridad": "Media",
                "responsable": "Soporte",
                "_csrf_token": csrf,
            },
            follow_redirects=False,
        )
        comprobar(respuesta.status_code == 302, "el solicitante reporta una falla de su activo")

        filas = consultar(
            "SELECT id, solicitante_id FROM incidencias WHERE descripcion = %s",
            (f"Falla de prueba {MARCA}",),
        )
        comprobar(len(filas) == 1, "la incidencia válida queda registrada")
        if filas:
            incidencia_id = filas[0]["id"]
            comprobar(
                filas[0]["solicitante_id"] == usuario_id,
                "la incidencia guarda al solicitante",
            )

        respuesta = usuario_cliente.get("/app/incidencias")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(f"Falla de prueba {MARCA}" in cuerpo, "ve su incidencia en el listado")

    # El administrador ve todas las incidencias, incluidas las del solicitante.
    with app.test_client() as admin:
        sesion_admin(admin)
        respuesta = admin.get("/app/incidencias")
        cuerpo = respuesta.get_data(as_text=True)
        comprobar(f"Falla de prueba {MARCA}" in cuerpo, "el administrador ve la incidencia del solicitante")

        # -----------------------------------------------------
        # 4. Restablecimiento de contraseña
        # -----------------------------------------------------
        respuesta = admin.post(
            f"/app/usuarios/{usuario_id}/password",
            data={"password": PASSWORD_RESET, "_csrf_token": "token-admin"},
            follow_redirects=False,
        )
        comprobar(respuesta.status_code == 302, "el administrador restablece la contraseña")
        fila = consultar(
            "SELECT debe_cambiar_password FROM usuarios WHERE id = %s", (usuario_id,)
        )[0]
        comprobar(bool(fila["debe_cambiar_password"]), "la contraseña restablecida es temporal")

        # -----------------------------------------------------
        # 5. Protecciones del administrador
        # -----------------------------------------------------
        respuesta = admin.post(
            "/app/usuarios/1/estado",
            data={"_csrf_token": "token-admin"},
            follow_redirects=False,
        )
        comprobar(respuesta.status_code == 302, "el administrador no puede desactivarse a sí mismo")
        fila = consultar("SELECT activo FROM usuarios WHERE id = 1")[0]
        comprobar(bool(fila["activo"]), "la cuenta del administrador sigue activa")

        respuesta = admin.post(
            "/app/usuarios/1/editar",
            data={
                "nombre": "Administrador",
                "email": "admin@techtrack.com",
                "departamento_id": 1,
                "rol_id": 3,
                "_csrf_token": "token-admin",
            },
            follow_redirects=False,
        )
        comprobar(respuesta.status_code == 302, "se procesa el intento de cambiar el rol propio")
        fila = consultar("SELECT rol_id FROM usuarios WHERE id = 1")[0]
        comprobar(fila["rol_id"] == 1, "el rol propio no se puede cambiar")

        # -----------------------------------------------------
        # 6. Desactivación de la cuenta
        # -----------------------------------------------------
        respuesta = admin.post(
            f"/app/usuarios/{usuario_id}/estado",
            data={"_csrf_token": "token-admin"},
            follow_redirects=False,
        )
        comprobar(respuesta.status_code == 302, "el administrador desactiva la cuenta")
        fila = consultar("SELECT activo FROM usuarios WHERE id = %s", (usuario_id,))[0]
        comprobar(not fila["activo"], "la cuenta queda inactiva en la base de datos")

    # La cuenta inactiva no puede iniciar sesión.
    with app.test_client() as usuario_cliente:
        respuesta = login(usuario_cliente, EMAIL, PASSWORD_RESET)
        comprobar(
            respuesta.headers.get("Location", "").endswith("/login"),
            "una cuenta inactiva no puede iniciar sesión",
        )
        with usuario_cliente.session_transaction() as sesion:
            comprobar("usuario_id" not in sesion, "no se crea sesión para una cuenta inactiva")

    print()
    if fallos:
        print(f"FALLOS: {len(fallos)}")
        raise SystemExit(1)
    print("BLOQUE 6 OK")
finally:
    limpiar()
