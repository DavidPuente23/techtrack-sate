# TechTrack SATE

Sistema de Administración y Trazabilidad de Equipos (SATE) para TechTrack Solutions.

Aplicación web desarrollada con **Flask + MySQL**. Incluye el sitio público del PIA (empresa, departamentos, políticas, perfiles y producto SATE) y el sistema privado SATE con panel, activos e historial, mantenimientos, incidencias y usuarios/roles.

> Esta es la copia de trabajo con las correcciones del bloque P0. La carpeta original `techtrack_sate` no se modificó.

---

## 1. Requisitos

- Python 3.10 o superior
- MySQL 8 o superior
- MySQL Workbench (opcional, para administrar la BD)

## 2. Instalación

```bash
cd techtrack_sate_copia

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

## 3. Base de datos

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed.sql
```

Esto crea la base `techtrack_sate`, todas las tablas y el usuario inicial.

### Si ya tienes una base de datos con datos

**No ejecutes `schema.sql`**: ese script recrea las tablas y borra la información.
Aplica solo las migraciones, que agregan columnas, índices y roles sin borrar datos:

```bash
mysql -u root -p techtrack_sate < database/migrate_p0.sql
mysql -u root -p techtrack_sate < database/migrate_bloque6.sql
```

También puedes aplicar la migración del Bloque 6 con:

```bash
python scripts/apply_bloque6.py
```

Ambas migraciones son idempotentes y se pueden ejecutar varias veces.

### Usuario inicial

| Campo | Valor |
|---|---|
| Correo | `admin@techtrack.com` |
| Contraseña | `Admin123!` |

**Cambia la contraseña al primer inicio de sesión.**

### Datos de demostración (opcional)

Para presentar el sistema con información realista:

```bash
python scripts/seed_demo.py
```

El script crea un usuario por cada rol restante, doce activos en los cuatro
departamentos, mantenimientos vencidos y próximos, incidencias en distintos
estados e historial de movimientos. Es idempotente: se puede ejecutar varias
veces y refresca solo sus propios datos.

| Correo | Rol |
|---|---|
| `admin@demo.techtrack.com` | Administrador General |
| `direccion@demo.techtrack.com` | Dirección General |
| `activos@demo.techtrack.com` | Administrador de Activos |
| `redes@demo.techtrack.com` | Administrador de Redes |
| `desarrollo@demo.techtrack.com` | Desarrollador |
| `soporte@demo.techtrack.com` | Técnico de Soporte |
| `solicitante@demo.techtrack.com` | Usuario Solicitante |

Contraseña para todas las cuentas demo: `Demo123!`

Los datos se identifican por el dominio `@demo.techtrack.com` y el prefijo
`DEMO-`, así que se eliminan sin tocar información real:

```bash
python scripts/seed_demo.py --limpiar
```

No uses estas cuentas en producción.

### Usuario dedicado de MySQL (recomendado)

```bash
mysql -u root -p < database/create_user.sql
```

Después actualiza `DB_USER` y `DB_PASSWORD` en `.env`.

## 4. Configuración

Copia `.env.example` a `.env` y ajusta los valores:

```bash
copy .env.example .env        # Windows
cp .env.example .env          # Linux/macOS
```

Variables principales:

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave de sesiones. Genera una aleatoria. |
| `DB_HOST`, `DB_PORT` | Servidor MySQL. |
| `DB_USER`, `DB_PASSWORD` | Credenciales de MySQL. |
| `DB_NAME` | Nombre de la base. |
| `FLASK_DEBUG` | `1` solo en desarrollo. |
| `SESSION_COOKIE_SECURE` | `1` si usas HTTPS. |

Generar una clave:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 5. Ejecutar

Desarrollo:

```bash
python app.py
```

Abrir `http://127.0.0.1:5000`.

Producción en Windows (Waitress):

```bash
waitress-serve --listen=0.0.0.0:8000 app:app
```

Para subir el proyecto a GitHub y publicarlo con un enlace para el equipo,
consulta [`DESPLIEGUE.md`](DESPLIEGUE.md). Incluye GitHub, un túnel temporal,
PythonAnywhere y Render + MySQL en la nube.

## 6. Roles

SATE usa los siete roles de la estructura organizacional del PIA:

| Rol | Alcance |
|---|---|
| Administrador General | Control total, incluida la gestión de usuarios y roles. |
| Dirección General | Consulta del panel, activos, mantenimientos e incidencias. |
| Administrador de Activos | Gestiona el inventario y los mantenimientos; consulta incidencias. |
| Administrador de Redes | Atiende mantenimientos e incidencias; consulta el inventario. |
| Desarrollador | Atiende incidencias de software; consulta activos y mantenimientos. |
| Técnico de Soporte | Atiende incidencias y mantenimientos; edita activos. |
| Usuario Solicitante | Consulta los activos de su departamento y reporta sus propias incidencias. |

Las cuentas nuevas y las contraseñas restablecidas son temporales: el usuario
debe cambiarlas en su primer acceso antes de usar el resto de SATE.

## 7. Inventario, mantenimientos e incidencias

El módulo de activos incluye:

- Filtros por texto (nombre, identificador, serie, marca, modelo o
  responsable), estado, tipo y departamento, combinables entre sí.
- Alcance automático por departamento para el rol Usuario Solicitante: los
  filtros nunca muestran equipos de otras áreas.
- Ficha del activo con datos de asignación y línea de tiempo de movimientos.
- Historial real: cada edición guarda el valor anterior y el nuevo, el usuario
  que la realizó y la fecha. Si no hay cambios, no se escribe ningún registro.

Los módulos de mantenimientos e incidencias incluyen:

- Filtros por texto, estado, tipo o prioridad, con el calendario sincronizado.
- Ficha de mantenimiento con fechas, responsable, equipo, descripción y
  observaciones.
- Ficha de incidencia con reporte, solicitante, equipo, diagnóstico y
  resolución.
- El Usuario Solicitante solo puede abrir sus propias incidencias; las ajenas
  responden 403.

## 8. Panel principal y navegación móvil

El panel se adapta a los permisos del rol:

- Las métricas, los accesos rápidos y las acciones de alta solo aparecen si el
  rol puede usarlos. Dirección General ve únicamente accesos de consulta.
- El Usuario Solicitante ve «Activos de mi área», sus incidencias abiertas y
  una nota con el alcance de su departamento.
- La actividad reciente muestra incidencias, mantenimientos próximos y
  movimientos de activos dentro del alcance del usuario.
- Las alertas enlazan a la vista filtrada de mantenimientos o incidencias.
- Las gráficas de inventario e incidencias muestran un estado vacío con una
  acción cuando todavía no hay datos.

En pantallas de hasta 900 px el menú lateral se convierte en un panel
off-canvas: el botón «Menú» lo abre, el overlay o la tecla Escape lo cierran y
el foco vuelve al botón. El sidebar se marca como `inert` cuando está cerrado
para que no sea accesible con teclado ni lectores de pantalla.

## 9. Alertas, reportes y cumplimiento del PIA

El panel muestra dos alertas de mantenimiento con enlace directo a la vista
filtrada:

- **Vencidos sin finalizar:** mantenimientos con fecha anterior a hoy.
- **Próximos 7 días:** mantenimientos que vencen entre hoy y dentro de siete
  días, para anticipar el servicio preventivo.

La vista de mantenimientos agrega el filtro `vencimiento` (`7` o `vencidos`),
combinable con texto, estado y tipo.

El inventario incluye el botón **Reporte PDF**, que genera un PDF horizontal con
los filtros activos (texto, estado, tipo y departamento) y respeta el alcance por
rol: el Usuario Solicitante solo obtiene los activos de su departamento.

La página pública **Cumplimiento del PIA** (`/cumplimiento-pia`) presenta una
matriz con 16 evidencias que conectan cada apartado del documento —empresa,
misión y visión, objetivos, organigrama, políticas, departamentos, perfiles y
metas de SATE— con la página o módulo donde se demuestra. Distingue entre
contenido **Publicado** y funcionalidad **Implementado**, y explica el alcance de
la primera versión.

## 10. Identificación por QR

Cada activo tiene un código QR que abre su ficha dentro de SATE, útil para
etiquetar equipos y consultar el historial desde un teléfono.

- `GET /app/activos/<id>/qr.svg` genera el QR en SVG (escalable e imprimible) con
  la URL absoluta de la ficha.
- `GET /app/activos/<id>/etiqueta` muestra una etiqueta de 90 × 55 mm con la
  marca, el identificador, el nombre, el departamento, el estado y el QR.
  Incluye un botón **Imprimir etiqueta** y estilos `@media print`.
- La ficha del activo muestra el QR y los botones **Imprimir etiqueta** y
  **Descargar QR**.
- Ambas rutas respetan los permisos y el alcance por departamento del inventario;
  sin sesión redirigen al login.

El QR se genera con `qrcode` (salida SVG, sin dependencias de imagen) y no
guarda datos del activo: solo codifica la URL de la ficha.

## 11. SEO, favicon y metadatos

- `/favicon.ico` sirve el icono multitamaño; también existen `favicon-32.png` y
  `apple-touch-icon.png` para navegadores y dispositivos móviles.
- `/robots.txt` permite el sitio público y bloquea `/app/`, `/login` y
  `/logout`; enlaza el sitemap.
- `/sitemap.xml` genera las 27 URLs públicas (páginas principales, los cuatro
  departamentos, las diez políticas y los cuatro perfiles).
- `templates/base.html` incluye `canonical`, Open Graph, Twitter Card,
  `theme-color` y JSON-LD de `Organization`. La imagen para compartir es
  `static/og-image.png` (1200 × 630).
- Las vistas de SATE y el login declaran `noindex, nofollow`.

## 12. Manual de usuario

El manual completo está en `docs/Manual_Usuario_SATE.pdf` (51 páginas, 30 figuras y
31 tablas). Recorre el sitio público, el acceso, los seis módulos de SATE, la
administración de usuarios, los datos demo, la solución de problemas y un
glosario.

Se genera con:

```bash
pip install fpdf==1.7.2
python scripts/generar_manual.py
```

El generador usa las capturas de `docs/capturas/` y escribe el PDF en
`docs/Manual_Usuario_SATE.pdf`. Requiere Pillow y `pymupdf` solo para mantener y
revisar el manual; no son dependencias de ejecución de la aplicación.

## 13. Estructura

```
app.py                  Rutas y lógica principal
config.py               Configuración y carga de .env
contenido.py            Contenido del PIA (empresa, políticas, perfiles)
permisos.py             Matriz de permisos de los 7 roles
database/schema.sql     Esquema completo
database/seed.sql       Datos base, roles y usuario inicial
database/schema_deploy.sql  Esquema sin CREATE DATABASE/USE, para hosting
database/seed_deploy.sql    Datos base sin USE, para hosting
database/migrate_p0.sql Migración P0 sin pérdida de datos
database/migrate_bloque6.sql Roles del PIA y columnas de usuarios
database/create_user.sql Usuario dedicado de MySQL
DESPLIEGUE.md           Guía para GitHub y hosting
Procfile                Arranque en Render/Railway
runtime.txt             Versión de Python para el hosting
static/css/style.css    Estilos
static/js/main.js       DataTables y FullCalendar
static/js/sate_nav.js   Navegación móvil del sidebar de SATE
static/favicon.ico      Icono del sitio
static/og-image.png     Imagen para compartir (Open Graph)
templates/              Vistas públicas y privadas
docs/Manual_Usuario_SATE.pdf  Manual de usuario completo
docs/capturas/          Capturas usadas por el manual
scripts/generar_manual.py     Generador del manual en PDF
scripts/                Pruebas de humo, validaciones y datos demo
```

## 14. Pruebas

```bash
python -m py_compile app.py config.py permisos.py contenido.py
python scripts/smoke_test.py       # rutas públicas, login y CSRF
python scripts/smoke_private.py    # vistas privadas con sesión simulada
python scripts/smoke_rbac.py       # permisos de los 7 roles
python scripts/smoke_bloque6.py    # alta, contraseña temporal, alcance y bajas
python scripts/smoke_bloque7.py    # filtros del inventario e historial de cambios
python scripts/smoke_bloque8.py    # filtros y fichas de mantenimientos e incidencias
python scripts/smoke_bloque9.py    # panel por rol y navegación móvil
python scripts/smoke_bloque10.py   # alertas, reporte PDF y cumplimiento del PIA
python scripts/smoke_qr.py         # QR, etiqueta imprimible y alcance por rol
python scripts/smoke_detalles.py   # detalles y edición con IDs reales
python scripts/smoke_post.py       # POST reales con CSRF y limpieza
python scripts/smoke_flujo.py      # mantenimiento -> incidencia -> cierre
python scripts/check_permisos.py   # matriz de permisos
python scripts/check_public.py     # sitio público, SEO y slugs del PIA
python scripts/check_endpoints.py  # url_for() válidos
python scripts/check_templates.py  # plantillas Jinja compilables
python scripts/check_schema.py     # schema vs base de datos local
python scripts/seed_demo.py        # datos demo (opcional)
```

Las pruebas de vistas privadas necesitan una base de datos accesible.

## 15. Notas

- `fpdf` se fija en `1.7.2` porque el código actual usa su API clásica (`output(dest='S')`).
- El archivo `.env` no debe subirse a git.
- Las cuentas `@demo.techtrack.com` son solo para demostración; no usarlas en producción.
- Pillow se usó únicamente para generar los iconos y la imagen social; no es una dependencia de ejecución.
- Para producción: `FLASK_DEBUG=0`, HTTPS, `SESSION_COOKIE_SECURE=1` y un usuario MySQL con permisos mínimos.
