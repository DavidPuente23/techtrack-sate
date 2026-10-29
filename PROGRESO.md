# Progreso de correcciones P0

Copia de trabajo: `C:\Users\pmdav\Downloads\techtrack_sate_copia`
Carpeta original: `C:\Users\pmdav\Downloads\techtrack_sate` (sin modificar)

## Bloque 1 - Base de datos y configuración

- [x] Copia del proyecto creada.
- [x] `database/schema.sql` reconstruido con las 13 tablas reales.
- [x] Columnas faltantes agregadas (`identificador`, `tema`, `observaciones`,
      `resolucion`, `fecha_cierre`, `fecha_finalizacion`, `acepta_privacidad`).
- [x] `database/seed.sql` con contraseña hasheada (scrypt).
- [x] `database/migrate_p0.sql` para bases existentes, sin pérdida de datos.
- [x] `database/create_user.sql` para usuario MySQL dedicado.
- [x] `config.py` con carga de `.env` sin dependencias externas.
- [x] `.env`, `.env.example` y `.gitignore`.
- [x] `requirements.txt` (`fpdf` fijado en 1.7.2).
- [x] `README.md` con instalación, migración, credenciales y pruebas.

## Bloque 2 - Seguridad, login y RBAC

- [x] `SECRET_KEY`, credenciales MySQL y `DEBUG` fuera del código.
- [x] Cookies de sesión `HttpOnly`, `SameSite=Lax` y `Secure` configurable.
- [x] Login valida `activo`, usa `rol_id` + join a `roles` y `session.clear()`.
- [x] Logout cambiado a `POST` y protegido con sesión + CSRF.
- [x] Decoradores `login_required`, `role_required`, `admin_required`,
      `staff_required` y `read_required` aplicados a las rutas privadas.
- [x] RBAC por nombre de rol: Administrador General, Dirección General,
      Técnico de Soporte y Usuario Solicitante.
- [x] `perfil()` exige contraseña actual y valida el tema.
- [x] `cambiar_tema()` valida tema y evita open redirect.
- [x] CSRF global en `before_request` con token en sesión y comparación segura.
- [x] Headers de seguridad (`nosniff`, `X-Frame-Options`, CSP, Referrer-Policy,
      Permissions-Policy, HSTS sobre HTTPS).
- [x] Handlers 400, 403, 404 y 500 con plantillas propias.
- [x] Helpers `registrar_historial`, `registrar_auditoria`,
      `generar_identificador` y `recalcular_estado_activo`.
- [x] CSV con BOM UTF-8 y saneo de fórmulas.

## Bloque 3 - UI, CSS, CSRF y rutas

- [x] `templates/sate/base_sate.html` reescrito: layout correcto, sidebar por rol,
      logout POST, selector de tema, mensajes flash y `url_for`.
- [x] Token CSRF en los 16 formularios POST de las plantillas.
- [x] `templates/base.html` con navegación sin duplicados y enlaces válidos.
- [x] `templates/sate/login.html` sin estilos inline y con CSRF.
- [x] `templates/sate/perfil.html` con `password_actual` y validaciones.
- [x] `templates/sate/editar_incidencia.html` con los 5 estados reales.
- [x] `templates/sate/editar_activo.html` incluye el estado `Con Falla`.
- [x] Checkboxes `acepta_privacidad` con `name` en contacto y postulación.
- [x] Plantillas `public/400.html`, `403.html`, `500.html` y `404.html`.
- [x] Alias CSS (`--accent-color`, `--text-primary`, `--text-secondary`,
      `--border-color`, `--surface-color`, `--bg-color`, `--info`).
- [x] Estilos de cabecera, flash, botones, formularios y páginas de error.
- [x] Media queries responsive y `prefers-reduced-motion`.
- [x] Enlace roto `/trabaja-con-nosotros` resuelto (redirige a `/vacantes`).
- [x] Enlaces `href="#"` de departamentos y políticas reemplazados por contacto.
- [x] Botones de acción visibles solo para los roles que pueden usarlos.

## Bloque 4 - Validaciones, estados y pruebas

- [x] Validación de activo/departamento/rol/estado en formularios privados.
- [x] IDs inexistentes devuelven 404 en detalles y ediciones.
- [x] `nueva_incidencia()` fuerza `estado = 'Nueva'` (no depende del default).
- [x] `editar_incidencia()` guarda `fecha_cierre` al resolver/cerrar.
- [x] `editar_mantenimiento()` guarda `fecha_finalizacion` al finalizar.
- [x] Los mantenimientos ya no cierran incidencias automáticamente.
- [x] `nuevo_cambio`, `nuevo_problema` y `nuevo_proveedor` validan datos.
- [x] Código muerto eliminado (bloque duplicado de `nuevo_activo`).
- [x] Migración P0 aplicada a la base local (solo columnas e índices).
- [x] Estado legado `Pendiente` de incidencias normalizado a `Nueva`.

## Bloque 5 - Contenido del PIA y sitio público

- [x] `contenido.py` centraliza empresa, 4 departamentos, 10 políticas y
      4 perfiles de puesto extraídos del PIA.
- [x] Sitio público con Inicio, Empresa, Departamentos, Políticas,
      Trabaja con nosotros, Producto SATE y Contacto.
- [x] Subpáginas de departamento, política y perfil con navegación cruzada.
- [x] Matriz de participación en políticas y políticas por responsable.
- [x] Rutas antiguas `/vacantes` y `/vacantes/<slug>` redirigidas (301/308).
- [x] Plantillas públicas responsive y contenido accesible.
- [x] `scripts/check_public.py` valida rutas, slugs y enlaces internos.
- [x] Lighthouse en `/`: accesibilidad, buenas prácticas y SEO en 1.0.

## Bloque 6 - Roles del PIA, alcance y gestión de usuarios

- [x] `permisos.py` con los 7 roles del PIA y la matriz de 5 módulos internos
      (`panel`, `activos`, `mantenimientos`, `incidencias`, `usuarios`).
- [x] Acciones `ver`, `crear`, `editar` y `administrar`; helpers `puede`,
      `menu_modulos`, `alcance_activos`, `alcance_incidencias`.
- [x] Decorador `require_perm` aplicado a todas las rutas privadas.
- [x] Menú lateral dinámico según los permisos del rol.
- [x] Alcance por departamento para activos y por solicitante para incidencias.
- [x] El rol Usuario Solicitante solo ve activos de su área y sus incidencias.
- [x] CRUD de usuarios: listado, alta, edición, activación/desactivación y
      restablecimiento de contraseña temporal.
- [x] Protección de la propia cuenta y del último administrador general activo.
- [x] Contraseña temporal obligatoria: `debe_cambiar_password` y bloqueo hasta
      cambiarla desde Mi Perfil.
- [x] `ultimo_acceso` actualizado en cada login.
- [x] Sesión invalidada si la cuenta se desactiva o elimina.
- [x] Módulos fuera del PIA retirados de SATE (proveedores, cambios, problemas,
      reportes, políticas internas y exportación CSV).
- [x] `database/migrate_bloque6.sql` y `scripts/apply_bloque6.py` idempotentes.
- [x] `schema.sql` y `seed.sql` actualizados con los 7 roles y columnas nuevas.
- [x] Tablas de usuarios, incidencias y mantenimientos compactadas para evitar
      cortes horizontales; calendario y tabla de mantenimientos apilados.
- [x] CSP ajustada para DataTables (i18n HTTPS) y la fuente de FullCalendar.

## Bloque 7 - Inventario con filtros e historial real

- [x] Filtros del inventario por texto (`q`), estado, tipo y departamento,
      combinables y con validación de valores.
- [x] El filtro por texto busca en nombre, identificador, serie, marca, modelo
      y responsable.
- [x] Los filtros respetan el alcance por departamento del Usuario Solicitante.
- [x] Formulario de filtros que conserva la selección y resumen de resultados.
- [x] DataTables sin buscador propio para no duplicar el filtrado del servidor.
- [x] Ficha del activo reorganizada en dos tarjetas (equipo y asignación).
- [x] Historial como línea de tiempo con color por tipo de movimiento, fecha
      `dd/mm/yyyy HH:mm` y usuario responsable.
- [x] Fallback «Usuario eliminado» cuando la cuenta ya no existe.
- [x] Contador de movimientos y fecha del último movimiento en la ficha.
- [x] `editar_activo()` calcula el diff real antes/después (nombre, ubicación,
      responsable, departamento y estado).
- [x] Una edición sin cambios no escribe historial ni auditoría.
- [x] El detalle del historial guarda los valores anterior y nuevo.
- [x] `scripts/smoke_bloque7.py` cubre filtros, alcance, diff y limpieza.

## Bloque 8 - Filtros y fichas de mantenimientos e incidencias

- [x] Filtros de mantenimientos por texto (equipo, identificador, descripción
      o responsable), estado y tipo, con validación de valores.
- [x] Filtros de incidencias por texto, estado y prioridad, respetando el
      alcance del Usuario Solicitante.
- [x] Calendario de mantenimientos sincronizado con los filtros aplicados.
- [x] Formularios de filtros que conservan la selección y resumen de resultados.
- [x] Ficha de mantenimiento con datos del servicio, fechas, responsable,
      equipo intervenido, descripción y observaciones.
- [x] Ficha de incidencia con reporte, solicitante, equipo afectado,
      diagnóstico y resolución.
- [x] Botón «Ver» en las tablas y acciones de edición/PDF según permisos.
- [x] El detalle de una incidencia ajena devuelve 403 al Usuario Solicitante.
- [x] `scripts/smoke_bloque8.py` cubre filtros, fichas, alcance y limpieza.

## Bloque 9 - Panel por rol y navegación móvil

- [x] Panel principal coherente con el rol: métricas, accesos rápidos y
      acciones visibles solo con permiso.
- [x] El Usuario Solicitante ve «Activos de mi área», sus incidencias y una
      nota de alcance con su departamento.
- [x] Actividad reciente con incidencias, mantenimientos próximos y
      movimientos de activos, respetando el alcance de cada rol.
- [x] Gráficas de estado del inventario e incidencias por estado, con estados
      vacíos y enlaces de acción cuando no hay datos.
- [x] Alertas de mantenimientos vencidos e incidencias críticas +24 h con
      enlace a la vista filtrada correspondiente.
- [x] Navegación móvil: botón «Menú», sidebar off-canvas, overlay, cierre con
      Escape, overlay o enlace, `aria-expanded`, foco e `inert`.
- [x] `static/js/sate_nav.js` con la lógica de la navegación móvil.
- [x] CSS responsive del panel y de la cabecera: acciones en cuadrícula y
      tarjetas KPI a una columna en móvil.
- [x] `scripts/smoke_bloque9.py` cubre el panel por rol, el alcance del
      solicitante, el marcado móvil y los siete roles.

## Bloque 10 - Alertas preventivas, reportes y cumplimiento del PIA

- [x] Alerta en el panel de mantenimientos que vencen en los próximos 7 días,
      además de los ya vencidos, con enlace a la vista filtrada.
- [x] El KPI de mantenimientos pendientes muestra «vencidos» y «por vencer».
- [x] `mantenimientos()` acepta `vencimiento` (`7` o `vencidos`), excluye los
      finalizados y conserva los filtros existentes.
- [x] Selector «Vencimiento» y chips de filtro en la vista de mantenimientos.
- [x] Reporte de inventario en PDF (`/app/activos/reporte`) con filtros y
      alcance por rol, en formato horizontal y con paginación.
- [x] Botón «Reporte PDF» en el inventario que conserva los filtros activos.
- [x] Página pública `/cumplimiento-pia` con la matriz que enlaza cada apartado
      del PIA con la página o módulo donde se demuestra.
- [x] `CUMPLIMIENTO_PIA` centraliza 16 evidencias entre contenido publicado y
      funcionalidad implementada.
- [x] La matriz del PIA se apila como tarjetas en móvil, sin desplazamiento
      horizontal.
- [x] Barra de navegación pública sin `sticky` en móvil y con menú horizontal
      desplazable, para no tapar el contenido.
- [x] Una sesión de una cuenta eliminada ya no bloquea las páginas públicas:
      se limpia la sesión y solo las rutas privadas redirigen al login.
- [x] `scripts/smoke_bloque10.py` cubre alertas, filtros de vencimiento, PDF
      con alcance por rol, página de cumplimiento y sesión inválida.

## Bloque 11 - Acabado del sitio y datos de demostración

- [x] Favicon multitamaño (`favicon.ico`), `favicon-32.png` y
      `apple-touch-icon.png` generados a partir de la marca TS.
- [x] Imagen Open Graph 1200 × 630 (`static/og-image.png`) para compartir el
      sitio en redes y mensajería.
- [x] Rutas `/favicon.ico`, `/robots.txt` y `/sitemap.xml`; el sitemap incluye
      las 27 URLs públicas y excluye las rutas privadas.
- [x] Metadatos Open Graph, Twitter Card, `canonical`, `theme-color` y
      JSON-LD de Organization en el sitio público.
- [x] Las vistas de SATE y el login declaran `noindex, nofollow`.
- [x] `scripts/seed_demo.py`: un usuario por cada rol restante, 12 activos en
      los cuatro departamentos, 6 mantenimientos, 5 incidencias y 5
      movimientos de historial.
- [x] El script es idempotente y `--limpiar` elimina solo los datos demo.
- [x] Tabla de activos con clase `table-compact` y columna de acciones fija,
      para que los 14 registros demo no oculten los botones.
- [x] `check_public.py` valida favicon, robots, sitemap y metadatos sociales.

## Bloque 12 - Identificación por QR

- [x] `GET /app/activos/<id>/qr.svg` genera el QR en SVG con la URL de la ficha.
- [x] `GET /app/activos/<id>/etiqueta` crea una etiqueta imprimible de
      90 × 55 mm con marca, identificador, nombre, departamento, estado y QR.
- [x] La ficha del activo muestra el QR y los botones **Imprimir etiqueta** y
      **Descargar QR**.
- [x] Las dos rutas respetan permisos y alcance por departamento; sin sesión
      redirigen al login.
- [x] `qrcode` se agrega a `requirements.txt`; la salida SVG no necesita Pillow.
- [x] `scripts/smoke_qr.py` cubre la ficha, el SVG, la etiqueta, los códigos
      distintos por activo y el alcance por rol.

## Bloque 13 - Manual de usuario en PDF

- [x] `scripts/generar_manual.py` construye el manual completo con FPDF
      (Helvetica, latin-1) y las capturas de `docs/capturas/`.
- [x] Portada, ficha del documento, índice automático de dos pasadas y
      15 capítulos: sitio público, acceso, conceptos, permisos, panel, activos,
      mantenimientos, incidencias, usuarios, perfil, datos demo, problemas,
      preguntas frecuentes, buenas prácticas y glosario.
- [x] 51 páginas, 30 figuras y 31 tablas; índice de 2 páginas con 108 entradas
      y numeración correcta.
- [x] Maquetación: figuras a 152 mm con reducción automática, títulos unidos a
      su figura, tablas y listas pequeñas sin cortes ni filas huérfanas.
- [x] Se añadieron secciones de apoyo: resumen de módulos, sesión y seguridad,
      ciclo de vida del activo, indicadores de mantenimiento e incidencias,
      casos prácticos y verificación de los datos demo.
- [x] `docs/Manual_Usuario_SATE.pdf` generado y revisado página por página.

## Pruebas ejecutadas

- [x] `python -m py_compile app.py config.py permisos.py contenido.py`
- [x] `python scripts/smoke_test.py` (rutas públicas, login, CSRF, 404)
- [x] `python scripts/smoke_private.py` (vistas privadas + rutas retiradas)
- [x] `python scripts/smoke_rbac.py` (permisos de los 7 roles)
- [x] `python scripts/smoke_bloque6.py` (alta, contraseña temporal, alcance,
      restablecimiento, desactivación y protecciones)
- [x] `python scripts/smoke_bloque7.py` (filtros, alcance, diff e historial)
- [x] `python scripts/smoke_bloque8.py` (filtros y fichas de mantenimientos e
      incidencias)
- [x] `python scripts/smoke_bloque9.py` (panel por rol, alcance y menú móvil)
- [x] `python scripts/smoke_bloque10.py` (alertas de vencimiento, reporte PDF,
      cumplimiento del PIA y sesión inválida)
- [x] `python scripts/smoke_qr.py` (QR SVG, etiqueta imprimible y alcance por rol)
- [x] `python scripts/smoke_detalles.py` (detalles, edición, PDFs)
- [x] `python scripts/smoke_post.py` (POST reales con CSRF y limpieza)
- [x] `python scripts/smoke_flujo.py` (mantenimiento -> incidencia -> cierre)
- [x] `python scripts/check_permisos.py` (matriz de permisos)
- [x] `python scripts/check_public.py` (sitio público, slugs del PIA, favicon,
      robots, sitemap y metadatos sociales)
- [x] `python scripts/seed_demo.py` (datos demo idempotentes y `--limpiar`)
- [x] `python scripts/check_endpoints.py` (38 `url_for` válidos)
- [x] `python scripts/check_templates.py` (todas las plantillas compilan)
- [x] `python scripts/check_schema.py` (13 tablas alineadas)
- [x] `python scripts/check_migration.py` (migración validada en BD temporal)
- [x] `python scripts/generar_manual.py` (manual de 51 páginas generado)
- [x] Revisión visual de las 51 páginas del manual y verificación de que no
      quedan títulos huérfanos ni tablas partidas con filas sueltas

## Pendiente / recomendado

- [ ] Cambiar la contraseña del administrador al primer inicio de sesión.
- [ ] Configurar HTTPS y `SESSION_COOKIE_SECURE=1` en producción.
- [ ] Ejecutar `database/create_user.sql` y usar un usuario MySQL con permisos mínimos.
- [ ] Revisar los estilos de las plantillas antiguas que aún conservan estilos inline
      (funcionan, pero no son P0).
