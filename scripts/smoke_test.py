"""Pruebas de humo sin base de datos: rutas públicas, login y CSRF."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app

app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)

PUBLICAS = [
    "/",
    "/empresa",
    "/departamentos",
    "/departamentos/sit",
    "/departamentos/redes",
    "/departamentos/desarrollo",
    "/departamentos/soporte",
    "/politicas",
    "/politicas/gestion-activos",
    "/politicas/seguridad-informacion",
    "/trabaja-con-nosotros",
    "/trabaja-con-nosotros/tecnico-soporte",
    "/sate",
    "/contacto",
    "/privacidad",
    "/login",
]

fallos = []

with app.test_client() as cliente:
    for ruta in PUBLICAS:
        respuesta = cliente.get(ruta)
        estado = "OK " if respuesta.status_code == 200 else "FALLO"
        if respuesta.status_code != 200:
            fallos.append((ruta, respuesta.status_code))
        print(f"{estado} GET {ruta} -> {respuesta.status_code}")

    # Las rutas privadas deben redirigir al login.
    for ruta in ["/app/dashboard", "/app/activos", "/app/usuarios"]:
        respuesta = cliente.get(ruta)
        ok = respuesta.status_code == 302 and "/login" in respuesta.headers.get("Location", "")
        print(f"{'OK ' if ok else 'FALLO'} GET {ruta} -> {respuesta.status_code}")
        if not ok:
            fallos.append((ruta, respuesta.status_code))

    # POST sin token CSRF debe devolver 400.
    for ruta in ["/login", "/contacto"]:
        respuesta = cliente.post(ruta, data={"email": "x@x.com", "password": "x"})
        ok = respuesta.status_code == 400
        print(f"{'OK ' if ok else 'FALLO'} POST {ruta} sin CSRF -> {respuesta.status_code}")
        if not ok:
            fallos.append((ruta, respuesta.status_code))

    # Ruta de error 404 personalizada.
    respuesta = cliente.get("/ruta-que-no-existe")
    ok = respuesta.status_code == 404
    print(f"{'OK ' if ok else 'FALLO'} GET /ruta-que-no-existe -> {respuesta.status_code}")
    if not ok:
        fallos.append(("/ruta-que-no-existe", respuesta.status_code))

print()
if fallos:
    print("FALLOS:", fallos)
    raise SystemExit(1)
print("TODAS LAS PRUEBAS DE HUMO PASARON")
