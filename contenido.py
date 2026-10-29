"""Contenido institucional de TechTrack Solutions.

Fuente base: PIA "TechTrack Solutions: estructura organizacional, políticas
y perfiles de puesto" (octubre de 2026).

Los apartados marcados como ampliados desarrollan la información del PIA
para el sitio web; no se presentan como texto literal del documento original.
"""

EMPRESA = {
    "nombre": "TechTrack Solutions",
    "giro": (
        "Tecnología: desarrollo de software para la gestión y trazabilidad "
        "de activos tecnológicos."
    ),
    "descripcion": (
        "TechTrack Solutions es una empresa de tecnología que ofrece soluciones "
        "para que las organizaciones tengan control y trazabilidad de sus equipos. "
        "Su producto SATE permite registrar cada activo con un identificador único, "
        "dar seguimiento a responsables y ubicaciones, llevar el historial de "
        "mantenimientos y reparaciones, y generar alertas y reportes que apoyan "
        "la toma de decisiones."
    ),
    "propuesta": (
        "Pasar de un control reactivo a uno preventivo, con historial completo, "
        "alertas y reportes."
    ),
    "clientes": (
        "Organizaciones que administran equipos de cómputo, redes y otros activos "
        "tecnológicos."
    ),
    "mision": (
        "Brindar soluciones tecnológicas para la gestión eficiente y preventiva de "
        "activos tecnológicos, facilitando la toma de decisiones y la organización "
        "de las instituciones."
    ),
    "vision": (
        "Ser reconocidos por soluciones innovadoras en administración y trazabilidad "
        "de activos tecnológicos, ayudando a optimizar recursos y mejorar la gestión "
        "de equipos."
    ),
    "objetivos": [
        "Registrar y organizar los activos tecnológicos de la organización.",
        "Facilitar el seguimiento de equipos, responsables y ubicaciones.",
        "Mantener el historial de mantenimientos y reparaciones.",
        "Identificar equipos con fallas o con mantenimiento próximo.",
        "Generar reportes e indicadores para apoyar la toma de decisiones.",
        "Reducir la pérdida de información y los tiempos de atención.",
    ],
    "metas": [
        "Interfaz sencilla y amigable para todos los usuarios.",
        "Registro y consulta rápida de activos.",
        "Identificadores únicos para cada equipo.",
        "Módulo de mantenimiento e incidencias.",
        "Alertas para mantenimientos próximos.",
        "Historial completo para un control total de los activos.",
    ],
}

SATE = {
    "nombre": "SATE",
    "significado": "Sistema de Administración y Trazabilidad de Equipos",
    "descripcion": (
        "Plataforma web para registrar, controlar y monitorear equipos y activos "
        "tecnológicos. Centraliza el inventario, los mantenimientos y las incidencias "
        "para que la organización pase de un control reactivo a uno preventivo."
    ),
    "problema": (
        "Muchas organizaciones no saben con certeza dónde están sus equipos, quién "
        "los tiene, cuándo les toca mantenimiento o qué fallas se repiten. Esa "
        "información suele estar dispersa en hojas de cálculo, correos y memoria "
        "del personal, lo que provoca pérdidas de tiempo, compras duplicadas y "
        "decisiones sin datos."
    ),
    "beneficios": [
        "Inventario centralizado con identificador único por equipo.",
        "Trazabilidad de responsables, ubicaciones y cambios de estado.",
        "Mantenimientos programados y alertas de vencimiento.",
        "Incidencias con prioridad, responsable, diagnóstico y solución.",
        "Indicadores reales para Dirección General y jefaturas.",
        "Acceso controlado por roles y registro de auditoría.",
    ],
    "modulos": [
        {
            "nombre": "Panel principal",
            "descripcion": (
                "Resumen de activos, equipos operativos, mantenimientos próximos "
                "e incidencias abiertas, con accesos directos a las tareas frecuentes."
            ),
        },
        {
            "nombre": "Activos e historial",
            "descripcion": (
                "Alta, consulta, edición y baja lógica de equipos. Cada cambio de "
                "responsable, ubicación o estado queda registrado en una línea de tiempo."
            ),
        },
        {
            "nombre": "Mantenimientos",
            "descripcion": (
                "Programación de mantenimientos preventivos y correctivos, control "
                "de estados y registro de los trabajos realizados."
            ),
        },
        {
            "nombre": "Incidencias",
            "descripcion": (
                "Registro y seguimiento de fallas o solicitudes, con prioridad, "
                "responsable, diagnóstico, solución y cierre."
            ),
        },
        {
            "nombre": "Usuarios y roles",
            "descripcion": (
                "Administración de cuentas, departamentos y permisos de acceso a "
                "cada módulo del sistema."
            ),
        },
    ],
}

DEPARTAMENTOS = {
    "sit": {
        "slug": "sit",
        "nombre": "SIT",
        "nombre_largo": "Administración y gestión de activos tecnológicos",
        "funcion": (
            "Administrar y gestionar el ciclo de vida de los activos tecnológicos "
            "de la organización, desde su alta hasta su baja."
        ),
        "objetivo": (
            "Mantener un inventario confiable, actualizado y trazable de todos los "
            "equipos y sus responsables."
        ),
        "funciones": [
            "Registrar y mantener actualizado el inventario de activos tecnológicos.",
            "Asignar, reasignar y dar de baja equipos con resguardo documentado.",
            "Mantener la configuración, garantías y documentación de cada equipo.",
            "Coordinar los mantenimientos preventivos y correctivos.",
            "Conciliar el inventario físico con la información de SATE.",
            "Dar seguimiento a proveedores, contratos y garantías.",
        ],
        "perfil": "administrador-activos",
        "politicas_responsable": [
            "gestion-activos",
            "gestion-configuracion",
            "gestion-proveedores",
        ],
        "politicas_participa": [
            "gestion-cambios",
            "gestion-continuidad",
            "seguridad-informacion",
        ],
    },
    "redes": {
        "slug": "redes",
        "nombre": "Redes",
        "nombre_largo": "Administración y seguridad de la infraestructura de red",
        "funcion": (
            "Administrar, monitorear y proteger la infraestructura de red de la "
            "organización."
        ),
        "objetivo": (
            "Asegurar que la red sea segura, tenga capacidad suficiente y esté "
            "disponible para usuarios y sistemas, incluido SATE."
        ),
        "funciones": [
            "Configurar y mantener switches, routers, puntos de acceso y firewall.",
            "Monitorear el tráfico, la capacidad y la disponibilidad de la red.",
            "Administrar accesos, cuentas, permisos de red y conexiones remotas.",
            "Respaldar configuraciones y mantener esquemas de redundancia.",
            "Atender incidentes de red escalados por Soporte.",
            "Documentar cambios, vulnerabilidades y eventos de seguridad.",
        ],
        "perfil": "administrador-redes",
        "politicas_responsable": [
            "gestion-capacidad",
            "gestion-disponibilidad",
            "gestion-continuidad",
            "seguridad-informacion",
        ],
        "politicas_participa": [
            "gestion-configuracion",
            "gestion-cambios",
            "gestion-incidentes",
            "gestion-problemas",
        ],
    },
    "desarrollo": {
        "slug": "desarrollo",
        "nombre": "Desarrollo",
        "nombre_largo": "Desarrollo y mantenimiento del sistema SATE",
        "funcion": (
            "Diseñar, programar, probar y mantener el sistema SATE, el producto "
            "principal de la empresa."
        ),
        "objetivo": (
            "Entregar un sistema estable, seguro y alineado con las metas de "
            "desarrollo y las necesidades de los usuarios."
        ),
        "funciones": [
            "Analizar requerimientos y proponer soluciones técnicas.",
            "Programar, probar y mantener los módulos del sistema.",
            "Administrar la base de datos y las migraciones.",
            "Aplicar control de versiones y documentar el código.",
            "Corregir errores y atender incidentes de software.",
            "Implementar roles, autenticación, respaldos y seguridad.",
        ],
        "perfil": "desarrollador-sate",
        "politicas_responsable": ["gestion-cambios"],
        "politicas_participa": [
            "gestion-configuracion",
            "gestion-disponibilidad",
            "gestion-incidentes",
            "gestion-problemas",
            "gestion-continuidad",
            "seguridad-informacion",
        ],
    },
    "soporte": {
        "slug": "soporte",
        "nombre": "Soporte",
        "nombre_largo": "Atención de incidentes y solicitudes de los usuarios",
        "funcion": (
            "Atender, resolver y dar seguimiento a los incidentes y solicitudes de "
            "los usuarios sobre equipos, servicios y el sistema SATE."
        ),
        "objetivo": (
            "Restablecer el servicio lo antes posible y mantener informados a los "
            "usuarios, escalando correctamente lo que no pueda resolverse en el área."
        ),
        "funciones": [
            "Recibir y registrar incidentes y solicitudes de los usuarios.",
            "Diagnosticar y resolver fallas de equipos, software y uso de SATE.",
            "Escalar los casos que requieran a Redes, Desarrollo o SIT.",
            "Dar seguimiento a cada caso hasta su cierre y confirmar la solución.",
            "Identificar incidentes recurrentes y reportarlos como problemas.",
            "Actualizar en SATE el estado de los equipos atendidos.",
            "Orientar a los usuarios y mantener una base de conocimiento.",
        ],
        "perfil": "tecnico-soporte",
        "politicas_responsable": ["gestion-incidentes", "gestion-problemas"],
        "politicas_participa": [
            "gestion-activos",
            "gestion-cambios",
            "gestion-disponibilidad",
            "seguridad-informacion",
        ],
    },
}

POLITICAS = {
    "gestion-activos": {
        "slug": "gestion-activos",
        "numero": 1,
        "nombre": "Gestión de activos",
        "nombre_completo": "Política de gestión de activos",
        "objetivo": (
            "Mantener un inventario confiable, actualizado y trazable de todos los "
            "activos tecnológicos, con identificador único, responsable, ubicación "
            "y estado."
        ),
        "alcance": (
            "Equipos de cómputo, servidores, monitores, impresoras, dispositivos de "
            "red, componentes y cualquier activo tecnológico que la organización "
            "registre en SATE."
        ),
        "descripcion": (
            "Regula el alta, identificación, asignación, reasignación, resguardo, "
            "actualización y baja de los activos, así como la conservación de su "
            "historial."
        ),
        "responsable": "sit",
        "participantes": ["soporte"],
        "reglas": [
            "Todo activo debe registrarse en SATE antes de ser entregado a un usuario o área.",
            "El identificador único es obligatorio y no se reutiliza, incluso si el equipo se da de baja.",
            "Todo cambio de responsable, ubicación, departamento o estado debe quedar en el historial.",
            "La baja se maneja como cambio de estado; el registro histórico no se elimina.",
            "El inventario físico se concilia periódicamente con la información de SATE.",
            "Los equipos con información sensible requieren resguardo y baja segura.",
        ],
        "procedimiento": [
            "Solicitar el alta y capturar los datos mínimos: nombre, tipo, marca, modelo, número de serie, ubicación y departamento.",
            "Generar o asignar el identificador único y registrar el alta en el historial.",
            "Asignar el equipo a un responsable y documentar la entrega.",
            "Actualizar ubicación, responsable o estado cuando ocurra un cambio.",
            "Realizar inventarios físicos y conciliar diferencias.",
            "Dar de baja el activo conservando su historial y verificando el destino de la información.",
        ],
        "responsabilidades": [
            {"area": "sit", "rol": "Responsable", "accion": "Registrar, actualizar y conciliar el inventario; coordinar asignaciones y bajas."},
            {"area": "soporte", "rol": "Participa", "accion": "Informar a SIT los cambios de estado detectados durante la atención."},
            {"area": "direccion", "rol": "Autoriza", "accion": "Autorizar bajas de activos críticos o con información sensible."},
        ],
        "relacion_sate": (
            "Se implementa en el módulo Activos e historial: identificador único, "
            "ficha del equipo, estados, asignación y bitácora de cambios."
        ),
        "origen": "PIA",
        "ampliado": True,
    },
    "gestion-configuracion": {
        "slug": "gestion-configuracion",
        "numero": 2,
        "nombre": "Gestión de configuración",
        "nombre_completo": "Política de gestión de configuración",
        "objetivo": (
            "Mantener actualizada la información de configuración de equipos, "
            "sistemas y componentes para conocer su estado real y facilitar su soporte."
        ),
        "alcance": (
            "Equipos registrados, software instalado, versiones, parámetros, "
            "componentes y documentación técnica."
        ),
        "descripcion": (
            "Regula la captura y actualización de la configuración de cada activo y "
            "de los entornos que soportan los servicios."
        ),
        "responsable": "sit",
        "participantes": ["redes", "desarrollo"],
        "reglas": [
            "Cada activo debe tener una ficha de configuración mínima.",
            "Los cambios de hardware, software o parámetros deben documentarse.",
            "Las versiones de sistemas y aplicaciones deben identificarse.",
            "La configuración se revisa antes de un cambio o mantenimiento.",
            "La documentación debe estar disponible para Soporte, Redes y Desarrollo.",
        ],
        "procedimiento": [
            "Registrar la configuración inicial del activo.",
            "Documentar componentes, software y versiones.",
            "Actualizar la ficha cuando se instale, retire o modifique un componente.",
            "Revisar la configuración antes de aplicar cambios.",
            "Conservar la documentación y el historial de modificaciones.",
        ],
        "responsabilidades": [
            {"area": "sit", "rol": "Responsable", "accion": "Mantener la configuración de equipos y componentes."},
            {"area": "redes", "rol": "Participa", "accion": "Documentar la configuración de la infraestructura de red."},
            {"area": "desarrollo", "rol": "Participa", "accion": "Documentar la configuración de entornos y versiones de SATE."},
        ],
        "relacion_sate": (
            "Se refleja en los datos técnicos del activo y en el historial; la "
            "configuración detallada queda como fase posterior."
        ),
        "origen": "PIA",
        "ampliado": True,
    },
    "gestion-cambios": {
        "slug": "gestion-cambios",
        "numero": 3,
        "nombre": "Gestión de cambios",
        "nombre_completo": "Política de gestión de cambios",
        "objetivo": (
            "Registrar, evaluar y autorizar los cambios realizados a equipos o "
            "sistemas para reducir riesgos y evitar interrupciones."
        ),
        "alcance": (
            "Cambios de hardware, software, configuración, ubicación, responsables "
            "y versiones de SATE."
        ),
        "descripcion": (
            "Regula el ciclo de vida de un cambio: solicitud, evaluación de impacto, "
            "autorización, ejecución, verificación y cierre."
        ),
        "responsable": "desarrollo",
        "participantes": ["sit", "redes", "soporte"],
        "reglas": [
            "Ningún cambio significativo se aplica sin registro y autorización.",
            "Todo cambio debe evaluar impacto y riesgo.",
            "Los cambios de SATE se prueban antes de liberarse.",
            "Debe existir un plan de reversión cuando el cambio sea crítico.",
            "El cambio se documenta en el historial del activo o en la bitácora correspondiente.",
        ],
        "procedimiento": [
            "Registrar la solicitud y el motivo.",
            "Evaluar impacto, riesgo y áreas afectadas.",
            "Autorizar el cambio y definir la ventana de ejecución.",
            "Ejecutar, probar y verificar el resultado.",
            "Documentar el cierre y, si aplica, la reversión.",
        ],
        "responsabilidades": [
            {"area": "desarrollo", "rol": "Responsable", "accion": "Liderar cambios de software y versiones de SATE."},
            {"area": "sit", "rol": "Participa", "accion": "Registrar cambios de equipos, ubicación o componentes."},
            {"area": "redes", "rol": "Participa", "accion": "Autorizar y documentar cambios de infraestructura."},
            {"area": "soporte", "rol": "Participa", "accion": "Registrar cambios realizados durante una reparación."},
        ],
        "relacion_sate": (
            "En la primera versión se documenta en el historial y las observaciones; "
            "el módulo formal de cambios queda para fase 2."
        ),
        "origen": "PIA",
        "ampliado": True,
    },
    "gestion-capacidad": {
        "slug": "gestion-capacidad",
        "numero": 4,
        "nombre": "Gestión de capacidad",
        "nombre_completo": "Política de gestión de capacidad",
        "objetivo": (
            "Asegurar que los recursos tecnológicos tengan capacidad suficiente para "
            "las necesidades actuales y futuras."
        ),
        "alcance": (
            "Ancho de banda, puertos, servidores, almacenamiento y recursos de los "
            "servicios tecnológicos."
        ),
        "descripcion": (
            "Regula el monitoreo, la proyección y la ampliación de la capacidad de "
            "la infraestructura."
        ),
        "responsable": "redes",
        "participantes": [],
        "reglas": [
            "Monitorear de forma periódica los recursos críticos.",
            "Definir umbrales de alerta.",
            "Proyectar el crecimiento con base en el uso real.",
            "Documentar las ampliaciones y su justificación.",
            "Coordinar con Dirección General las inversiones.",
        ],
        "procedimiento": [
            "Identificar los recursos críticos.",
            "Medir el uso y la tendencia.",
            "Comparar con los umbrales y la capacidad disponible.",
            "Proponer la ampliación o el ajuste.",
            "Implementar y verificar el resultado.",
        ],
        "responsabilidades": [
            {"area": "redes", "rol": "Responsable", "accion": "Monitorear y planear la capacidad de red y servidores."},
            {"area": "direccion", "rol": "Autoriza", "accion": "Autorizar las inversiones necesarias."},
        ],
        "relacion_sate": (
            "El panel puede apoyar con indicadores de activos y mantenimientos; el "
            "monitoreo de red se integra en fase 2."
        ),
        "origen": "PIA",
        "ampliado": True,
    },
    "gestion-disponibilidad": {
        "slug": "gestion-disponibilidad",
        "numero": 5,
        "nombre": "Gestión de disponibilidad",
        "nombre_completo": "Política de gestión de disponibilidad",
        "objetivo": (
            "Procurar que los equipos, sistemas y servicios estén disponibles cuando "
            "se necesiten."
        ),
        "alcance": "Servicios tecnológicos, red, SATE y equipos críticos.",
        "descripcion": (
            "Regula la disponibilidad, el monitoreo, la atención de fallas y la "
            "comunicación a los usuarios."
        ),
        "responsable": "redes",
        "participantes": ["desarrollo", "soporte"],
        "reglas": [
            "Definir horarios y niveles de servicio.",
            "Monitorear los servicios críticos.",
            "Atender fallas con prioridad según su impacto.",
            "Informar a los usuarios sobre las interrupciones.",
            "Registrar métricas de disponibilidad.",
        ],
        "procedimiento": [
            "Identificar los servicios y sus horarios.",
            "Monitorear la disponibilidad.",
            "Registrar las interrupciones.",
            "Restablecer el servicio.",
            "Analizar causas y métricas.",
        ],
        "responsabilidades": [
            {"area": "redes", "rol": "Responsable", "accion": "Mantener la red y los servicios disponibles."},
            {"area": "desarrollo", "rol": "Participa", "accion": "Diseñar SATE para una alta disponibilidad."},
            {"area": "soporte", "rol": "Participa", "accion": "Restablecer servicios y comunicar a los usuarios."},
        ],
        "relacion_sate": (
            "Se apoya en las incidencias y los mantenimientos; las métricas "
            "avanzadas quedan para fase 2."
        ),
        "origen": "PIA",
        "ampliado": True,
    },
    "gestion-incidentes": {
        "slug": "gestion-incidentes",
        "numero": 6,
        "nombre": "Gestión de incidentes",
        "nombre_completo": "Política de gestión de incidentes",
        "objetivo": (
            "Registrar, atender y dar seguimiento a las fallas o solicitudes que "
            "afecten los servicios tecnológicos."
        ),
        "alcance": "Incidentes de equipos, software, red y uso de SATE.",
        "descripcion": (
            "Regula el registro, la clasificación, la asignación, el diagnóstico, "
            "la solución, el cierre y la comunicación."
        ),
        "responsable": "soporte",
        "participantes": ["redes", "desarrollo"],
        "reglas": [
            "Todo incidente se registra con descripción, prioridad y solicitante.",
            "La prioridad se asigna según impacto y urgencia.",
            "Cada caso tiene un responsable y seguimiento.",
            "El cierre requiere diagnóstico y solución.",
            "Los casos que excedan el alcance se escalan.",
            "El usuario confirma la solución.",
        ],
        "procedimiento": [
            "Registrar el incidente.",
            "Clasificar y priorizar.",
            "Asignar responsable.",
            "Diagnosticar y resolver.",
            "Documentar la solución y cerrar.",
            "Escalar si no se resuelve dentro del alcance.",
        ],
        "responsabilidades": [
            {"area": "soporte", "rol": "Responsable", "accion": "Registrar, diagnosticar, atender y cerrar los casos."},
            {"area": "redes", "rol": "Participa", "accion": "Atender incidentes de red escalados."},
            {"area": "desarrollo", "rol": "Participa", "accion": "Atender incidentes de software."},
        ],
        "relacion_sate": (
            "Módulo Incidencias: estados, prioridad, responsable, diagnóstico, "
            "solución y fecha de cierre."
        ),
        "origen": "PIA",
        "ampliado": True,
    },
    "gestion-problemas": {
        "slug": "gestion-problemas",
        "numero": 7,
        "nombre": "Gestión de problemas",
        "nombre_completo": "Política de gestión de problemas",
        "objetivo": (
            "Identificar las causas de los incidentes recurrentes y aplicar "
            "soluciones permanentes."
        ),
        "alcance": (
            "Incidentes repetitivos, fallas crónicas y problemas de infraestructura "
            "o software."
        ),
        "descripcion": (
            "Regula el análisis de tendencias, la causa raíz, la solución permanente "
            "y la base de conocimiento."
        ),
        "responsable": "soporte",
        "participantes": ["redes", "desarrollo"],
        "reglas": [
            "Identificar los incidentes recurrentes.",
            "Analizar la causa raíz.",
            "Definir una solución permanente y un responsable.",
            "Documentar la solución en la base de conocimiento.",
            "Verificar que el problema no se repita.",
        ],
        "procedimiento": [
            "Detectar la recurrencia.",
            "Abrir el análisis del problema.",
            "Investigar la causa raíz.",
            "Implementar la solución.",
            "Verificar y cerrar.",
        ],
        "responsabilidades": [
            {"area": "soporte", "rol": "Responsable", "accion": "Identificar y canalizar los problemas recurrentes."},
            {"area": "redes", "rol": "Participa", "accion": "Analizar las causas de red."},
            {"area": "desarrollo", "rol": "Participa", "accion": "Corregir las causas de software."},
        ],
        "relacion_sate": (
            "En la primera versión se documenta en el diagnóstico y la solución de "
            "las incidencias; el módulo independiente queda para fase 2."
        ),
        "origen": "PIA",
        "ampliado": True,
    },
    "gestion-continuidad": {
        "slug": "gestion-continuidad",
        "numero": 8,
        "nombre": "Gestión de continuidad",
        "nombre_completo": "Política de gestión de continuidad",
        "objetivo": (
            "Establecer medidas para mantener o recuperar los servicios tecnológicos "
            "ante fallas o interrupciones."
        ),
        "alcance": "Activos críticos, red, SATE, base de datos y respaldos.",
        "descripcion": (
            "Regula la identificación de activos críticos, los respaldos, la "
            "redundancia, el plan de recuperación y sus pruebas."
        ),
        "responsable": "redes",
        "participantes": ["sit", "desarrollo"],
        "reglas": [
            "Identificar los activos y servicios críticos.",
            "Realizar respaldos periódicos.",
            "Mantener configuraciones de respaldo.",
            "Documentar el plan de recuperación.",
            "Probar la restauración.",
            "Revisar el plan después de un incidente.",
        ],
        "procedimiento": [
            "Identificar la criticidad de los servicios.",
            "Definir respaldos y redundancia.",
            "Documentar el plan.",
            "Probar la recuperación.",
            "Actualizar y mejorar el plan.",
        ],
        "responsabilidades": [
            {"area": "redes", "rol": "Responsable", "accion": "Liderar la continuidad de la infraestructura."},
            {"area": "sit", "rol": "Participa", "accion": "Identificar activos críticos y equipos de respaldo."},
            {"area": "desarrollo", "rol": "Participa", "accion": "Respaldar el código y la base de datos."},
        ],
        "relacion_sate": (
            "Se implementan respaldos de la base de datos y del código; el módulo "
            "de continuidad queda para fase 2."
        ),
        "origen": "PIA",
        "ampliado": True,
    },
    "seguridad-informacion": {
        "slug": "seguridad-informacion",
        "numero": 9,
        "nombre": "Seguridad de la información",
        "nombre_completo": "Política de seguridad de la información",
        "objetivo": (
            "Proteger los activos y la información mediante controles de acceso, "
            "confidencialidad, integridad y disponibilidad."
        ),
        "alcance": "Usuarios, equipos, sistemas, base de datos, red y documentación.",
        "descripcion": (
            "Regula el acceso, la gestión de cuentas, la protección de datos, la "
            "seguridad de la red y la respuesta a incidentes de seguridad."
        ),
        "responsable": "redes",
        "participantes": ["sit", "desarrollo", "soporte"],
        "reglas": [
            "Aplicar el principio de mínimo privilegio.",
            "Usar contraseñas robustas y cambiarlas periódicamente.",
            "Proteger la autenticación y las sesiones.",
            "Resguardar la información sensible.",
            "Registrar accesos y cambios relevantes.",
            "Reportar incidentes de seguridad.",
            "Realizar la baja segura de equipos y cuentas.",
        ],
        "procedimiento": [
            "Clasificar la información.",
            "Definir roles y permisos.",
            "Aplicar controles técnicos.",
            "Monitorear y auditar.",
            "Responder a incidentes.",
            "Revisar y mejorar los controles.",
        ],
        "responsabilidades": [
            {"area": "redes", "rol": "Responsable", "accion": "Liderar la seguridad de la infraestructura."},
            {"area": "sit", "rol": "Participa", "accion": "Resguardo y baja segura de equipos."},
            {"area": "desarrollo", "rol": "Participa", "accion": "Roles, autenticación y protección de datos en SATE."},
            {"area": "soporte", "rol": "Participa", "accion": "Verificar la identidad y reportar incidentes."},
        ],
        "relacion_sate": (
            "Login, control de acceso por roles, CSRF, sesiones, auditoría y respaldos."
        ),
        "origen": "PIA",
        "ampliado": True,
    },
    "gestion-proveedores": {
        "slug": "gestion-proveedores",
        "numero": 10,
        "nombre": "Gestión de proveedores",
        "nombre_completo": "Política de gestión de proveedores",
        "objetivo": (
            "Controlar y dar seguimiento a los proveedores que proporcionan equipos, "
            "software, mantenimiento o servicios tecnológicos."
        ),
        "alcance": (
            "Proveedores de hardware, software, mantenimiento, conectividad y "
            "servicios tecnológicos."
        ),
        "descripcion": (
            "Regula el registro, la evaluación, los contratos, las garantías y el "
            "seguimiento de los proveedores."
        ),
        "responsable": "sit",
        "participantes": [],
        "reglas": [
            "Registrar los datos de contacto y el servicio.",
            "Conservar contratos y garantías.",
            "Evaluar el cumplimiento y la calidad.",
            "Definir responsables de seguimiento.",
            "Documentar las incidencias con proveedores.",
        ],
        "procedimiento": [
            "Registrar al proveedor.",
            "Documentar contrato y garantía.",
            "Evaluar el servicio.",
            "Dar seguimiento a los compromisos.",
            "Actualizar o dar de baja.",
        ],
        "responsabilidades": [
            {"area": "sit", "rol": "Responsable", "accion": "Administrar proveedores, contratos y garantías."},
            {"area": "direccion", "rol": "Autoriza", "accion": "Autorizar las contrataciones."},
        ],
        "relacion_sate": (
            "En la primera versión se documenta en la ficha del activo; el módulo "
            "de proveedores queda para fase 2."
        ),
        "origen": "PIA",
        "ampliado": True,
    },
}

PERFILES = {
    "administrador-activos": {
        "slug": "administrador-activos",
        "nombre": "Administrador de Activos Tecnológicos",
        "departamento": "sit",
        "reporta_a": "Dirección General",
        "jornada": "Tiempo completo",
        "objetivo": (
            "Garantizar el registro, control y seguimiento de los activos "
            "tecnológicos de la organización, asegurando que la información del "
            "inventario esté completa y actualizada."
        ),
        "funciones": [
            "Registrar los activos en SATE con su identificador único.",
            "Mantener actualizados la ubicación, el responsable y el estado de cada equipo.",
            "Coordinar la asignación, reasignación y baja de equipos.",
            "Mantener el inventario de configuraciones de equipos y componentes.",
            "Dar seguimiento a proveedores, garantías y contratos.",
            "Programar y registrar mantenimientos preventivos y correctivos.",
            "Generar reportes y atender las alertas de mantenimientos próximos.",
            "Realizar inventarios físicos periódicos y conciliarlos con SATE.",
        ],
        "escolaridad": (
            "Licenciatura o ingeniería en Tecnologías de la Información, Sistemas "
            "o carrera afín (titulado o pasante)."
        ),
        "experiencia": (
            "De 1 a 2 años en administración de inventarios de TI o soporte técnico."
        ),
        "conocimientos": [
            "Gestión de activos y buenas prácticas ITIL.",
            "Hardware y software.",
            "Hojas de cálculo y bases de datos básicas.",
            "Manejo de contratos y garantías.",
        ],
        "competencias": [
            "Organización y atención al detalle.",
            "Responsabilidad.",
            "Comunicación efectiva.",
            "Trabajo en equipo.",
        ],
        "herramientas": [
            "SATE.",
            "Hojas de cálculo.",
            "Etiquetas con código de barras o QR.",
            "Correo electrónico.",
        ],
        "resumen": (
            "Responsable del inventario, las asignaciones, el seguimiento de equipos, "
            "los mantenimientos y los proveedores."
        ),
        "requisitos_resumen": (
            "Licenciatura o ingeniería afín; 1–2 años de experiencia en inventarios "
            "de TI, hardware, software y garantías."
        ),
    },
    "administrador-redes": {
        "slug": "administrador-redes",
        "nombre": "Administrador de Redes y Seguridad",
        "departamento": "redes",
        "reporta_a": "Dirección General",
        "jornada": "Tiempo completo",
        "objetivo": (
            "Administrar y proteger la infraestructura de red para garantizar su "
            "disponibilidad, rendimiento y seguridad."
        ),
        "funciones": [
            "Configurar y mantener switches, routers, puntos de acceso y firewall.",
            "Monitorear el tráfico y la capacidad de la red.",
            "Administrar accesos, cuentas, permisos de red y conexiones remotas.",
            "Respaldar las configuraciones de los equipos de red.",
            "Elaborar y probar el plan de continuidad de la infraestructura.",
            "Atender incidentes de red escalados y documentar su solución.",
            "Registrar y documentar los cambios realizados a la red.",
            "Reportar y atender vulnerabilidades y eventos de seguridad.",
        ],
        "escolaridad": (
            "Ingeniería en Telecomunicaciones, Sistemas, Redes o carrera afín."
        ),
        "experiencia": "Mínimo 2 años en administración de redes.",
        "conocimientos": [
            "TCP/IP, VLAN y enrutamiento.",
            "Firewalls y VPN.",
            "Monitoreo de red.",
            "Fundamentos de ciberseguridad.",
            "Certificación tipo CCNA o equivalente (deseable).",
        ],
        "competencias": [
            "Pensamiento analítico.",
            "Responsabilidad.",
            "Trabajo bajo presión.",
            "Discreción.",
            "Comunicación técnica clara.",
        ],
        "herramientas": [
            "Consolas de administración de red y firewall.",
            "Herramientas de monitoreo y análisis de tráfico.",
            "SATE.",
        ],
        "resumen": (
            "Responsable de configurar y proteger la red, supervisar su rendimiento "
            "y atender incidentes de infraestructura."
        ),
        "requisitos_resumen": (
            "Ingeniería afín; mínimo 2 años en redes; TCP/IP, VLAN, enrutamiento, "
            "firewall, VPN y ciberseguridad."
        ),
    },
    "desarrollador-sate": {
        "slug": "desarrollador-sate",
        "nombre": "Desarrollador de Software (SATE)",
        "departamento": "desarrollo",
        "reporta_a": "Dirección General",
        "jornada": "Tiempo completo",
        "objetivo": (
            "Desarrollar y mantener los módulos del sistema SATE, asegurando su "
            "calidad, seguridad y buen funcionamiento."
        ),
        "funciones": [
            "Analizar requerimientos y proponer soluciones técnicas.",
            "Diseñar, programar y probar los módulos de SATE: activos, mantenimientos, incidencias, reportes y alertas.",
            "Administrar la base de datos del sistema.",
            "Aplicar control de versiones y documentar el código.",
            "Corregir errores y atender los incidentes de software escalados.",
            "Liberar nuevas versiones siguiendo la política de gestión de cambios.",
            "Implementar medidas de seguridad como roles, autenticación y respaldo de datos.",
        ],
        "escolaridad": (
            "Ingeniería o licenciatura en Software, Sistemas o carrera afín "
            "(titulado o pasante)."
        ),
        "experiencia": "De 1 a 3 años en desarrollo de aplicaciones web.",
        "conocimientos": [
            "Desarrollo web front-end y back-end.",
            "Bases de datos relacionales.",
            "Control de versiones con Git.",
            "APIs.",
            "Pruebas de software.",
            "Seguridad web.",
        ],
        "competencias": [
            "Lógica y resolución de problemas.",
            "Trabajo en equipo.",
            "Orden y documentación.",
            "Aprendizaje continuo.",
            "Orientación a la calidad.",
        ],
        "herramientas": [
            "Entorno de desarrollo (IDE).",
            "Git.",
            "Gestor de base de datos.",
            "Herramientas de pruebas.",
            "Gestor de tareas.",
        ],
        "resumen": (
            "Responsable de diseñar, programar, probar y mantener los módulos y la "
            "base de datos del sistema."
        ),
        "requisitos_resumen": (
            "Licenciatura o ingeniería afín; 1–3 años en desarrollo web; bases de "
            "datos, Git, APIs y seguridad web."
        ),
    },
    "tecnico-soporte": {
        "slug": "tecnico-soporte",
        "nombre": "Técnico de Soporte",
        "departamento": "soporte",
        "reporta_a": "Responsable de Desarrollo (según el organigrama)",
        "jornada": "Tiempo completo",
        "objetivo": (
            "Brindar atención oportuna y de calidad a los usuarios, resolviendo "
            "incidentes y solicitudes o escalándolos al área correspondiente."
        ),
        "funciones": [
            "Recibir y registrar incidentes y solicitudes de los usuarios.",
            "Diagnosticar y resolver fallas de equipos, software y uso de SATE.",
            "Escalar los casos que requieran a Redes, Desarrollo o SIT.",
            "Dar seguimiento a cada caso hasta su cierre y confirmar la solución con el usuario.",
            "Identificar incidentes recurrentes y reportarlos como problemas.",
            "Actualizar en SATE el estado de los equipos atendidos.",
            "Orientar a los usuarios en el uso del sistema.",
            "Mantener una base de conocimiento con las soluciones más comunes.",
        ],
        "escolaridad": (
            "Técnico superior universitario, ingeniería o carrera técnica en "
            "Tecnologías de la Información, Sistemas o afín."
        ),
        "experiencia": "Mínimo 1 año en soporte técnico o mesa de ayuda.",
        "conocimientos": [
            "Sistemas operativos.",
            "Hardware.",
            "Ofimática.",
            "Redes básicas.",
            "Atención a usuarios.",
        ],
        "competencias": [
            "Comunicación clara.",
            "Paciencia.",
            "Orientación al servicio.",
            "Resolución de problemas.",
            "Trabajo en equipo.",
        ],
        "herramientas": [
            "SATE.",
            "Sistema de tickets.",
            "Herramientas de acceso remoto.",
            "Correo electrónico.",
        ],
        "resumen": (
            "Responsable de atender solicitudes, diagnosticar fallas, resolver "
            "incidencias y orientar a los usuarios."
        ),
        "requisitos_resumen": (
            "Formación técnica o profesional afín; mínimo 1 año en soporte; sistemas "
            "operativos, hardware, redes básicas y atención a usuarios."
        ),
    },
}

# La Dirección General no es un departamento operativo del PIA, pero aparece
# en el organigrama y en las responsabilidades de autorización.
DIRECCION = {
    "slug": "direccion",
    "nombre": "Dirección General",
    "nombre_largo": "Dirección General",
    "funcion": (
        "Coordinar las áreas principales de SIT, Redes y Desarrollo, y autorizar "
        "las decisiones estratégicas, las inversiones y las bajas críticas."
    ),
    "objetivo": (
        "Alinear la operación de las áreas con la misión, la visión y los objetivos "
        "de TechTrack Solutions."
    ),
    "funciones": [
        "Coordinar a los responsables de SIT, Redes y Desarrollo.",
        "Autorizar inversiones, contrataciones y cambios críticos.",
        "Dar seguimiento a los indicadores del negocio y de SATE.",
        "Aprobar las políticas y los perfiles de puesto.",
    ],
    "perfil": None,
    "politicas_responsable": [],
    "politicas_participa": [],
}

# Áreas que pueden aparecer en la matriz y en las responsabilidades.
AREAS = {**DEPARTAMENTOS, "direccion": DIRECCION}


def politicas_por_responsable(slug):
    """Devuelve las políticas ordenadas que lidera un área."""
    return sorted(
        (p for p in POLITICAS.values() if p["responsable"] == slug),
        key=lambda p: p["numero"],
    )


def politicas_por_participacion(slug):
    """Devuelve las políticas ordenadas en las que participa un área."""
    return sorted(
        (p for p in POLITICAS.values() if slug in p["participantes"]),
        key=lambda p: p["numero"],
    )


def perfil_de_departamento(slug):
    """Devuelve el perfil de puesto asociado a un departamento, si existe."""
    departamento = DEPARTAMENTOS.get(slug)
    if not departamento or not departamento.get("perfil"):
        return None
    return PERFILES.get(departamento["perfil"])


def matriz_politicas():
    """Matriz R/P/— de políticas por departamento, según el PIA."""
    filas = []
    for politica in sorted(POLITICAS.values(), key=lambda p: p["numero"]):
        participacion = {}
        for slug in DEPARTAMENTOS:
            if politica["responsable"] == slug:
                participacion[slug] = "R"
            elif slug in politica["participantes"]:
                participacion[slug] = "P"
            else:
                participacion[slug] = "—"
        filas.append({"politica": politica, "participacion": participacion})
    return filas


# Trazabilidad entre los apartados del PIA y el sitio público o SATE.
# `endpoint` enlaza a la página donde se demuestra; `estado` distingue entre
# contenido publicado y funcionalidad implementada en el sistema.
CUMPLIMIENTO_PIA = [
    {
        "seccion": "2. Datos generales de la empresa",
        "requisito": (
            "Nombre, giro, producto principal, descripción, propuesta de valor "
            "y clientes objetivo."
        ),
        "evidencia": (
            "Ficha institucional con los datos generales de TechTrack Solutions."
        ),
        "donde": "Empresa",
        "endpoint": "empresa",
        "estado": "Publicado",
    },
    {
        "seccion": "2.1 Misión y 2.2 Visión",
        "requisito": "Misión y visión de la empresa alineadas a la gestión preventiva.",
        "evidencia": "Tarjetas de misión y visión dentro de la página de la empresa.",
        "donde": "Empresa",
        "endpoint": "empresa",
        "estado": "Publicado",
    },
    {
        "seccion": "2.3 Objetivos del SATE",
        "requisito": (
            "Objetivo general y objetivos específicos: registrar activos, dar "
            "seguimiento, conservar historial, identificar fallas y generar reportes."
        ),
        "evidencia": "Listado de objetivos de la empresa y del producto.",
        "donde": "Empresa",
        "endpoint": "empresa",
        "estado": "Publicado",
    },
    {
        "seccion": "2.4 Metas y funcionalidades",
        "requisito": (
            "Interfaz amigable, registro y consulta de activos, identificadores "
            "únicos, mantenimientos e incidencias, alertas, historial y reportes."
        ),
        "evidencia": "Metas clave y módulos del producto explicados en la página de SATE.",
        "donde": "Producto SATE",
        "endpoint": "sate_info",
        "estado": "Publicado",
    },
    {
        "seccion": "3. Organigrama",
        "requisito": (
            "Dirección General coordina SIT, Redes y Desarrollo; Soporte depende "
            "de Desarrollo y opera con funciones propias."
        ),
        "evidencia": "Organigrama interactivo con enlaces a cada departamento.",
        "donde": "Empresa · Organigrama",
        "endpoint": "empresa",
        "estado": "Publicado",
    },
    {
        "seccion": "4. Políticas generales",
        "requisito": "Diez políticas de gestión de TI con su objetivo y alcance.",
        "evidencia": "Catálogo completo con ficha de objetivo, alcance, reglas y procedimiento.",
        "donde": "Políticas",
        "endpoint": "politicas",
        "estado": "Publicado",
    },
    {
        "seccion": "5 y 6. Asignación de políticas",
        "requisito": (
            "Cada política indica el área responsable y las áreas participantes, "
            "incluida la matriz R/P por departamento."
        ),
        "evidencia": "Matriz de responsabilidad y bloques de políticas en cada departamento.",
        "donde": "Políticas · Matriz",
        "endpoint": "politicas",
        "estado": "Publicado",
    },
    {
        "seccion": "5.1 a 5.4 Departamentos",
        "requisito": "Función, objetivo y funciones principales de SIT, Redes, Desarrollo y Soporte.",
        "evidencia": "Página de departamentos y ficha detallada de cada área.",
        "donde": "Departamentos",
        "endpoint": "departamentos",
        "estado": "Publicado",
    },
    {
        "seccion": "5.1 a 5.4 Perfiles de puesto",
        "requisito": (
            "Perfil por departamento con objetivo, funciones, requisitos, "
            "competencias y herramientas."
        ),
        "evidencia": "Fichas de perfil publicadas y postulación en línea.",
        "donde": "Trabaja con nosotros",
        "endpoint": "trabaja_con_nosotros",
        "estado": "Publicado",
    },
    {
        "seccion": "Metas · Registro e identificadores",
        "requisito": "Registrar activos con identificador único, ubicación, responsable y estado.",
        "evidencia": (
            "Módulo Activos e historial: alta con identificador generado, ficha, "
            "filtros y resguardo en PDF."
        ),
        "donde": "SATE · Activos e historial",
        "endpoint": "activos",
        "estado": "Implementado",
    },
    {
        "seccion": "Metas · Historial completo",
        "requisito": "Conservar el historial de mantenimientos, reparaciones y cambios.",
        "evidencia": (
            "Línea de tiempo por activo con altas, cambios de datos, "
            "mantenimientos e incidencias."
        ),
        "donde": "SATE · Ficha del activo",
        "endpoint": "activos",
        "estado": "Implementado",
    },
    {
        "seccion": "Metas · Mantenimiento e incidencias",
        "requisito": "Programar mantenimientos y registrar incidencias con seguimiento.",
        "evidencia": (
            "Módulos de mantenimientos e incidencias con estados, prioridad, "
            "responsable, calendario y fichas de detalle."
        ),
        "donde": "SATE · Mantenimientos",
        "endpoint": "mantenimientos",
        "estado": "Implementado",
    },
    {
        "seccion": "Metas · Alertas preventivas",
        "requisito": "Alertar sobre mantenimientos vencidos y próximos a vencer.",
        "evidencia": (
            "Panel con alertas de vencidos y de los próximos 7 días, con enlace "
            "a la vista filtrada."
        ),
        "donde": "SATE · Panel principal",
        "endpoint": "dashboard",
        "estado": "Implementado",
    },
    {
        "seccion": "Metas · Reportes",
        "requisito": "Generar reportes que apoyen la toma de decisiones.",
        "evidencia": (
            "Reporte de inventario en PDF con filtros, además del resguardo de "
            "activo y la orden de mantenimiento."
        ),
        "donde": "SATE · Activos · Reporte PDF",
        "endpoint": "activos",
        "estado": "Implementado",
    },
    {
        "seccion": "Política 9 · Seguridad de la información",
        "requisito": "Control de acceso por roles, autenticación y protección de datos.",
        "evidencia": (
            "Siete roles del PIA, permisos por módulo, CSRF, sesiones seguras, "
            "contraseñas cifradas y auditoría."
        ),
        "donde": "SATE · Usuarios y roles",
        "endpoint": "usuarios",
        "estado": "Implementado",
    },
    {
        "seccion": "Aviso de privacidad",
        "requisito": "Informar el tratamiento de datos personales del sitio y los formularios.",
        "evidencia": "Aviso de privacidad enlazado desde el pie de página y los formularios.",
        "donde": "Aviso de privacidad",
        "endpoint": "privacidad",
        "estado": "Publicado",
    },
]
