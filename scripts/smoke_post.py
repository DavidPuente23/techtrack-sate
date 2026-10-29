"""Pruebas de humo de POST con CSRF real. Limpia los datos de prueba."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mysql.connector
from config import Config
from app import app

marca = f"smoke-{int(time.time())}@example.com"
fallos = []


def conectar():
    return mysql.connector.connect(
        host=Config.DB_HOST, port=Config.DB_PORT, user=Config.DB_USER,
        password=Config.DB_PASSWORD, database=Config.DB_NAME,
    )


def token_de(cliente, ruta):
    cliente.get(ruta)
    with cliente.session_transaction() as sesion:
        return sesion.get("_csrf_token")


with app.test_client() as cliente:
    # Contacto válido
    token = token_de(cliente, "/contacto")
    respuesta = cliente.post(
        "/contacto",
        data={
            "_csrf_token": token,
            "nombre": "Prueba Smoke",
            "organizacion": "TechTrack QA",
            "correo": marca,
            "motivo": "Otro",
            "mensaje": "Mensaje de prueba automatizada.",
            "acepta_privacidad": "1",
        },
    )
    ok = respuesta.status_code == 302
    print(f"{'OK ' if ok else 'FALLO'} POST /contacto -> {respuesta.status_code}")
    if not ok:
        fallos.append("contacto")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM mensajes_contacto WHERE correo = %s", (marca,))
    existe = cursor.fetchone()[0]
    cursor.execute("DELETE FROM mensajes_contacto WHERE correo = %s", (marca,))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"{'OK ' if existe == 1 else 'FALLO'} contacto guardado en BD")
    if existe != 1:
        fallos.append("contacto_bd")

    # Contacto sin aceptar privacidad: no debe insertar
    token = token_de(cliente, "/contacto")
    cliente.post(
        "/contacto",
        data={
            "_csrf_token": token,
            "nombre": "Prueba Smoke",
            "organizacion": "TechTrack QA",
            "correo": marca,
            "motivo": "Otro",
            "mensaje": "Sin consentimiento.",
        },
    )
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM mensajes_contacto WHERE correo = %s", (marca,))
    existe = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    ok = existe == 0
    print(f"{'OK ' if ok else 'FALLO'} contacto sin consentimiento no se guarda")
    if not ok:
        fallos.append("contacto_privacidad")

    # Postulación válida
    token = token_de(cliente, "/trabaja-con-nosotros/tecnico-soporte")
    respuesta = cliente.post(
        "/trabaja-con-nosotros/tecnico-soporte",
        data={
            "_csrf_token": token,
            "nombre": "Prueba Smoke",
            "correo": marca,
            "mensaje": "CV de prueba",
            "acepta_privacidad": "1",
        },
    )
    ok = respuesta.status_code == 302
    print(f"{'OK ' if ok else 'FALLO'} POST /trabaja-con-nosotros/tecnico-soporte -> {respuesta.status_code}")
    if not ok:
        fallos.append("vacante")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM postulaciones WHERE correo = %s", (marca,))
    existe = cursor.fetchone()[0]
    cursor.execute("DELETE FROM postulaciones WHERE correo = %s", (marca,))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"{'OK ' if existe == 1 else 'FALLO'} postulación guardada en BD")
    if existe != 1:
        fallos.append("vacante_bd")

    # Logout con token válido
    with cliente.session_transaction() as sesion:
        sesion["usuario_id"] = 1
        sesion["nombre"] = "Administrador"
        sesion["rol"] = "Administrador General"
        sesion["tema"] = "blue"
        sesion["_csrf_token"] = "token-logout"
    respuesta = cliente.post("/logout", data={"_csrf_token": "token-logout"})
    ok = respuesta.status_code == 302 and "/login" in respuesta.headers.get("Location", "")
    print(f"{'OK ' if ok else 'FALLO'} POST /logout -> {respuesta.status_code}")
    if not ok:
        fallos.append("logout")

print()
if fallos:
    print("FALLOS:", fallos)
    raise SystemExit(1)
print("POST CON CSRF OK")
