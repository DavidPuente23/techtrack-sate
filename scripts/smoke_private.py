"""Pruebas de humo de las vistas privadas con una sesión de administrador."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app

RUTAS = [
    "/app/dashboard",
    "/app/activos",
    "/app/activos/nuevo",
    "/app/mantenimientos",
    "/app/mantenimientos/nuevo",
    "/app/incidencias",
    "/app/incidencias/nueva",
    "/app/usuarios",
    "/app/usuarios/nuevo",
    "/app/usuarios/1/editar",
    "/app/perfil",
]

RETIRADAS = [
    "/app/reportes",
    "/app/proveedores",
    "/app/cambios",
    "/app/problemas",
    "/app/politicas",
]

fallos = []

with app.test_client() as cliente:
    with cliente.session_transaction() as sesion:
        sesion["usuario_id"] = 1
        sesion["nombre"] = "Administrador"
        sesion["rol"] = "Administrador General"
        sesion["departamento_id"] = 1
        sesion["tema"] = "blue"
        sesion["_csrf_token"] = "token-de-prueba"

    for ruta in RUTAS:
        respuesta = cliente.get(ruta)
        ok = respuesta.status_code == 200
        print(f"{'OK ' if ok else 'FALLO'} GET {ruta} -> {respuesta.status_code}")
        if not ok:
            fallos.append((ruta, respuesta.status_code))

    # Detalle inexistente debe ser 404, no 500.
    respuesta = cliente.get("/app/activos/999999")
    ok = respuesta.status_code == 404
    print(f"{'OK ' if ok else 'FALLO'} GET /app/activos/999999 -> {respuesta.status_code}")
    if not ok:
        fallos.append(("/app/activos/999999", respuesta.status_code))

    for ruta in RETIRADAS:
        respuesta = cliente.get(ruta)
        ok = respuesta.status_code == 404
        print(f"{'OK ' if ok else 'FALLO'} GET {ruta} (retirada) -> {respuesta.status_code}")
        if not ok:
            fallos.append((ruta, respuesta.status_code))

print()
if fallos:
    print("FALLOS:", fallos)
    raise SystemExit(1)
print("VISTAS PRIVADAS OK")
