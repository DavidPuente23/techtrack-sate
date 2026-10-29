"""Matriz de permisos de SATE por rol, módulo y acción.

Los siete roles provienen de la estructura organizacional del PIA. SATE se
limita a seis módulos: acceso (login), panel, activos e historial,
mantenimientos, incidencias y usuarios/roles.

Acciones:
    ver         Consultar listados y fichas.
    crear       Registrar nuevos elementos.
    editar      Modificar elementos existentes.
    administrar Gestionar cuentas: activar/desactivar y restablecer contraseñas.
"""

ROLES = (
    "Administrador General",
    "Dirección General",
    "Administrador de Activos",
    "Administrador de Redes",
    "Desarrollador",
    "Técnico de Soporte",
    "Usuario Solicitante",
)

ROL_ADMIN = "Administrador General"
ROL_DIRECCION = "Dirección General"
ROL_ACTIVOS = "Administrador de Activos"
ROL_REDES = "Administrador de Redes"
ROL_DESARROLLO = "Desarrollador"
ROL_SOPORTE = "Técnico de Soporte"
ROL_USUARIO = "Usuario Solicitante"

ROLES_DESCRIPCION = {
    ROL_ADMIN: "Control total de SATE, incluida la gestión de usuarios y roles.",
    ROL_DIRECCION: "Consulta de indicadores, activos, mantenimientos e incidencias.",
    ROL_ACTIVOS: "Administra el inventario, las asignaciones y los mantenimientos.",
    ROL_REDES: "Atiende incidencias y mantenimientos de infraestructura.",
    ROL_DESARROLLO: "Atiende incidencias de software y consulta el inventario.",
    ROL_SOPORTE: "Registra, atiende y cierra incidencias y mantenimientos.",
    ROL_USUARIO: "Consulta los activos de su área y reporta sus propias incidencias.",
}

MODULOS = (
    {
        "clave": "panel",
        "nombre": "Panel principal",
        "endpoint": "dashboard",
        "endpoints": ("dashboard",),
    },
    {
        "clave": "activos",
        "nombre": "Activos e historial",
        "endpoint": "activos",
        "endpoints": ("activos", "detalle_activo", "nuevo_activo", "editar_activo"),
    },
    {
        "clave": "mantenimientos",
        "nombre": "Mantenimientos",
        "endpoint": "mantenimientos",
        "endpoints": (
            "mantenimientos",
            "nuevo_mantenimiento",
            "editar_mantenimiento",
            "orden_mantenimiento_pdf",
        ),
    },
    {
        "clave": "incidencias",
        "nombre": "Incidencias",
        "endpoint": "incidencias",
        "endpoints": ("incidencias", "nueva_incidencia", "editar_incidencia"),
    },
    {
        "clave": "usuarios",
        "nombre": "Usuarios y roles",
        "endpoint": "usuarios",
        "endpoints": (
            "usuarios",
            "nuevo_usuario",
            "editar_usuario",
            "cambiar_estado_usuario",
            "restablecer_password_usuario",
        ),
    },
)

MODULOS_POR_CLAVE = {modulo["clave"]: modulo for modulo in MODULOS}

# Conjunto de acciones permitidas por rol y módulo.
PERMISOS = {
    ROL_ADMIN: {
        "panel": {"ver"},
        "activos": {"ver", "crear", "editar"},
        "mantenimientos": {"ver", "crear", "editar"},
        "incidencias": {"ver", "crear", "editar"},
        "usuarios": {"ver", "crear", "editar", "administrar"},
    },
    ROL_DIRECCION: {
        "panel": {"ver"},
        "activos": {"ver"},
        "mantenimientos": {"ver"},
        "incidencias": {"ver"},
    },
    ROL_ACTIVOS: {
        "panel": {"ver"},
        "activos": {"ver", "crear", "editar"},
        "mantenimientos": {"ver", "crear", "editar"},
        "incidencias": {"ver"},
    },
    ROL_REDES: {
        "panel": {"ver"},
        "activos": {"ver"},
        "mantenimientos": {"ver", "crear", "editar"},
        "incidencias": {"ver", "crear", "editar"},
    },
    ROL_DESARROLLO: {
        "panel": {"ver"},
        "activos": {"ver"},
        "mantenimientos": {"ver"},
        "incidencias": {"ver", "crear", "editar"},
    },
    ROL_SOPORTE: {
        "panel": {"ver"},
        "activos": {"ver", "editar"},
        "mantenimientos": {"ver", "crear", "editar"},
        "incidencias": {"ver", "crear", "editar"},
    },
    ROL_USUARIO: {
        "panel": {"ver"},
        "activos": {"ver"},
        "incidencias": {"ver", "crear"},
    },
}


def normalizar_rol(rol):
    """Devuelve un rol válido; cualquier valor desconocido se trata como solicitante."""
    return rol if rol in PERMISOS else ROL_USUARIO


def puede(rol, modulo, accion):
    """Indica si un rol puede ejecutar una acción en un módulo."""
    return accion in PERMISOS.get(normalizar_rol(rol), {}).get(modulo, set())


def menu_modulos(rol):
    """Módulos visibles en el menú lateral para el rol indicado."""
    rol = normalizar_rol(rol)
    return [
        {
            "clave": modulo["clave"],
            "nombre": modulo["nombre"],
            "endpoint": modulo["endpoint"],
            "endpoints": modulo["endpoints"],
        }
        for modulo in MODULOS
        if puede(rol, modulo["clave"], "ver")
    ]


def alcance_activos(rol):
    """Alcance de consulta de activos: global o limitado al departamento."""
    return "departamento" if normalizar_rol(rol) == ROL_USUARIO else "global"


def alcance_incidencias(rol):
    """Alcance de consulta de incidencias: global o solo las propias."""
    return "propias" if normalizar_rol(rol) == ROL_USUARIO else "global"


def resumen_permisos():
    """Matriz legible por módulo, útil para pruebas y documentación."""
    return {
        rol: {
            modulo: sorted(PERMISOS.get(rol, {}).get(modulo, set()))
            for modulo in MODULOS_POR_CLAVE
        }
        for rol in ROLES
    }
