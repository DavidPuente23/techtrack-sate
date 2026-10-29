# Guía de publicación de TechTrack SATE

Esta guía explica cómo subir el proyecto a GitHub y cómo obtener un enlace
público para compartirlo con tu equipo.

> **Importante:** GitHub aloja el código, pero **no ejecuta Flask ni MySQL**.
> Un repositorio de GitHub da un enlace al código, no a la página funcionando.
> Para tener un enlace como `https://techtrack-sate.onrender.com` o
> `https://tuusuario.pythonanywhere.com` hay que desplegar la aplicación en un
> servicio de hosting y usar una base de datos MySQL en la nube.

---

## 1. Subir el proyecto a GitHub

El proyecto ya está preparado como repositorio local. Solo falta crear el
repositorio remoto y hacer el primer `push`.

### 1.1 Crear el repositorio

1. Entra a <https://github.com/new>.
2. Nombre sugerido: `techtrack-sate`.
3. Déjalo **público** o privado (si es privado, invita a tu equipo en
   *Settings > Collaborators*).
4. **No** marques «Add a README», «Add .gitignore» ni «Choose a license»:
   el proyecto ya los tiene.
5. Pulsa **Create repository**.

### 1.2 Conectar y subir

En PowerShell, dentro de la carpeta del proyecto:

```powershell
cd C:\Users\pmdav\Downloads\techtrack_sate_copia

git remote add origin https://github.com/TU-USUARIO/techtrack-sate.git
git branch -M main
git push -u origin main
```

GitHub pedirá autenticación. La contraseña normal ya no sirve: usa un
**Personal Access Token** (Settings > Developer settings > Personal access
tokens > Tokens classic, permiso `repo`) o instala **GitHub CLI** y ejecuta
`gh auth login`.

### 1.3 Verificar que no se subió información sensible

```powershell
git status --ignored
```

`.env` debe aparecer como ignorado. Nunca subas ese archivo: contiene la
contraseña de MySQL y la `SECRET_KEY`.

---

## 2. Opción rápida: enlace temporal desde tu PC

Si solo necesitas mostrar la página un rato (por ejemplo, en una reunión), no
hace falta desplegar. Con la aplicación corriendo en `127.0.0.1:5000`:

### Cloudflare Tunnel (sin cuenta)

La forma más simple es el script incluido, que arranca la aplicación si hace
falta, descarga `cloudflared` y abre el túnel:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\publicar_tunel.ps1
```

También se puede hacer a mano:

```powershell
winget install Cloudflare.cloudflared
cloudflared tunnel --url http://127.0.0.1:5000
```

Cloudflare muestra una URL `https://algo.trycloudflare.com` que funciona
mientras la consola siga abierta y tu PC esté encendida. Esa URL cambia cada
vez que se reinicia el túnel, así que hay que volver a compartirla.

### ngrok (requiere cuenta gratuita)

```powershell
winget install ngrok.ngrok
ngrok config add-authtoken TU_TOKEN
ngrok http 5000
```

**Limitación:** el enlace deja de funcionar al cerrar la consola o apagar la
PC. Para un enlace permanente usa la opción 3 o 4.

---

## 3. Opción recomendada y gratuita: PythonAnywhere

PythonAnywhere ofrece Flask + MySQL en el plan gratuito, sin tarjeta, con un
dominio `https://TUUSUARIO.pythonanywhere.com`.

### 3.1 Crear la cuenta y la base de datos

1. Regístrate en <https://www.pythonanywhere.com/registration/register/beginner/>.
2. En el panel, abre **Databases > MySQL** y crea una base.
   PythonAnywhere la nombra `TUUSUARIO$techtrack_sate`.
3. Anota el host (`TUUSUARIO.mysql.pythonanywhere-services.com`), el usuario
   (`TUUSUARIO`) y la contraseña que definas.

### 3.2 Subir el código

En una consola **Bash** de PythonAnywhere:

```bash
git clone https://github.com/TU-USUARIO/techtrack-sate.git
cd techtrack-sate
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Si el repositorio es privado, configura una clave SSH o usa un token en la URL.

### 3.3 Crear las tablas

El archivo `database/schema_deploy.sql` no incluye `CREATE DATABASE` ni `USE`,
para que funcione con el nombre de base que asigna el hosting.

```bash
mysql -u TUUSUARIO -h TUUSUARIO.mysql.pythonanywhere-services.com \
  -p 'TUUSUARIO$techtrack_sate' < database/schema_deploy.sql

mysql -u TUUSUARIO -h TUUSUARIO.mysql.pythonanywhere-services.com \
  -p 'TUUSUARIO$techtrack_sate' < database/seed_deploy.sql
```

`schema_deploy.sql` y `seed_deploy.sql` son las versiones sin `CREATE DATABASE`
ni `USE`, pensadas para bases cuyo nombre ya define el hosting.

### 3.4 Configurar variables de entorno

Crea un archivo `.env` en la carpeta del proyecto en el servidor:

```bash
nano .env
```

Contenido de ejemplo:

```env
SECRET_KEY=cambia-esto-por-una-clave-larga-y-aleatoria
FLASK_DEBUG=0
SESSION_COOKIE_SECURE=1
DB_HOST=TUUSUARIO.mysql.pythonanywhere-services.com
DB_PORT=3306
DB_USER=TUUSUARIO
DB_PASSWORD=TU_PASSWORD_DE_MYSQL
DB_NAME=TUUSUARIO$techtrack_sate
```

Genera la clave con:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3.5 Crear la aplicación web

1. Abre la pestaña **Web** y pulsa **Add a new web app**.
2. Elige **Manual configuration** y la misma versión de Python del entorno.
3. En **Virtualenv**, escribe `/home/TUUSUARIO/techtrack-sate/.venv`.
4. En **WSGI configuration file**, reemplaza el contenido por:

```python
import sys

path = "/home/TUUSUARIO/techtrack-sate"
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
```

5. Pulsa **Reload** y abre `https://TUUSUARIO.pythonanywhere.com`.

### 3.6 Datos demo (opcional)

```bash
cd ~/techtrack-sate
source .venv/bin/activate
python scripts/seed_demo.py
```

Recuerda que las cuentas demo usan `Demo123!` y no deben quedar activas en un
entorno real.

---

## 4. Alternativa: Render + MySQL en la nube

Render ejecuta el servicio web gratis (se suspende tras unos minutos de
inactividad) y se conecta a una base MySQL externa, por ejemplo Aiven.

### 4.1 Base de datos

1. Crea un MySQL gratuito en <https://aiven.io/> (o usa Railway, Clever Cloud
   o el proveedor que prefieras).
2. Anota host, puerto, usuario, contraseña y nombre de la base (`defaultdb` en
   Aiven).
3. Importa el esquema:

```bash
mysql -h HOST -P PUERTO -u USUARIO -p BASE < database/schema_deploy.sql
mysql -h HOST -P PUERTO -u USUARIO -p BASE < database/seed_deploy.sql
```

Usa siempre las versiones `schema_deploy.sql` y `seed_deploy.sql`, que no
intentan crear ni seleccionar una base con un nombre fijo.

### 4.2 Servicio web en Render

1. En <https://render.com/>, **New > Web Service** y conecta el repositorio de
   GitHub.
2. Configuración:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `waitress-serve --listen=0.0.0.0:$PORT app:app`
3. En **Environment**, agrega:

```env
SECRET_KEY=una-clave-larga-y-aleatoria
FLASK_DEBUG=0
SESSION_COOKIE_SECURE=1
DB_HOST=...
DB_PORT=...
DB_USER=...
DB_PASSWORD=...
DB_NAME=...
```

4. Pulsa **Create Web Service** y espera el despliegue. Render te da una URL
   `https://techtrack-sate.onrender.com`.

El archivo `Procfile` ya contiene el comando de arranque, por si el proveedor
lo detecta automáticamente.

---

## 5. Después de publicar

- [ ] Cambiar la contraseña de `admin@techtrack.com`.
- [ ] No cargar `seed_demo.py` en producción, o ejecutarlo y luego limpiarlo.
- [ ] Verificar que el login, el panel y el reporte PDF funcionan en el dominio
      público.
- [ ] Abrir la ficha de un activo y comprobar que el QR apunta al dominio
      público (no a `127.0.0.1`).
- [ ] Configurar HTTPS (PythonAnywhere y Render lo dan gratis).
- [ ] Invitar al equipo al repositorio y compartir el enlace del sitio.

## 6. Enlaces que puedes compartir

| Recurso | Enlace |
|---|---|
| Código | `https://github.com/TU-USUARIO/techtrack-sate` |
| Sitio público | `https://TUUSUARIO.pythonanywhere.com` |
| Panel SATE | `https://TUUSUARIO.pythonanywhere.com/login` |
| Manual PDF | `https://github.com/TU-USUARIO/techtrack-sate/blob/main/docs/Manual_Usuario_SATE.pdf` |

En GitHub, el PDF se puede ver y descargar con el botón **Download raw file**.
