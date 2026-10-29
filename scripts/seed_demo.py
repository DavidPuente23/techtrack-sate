"""Datos de demostración para SATE.

Crea un usuario demo por cada uno de los siete roles del PIA, doce activos
repartidos en los cuatro departamentos, mantenimientos vencidos y próximos,
incidencias en distintos estados e historial de movimientos.

Uso:
    python scripts/seed_demo.py            # crea o refresca los datos demo
    python scripts/seed_demo.py --limpiar  # elimina solo los datos demo

Los datos se identifican por el dominio @demo.techtrack.com y el prefijo
DEMO- en los identificadores, así que se pueden borrar sin tocar datos reales.
No usar estas cuentas en producción.
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from werkzeug.security import generate_password_hash

from app import get_db_connection

PASSWORD_DEMO = "Demo123!"
DOMINIO_DEMO = "@demo.techtrack.com"
PREFIJO = "DEMO-"

USUARIOS = [
    ("Administrador Demo", "admin", "Administrador General", "SIT"),
    ("Laura Méndez", "direccion", "Dirección General", "SIT"),
    ("Carlos Ramírez", "activos", "Administrador de Activos", "SIT"),
    ("Ana Torres", "redes", "Administrador de Redes", "Redes"),
    ("Luis Herrera", "desarrollo", "Desarrollador", "Desarrollo"),
    ("María López", "soporte", "Técnico de Soporte", "Soporte"),
    ("Jorge Salinas", "solicitante", "Usuario Solicitante", "Desarrollo"),
]

ACTIVOS = [
    # identificador, nombre, tipo, marca, modelo, serie, ubicación, responsable, departamento, estado
    ("DEMO-001", "Laptop HP ProBook 450 G9", "Laptop", "HP", "ProBook 450 G9", "SN-DEMO-001", "SIT · Oficina", "Carlos Ramírez", "SIT", "Operativo"),
    ("DEMO-002", "Servidor Dell PowerEdge R750", "Servidor", "Dell", "PowerEdge R750", "SN-DEMO-002", "SIT · Site de servidores", "Carlos Ramírez", "SIT", "Operativo"),
    ("DEMO-003", "Impresora HP LaserJet Pro M404", "Impresora", "HP", "LaserJet Pro M404", "SN-DEMO-003", "SIT · Recepción", "Carlos Ramírez", "SIT", "En Mantenimiento"),
    ("DEMO-004", "Switch Cisco Catalyst 9200", "Otro", "Cisco", "Catalyst 9200", "SN-DEMO-004", "Redes · Rack A", "Ana Torres", "Redes", "Operativo"),
    ("DEMO-005", "Router MikroTik CCR2004", "Otro", "MikroTik", "CCR2004", "SN-DEMO-005", "Redes · Rack A", "Ana Torres", "Redes", "Operativo"),
    ("DEMO-006", "Access Point Ubiquiti UniFi 6 Pro", "Otro", "Ubiquiti", "UniFi 6 Pro", "SN-DEMO-006", "Redes · Piso 2", "Ana Torres", "Redes", "Con Falla"),
    ("DEMO-007", "Laptop Lenovo ThinkPad T14", "Laptop", "Lenovo", "ThinkPad T14", "SN-DEMO-007", "Desarrollo · Mesa 1", "Luis Herrera", "Desarrollo", "Operativo"),
    ("DEMO-008", "Monitor LG UltraWide 34", "Monitor", "LG", "UltraWide 34", "SN-DEMO-008", "Desarrollo · Mesa 2", "Jorge Salinas", "Desarrollo", "Operativo"),
    ("DEMO-009", "Computadora Dell OptiPlex 7090", "Computadora de Escritorio", "Dell", "OptiPlex 7090", "SN-DEMO-009", "Desarrollo · Mesa 3", "Luis Herrera", "Desarrollo", "Operativo"),
    ("DEMO-010", "Laptop Apple MacBook Air M2", "Laptop", "Apple", "MacBook Air M2", "SN-DEMO-010", "Soporte · Mesa 1", "María López", "Soporte", "Operativo"),
    ("DEMO-011", "Monitor Samsung 27", "Monitor", "Samsung", "S27", "SN-DEMO-011", "Soporte · Mesa 2", "María López", "Soporte", "Operativo"),
    ("DEMO-012", "Impresora Epson EcoTank L3250", "Impresora", "Epson", "EcoTank L3250", "SN-DEMO-012", "Soporte · Almacén", "María López", "Soporte", "Baja"),
]

# activo, tipo, descripción, días respecto a hoy, estado, responsable, observaciones
MANTENIMIENTOS = [
    ("DEMO-001", "Preventivo", "Limpieza interna y revisión de batería", -5, "Pendiente", "María López", "Equipo con dos años de uso."),
    ("DEMO-004", "Preventivo", "Actualización de firmware del switch", -2, "Pendiente", "Ana Torres", "Ventana de mantenimiento nocturna."),
    ("DEMO-007", "Preventivo", "Mantenimiento preventivo trimestral", 3, "Pendiente", "María López", None),
    ("DEMO-002", "Correctivo", "Reemplazo de ventilador del servidor", 6, "Pendiente", "Carlos Ramírez", "Se detectó ruido anómalo."),
    ("DEMO-005", "Correctivo", "Revisión del puerto WAN principal", 0, "En proceso", "Ana Torres", "Enlace redundante activo."),
    ("DEMO-009", "Preventivo", "Limpieza de polvo y cambio de pasta térmica", -20, "Finalizado", "María López", "Equipo entregado en buen estado."),
]

# activo, descripción, prioridad, estado, responsable, días de registro, diagnóstico, resolución, solicitante, días de cierre
INCIDENCIAS = [
    ("DEMO-006", "El access point no responde y deja sin red al piso 2", "Crítica", "Nueva", None, -2, None, None, "solicitante", None),
    ("DEMO-003", "Atasco de papel recurrente en la impresora", "Alta", "Nueva", None, -2, None, None, "solicitante", None),
    ("DEMO-001", "La laptop se apaga sola al desconectar el cargador", "Media", "Asignada", "María López", -3, "Posible falla de batería.", None, "solicitante", None),
    ("DEMO-008", "El monitor parpadea de forma intermitente", "Baja", "En proceso", "María López", -4, "Se revisa cable DisplayPort.", None, "solicitante", None),
    ("DEMO-010", "Solicitud de instalación de cliente VPN", "Baja", "Resuelta", "Luis Herrera", -6, "Equipo sin cliente corporativo.", "Cliente VPN instalado y probado.", "solicitante", -5),
]

# activo, tipo de movimiento, detalle, días de antigüedad
HISTORIAL = [
    ("DEMO-001", "Alta", "Registro inicial del activo en SATE.", -40),
    ("DEMO-001", "Asignación", "Asignado a Carlos Ramírez en SIT · Oficina.", -38),
    ("DEMO-003", "Mantenimiento", "Enviado a mantenimiento correctivo por atascos de papel.", -6),
    ("DEMO-007", "Alta", "Registro inicial del activo en SATE.", -30),
    ("DEMO-012", "Baja", "Baja por equipo obsoleto y sin refacciones disponibles.", -15),
]


def conectar():
    return get_db_connection()


def limpiar(cursor):
    """Elimina únicamente los datos creados por este script."""
    cursor.execute(
        "SELECT id FROM activos WHERE identificador LIKE %s", (f"{PREFIJO}%",)
    )
    ids_activos = [fila[0] for fila in cursor.fetchall()]
    cursor.execute(
        "SELECT id FROM usuarios WHERE email LIKE %s", (f"%{DOMINIO_DEMO}",)
    )
    ids_usuarios = [fila[0] for fila in cursor.fetchall()]

    if ids_activos:
        marcas = ",".join(["%s"] * len(ids_activos))
        cursor.execute(
            f"SELECT id FROM incidencias WHERE activo_id IN ({marcas})", ids_activos
        )
        ids_incidencias = [fila[0] for fila in cursor.fetchall()]
        cursor.execute(
            f"SELECT id FROM mantenimientos WHERE activo_id IN ({marcas})", ids_activos
        )
        ids_mantenimientos = [fila[0] for fila in cursor.fetchall()]

        cursor.execute(
            f"DELETE FROM incidencias WHERE activo_id IN ({marcas})", ids_activos
        )
        cursor.execute(
            f"DELETE FROM mantenimientos WHERE activo_id IN ({marcas})", ids_activos
        )
        cursor.execute(
            f"DELETE FROM historial_activos WHERE activo_id IN ({marcas})", ids_activos
        )
        cursor.execute(
            f"DELETE FROM auditoria WHERE entidad = 'Activo' AND entidad_id IN ({marcas})",
            ids_activos,
        )
        if ids_incidencias:
            marcas_inc = ",".join(["%s"] * len(ids_incidencias))
            cursor.execute(
                f"DELETE FROM auditoria WHERE entidad = 'Incidencia' AND entidad_id IN ({marcas_inc})",
                ids_incidencias,
            )
        if ids_mantenimientos:
            marcas_mant = ",".join(["%s"] * len(ids_mantenimientos))
            cursor.execute(
                f"DELETE FROM auditoria WHERE entidad = 'Mantenimiento' AND entidad_id IN ({marcas_mant})",
                ids_mantenimientos,
            )

    if ids_usuarios:
        marcas = ",".join(["%s"] * len(ids_usuarios))
        cursor.execute(
            f"DELETE FROM auditoria WHERE usuario_id IN ({marcas})", ids_usuarios
        )
        cursor.execute(
            f"DELETE FROM usuarios WHERE id IN ({marcas})", ids_usuarios
        )

    if ids_activos:
        marcas = ",".join(["%s"] * len(ids_activos))
        cursor.execute(f"DELETE FROM activos WHERE id IN ({marcas})", ids_activos)

    return len(ids_usuarios), len(ids_activos)


def sembrar(cursor):
    cursor.execute("SELECT id, nombre FROM departamentos")
    departamentos = {nombre: id_ for id_, nombre in cursor.fetchall()}
    cursor.execute("SELECT id, nombre FROM roles")
    roles = {nombre: id_ for id_, nombre in cursor.fetchall()}

    faltantes = [
        nombre
        for _, _, rol, depto in USUARIOS
        for nombre in (rol, depto)
        if nombre not in roles and nombre not in departamentos
    ]
    if faltantes:
        raise SystemExit(
            "Faltan roles o departamentos en la base: " + ", ".join(sorted(set(faltantes)))
        )

    hash_password = generate_password_hash(PASSWORD_DEMO)
    ids_usuarios = {}
    for nombre, alias, rol, depto in USUARIOS:
        email = f"{alias}{DOMINIO_DEMO}"
        cursor.execute(
            """
            INSERT INTO usuarios
                (nombre, email, password, departamento_id, rol_id, activo, tema,
                 rol, debe_cambiar_password)
            VALUES (%s, %s, %s, %s, %s, 1, 'blue', %s, 0)
            """,
            (
                nombre,
                email,
                hash_password,
                departamentos[depto],
                roles[rol],
                rol,
            ),
        )
        ids_usuarios[alias] = cursor.lastrowid

    ids_activos = {}
    for fila in ACTIVOS:
        (
            identificador,
            nombre,
            tipo,
            marca,
            modelo,
            serie,
            ubicacion,
            responsable,
            depto,
            estado,
        ) = fila
        cursor.execute(
            """
            INSERT INTO activos
                (identificador, nombre, tipo, marca, modelo, numero_serie,
                 ubicacion, responsable, departamento_id, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                identificador,
                nombre,
                tipo,
                marca,
                modelo,
                serie,
                ubicacion,
                responsable,
                departamentos[depto],
                estado,
            ),
        )
        ids_activos[identificador] = cursor.lastrowid

    ahora = datetime.now()
    for identificador, tipo, descripcion, dias, estado, responsable, observaciones in MANTENIMIENTOS:
        fecha = (ahora + timedelta(days=dias)).date()
        fecha_finalizacion = ahora + timedelta(days=dias) if estado == "Finalizado" else None
        cursor.execute(
            """
            INSERT INTO mantenimientos
                (activo_id, tipo, descripcion, fecha_programada, responsable,
                 estado, observaciones, fecha_finalizacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                ids_activos[identificador],
                tipo,
                descripcion,
                fecha,
                responsable,
                estado,
                observaciones,
                fecha_finalizacion,
            ),
        )

    for (
        identificador,
        descripcion,
        prioridad,
        estado,
        responsable,
        dias_registro,
        diagnostico,
        resolucion,
        alias_solicitante,
        dias_cierre,
    ) in INCIDENCIAS:
        fecha_registro = ahora + timedelta(days=dias_registro)
        fecha_cierre = ahora + timedelta(days=dias_cierre) if dias_cierre else None
        cursor.execute(
            """
            INSERT INTO incidencias
                (activo_id, descripcion, prioridad, responsable, estado,
                 diagnostico, resolucion, solicitante_id, fecha_registro,
                 fecha_cierre)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                ids_activos[identificador],
                descripcion,
                prioridad,
                responsable,
                estado,
                diagnostico,
                resolucion,
                ids_usuarios.get(alias_solicitante),
                fecha_registro,
                fecha_cierre,
            ),
        )

    for identificador, tipo_movimiento, detalle, dias in HISTORIAL:
        cursor.execute(
            """
            INSERT INTO historial_activos
                (activo_id, tipo_movimiento, detalle, usuario_id, fecha)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                ids_activos[identificador],
                tipo_movimiento,
                detalle,
                ids_usuarios["activos"],
                ahora + timedelta(days=dias),
            ),
        )

    return len(ids_usuarios), len(ids_activos)


def main():
    limpiar_solo = "--limpiar" in sys.argv[1:]
    conn = conectar()
    cursor = conn.cursor()
    try:
        usuarios_borrados, activos_borrados = limpiar(cursor)
        if limpiar_solo:
            conn.commit()
            print(
                f"Datos demo eliminados: {usuarios_borrados} usuario(s) "
                f"y {activos_borrados} activo(s)."
            )
            return
        usuarios_creados, activos_creados = sembrar(cursor)
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    print("Datos demo listos.")
    print(f"  Usuarios: {usuarios_creados} (contraseña: {PASSWORD_DEMO})")
    print(f"  Activos: {activos_creados}")
    print(f"  Mantenimientos: {len(MANTENIMIENTOS)}")
    print(f"  Incidencias: {len(INCIDENCIAS)}")
    print()
    print("Cuentas:")
    for nombre, alias, rol, _ in USUARIOS:
        email = alias + DOMINIO_DEMO
        print(f"  {email:38} {rol:26} {nombre}")
    print()
    print("Para eliminar solo estos datos: python scripts/seed_demo.py --limpiar")


if __name__ == "__main__":
    main()
