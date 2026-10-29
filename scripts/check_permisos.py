"""Valida la matriz de permisos de SATE sin base de datos."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from permisos import (
    MODULOS,
    MODULOS_POR_CLAVE,
    PERMISOS,
    ROLES,
    ROL_ADMIN,
    ROL_DIRECCION,
    ROL_USUARIO,
    alcance_activos,
    alcance_incidencias,
    menu_modulos,
    puede,
)

ACCIONES_VALIDAS = {"ver", "crear", "editar", "administrar"}
MODULOS_ESPERADOS = {"panel", "activos", "mantenimientos", "incidencias", "usuarios"}

fallos = []


def comprobar(condicion, mensaje):
    print(f"{'OK ' if condicion else 'FALLO'} {mensaje}")
    if not condicion:
        fallos.append(mensaje)


comprobar(len(ROLES) == 7, "hay exactamente siete roles")
comprobar(set(PERMISOS) == set(ROLES), "la matriz cubre los siete roles")
comprobar({m["clave"] for m in MODULOS} == MODULOS_ESPERADOS, "SATE expone solo los cinco módulos internos")

for rol in ROLES:
    for modulo, acciones in PERMISOS[rol].items():
        comprobar(modulo in MODULOS_ESPERADOS, f"{rol}: módulo válido {modulo}")
        comprobar(acciones <= ACCIONES_VALIDAS, f"{rol}: acciones válidas en {modulo}")
    comprobar(puede(rol, "panel", "ver"), f"{rol}: puede ver el panel")
    comprobar(not puede(rol, "usuarios", "ver") or rol == ROL_ADMIN, f"{rol}: usuarios solo para administración")

# El administrador general conserva todas las acciones de cada módulo.
ACCIONES_POR_MODULO = {
    "panel": {"ver"},
    "activos": {"ver", "crear", "editar"},
    "mantenimientos": {"ver", "crear", "editar"},
    "incidencias": {"ver", "crear", "editar"},
    "usuarios": {"ver", "crear", "editar", "administrar"},
}
for modulo in MODULOS_ESPERADOS:
    comprobar(
        PERMISOS[ROL_ADMIN].get(modulo, set()) == ACCIONES_POR_MODULO[modulo],
        f"Administrador General: control total en {modulo}",
    )

# Dirección General solo consulta.
for modulo in MODULOS_ESPERADOS - {"usuarios"}:
    comprobar(
        PERMISOS[ROL_DIRECCION].get(modulo, set()) == {"ver"},
        f"Dirección General: solo lectura en {modulo}",
    )
comprobar("usuarios" not in PERMISOS[ROL_DIRECCION], "Dirección General: sin acceso a usuarios")

# Usuario Solicitante: sin mantenimientos ni administración.
comprobar(not puede(ROL_USUARIO, "mantenimientos", "ver"), "Usuario Solicitante: sin mantenimientos")
comprobar(not puede(ROL_USUARIO, "activos", "crear"), "Usuario Solicitante: no crea activos")
comprobar(not puede(ROL_USUARIO, "activos", "editar"), "Usuario Solicitante: no edita activos")
comprobar(puede(ROL_USUARIO, "activos", "ver"), "Usuario Solicitante: consulta activos")
comprobar(puede(ROL_USUARIO, "incidencias", "crear"), "Usuario Solicitante: reporta incidencias")
comprobar(not puede(ROL_USUARIO, "incidencias", "editar"), "Usuario Solicitante: no edita incidencias")

# Alcances.
comprobar(alcance_activos(ROL_USUARIO) == "departamento", "Usuario Solicitante: activos de su departamento")
comprobar(alcance_activos(ROL_ADMIN) == "global", "Administrador: alcance global de activos")
comprobar(alcance_incidencias(ROL_USUARIO) == "propias", "Usuario Solicitante: solo sus incidencias")
comprobar(alcance_incidencias(ROL_ADMIN) == "global", "Administrador: todas las incidencias")

# Menú: solo módulos permitidos y en el orden definido.
menu_usuario = [m["clave"] for m in menu_modulos(ROL_USUARIO)]
comprobar(menu_usuario == ["panel", "activos", "incidencias"], "menú del solicitante sin módulos fuera de alcance")
menu_admin = [m["clave"] for m in menu_modulos(ROL_ADMIN)]
comprobar(menu_admin == list(MODULOS_POR_CLAVE), "menú del administrador con los cinco módulos")

print()
if fallos:
    print(f"FALLOS: {len(fallos)}")
    raise SystemExit(1)
print("MATRIZ DE PERMISOS OK")
