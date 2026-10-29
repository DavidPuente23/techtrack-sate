"""Verifica la matriz de permisos de los siete roles del PIA."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app

CASOS = [
    # Administrador General: control total
    ("Administrador General", "/app/dashboard", 200),
    ("Administrador General", "/app/activos", 200),
    ("Administrador General", "/app/activos/nuevo", 200),
    ("Administrador General", "/app/mantenimientos", 200),
    ("Administrador General", "/app/mantenimientos/nuevo", 200),
    ("Administrador General", "/app/incidencias", 200),
    ("Administrador General", "/app/incidencias/nueva", 200),
    ("Administrador General", "/app/usuarios", 200),
    ("Administrador General", "/app/usuarios/nuevo", 200),

    # Dirección General: consulta, sin altas ni administración de cuentas
    ("Dirección General", "/app/dashboard", 200),
    ("Dirección General", "/app/activos", 200),
    ("Dirección General", "/app/activos/nuevo", 403),
    ("Dirección General", "/app/mantenimientos", 200),
    ("Dirección General", "/app/mantenimientos/nuevo", 403),
    ("Dirección General", "/app/incidencias", 200),
    ("Dirección General", "/app/incidencias/nueva", 403),
    ("Dirección General", "/app/usuarios", 403),

    # Administrador de Activos (SIT)
    ("Administrador de Activos", "/app/activos/nuevo", 200),
    ("Administrador de Activos", "/app/mantenimientos/nuevo", 200),
    ("Administrador de Activos", "/app/incidencias/nueva", 403),
    ("Administrador de Activos", "/app/usuarios", 403),

    # Administrador de Redes
    ("Administrador de Redes", "/app/activos/nuevo", 403),
    ("Administrador de Redes", "/app/mantenimientos/nuevo", 200),
    ("Administrador de Redes", "/app/incidencias/nueva", 200),
    ("Administrador de Redes", "/app/usuarios", 403),

    # Desarrollador
    ("Desarrollador", "/app/activos/nuevo", 403),
    ("Desarrollador", "/app/mantenimientos/nuevo", 403),
    ("Desarrollador", "/app/incidencias/nueva", 200),
    ("Desarrollador", "/app/usuarios", 403),

    # Técnico de Soporte
    ("Técnico de Soporte", "/app/activos/nuevo", 403),
    ("Técnico de Soporte", "/app/mantenimientos/nuevo", 200),
    ("Técnico de Soporte", "/app/incidencias/nueva", 200),
    ("Técnico de Soporte", "/app/usuarios", 403),

    # Usuario Solicitante: solo su departamento y sus incidencias
    ("Usuario Solicitante", "/app/dashboard", 200),
    ("Usuario Solicitante", "/app/activos", 200),
    ("Usuario Solicitante", "/app/activos/nuevo", 403),
    ("Usuario Solicitante", "/app/mantenimientos", 403),
    ("Usuario Solicitante", "/app/incidencias", 200),
    ("Usuario Solicitante", "/app/incidencias/nueva", 200),
    ("Usuario Solicitante", "/app/usuarios", 403),
]

MODULOS_RETIRADOS = [
    "/app/reportes",
    "/app/proveedores",
    "/app/cambios",
    "/app/problemas",
    "/app/politicas",
]

fallos = []

with app.test_client() as cliente:
    for rol, ruta, esperado in CASOS:
        with cliente.session_transaction() as sesion:
            sesion.clear()
            sesion["usuario_id"] = 1
            sesion["nombre"] = "Prueba"
            sesion["rol"] = rol
            sesion["departamento_id"] = 1
            sesion["tema"] = "blue"
            sesion["_csrf_token"] = "token-de-prueba"

        respuesta = cliente.get(ruta)
        ok = respuesta.status_code == esperado
        print(f"{'OK ' if ok else 'FALLO'} [{rol}] {ruta} -> {respuesta.status_code} (esperado {esperado})")
        if not ok:
            fallos.append((rol, ruta, respuesta.status_code, esperado))

    # Los módulos fuera del alcance del PIA ya no existen en SATE.
    with cliente.session_transaction() as sesion:
        sesion.clear()
        sesion["usuario_id"] = 1
        sesion["nombre"] = "Administrador"
        sesion["rol"] = "Administrador General"
        sesion["departamento_id"] = 1
        sesion["tema"] = "blue"
        sesion["_csrf_token"] = "token-de-prueba"

    for ruta in MODULOS_RETIRADOS:
        respuesta = cliente.get(ruta)
        ok = respuesta.status_code == 404
        print(f"{'OK ' if ok else 'FALLO'} [retirado] {ruta} -> {respuesta.status_code} (esperado 404)")
        if not ok:
            fallos.append(("retirado", ruta, respuesta.status_code, 404))

print()
if fallos:
    print("FALLOS:", fallos)
    raise SystemExit(1)
print("RBAC DE LOS SIETE ROLES OK")
