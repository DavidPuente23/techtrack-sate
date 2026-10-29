# Cómo ejecutar TechTrack SATE en tu computadora

Guía para el equipo. Tiempo estimado: 15 minutos.

Al terminar tendrás el sistema completo corriendo en tu equipo, con la base de
datos y los datos de demostración, sin depender de internet ni de nadie más.

---

## Antes de empezar

Necesitas instalar dos cosas:

1. **Python 3.10 o superior** — https://www.python.org/downloads/
   En el instalador marca la casilla **"Add Python to PATH"**.
2. **MySQL 8** — https://dev.mysql.com/downloads/installer/
   Elige **MySQL Installer for Windows**, tipo **Developer Default**.
   Durante la instalación te pedirá una contraseña para el usuario `root`:
   apúntala, la vas a necesitar.

Para comprobar que quedaron bien, abre **PowerShell** y ejecuta:

```powershell
python --version
mysql --version
```

Deben responder con un número de versión. Si `mysql` dice "no se reconoce",
cierra y vuelve a abrir PowerShell; si sigue igual, agrega
`C:\Program Files\MySQL\MySQL Server 8.0\bin` al PATH de Windows.

---

## Paso 1. Descargar el proyecto

Opción A, con Git:

```powershell
git clone https://github.com/DavidPuente23/techtrack-sate.git
cd techtrack-sate
```

Opción B, sin Git: entra a https://github.com/DavidPuente23/techtrack-sate,
botón verde **Code** → **Download ZIP**, y descomprime el archivo.

---

## Paso 2. Instalar las dependencias de Python

Dentro de la carpeta del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Sabrás que funcionó porque el prompt empieza con `(.venv)`.

---

## Paso 3. Crear la base de datos

Desde la carpeta del proyecto, ejecuta los dos scripts. Te pedirá la
contraseña de `root` que pusiste al instalar MySQL:

```powershell
mysql -u root -p < database\schema.sql
mysql -u root -p < database\seed.sql
```

El primero crea la base `techtrack_sate` con todas las tablas y el usuario
administrador. El segundo carga los datos iniciales (departamentos, políticas,
perfiles y catálogos).

Si PowerShell se queja con el símbolo `<`, ejecuta esto en su lugar:

```powershell
cmd /c "mysql -u root -p < database\schema.sql"
cmd /c "mysql -u root -p < database\seed.sql"
```

---

## Paso 4. Configurar la conexión

Copia el archivo de ejemplo y ábrelo con el Bloc de notas:

```powershell
copy .env.example .env
notepad .env
```

Deja estos valores (cambia solo la contraseña por la tuya de MySQL):

```ini
SECRET_KEY=cualquier-texto-largo-y-raro
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=TU_CONTRASEÑA_DE_MYSQL
DB_NAME=techtrack_sate
DB_CHARSET=utf8mb4
FLASK_DEBUG=0
SESSION_COOKIE_SECURE=0
```

Guarda y cierra.

---

## Paso 5. Arrancar el sistema

```powershell
python app.py
```

Debe aparecer algo como `Running on http://127.0.0.1:5000`.
Abre esa dirección en el navegador: **http://127.0.0.1:5000**

Para detenerlo, vuelve a PowerShell y pulsa `Ctrl + C`.

---

## Paso 6. Entrar

| Campo | Valor |
|---|---|
| Correo | `admin@techtrack.com` |
| Contraseña | `Admin123!` |

---

## Paso 7 (opcional). Cargar datos de ejemplo

Si quieres ver el sistema con información realista (12 activos, mantenimientos,
incidencias e historial) y las siete cuentas de los distintos roles:

```powershell
python scripts\seed_demo.py
```

| Correo | Rol |
|---|---|
| `admin@demo.techtrack.com` | Administrador General |
| `direccion@demo.techtrack.com` | Dirección General |
| `activos@demo.techtrack.com` | Administrador de Activos |
| `redes@demo.techtrack.com` | Administrador de Redes |
| `desarrollo@demo.techtrack.com` | Desarrollador |
| `soporte@demo.techtrack.com` | Técnico de Soporte |
| `solicitante@demo.techtrack.com` | Usuario Solicitante |

Contraseña de todas: `Demo123!`

Para borrar solo esos datos de prueba: `python scripts\seed_demo.py --limpiar`

---

## Si algo falla

| Mensaje | Qué hacer |
|---|---|
| `'python' no se reconoce` | Reinstala Python marcando "Add Python to PATH" |
| `'mysql' no se reconoce` | Agrega `C:\Program Files\MySQL\MySQL Server 8.0\bin` al PATH |
| `Access denied for user 'root'` | La contraseña en `.env` no coincide con la de MySQL |
| `Can't connect to MySQL server` | El servicio MySQL no está corriendo: abre "Servicios" de Windows y arráncalo |
| `Unknown database 'techtrack_sate'` | No se ejecutó el Paso 3 |
| `Address already in use` | Otro programa usa el puerto 5000: cierra la app anterior o reinicia |
| La página carga sin estilos | Espera unos segundos y recarga con `Ctrl + F5` |

---

## Resumen de comandos

```powershell
git clone https://github.com/DavidPuente23/techtrack-sate.git
cd techtrack-sate
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
mysql -u root -p < database\schema.sql
mysql -u root -p < database\seed.sql
copy .env.example .env
python app.py
```

Documentación completa del sistema: `README.md` y `docs/Manual_Usuario_SATE.pdf`.
