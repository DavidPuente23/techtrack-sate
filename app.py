from flask import (
    Flask,
    abort,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
import mysql.connector
from mysql.connector import IntegrityError
import secrets
from datetime import date
from functools import wraps
from io import BytesIO
from xml.sax.saxutils import escape
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
import qrcode
from qrcode.image.svg import SvgPathImage
from config import Config
from permisos import (
    ROL_ACTIVOS,
    ROL_ADMIN,
    ROL_DESARROLLO,
    ROL_DIRECCION,
    ROL_REDES,
    ROL_SOPORTE,
    ROL_USUARIO,
    ROLES_DESCRIPCION,
    alcance_activos,
    alcance_incidencias,
    menu_modulos,
    puede,
)
from contenido import (
    AREAS,
    CUMPLIMIENTO_PIA,
    DEPARTAMENTOS,
    EMPRESA,
    PERFILES,
    POLITICAS,
    SATE,
    matriz_politicas,
    perfil_de_departamento,
    politicas_por_participacion,
    politicas_por_responsable,
)

app = Flask(__name__)
app.config.from_object(Config)

db_config = {
    'host': app.config['DB_HOST'],
    'port': app.config['DB_PORT'],
    'user': app.config['DB_USER'],
    'password': app.config['DB_PASSWORD'],
    'database': app.config['DB_NAME'],
    'charset': app.config['DB_CHARSET'],
    'autocommit': False,
}

TEMAS_VALIDOS = {'blue', 'emerald', 'fire', 'purple'}

ESTADOS_ACTIVO = ('Operativo', 'En Mantenimiento', 'Con Falla', 'Baja')
TIPOS_ACTIVO = (
    'Laptop',
    'Computadora de Escritorio',
    'Monitor',
    'Servidor',
    'Impresora',
    'Otro',
)
ESTADOS_MANTENIMIENTO = ('Pendiente', 'En proceso', 'Finalizado')
TIPOS_MANTENIMIENTO = ('Preventivo', 'Correctivo')
ESTADOS_INCIDENCIA = ('Nueva', 'Asignada', 'En proceso', 'Resuelta', 'Cerrada')
PRIORIDADES_INCIDENCIA = ('Baja', 'Media', 'Alta', 'Crítica')

# Rutas que se pueden ver sin sesión. Si la cuenta de una sesión guardada ya no
# existe, se limpia la sesión pero la página pública sigue siendo accesible.
ENDPOINTS_PUBLICOS = {
    'inicio',
    'empresa',
    'departamentos',
    'detalle_departamento',
    'politicas',
    'detalle_politica',
    'cumplimiento_pia',
    'trabaja_con_nosotros',
    'detalle_perfil',
    'sate_info',
    'contacto',
    'privacidad',
    'login',
    'static',
}


def get_db_connection():
    return mysql.connector.connect(**db_config)


def login_required(view):
    """Exige una sesión activa."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Inicia sesión para continuar.', 'error')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped


def require_perm(modulo, accion):
    """Exige un permiso concreto de la matriz de permisos."""
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if 'usuario_id' not in session:
                flash('Inicia sesión para continuar.', 'error')
                return redirect(url_for('login'))
            if not puede(session.get('rol'), modulo, accion):
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


def filtro_departamento(campo='a.departamento_id'):
    """Devuelve un filtro SQL y sus parámetros según el alcance del rol."""
    if alcance_activos(session.get('rol')) == 'departamento':
        return f" AND {campo} = %s", (session.get('departamento_id'),)
    return "", ()


def filtro_incidencias(campo='i.solicitante_id'):
    """Devuelve un filtro SQL y sus parámetros para las incidencias visibles."""
    if alcance_incidencias(session.get('rol')) == 'propias':
        return f" AND {campo} = %s", (session.get('usuario_id'),)
    return "", ()


def activo_visible(activo):
    """Comprueba si el activo cae dentro del alcance del rol actual."""
    if alcance_activos(session.get('rol')) == 'departamento':
        return activo.get('departamento_id') == session.get('departamento_id')
    return True


def contar_administradores(cursor, excluir_id=None):
    """Cuenta administradores generales activos, opcionalmente excluyendo uno."""
    consulta = """
        SELECT COUNT(*) AS total
        FROM usuarios u
        JOIN roles r ON u.rol_id = r.id
        WHERE r.nombre = %s AND u.activo = TRUE
    """
    parametros = [ROL_ADMIN]
    if excluir_id is not None:
        consulta += " AND u.id != %s"
        parametros.append(excluir_id)
    cursor.execute(consulta, tuple(parametros))
    return cursor.fetchone()['total']



def registrar_historial(cursor, activo_id, tipo_movimiento, detalle, usuario_id=None):
    cursor.execute(
        """
        INSERT INTO historial_activos (activo_id, tipo_movimiento, detalle, usuario_id)
        VALUES (%s, %s, %s, %s)
        """,
        (activo_id, tipo_movimiento, detalle, usuario_id or session.get('usuario_id')),
    )


def registrar_auditoria(cursor, accion, entidad, entidad_id, detalle=None):
    cursor.execute(
        """
        INSERT INTO auditoria (usuario_id, accion, entidad, entidad_id, detalle)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (session.get('usuario_id'), accion, entidad, entidad_id, detalle),
    )


def generar_identificador(cursor, prefijo):
    """Genera el siguiente identificador secuencial sin reutilizar huecos."""
    cursor.execute(
        """
        SELECT COALESCE(MAX(CAST(SUBSTRING(identificador, %s) AS UNSIGNED)), 0) AS max_num
        FROM activos
        WHERE identificador LIKE %s
        """,
        (len(prefijo) + 2, f"{prefijo}-%"),
    )
    max_num = cursor.fetchone()['max_num'] or 0
    return f"{prefijo}-{max_num + 1:03d}"


def recalcular_estado_activo(cursor, activo_id):
    """Recalcula el estado del activo según mantenimientos e incidencias abiertas."""
    cursor.execute("SELECT estado FROM activos WHERE id = %s", (activo_id,))
    activo = cursor.fetchone()
    if not activo:
        return
    if activo['estado'] == 'Baja':
        return

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM mantenimientos
        WHERE activo_id = %s
          AND (estado = 'En proceso'
               OR (estado = 'Pendiente' AND fecha_programada <= CURDATE()))
        """,
        (activo_id,),
    )
    mantenimientos_abiertos = cursor.fetchone()['total']

    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM incidencias
        WHERE activo_id = %s
          AND estado IN ('Nueva', 'Asignada', 'En proceso')
        """,
        (activo_id,),
    )
    incidencias_abiertas = cursor.fetchone()['total']

    if mantenimientos_abiertos:
        nuevo_estado = 'En Mantenimiento'
    elif incidencias_abiertas:
        nuevo_estado = 'Con Falla'
    else:
        nuevo_estado = 'Operativo'

    cursor.execute(
        "UPDATE activos SET estado = %s WHERE id = %s",
        (nuevo_estado, activo_id),
    )


def texto_pdf(valor):
    """Normaliza un valor para las fuentes core de FPDF (latin-1)."""
    return str(valor if valor is not None else '').encode('latin-1', 'replace').decode('latin-1')


@app.before_request
def csrf_protect():
    if request.method == 'POST':
        token_sesion = session.get('_csrf_token')
        token_formulario = request.form.get('_csrf_token')
        if not token_sesion or not token_formulario or not secrets.compare_digest(token_sesion, token_formulario):
            abort(400, description='Token CSRF inválido o expirado. Recarga la página e inténtalo de nuevo.')


@app.before_request
def verificar_cuenta_activa():
    """Cierra la sesión si la cuenta fue desactivada o eliminada."""
    if 'usuario_id' not in session or request.endpoint == 'static':
        return None

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT activo FROM usuarios WHERE id = %s", (session['usuario_id'],))
    fila = cursor.fetchone()
    cursor.close()
    conn.close()

    if not fila or not fila['activo']:
        session.clear()
        if request.endpoint in ENDPOINTS_PUBLICOS:
            return None
        flash('Tu cuenta ya no está activa. Contacta al administrador.', 'error')
        return redirect(url_for('login'))
    return None


@app.before_request
def exigir_cambio_password():
    """Fuerza el cambio de contraseña temporal antes de usar SATE."""
    if not session.get('debe_cambiar_password'):
        return None
    permitidos = {'perfil', 'logout', 'cambiar_tema', 'static'}
    if request.endpoint in permitidos:
        return None
    flash('Debes cambiar tu contraseña temporal antes de continuar.', 'error')
    return redirect(url_for('perfil'))


@app.context_processor
def inject_common_data():
    token = session.get('_csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['_csrf_token'] = token
    return {
        'csrf_token': token,
        'app_name': app.config['APP_NAME'],
        'rol_admin': ROL_ADMIN,
        'rol_direccion': ROL_DIRECCION,
        'rol_activos': ROL_ACTIVOS,
        'rol_redes': ROL_REDES,
        'rol_desarrollo': ROL_DESARROLLO,
        'rol_tecnico': ROL_SOPORTE,
        'rol_usuario': ROL_USUARIO,
        'menu_modulos': menu_modulos(session.get('rol')),
        'puede': puede,
    }



@app.route('/')
def inicio():
    return render_template(
        'public/inicio.html',
        empresa=EMPRESA,
        sate=SATE,
        total_politicas=len(POLITICAS),
        total_perfiles=len(PERFILES),
        total_departamentos=len(DEPARTAMENTOS),
    )


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon'
    )


@app.route('/robots.txt')
def robots_txt():
    lineas = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /app/',
        'Disallow: /login',
        'Disallow: /logout',
        f'Sitemap: {url_for("sitemap_xml", _external=True)}',
    ]
    return app.response_class('\n'.join(lineas) + '\n', mimetype='text/plain')


@app.route('/sitemap.xml')
def sitemap_xml():
    hoy = date.today().isoformat()
    paginas = [
        (url_for('inicio', _external=True), '1.0', 'monthly'),
        (url_for('empresa', _external=True), '0.8', 'monthly'),
        (url_for('departamentos', _external=True), '0.8', 'monthly'),
        (url_for('politicas', _external=True), '0.8', 'monthly'),
        (url_for('trabaja_con_nosotros', _external=True), '0.7', 'monthly'),
        (url_for('sate_info', _external=True), '0.8', 'monthly'),
        (url_for('cumplimiento_pia', _external=True), '0.7', 'monthly'),
        (url_for('contacto', _external=True), '0.6', 'yearly'),
        (url_for('privacidad', _external=True), '0.3', 'yearly'),
    ]
    for slug in DEPARTAMENTOS:
        paginas.append(
            (url_for('detalle_departamento', slug=slug, _external=True), '0.6', 'monthly')
        )
    for slug in POLITICAS:
        paginas.append(
            (url_for('detalle_politica', slug=slug, _external=True), '0.6', 'monthly')
        )
    for slug in PERFILES:
        paginas.append(
            (url_for('detalle_perfil', slug=slug, _external=True), '0.5', 'monthly')
        )

    entradas = []
    for url, prioridad, frecuencia in paginas:
        entradas.append(
            '  <url>'
            f'<loc>{escape(url)}</loc>'
            f'<lastmod>{hoy}</lastmod>'
            f'<changefreq>{frecuencia}</changefreq>'
            f'<priority>{prioridad}</priority>'
            '</url>'
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(entradas)
        + '\n</urlset>\n'
    )
    return app.response_class(xml, mimetype='application/xml')


@app.route('/empresa')
def empresa():
    return render_template(
        'public/empresa.html',
        empresa=EMPRESA,
        departamentos=DEPARTAMENTOS,
        perfiles=PERFILES,
    )


@app.route('/departamentos')
def departamentos():
    return render_template(
        'public/departamentos.html',
        departamentos=DEPARTAMENTOS,
        perfiles=PERFILES,
    )


@app.route('/departamentos/<slug>')
def detalle_departamento(slug):
    departamento = DEPARTAMENTOS.get(slug)
    if not departamento:
        abort(404)

    return render_template(
        'public/departamento_detalle.html',
        departamento=departamento,
        responsables=politicas_por_responsable(slug),
        participa=politicas_por_participacion(slug),
        perfil=perfil_de_departamento(slug),
        departamentos=DEPARTAMENTOS,
    )


@app.route('/politicas')
def politicas():
    return render_template(
        'public/politicas.html',
        politicas=POLITICAS,
        matriz=matriz_politicas(),
        departamentos=DEPARTAMENTOS,
    )


@app.route('/politicas/<slug>')
def detalle_politica(slug):
    politica = POLITICAS.get(slug)
    if not politica:
        abort(404)

    return render_template(
        'public/politica_detalle.html',
        politica=politica,
        areas=AREAS,
        departamentos=DEPARTAMENTOS,
    )


@app.route('/cumplimiento-pia')
def cumplimiento_pia():
    return render_template(
        'public/cumplimiento_pia.html',
        secciones=CUMPLIMIENTO_PIA,
    )


@app.route('/trabaja-con-nosotros')
def trabaja_con_nosotros():
    return render_template(
        'public/trabaja_con_nosotros.html',
        perfiles=PERFILES,
        departamentos=DEPARTAMENTOS,
    )


@app.route('/trabaja-con-nosotros/<slug>', methods=['GET', 'POST'])
def detalle_perfil(slug):
    perfil = PERFILES.get(slug)
    if not perfil:
        abort(404)

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip().lower()
        telefono = request.form.get('telefono', '').strip() or None
        mensaje = request.form.get('mensaje', '').strip() or None
        acepta_privacidad = bool(request.form.get('acepta_privacidad'))

        if not nombre or not correo or '@' not in correo:
            flash('Nombre y correo electrónico válidos son obligatorios.', 'error')
            return redirect(url_for('detalle_perfil', slug=slug))

        if not acepta_privacidad:
            flash('Debes aceptar el aviso de privacidad para enviar tu postulación.', 'error')
            return redirect(url_for('detalle_perfil', slug=slug))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO postulaciones
                (puesto_id, nombre, correo, telefono, mensaje, acepta_privacidad)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (slug, nombre, correo, telefono, mensaje, acepta_privacidad),
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash('¡Postulación enviada correctamente! Evaluaremos tu perfil.', 'success')
        return redirect(url_for('detalle_perfil', slug=slug))

    return render_template(
        'public/detalle_perfil.html',
        perfil=perfil,
        departamentos=DEPARTAMENTOS,
    )


# Rutas antiguas: se conservan como redirecciones permanentes para no romper
# enlaces existentes ni marcadores de los usuarios.
@app.route('/vacantes')
def vacantes_legacy():
    return redirect(url_for('trabaja_con_nosotros'), code=301)


@app.route('/vacantes/<slug>', methods=['GET', 'POST'])
def detalle_vacante_legacy(slug):
    codigo = 308 if request.method == 'POST' else 301
    return redirect(url_for('detalle_perfil', slug=slug), code=codigo)


@app.route('/sate')
def sate_info():
    return render_template('public/sate_info.html', sate=SATE, empresa=EMPRESA)

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        organizacion = request.form.get('organizacion', '').strip()
        correo = request.form.get('correo', '').strip().lower()
        telefono = request.form.get('telefono', '').strip() or None
        motivo = request.form.get('motivo', '').strip()
        mensaje = request.form.get('mensaje', '').strip()
        acepta_privacidad = bool(request.form.get('acepta_privacidad'))

        if not nombre or not organizacion or not correo or '@' not in correo or not motivo or not mensaje:
            flash('Revisa los campos obligatorios del formulario.', 'error')
            return redirect(url_for('contacto'))

        if not acepta_privacidad:
            flash('Debes aceptar el aviso de privacidad para enviar el mensaje.', 'error')
            return redirect(url_for('contacto'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO mensajes_contacto
                (nombre, organizacion, correo, telefono, motivo, mensaje, acepta_privacidad)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (nombre, organizacion, correo, telefono, motivo, mensaje, acepta_privacidad),
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash('¡Mensaje enviado correctamente! Nos pondremos en contacto contigo pronto.', 'success')
        return redirect(url_for('contacto'))

    return render_template('public/contacto.html')

@app.route('/privacidad')
def privacidad():
    return render_template('public/privacidad.html')

@app.after_request
def add_security_headers(response):
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    response.headers.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
    response.headers.setdefault(
        'Content-Security-Policy',
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com https://cdn.datatables.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.datatables.net https://fonts.googleapis.com; "
        "font-src 'self' data: https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self' https://cdn.datatables.net; "
        "frame-ancestors 'self'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )
    if request.is_secure:
        response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
    return response


@app.errorhandler(400)
def bad_request(e):
    return render_template('public/400.html', error=e), 400


@app.errorhandler(403)
def forbidden(e):
    return render_template('public/403.html', error=e), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template('public/404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('public/500.html'), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT u.*, r.nombre AS rol_nombre
            FROM usuarios u
            LEFT JOIN roles r ON u.rol_id = r.id
            WHERE u.email = %s
            """,
            (email,),
        )
        usuario = cursor.fetchone()

        cursor.close()
        conn.close()

        try:
            password_ok = bool(usuario) and check_password_hash(usuario['password'], password)
        except (ValueError, TypeError):
            password_ok = False

        if not password_ok:
            flash('Correo o contraseña incorrectos.', 'error')
            return redirect(url_for('login'))

        if not usuario['activo']:
            flash('Tu usuario está desactivado. Contacta al administrador.', 'error')
            return redirect(url_for('login'))

        session.clear()
        session['usuario_id'] = usuario['id']
        session['nombre'] = usuario['nombre']
        session['rol'] = usuario['rol_nombre'] or ROL_USUARIO
        session['departamento_id'] = usuario['departamento_id']
        session['tema'] = usuario['tema'] if usuario['tema'] in TEMAS_VALIDOS else 'blue'
        session['debe_cambiar_password'] = bool(usuario.get('debe_cambiar_password'))
        session.permanent = True

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s", (usuario['id'],))
        conn.commit()
        cursor.close()
        conn.close()

        if session['debe_cambiar_password']:
            flash('Tu contraseña es temporal. Cámbiala para continuar.', 'error')
            return redirect(url_for('perfil'))

        return redirect(url_for('dashboard'))

    return render_template('sate/login.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/app/dashboard')
@require_perm('panel', 'ver')
def dashboard():
    rol = session.get('rol')
    ver_activos = puede(rol, 'activos', 'ver')
    ver_mantenimientos = puede(rol, 'mantenimientos', 'ver')
    ver_incidencias = puede(rol, 'incidencias', 'ver')
    ver_usuarios = puede(rol, 'usuarios', 'ver')
    es_solicitante = alcance_activos(rol) == 'departamento'

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    filtro_act, params_act = filtro_departamento('a.departamento_id')
    filtro_inc, params_inc = filtro_incidencias('i.solicitante_id')

    cursor.execute(
        f"SELECT COUNT(*) AS total FROM activos a WHERE a.estado != 'Baja'{filtro_act}",
        params_act,
    )
    total_activos = cursor.fetchone()['total']

    cursor.execute(
        f"SELECT COUNT(*) AS total FROM activos a WHERE a.estado = 'Operativo'{filtro_act}",
        params_act,
    )
    activos_operativos = cursor.fetchone()['total']

    mants_pendientes = 0
    alertas_mant = 0
    mants_proximos = 0
    if ver_mantenimientos:
        cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM mantenimientos m
            JOIN activos a ON m.activo_id = a.id
            WHERE m.estado != 'Finalizado'{filtro_act}
            """,
            params_act,
        )
        mants_pendientes = cursor.fetchone()['total']

        cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM mantenimientos m
            JOIN activos a ON m.activo_id = a.id
            WHERE m.fecha_programada < CURDATE()
              AND m.estado != 'Finalizado'{filtro_act}
            """,
            params_act,
        )
        alertas_mant = cursor.fetchone()['total']

        cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM mantenimientos m
            JOIN activos a ON m.activo_id = a.id
            WHERE m.fecha_programada BETWEEN CURDATE()
                  AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
              AND m.estado != 'Finalizado'{filtro_act}
            """,
            params_act,
        )
        mants_proximos = cursor.fetchone()['total']

    incidencias_abiertas = 0
    alertas_inc = 0
    if ver_incidencias:
        cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM incidencias i
            WHERE i.estado NOT IN ('Resuelta', 'Cerrada'){filtro_inc}
            """,
            params_inc,
        )
        incidencias_abiertas = cursor.fetchone()['total']

        cursor.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM incidencias i
            WHERE i.prioridad = 'Crítica'
              AND i.estado NOT IN ('Resuelta', 'Cerrada')
              AND i.fecha_registro <= NOW() - INTERVAL 1 DAY{filtro_inc}
            """,
            params_inc,
        )
        alertas_inc = cursor.fetchone()['total']

    usuarios_activos = 0
    if ver_usuarios:
        cursor.execute("SELECT COUNT(*) AS total FROM usuarios WHERE activo = TRUE")
        usuarios_activos = cursor.fetchone()['total']

    cursor.execute(
        f"SELECT a.estado, COUNT(*) AS cantidad FROM activos a WHERE 1 = 1{filtro_act} GROUP BY a.estado",
        params_act,
    )
    datos_estados = cursor.fetchall()
    nombres_estados = [fila['estado'] for fila in datos_estados]
    cantidades_estados = [fila['cantidad'] for fila in datos_estados]

    nombres_estados_inc = []
    cantidades_estados_inc = []
    if ver_incidencias:
        cursor.execute(
            f"""
            SELECT i.estado, COUNT(*) AS cantidad
            FROM incidencias i
            WHERE 1 = 1{filtro_inc}
            GROUP BY i.estado
            """,
            params_inc,
        )
        datos_estados_inc = cursor.fetchall()
        nombres_estados_inc = [fila['estado'] for fila in datos_estados_inc]
        cantidades_estados_inc = [fila['cantidad'] for fila in datos_estados_inc]
    total_incidencias = sum(cantidades_estados_inc)

    actividad_incidencias = []
    if ver_incidencias:
        cursor.execute(
            f"""
            SELECT i.id, i.descripcion, i.estado, i.prioridad, i.fecha_registro,
                   a.nombre AS activo_nombre
            FROM incidencias i
            JOIN activos a ON i.activo_id = a.id
            WHERE 1 = 1{filtro_inc}
            ORDER BY i.fecha_registro DESC, i.id DESC
            LIMIT 4
            """,
            params_inc,
        )
        actividad_incidencias = cursor.fetchall()

    actividad_mantenimientos = []
    if ver_mantenimientos:
        cursor.execute(
            f"""
            SELECT m.id, m.tipo, m.estado, m.fecha_programada,
                   a.nombre AS activo_nombre
            FROM mantenimientos m
            JOIN activos a ON m.activo_id = a.id
            WHERE m.estado != 'Finalizado'{filtro_act}
            ORDER BY m.fecha_programada ASC, m.id ASC
            LIMIT 4
            """,
            params_act,
        )
        actividad_mantenimientos = cursor.fetchall()

    actividad_activos = []
    if ver_activos:
        cursor.execute(
            f"""
            SELECT h.activo_id, h.tipo_movimiento, h.detalle, h.fecha,
                   a.nombre AS activo_nombre,
                   u.nombre AS usuario_nombre
            FROM historial_activos h
            JOIN activos a ON h.activo_id = a.id
            LEFT JOIN usuarios u ON h.usuario_id = u.id
            WHERE 1 = 1{filtro_act}
            ORDER BY h.fecha DESC, h.id DESC
            LIMIT 4
            """,
            params_act,
        )
        actividad_activos = cursor.fetchall()

    departamento_nombre = None
    if es_solicitante and session.get('departamento_id'):
        cursor.execute(
            "SELECT nombre FROM departamentos WHERE id = %s",
            (session['departamento_id'],),
        )
        fila_departamento = cursor.fetchone()
        departamento_nombre = fila_departamento['nombre'] if fila_departamento else None

    cursor.close()
    conn.close()

    return render_template(
        'sate/dashboard.html',
        nombre=session['nombre'],
        descripcion_rol=ROLES_DESCRIPCION.get(rol, ''),
        es_solicitante=es_solicitante,
        departamento_nombre=departamento_nombre,
        total_activos=total_activos,
        activos_operativos=activos_operativos,
        mants_pendientes=mants_pendientes,
        mants_proximos=mants_proximos,
        incidencias_abiertas=incidencias_abiertas,
        usuarios_activos=usuarios_activos,
        alertas_mant=alertas_mant,
        alertas_inc=alertas_inc,
        nombres_estados=nombres_estados,
        cantidades_estados=cantidades_estados,
        nombres_estados_inc=nombres_estados_inc,
        cantidades_estados_inc=cantidades_estados_inc,
        total_incidencias=total_incidencias,
        actividad_incidencias=actividad_incidencias,
        actividad_mantenimientos=actividad_mantenimientos,
        actividad_activos=actividad_activos,
    )

@app.route('/app/activos')
@require_perm('activos', 'ver')
def activos():
    q = request.args.get('q', '').strip()[:100]
    estado = request.args.get('estado', '').strip()
    tipo = request.args.get('tipo', '').strip()
    departamento_id = request.args.get('departamento_id', '').strip()

    if estado not in ESTADOS_ACTIVO:
        estado = ''
    if tipo not in TIPOS_ACTIVO:
        tipo = ''
    if not departamento_id.isdigit():
        departamento_id = ''

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    filtro, params = filtro_departamento('a.departamento_id')
    params = list(params)

    consulta = """
        SELECT a.*, d.nombre AS departamento_nombre
        FROM activos a
        LEFT JOIN departamentos d ON a.departamento_id = d.id
        WHERE 1 = 1
    """
    consulta += filtro

    if q:
        consulta += """
            AND (a.nombre LIKE %s OR a.identificador LIKE %s
                 OR a.responsable LIKE %s OR a.marca LIKE %s
                 OR a.modelo LIKE %s OR a.numero_serie LIKE %s)
        """
        like = f"%{q}%"
        params.extend([like] * 6)
    if estado:
        consulta += " AND a.estado = %s"
        params.append(estado)
    if tipo:
        consulta += " AND a.tipo = %s"
        params.append(tipo)
    if departamento_id:
        consulta += " AND a.departamento_id = %s"
        params.append(int(departamento_id))

    consulta += " ORDER BY a.id DESC"
    cursor.execute(consulta, tuple(params))
    lista_activos = cursor.fetchall()

    cursor.execute("SELECT id, nombre FROM departamentos ORDER BY nombre")
    departamentos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'sate/activos.html',
        activos=lista_activos,
        departamentos=departamentos,
        estados=ESTADOS_ACTIVO,
        tipos=TIPOS_ACTIVO,
        filtros={
            'q': q,
            'estado': estado,
            'tipo': tipo,
            'departamento_id': departamento_id,
        },
    )

@app.route('/app/activos/reporte')
@require_perm('activos', 'ver')
def reporte_inventario():
    q = request.args.get('q', '').strip()[:100]
    estado = request.args.get('estado', '').strip()
    tipo = request.args.get('tipo', '').strip()
    departamento_id = request.args.get('departamento_id', '').strip()

    if estado not in ESTADOS_ACTIVO:
        estado = ''
    if tipo not in TIPOS_ACTIVO:
        tipo = ''
    if not departamento_id.isdigit():
        departamento_id = ''

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    filtro, params = filtro_departamento('a.departamento_id')
    params = list(params)

    consulta = """
        SELECT a.*, d.nombre AS departamento_nombre
        FROM activos a
        LEFT JOIN departamentos d ON a.departamento_id = d.id
        WHERE 1 = 1
    """
    consulta += filtro

    if q:
        consulta += """
            AND (a.nombre LIKE %s OR a.identificador LIKE %s
                 OR a.responsable LIKE %s OR a.marca LIKE %s
                 OR a.modelo LIKE %s OR a.numero_serie LIKE %s)
        """
        like = f"%{q}%"
        params.extend([like] * 6)
    if estado:
        consulta += " AND a.estado = %s"
        params.append(estado)
    if tipo:
        consulta += " AND a.tipo = %s"
        params.append(tipo)
    if departamento_id:
        consulta += " AND a.departamento_id = %s"
        params.append(int(departamento_id))

    consulta += " ORDER BY d.nombre ASC, a.nombre ASC"
    cursor.execute(consulta, tuple(params))
    lista_activos = cursor.fetchall()
    cursor.close()
    conn.close()

    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    pdf.set_font('Arial', 'B', 15)
    pdf.cell(0, 9, texto_pdf('TechTrack Solutions'), ln=True, align='C')
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, texto_pdf('Reporte de inventario de activos tecnológicos'), ln=True, align='C')
    pdf.set_font('Arial', '', 9)
    pdf.cell(
        0,
        6,
        texto_pdf(
            f'Generado el {date.today().strftime("%d/%m/%Y")} · '
            f'{len(lista_activos)} activo(s)'
        ),
        ln=True,
        align='C',
    )

    resumen = []
    if q:
        resumen.append(f'Búsqueda: {q}')
    if estado:
        resumen.append(f'Estado: {estado}')
    if tipo:
        resumen.append(f'Tipo: {tipo}')
    if departamento_id:
        resumen.append('Departamento filtrado')
    if resumen:
        pdf.ln(2)
        pdf.set_font('Arial', 'I', 9)
        pdf.cell(0, 5, texto_pdf('Filtros: ' + ' · '.join(resumen)), ln=True)

    anchos = [28, 62, 40, 42, 50, 33]
    encabezados = ['ID', 'Nombre', 'Tipo', 'Departamento', 'Responsable', 'Estado']

    def cabecera():
        pdf.set_font('Arial', 'B', 9)
        pdf.set_fill_color(230, 230, 230)
        for ancho, titulo in zip(anchos, encabezados):
            pdf.cell(ancho, 7, texto_pdf(titulo), border=1, align='C', fill=True)
        pdf.ln()

    pdf.ln(3)
    cabecera()
    pdf.set_font('Arial', '', 8)

    for activo in lista_activos:
        if pdf.get_y() > 185:
            pdf.add_page()
            cabecera()
            pdf.set_font('Arial', '', 8)

        valores = [
            activo['identificador'] or activo['id'],
            activo['nombre'],
            activo['tipo'],
            activo['departamento_nombre'] or 'Sin departamento',
            activo['responsable'],
            activo['estado'],
        ]
        for ancho, valor in zip(anchos, valores):
            pdf.cell(ancho, 6, texto_pdf(valor), border=1)
        pdf.ln()

    if not lista_activos:
        pdf.set_font('Arial', 'I', 9)
        pdf.cell(0, 8, texto_pdf('No hay activos que coincidan con los filtros.'), ln=True)

    pdf.ln(3)
    pdf.set_font('Arial', 'I', 7)
    pdf.cell(
        0,
        5,
        texto_pdf('Documento generado por SATE · TechTrack Solutions'),
        ln=True,
        align='R',
    )

    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=Reporte_Inventario.pdf'
    response.headers['X-Activos-Reporte'] = str(len(lista_activos))
    return response


@app.route('/app/activos/nuevo', methods=['GET', 'POST'])
@require_perm('activos', 'crear')
def nuevo_activo():
    conn = get_db_connection()

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        tipo = request.form.get('tipo', '').strip()
        marca = request.form.get('marca', '').strip() or None
        modelo = request.form.get('modelo', '').strip() or None
        numero_serie = request.form.get('numero_serie', '').strip() or None
        ubicacion = request.form.get('ubicacion', '').strip() or None
        responsable = request.form.get('responsable', '').strip()
        departamento_id = request.form.get('departamento_id', '').strip()

        if not nombre or not tipo or not responsable or not departamento_id:
            flash('Nombre, tipo, responsable y departamento son obligatorios.', 'error')
            conn.close()
            return redirect(url_for('nuevo_activo'))

        try:
            departamento_id = int(departamento_id)
        except ValueError:
            flash('Departamento no válido.', 'error')
            conn.close()
            return redirect(url_for('nuevo_activo'))

        prefijos = {
            'Laptop': 'LAP',
            'Computadora de Escritorio': 'COM',
            'Monitor': 'MON',
            'Servidor': 'SRV',
            'Impresora': 'IMP',
            'Otro': 'OTR',
        }
        if tipo not in prefijos:
            tipo = 'Otro'
        prefijo = prefijos[tipo]

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM departamentos WHERE id = %s", (departamento_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            flash('El departamento seleccionado no existe.', 'error')
            return redirect(url_for('nuevo_activo'))

        identificador = None
        activo_id = None
        for intento in range(5):
            identificador = generar_identificador(cursor, prefijo)
            try:
                cursor.execute(
                    """
                    INSERT INTO activos
                        (identificador, nombre, tipo, marca, modelo, numero_serie,
                         ubicacion, responsable, departamento_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (identificador, nombre, tipo, marca, modelo, numero_serie,
                     ubicacion, responsable, departamento_id),
                )
                activo_id = cursor.lastrowid
                break
            except IntegrityError:
                conn.rollback()
                if intento == 4:
                    cursor.close()
                    conn.close()
                    flash('No se pudo generar un identificador único. Inténtalo de nuevo.', 'error')
                    return redirect(url_for('nuevo_activo'))

        registrar_historial(
            cursor,
            activo_id,
            'Alta de activo',
            f'Activo registrado con identificador {identificador} en {ubicacion or "sin ubicación"}.',
        )
        registrar_auditoria(cursor, 'Crear', 'Activo', activo_id, f'{identificador} - {nombre}')

        conn.commit()
        cursor.close()
        conn.close()

        flash(f'Activo registrado correctamente con el ID: {identificador}', 'success')
        return redirect(url_for('detalle_activo', id=activo_id))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM departamentos ORDER BY nombre")
    departamentos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('sate/nuevo_activo.html', departamentos=departamentos)

@app.route('/app/activos/<int:id>')
@require_perm('activos', 'ver')
def detalle_activo(id):
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT a.*, d.nombre as departamento_nombre 
        FROM activos a 
        LEFT JOIN departamentos d ON a.departamento_id = d.id
        WHERE a.id = %s
    """, (id,))
    activo = cursor.fetchone()

    if not activo:
        cursor.close()
        conn.close()
        abort(404)

    if not activo_visible(activo):
        cursor.close()
        conn.close()
        abort(403)

    cursor.execute("""
        SELECT h.fecha, h.tipo_movimiento, h.detalle, u.nombre as usuario
        FROM historial_activos h
        LEFT JOIN usuarios u ON h.usuario_id = u.id
        WHERE h.activo_id = %s
        ORDER BY h.fecha DESC, h.id DESC
    """, (id,))
    historial = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template(
        'sate/detalle_activo.html',
        activo=activo,
        historial=historial,
        total_historial=len(historial),
        ultimo_movimiento=historial[0]['fecha'] if historial else None,
    )

@app.route('/app/activos/<int:id>/resguardo')
@require_perm('activos', 'editar')
def generar_resguardo(id):
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, d.nombre as departamento_nombre 
        FROM activos a 
        LEFT JOIN departamentos d ON a.departamento_id = d.id
        WHERE a.id = %s
    """, (id,))
    activo = cursor.fetchone()
    cursor.close()
    conn.close()

    if not activo:
        return "Activo no encontrado", 404

    if not activo_visible(activo):
        abort(403)

    # Construcción del PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Título
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="TechTrack Solutions", ln=True, align='C')
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt="Acta de Resguardo de Equipo Tecnológico", ln=True, align='C')
    
    # Párrafo introductorio
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    texto_intro = f"Por medio del presente documento, se hace constar la entrega formal del equipo tecnológico a {activo['responsable']}, quien asume la responsabilidad de su uso, cuidado y salvaguarda bajo las políticas establecidas por la empresa."
    pdf.multi_cell(0, 8, txt=texto_intro)
    
    # Detalles del equipo
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Especificaciones Técnicas del Activo:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, txt=f"Identificador: {activo['identificador'] or activo['id']}", ln=True)
    pdf.cell(0, 8, txt=f"Nombre del Equipo: {activo['nombre']}", ln=True)
    pdf.cell(0, 8, txt=f"Categoría: {activo['tipo']}", ln=True)
    pdf.cell(0, 8, txt=f"Marca y Modelo: {activo['marca']} / {activo['modelo']}", ln=True)
    pdf.cell(0, 8, txt=f"Número de Serie: {activo['numero_serie']}", ln=True)
    pdf.cell(0, 8, txt=f"Departamento Asignado: {activo['departamento_nombre']}", ln=True)
    
    # Párrafo legal
    pdf.ln(10)
    texto_legal = "El usuario se compromete a reportar inmediatamente cualquier anomalía al departamento de Soporte mediante la plataforma SATE y a devolver el equipo en las mismas condiciones funcionales al término de sus labores."
    pdf.multi_cell(0, 8, txt=texto_legal)
    
    # Firmas
    pdf.ln(30)
    pdf.cell(95, 10, txt="_______________________________", ln=False, align='C')
    pdf.cell(95, 10, txt="_______________________________", ln=True, align='C')
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(95, 5, txt=f"Firma de Aceptación", ln=False, align='C')
    pdf.cell(95, 5, txt="Autoriza", ln=True, align='C')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(95, 5, txt=f"{activo['responsable']}", ln=False, align='C')
    pdf.cell(95, 5, txt="David Puente Muñiz - SIT", ln=True, align='C')

    # Enviar el archivo al navegador
    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Resguardo_{activo["identificador"] or activo["id"]}.pdf'
    return response

@app.route('/app/activos/<int:id>/qr.svg')
@require_perm('activos', 'ver')
def qr_activo(id):
    """Genera el código QR que abre la ficha del activo."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM activos WHERE id = %s", (id,))
    activo = cursor.fetchone()
    cursor.close()
    conn.close()

    if not activo:
        abort(404)
    if not activo_visible(activo):
        abort(403)

    destino = url_for('detalle_activo', id=activo['id'], _external=True)
    qr = qrcode.make(destino, image_factory=SvgPathImage, box_size=10, border=2)
    salida = BytesIO()
    qr.save(salida)

    respuesta = make_response(salida.getvalue())
    respuesta.headers['Content-Type'] = 'image/svg+xml'
    respuesta.headers['Cache-Control'] = 'private, max-age=3600'
    return respuesta

@app.route('/app/activos/<int:id>/etiqueta')
@require_perm('activos', 'ver')
def etiqueta_activo(id):
    """Etiqueta imprimible con el QR y los datos del activo."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, d.nombre as departamento_nombre
        FROM activos a
        LEFT JOIN departamentos d ON a.departamento_id = d.id
        WHERE a.id = %s
    """, (id,))
    activo = cursor.fetchone()
    cursor.close()
    conn.close()

    if not activo:
        abort(404)
    if not activo_visible(activo):
        abort(403)

    return render_template('sate/etiqueta_activo.html', activo=activo)

@app.route('/app/activos/<int:id>/editar', methods=['GET', 'POST'])
@require_perm('activos', 'editar')
def editar_activo(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM activos WHERE id = %s", (id,))
    activo = cursor.fetchone()
    if not activo:
        cursor.close()
        conn.close()
        abort(404)

    if not activo_visible(activo):
        cursor.close()
        conn.close()
        abort(403)

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        ubicacion = request.form.get('ubicacion', '').strip() or None
        responsable = request.form.get('responsable', '').strip()
        departamento_id = request.form.get('departamento_id', '').strip()
        estado = request.form.get('estado', '').strip()
        estados_validos = set(ESTADOS_ACTIVO)

        if not nombre or not responsable or not departamento_id or estado not in estados_validos:
            flash('Revisa los campos obligatorios y el estado del activo.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('editar_activo', id=id))

        try:
            departamento_id = int(departamento_id)
        except ValueError:
            flash('Departamento no válido.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('editar_activo', id=id))

        cursor.execute("SELECT id, nombre FROM departamentos WHERE id = %s", (departamento_id,))
        depto_nuevo = cursor.fetchone()
        if not depto_nuevo:
            flash('El departamento seleccionado no existe.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('editar_activo', id=id))

        cursor.execute(
            "SELECT nombre FROM departamentos WHERE id = %s",
            (activo['departamento_id'],),
        )
        depto_anterior = cursor.fetchone()
        nombre_depto_anterior = depto_anterior['nombre'] if depto_anterior else '—'

        cambios = []
        if activo['nombre'] != nombre:
            cambios.append(f"Nombre: «{activo['nombre']}» → «{nombre}»")
        if (activo['ubicacion'] or None) != (ubicacion or None):
            cambios.append(
                f"Ubicación: «{activo['ubicacion'] or 'sin ubicación'}» → "
                f"«{ubicacion or 'sin ubicación'}»"
            )
        if activo['responsable'] != responsable:
            cambios.append(
                f"Responsable: «{activo['responsable'] or '—'}» → «{responsable}»"
            )
        if activo['departamento_id'] != departamento_id:
            cambios.append(
                f"Departamento: «{nombre_depto_anterior}» → «{depto_nuevo['nombre']}»"
            )
        if activo['estado'] != estado:
            cambios.append(f"Estado: «{activo['estado']}» → «{estado}»")

        if not cambios:
            cursor.close()
            conn.close()
            flash('No se detectaron cambios en el activo.', 'info')
            return redirect(url_for('detalle_activo', id=id))

        cursor.execute(
            """
            UPDATE activos
            SET nombre = %s, ubicacion = %s, responsable = %s,
                departamento_id = %s, estado = %s
            WHERE id = %s
            """,
            (nombre, ubicacion, responsable, departamento_id, estado, id),
        )

        detalle_cambio = '; '.join(cambios)
        registrar_historial(cursor, id, 'Actualización de datos', detalle_cambio)
        registrar_auditoria(cursor, 'Editar', 'Activo', id, detalle_cambio)

        conn.commit()
        cursor.close()
        conn.close()

        flash('Activo actualizado y registrado en el historial correctamente.', 'success')
        return redirect(url_for('detalle_activo', id=id))

    cursor.execute("SELECT * FROM departamentos ORDER BY nombre")
    departamentos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('sate/editar_activo.html', activo=activo, departamentos=departamentos)

# ==========================================
# MÓDULO DE MANTENIMIENTOS
# ==========================================

@app.route('/app/mantenimientos')
@require_perm('mantenimientos', 'ver')
def mantenimientos():
    q = request.args.get('q', '').strip()[:100]
    estado = request.args.get('estado', '').strip()
    tipo = request.args.get('tipo', '').strip()
    vencimiento = request.args.get('vencimiento', '').strip()

    if estado not in ESTADOS_MANTENIMIENTO:
        estado = ''
    if tipo not in TIPOS_MANTENIMIENTO:
        tipo = ''
    if vencimiento not in ('7', 'vencidos'):
        vencimiento = ''

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    consulta = """
        SELECT m.*, a.nombre AS activo_nombre,
               a.identificador AS activo_identificador
        FROM mantenimientos m
        JOIN activos a ON m.activo_id = a.id
        WHERE 1 = 1
    """
    params = []

    if q:
        consulta += """
            AND (a.nombre LIKE %s OR a.identificador LIKE %s
                 OR m.descripcion LIKE %s OR m.responsable LIKE %s)
        """
        like = f"%{q}%"
        params.extend([like] * 4)
    if estado:
        consulta += " AND m.estado = %s"
        params.append(estado)
    if tipo:
        consulta += " AND m.tipo = %s"
        params.append(tipo)
    if vencimiento == '7':
        consulta += """
            AND m.fecha_programada BETWEEN CURDATE()
                AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            AND m.estado != 'Finalizado'
        """
    elif vencimiento == 'vencidos':
        consulta += " AND m.fecha_programada < CURDATE() AND m.estado != 'Finalizado'"

    consulta += " ORDER BY m.fecha_programada ASC, m.id ASC"
    cursor.execute(consulta, tuple(params))
    lista_mantenimientos = cursor.fetchall()

    mantenimientos_json = [
        {
            'tipo': mant['tipo'],
            'estado': mant['estado'],
            'fecha_str': mant['fecha_programada'].strftime('%Y-%m-%d'),
            'activo_nombre': mant['activo_nombre'],
        }
        for mant in lista_mantenimientos
    ]

    cursor.close()
    conn.close()

    return render_template(
        'sate/mantenimientos.html',
        mantenimientos=lista_mantenimientos,
        mantenimientos_json=mantenimientos_json,
        estados=ESTADOS_MANTENIMIENTO,
        tipos=TIPOS_MANTENIMIENTO,
        filtros={'q': q, 'estado': estado, 'tipo': tipo, 'vencimiento': vencimiento},
    )


@app.route('/app/mantenimientos/<int:id>')
@require_perm('mantenimientos', 'ver')
def detalle_mantenimiento(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT m.*, a.nombre AS activo_nombre, a.identificador AS activo_identificador,
               a.tipo AS activo_tipo, a.responsable AS activo_responsable,
               a.ubicacion AS activo_ubicacion, a.estado AS activo_estado,
               d.nombre AS departamento_nombre
        FROM mantenimientos m
        JOIN activos a ON m.activo_id = a.id
        LEFT JOIN departamentos d ON a.departamento_id = d.id
        WHERE m.id = %s
        """,
        (id,),
    )
    mantenimiento = cursor.fetchone()
    cursor.close()
    conn.close()

    if not mantenimiento:
        abort(404)

    return render_template('sate/detalle_mantenimiento.html', mantenimiento=mantenimiento)

@app.route('/app/mantenimientos/nuevo', methods=['GET', 'POST'])
@require_perm('mantenimientos', 'crear')
def nuevo_mantenimiento():
    conn = get_db_connection()

    if request.method == 'POST':
        activo_id = request.form.get('activo_id', '').strip()
        tipo = request.form.get('tipo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        fecha_programada = request.form.get('fecha_programada', '').strip()
        responsable = request.form.get('responsable', '').strip()

        if tipo not in {'Preventivo', 'Correctivo'} or not descripcion or not fecha_programada or not responsable:
            flash('Revisa el tipo, la descripción, la fecha y el responsable.', 'error')
            conn.close()
            return redirect(url_for('nuevo_mantenimiento'))

        try:
            activo_id = int(activo_id)
            fecha_programada = date.fromisoformat(fecha_programada)
        except (ValueError, TypeError):
            flash('Activo o fecha no válidos.', 'error')
            conn.close()
            return redirect(url_for('nuevo_mantenimiento'))

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, estado FROM activos WHERE id = %s", (activo_id,))
        activo = cursor.fetchone()
        if not activo or activo['estado'] == 'Baja':
            cursor.close()
            conn.close()
            flash('El activo seleccionado no existe o está dado de baja.', 'error')
            return redirect(url_for('nuevo_mantenimiento'))

        cursor.execute(
            """
            INSERT INTO mantenimientos
                (activo_id, tipo, descripcion, fecha_programada, responsable)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (activo_id, tipo, descripcion, fecha_programada, responsable),
        )
        mantenimiento_id = cursor.lastrowid

        recalcular_estado_activo(cursor, activo_id)
        registrar_historial(
            cursor,
            activo_id,
            'Mantenimiento programado',
            f'{tipo}: {descripcion}. Fecha: {fecha_programada}. Responsable: {responsable}.',
        )
        registrar_auditoria(
            cursor,
            'Crear',
            'Mantenimiento',
            mantenimiento_id,
            f'Activo {activo_id} - {tipo} - {fecha_programada}',
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash('Mantenimiento programado correctamente.', 'success')
        return redirect(url_for('mantenimientos'))

    # GET: activos disponibles
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, marca, modelo FROM activos WHERE estado != 'Baja' ORDER BY nombre")
    activos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('sate/nuevo_mantenimiento.html', activos=activos)


@app.route('/app/mantenimientos/<int:id>/editar', methods=['GET', 'POST'])
@require_perm('mantenimientos', 'editar')
def editar_mantenimiento(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM mantenimientos WHERE id = %s", (id,))
    mantenimiento = cursor.fetchone()
    if not mantenimiento:
        cursor.close()
        conn.close()
        abort(404)

    if request.method == 'POST':
        nuevo_estado = request.form.get('estado', '').strip()
        observaciones = request.form.get('observaciones', '').strip() or None
        estados_validos = {'Pendiente', 'En proceso', 'Finalizado'}

        if nuevo_estado not in estados_validos:
            flash('Estado de mantenimiento no válido.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('editar_mantenimiento', id=id))

        cursor.execute(
            """
            UPDATE mantenimientos
            SET estado = %s,
                observaciones = %s,
                fecha_finalizacion = CASE
                    WHEN %s = 'Finalizado' THEN COALESCE(fecha_finalizacion, NOW())
                    ELSE NULL
                END
            WHERE id = %s
            """,
            (nuevo_estado, observaciones, nuevo_estado, id),
        )

        recalcular_estado_activo(cursor, mantenimiento['activo_id'])
        registrar_historial(
            cursor,
            mantenimiento['activo_id'],
            'Mantenimiento actualizado',
            f'Estado: {nuevo_estado}. Observaciones: {observaciones or "sin observaciones"}.',
        )
        registrar_auditoria(
            cursor,
            'Editar',
            'Mantenimiento',
            id,
            f'Estado: {nuevo_estado}',
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash('Mantenimiento actualizado correctamente.', 'success')
        return redirect(url_for('mantenimientos'))

    cursor.close()
    conn.close()

    return render_template('sate/editar_mantenimiento.html', mantenimiento=mantenimiento)

# ==========================================
# MÓDULO DE INCIDENCIAS
# ==========================================

@app.route('/app/incidencias')
@require_perm('incidencias', 'ver')
def incidencias():
    q = request.args.get('q', '').strip()[:100]
    estado = request.args.get('estado', '').strip()
    prioridad = request.args.get('prioridad', '').strip()

    if estado not in ESTADOS_INCIDENCIA:
        estado = ''
    if prioridad not in PRIORIDADES_INCIDENCIA:
        prioridad = ''

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    filtro, params = filtro_incidencias('i.solicitante_id')
    consulta = """
        SELECT i.*, a.nombre AS activo_nombre,
               a.identificador AS activo_identificador,
               u.nombre AS solicitante_nombre
        FROM incidencias i
        JOIN activos a ON i.activo_id = a.id
        LEFT JOIN usuarios u ON i.solicitante_id = u.id
        WHERE 1 = 1
    """
    consulta += filtro
    params = list(params)

    if q:
        consulta += """
            AND (i.descripcion LIKE %s OR a.nombre LIKE %s
                 OR a.identificador LIKE %s OR i.responsable LIKE %s)
        """
        like = f"%{q}%"
        params.extend([like] * 4)
    if estado:
        consulta += " AND i.estado = %s"
        params.append(estado)
    if prioridad:
        consulta += " AND i.prioridad = %s"
        params.append(prioridad)

    consulta += " ORDER BY i.fecha_registro DESC, i.id DESC"
    cursor.execute(consulta, tuple(params))
    lista_incidencias = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'sate/incidencias.html',
        incidencias=lista_incidencias,
        estados=ESTADOS_INCIDENCIA,
        prioridades=PRIORIDADES_INCIDENCIA,
        filtros={'q': q, 'estado': estado, 'prioridad': prioridad},
    )


@app.route('/app/incidencias/<int:id>')
@require_perm('incidencias', 'ver')
def detalle_incidencia(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT i.*, a.nombre AS activo_nombre, a.identificador AS activo_identificador,
               a.tipo AS activo_tipo, a.responsable AS activo_responsable,
               a.ubicacion AS activo_ubicacion, a.estado AS activo_estado,
               d.nombre AS departamento_nombre,
               u.nombre AS solicitante_nombre, u.email AS solicitante_email
        FROM incidencias i
        JOIN activos a ON i.activo_id = a.id
        LEFT JOIN departamentos d ON a.departamento_id = d.id
        LEFT JOIN usuarios u ON i.solicitante_id = u.id
        WHERE i.id = %s
        """,
        (id,),
    )
    incidencia = cursor.fetchone()
    cursor.close()
    conn.close()

    if not incidencia:
        abort(404)

    if (
        alcance_incidencias(session.get('rol')) == 'propias'
        and incidencia['solicitante_id'] != session.get('usuario_id')
    ):
        abort(403)

    return render_template('sate/detalle_incidencia.html', incidencia=incidencia)

@app.route('/app/incidencias/nueva', methods=['GET', 'POST'])
@require_perm('incidencias', 'crear')
def nueva_incidencia():
    conn = get_db_connection()

    if request.method == 'POST':
        activo_id = request.form.get('activo_id', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        prioridad = request.form.get('prioridad', '').strip()
        responsable = request.form.get('responsable', '').strip()

        if prioridad not in {'Baja', 'Media', 'Alta', 'Crítica'} or not descripcion or not responsable:
            flash('Revisa la descripción, la prioridad y el responsable.', 'error')
            conn.close()
            return redirect(url_for('nueva_incidencia'))

        try:
            activo_id = int(activo_id)
        except (ValueError, TypeError):
            flash('Activo no válido.', 'error')
            conn.close()
            return redirect(url_for('nueva_incidencia'))

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, estado, departamento_id FROM activos WHERE id = %s",
            (activo_id,),
        )
        activo = cursor.fetchone()
        if not activo or activo['estado'] == 'Baja' or not activo_visible(activo):
            cursor.close()
            conn.close()
            flash('El activo seleccionado no existe, está dado de baja o no pertenece a tu área.', 'error')
            return redirect(url_for('nueva_incidencia'))

        cursor.execute(
            """
            INSERT INTO incidencias
                (activo_id, descripcion, prioridad, responsable, estado, solicitante_id)
            VALUES (%s, %s, %s, %s, 'Nueva', %s)
            """,
            (activo_id, descripcion, prioridad, responsable, session['usuario_id']),
        )
        incidencia_id = cursor.lastrowid

        recalcular_estado_activo(cursor, activo_id)
        registrar_historial(
            cursor,
            activo_id,
            'Incidencia reportada',
            f'Prioridad {prioridad}: {descripcion}. Responsable: {responsable}.',
        )
        registrar_auditoria(
            cursor,
            'Crear',
            'Incidencia',
            incidencia_id,
            f'Activo {activo_id} - {prioridad}',
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash('Incidencia reportada correctamente y enviada a Soporte.', 'success')
        return redirect(url_for('incidencias'))

    # GET: equipos disponibles según el alcance del rol
    cursor = conn.cursor(dictionary=True)
    filtro, params = filtro_departamento('a.departamento_id')
    cursor.execute(
        f"SELECT a.id, a.nombre FROM activos a WHERE a.estado != 'Baja'{filtro} ORDER BY a.nombre",
        params,
    )
    activos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('sate/nueva_incidencia.html', activos=activos)

# ==========================================
# MÓDULO DE USUARIOS Y ROLES
# ==========================================

@app.route('/app/usuarios')
@require_perm('usuarios', 'ver')
def usuarios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.id, u.nombre, u.email, u.activo, u.ultimo_acceso,
               u.debe_cambiar_password,
               d.nombre AS departamento, r.nombre AS rol
        FROM usuarios u
        LEFT JOIN departamentos d ON u.departamento_id = d.id
        LEFT JOIN roles r ON u.rol_id = r.id
        ORDER BY u.id ASC
    """)
    lista_usuarios = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('sate/usuarios.html', usuarios=lista_usuarios)

@app.route('/app/usuarios/nuevo', methods=['GET', 'POST'])
@require_perm('usuarios', 'crear')
def nuevo_usuario():
    conn = get_db_connection()

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        departamento_id = request.form.get('departamento_id', '').strip()
        rol_id = request.form.get('rol_id', '').strip()

        if not nombre or not email or not departamento_id or not rol_id:
            flash('Todos los campos son obligatorios.', 'error')
            conn.close()
            return redirect(url_for('nuevo_usuario'))

        if '@' not in email:
            flash('El correo electrónico no es válido.', 'error')
            conn.close()
            return redirect(url_for('nuevo_usuario'))

        if len(password) < 8:
            flash('La contraseña temporal debe tener al menos 8 caracteres.', 'error')
            conn.close()
            return redirect(url_for('nuevo_usuario'))

        try:
            departamento_id = int(departamento_id)
            rol_id = int(rol_id)
        except ValueError:
            flash('Departamento o rol no válidos.', 'error')
            conn.close()
            return redirect(url_for('nuevo_usuario'))

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM departamentos WHERE id = %s", (departamento_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            flash('El departamento seleccionado no existe.', 'error')
            return redirect(url_for('nuevo_usuario'))

        cursor.execute("SELECT id FROM roles WHERE id = %s", (rol_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            flash('El rol seleccionado no existe.', 'error')
            return redirect(url_for('nuevo_usuario'))

        password_cifrada = generate_password_hash(password)

        try:
            cursor.execute(
                """
                INSERT INTO usuarios
                    (nombre, email, password, departamento_id, rol_id,
                     debe_cambiar_password)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                """,
                (nombre, email, password_cifrada, departamento_id, rol_id),
            )
        except IntegrityError:
            conn.rollback()
            cursor.close()
            conn.close()
            flash('Ya existe un usuario con ese correo electrónico.', 'error')
            return redirect(url_for('nuevo_usuario'))

        nuevo_id = cursor.lastrowid
        registrar_auditoria(cursor, 'Crear', 'Usuario', nuevo_id, f'{email} - rol {rol_id}')

        conn.commit()
        cursor.close()
        conn.close()

        flash(
            'Usuario creado correctamente. Deberá cambiar su contraseña al iniciar sesión.',
            'success',
        )
        return redirect(url_for('usuarios'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM departamentos ORDER BY nombre")
    departamentos = cursor.fetchall()
    cursor.execute("SELECT * FROM roles ORDER BY nombre")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'sate/nuevo_usuario.html',
        departamentos=departamentos,
        roles=roles,
        descripciones=ROLES_DESCRIPCION,
    )


@app.route('/app/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@require_perm('usuarios', 'editar')
def editar_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT u.*, r.nombre AS rol_nombre
        FROM usuarios u
        LEFT JOIN roles r ON u.rol_id = r.id
        WHERE u.id = %s
        """,
        (id,),
    )
    usuario = cursor.fetchone()
    if not usuario:
        cursor.close()
        conn.close()
        abort(404)

    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip().lower()
        departamento_id = request.form.get('departamento_id', '').strip()
        rol_id = request.form.get('rol_id', '').strip()

        if not nombre or not email or not departamento_id or not rol_id:
            flash('Nombre, correo, departamento y rol son obligatorios.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('editar_usuario', id=id))

        if '@' not in email:
            flash('El correo electrónico no es válido.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('editar_usuario', id=id))

        try:
            departamento_id = int(departamento_id)
            rol_id = int(rol_id)
        except ValueError:
            flash('Departamento o rol no válidos.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('editar_usuario', id=id))

        cursor.execute("SELECT id FROM departamentos WHERE id = %s", (departamento_id,))
        if not cursor.fetchone():
            flash('El departamento seleccionado no existe.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('editar_usuario', id=id))

        cursor.execute("SELECT id, nombre FROM roles WHERE id = %s", (rol_id,))
        rol_nuevo = cursor.fetchone()
        if not rol_nuevo:
            flash('El rol seleccionado no existe.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('editar_usuario', id=id))

        if id == session['usuario_id'] and rol_nuevo['nombre'] != usuario['rol_nombre']:
            flash('No puedes cambiar tu propio rol. Pídeselo a otro administrador.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('editar_usuario', id=id))

        if (
            usuario['rol_nombre'] == ROL_ADMIN
            and rol_nuevo['nombre'] != ROL_ADMIN
            and contar_administradores(cursor, excluir_id=id) == 0
        ):
            flash('No puedes quitar el rol al último administrador general activo.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('editar_usuario', id=id))

        try:
            cursor.execute(
                """
                UPDATE usuarios
                SET nombre = %s, email = %s, departamento_id = %s, rol_id = %s
                WHERE id = %s
                """,
                (nombre, email, departamento_id, rol_id, id),
            )
        except IntegrityError:
            conn.rollback()
            flash('Ya existe otro usuario con ese correo electrónico.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('editar_usuario', id=id))

        registrar_auditoria(
            cursor,
            'Editar',
            'Usuario',
            id,
            f'{email} - rol {rol_nuevo["nombre"]}',
        )
        conn.commit()

        if id == session['usuario_id']:
            session['nombre'] = nombre
            session['departamento_id'] = departamento_id

        cursor.close()
        conn.close()

        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('usuarios'))

    cursor.execute("SELECT * FROM departamentos ORDER BY nombre")
    departamentos = cursor.fetchall()
    cursor.execute("SELECT * FROM roles ORDER BY nombre")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        'sate/editar_usuario.html',
        usuario=usuario,
        departamentos=departamentos,
        roles=roles,
        descripciones=ROLES_DESCRIPCION,
    )


@app.route('/app/usuarios/<int:id>/estado', methods=['POST'])
@require_perm('usuarios', 'administrar')
def cambiar_estado_usuario(id):
    if id == session['usuario_id']:
        flash('No puedes desactivar tu propia cuenta.', 'error')
        return redirect(url_for('usuarios'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT u.id, u.email, u.activo, r.nombre AS rol_nombre
        FROM usuarios u
        LEFT JOIN roles r ON u.rol_id = r.id
        WHERE u.id = %s
        """,
        (id,),
    )
    usuario = cursor.fetchone()
    if not usuario:
        cursor.close()
        conn.close()
        abort(404)

    if usuario['activo'] and usuario['rol_nombre'] == ROL_ADMIN and contar_administradores(cursor, excluir_id=id) == 0:
        cursor.close()
        conn.close()
        flash('No puedes desactivar al último administrador general activo.', 'error')
        return redirect(url_for('usuarios'))

    nuevo_estado = not usuario['activo']
    cursor.execute("UPDATE usuarios SET activo = %s WHERE id = %s", (nuevo_estado, id))
    registrar_auditoria(
        cursor,
        'Activar' if nuevo_estado else 'Desactivar',
        'Usuario',
        id,
        usuario['email'],
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash(
        f'Usuario {"activado" if nuevo_estado else "desactivado"} correctamente.',
        'success',
    )
    return redirect(url_for('usuarios'))


@app.route('/app/usuarios/<int:id>/password', methods=['POST'])
@require_perm('usuarios', 'administrar')
def restablecer_password_usuario(id):
    if id == session['usuario_id']:
        flash('Cambia tu propia contraseña desde Mi Perfil.', 'error')
        return redirect(url_for('editar_usuario', id=id))

    password = request.form.get('password', '').strip()
    if len(password) < 8:
        flash('La contraseña temporal debe tener al menos 8 caracteres.', 'error')
        return redirect(url_for('editar_usuario', id=id))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, email FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()
    if not usuario:
        cursor.close()
        conn.close()
        abort(404)

    cursor.execute(
        """
        UPDATE usuarios
        SET password = %s, debe_cambiar_password = TRUE
        WHERE id = %s
        """,
        (generate_password_hash(password), id),
    )
    registrar_auditoria(
        cursor,
        'Restablecer contraseña',
        'Usuario',
        id,
        usuario['email'],
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash(
        'Contraseña temporal restablecida. El usuario deberá cambiarla al entrar.',
        'success',
    )
    return redirect(url_for('editar_usuario', id=id))


# ==========================================
# PERFIL
# ==========================================

@app.route('/app/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    conn = get_db_connection()

    if request.method == 'POST':
        nueva_password = request.form.get('password', '').strip()
        password_actual = request.form.get('password_actual', '')
        nuevo_tema = request.form.get('tema', 'blue')
        usuario_id = session['usuario_id']

        if nuevo_tema not in TEMAS_VALIDOS:
            nuevo_tema = session.get('tema', 'blue')

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password FROM usuarios WHERE id = %s", (usuario_id,))
        fila = cursor.fetchone()

        if not fila:
            cursor.close()
            conn.close()
            session.clear()
            return redirect(url_for('login'))

        if nueva_password:
            if len(nueva_password) < 8:
                flash('La nueva contraseña debe tener al menos 8 caracteres.', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('perfil'))

            try:
                actual_ok = check_password_hash(fila['password'], password_actual)
            except (ValueError, TypeError):
                actual_ok = False

            if not actual_ok:
                flash('La contraseña actual no es correcta.', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('perfil'))

            password_cifrada = generate_password_hash(nueva_password)
            cursor.execute(
                """
                UPDATE usuarios
                SET password = %s, tema = %s, debe_cambiar_password = FALSE
                WHERE id = %s
                """,
                (password_cifrada, nuevo_tema, usuario_id),
            )
            session.pop('debe_cambiar_password', None)
            flash('Contraseña y tema actualizados correctamente.', 'success')
        else:
            cursor.execute(
                "UPDATE usuarios SET tema = %s WHERE id = %s",
                (nuevo_tema, usuario_id),
            )
            flash('Tema visual actualizado correctamente.', 'success')

        conn.commit()
        cursor.close()
        conn.close()

        session['tema'] = nuevo_tema
        return redirect(url_for('perfil'))

    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT u.nombre, u.email, u.tema, u.debe_cambiar_password,
               d.nombre AS departamento, r.nombre AS rol
        FROM usuarios u
        LEFT JOIN departamentos d ON u.departamento_id = d.id
        LEFT JOIN roles r ON u.rol_id = r.id
        WHERE u.id = %s
        """,
        (session['usuario_id'],),
    )
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('sate/perfil.html', usuario=usuario)

@app.route('/app/cambiar_tema', methods=['POST'])
@login_required
def cambiar_tema():
    nuevo_tema = request.form.get('tema')

    if nuevo_tema not in TEMAS_VALIDOS:
        flash('Tema visual no válido.', 'error')
        return redirect(url_for('dashboard'))

    usuario_id = session['usuario_id']


    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET tema = %s WHERE id = %s", (nuevo_tema, usuario_id))
    conn.commit()
    cursor.close()
    conn.close()

    session['tema'] = nuevo_tema

    destino = request.referrer
    if not destino or not destino.startswith(request.host_url):
        destino = url_for('dashboard')
    return redirect(destino)

@app.route('/app/mantenimientos/<int:id>/orden')
@require_perm('mantenimientos', 'ver')
def orden_mantenimiento_pdf(id):
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.*, a.nombre as activo_nombre, a.marca, a.modelo 
        FROM mantenimientos m 
        JOIN activos a ON m.activo_id = a.id
        WHERE m.id = %s
    """, (id,))
    mant = cursor.fetchone()
    cursor.close()
    conn.close()

    if not mant:
        return "Mantenimiento no encontrado", 404

    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="TechTrack Solutions", ln=True, align='C')
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt=f"Orden de Trabajo de Mantenimiento #{mant['id']}", ln=True, align='C')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Datos del Equipo y Servicio:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, txt=f"Equipo: {mant['activo_nombre']} ({mant['marca'] or 'N/A'} {mant['modelo'] or 'N/A'})", ln=True)
    pdf.cell(0, 8, txt=f"Tipo de Mantenimiento: {mant['tipo']}", ln=True)
    pdf.cell(0, 8, txt=f"Fecha Programada: {mant['fecha_programada']}", ln=True)
    pdf.cell(0, 8, txt=f"Estado: {mant['estado']}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Observaciones / Trabajo Realizado:", ln=True)
    pdf.set_font("Arial", '', 12)
    observaciones = mant.get('observaciones') or "________________________________________________________________________________________"
    pdf.multi_cell(0, 8, txt=observaciones)
    
    pdf.ln(30)
    pdf.cell(0, 10, txt="_______________________________", ln=True, align='C')
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, txt=f"Firma del Técnico: {mant['responsable']}", ln=True, align='C')

    response = make_response(pdf.output(dest='S').encode('latin-1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Orden_Trabajo_{mant["id"]}.pdf'
    return response

@app.route('/app/incidencias/<int:id>/editar', methods=['GET', 'POST'])
@require_perm('incidencias', 'editar')
def editar_incidencia(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM incidencias WHERE id = %s", (id,))
    incidencia = cursor.fetchone()
    if not incidencia:
        cursor.close()
        conn.close()
        abort(404)

    if request.method == 'POST':
        nuevo_estado = request.form.get('estado', '').strip()
        diagnostico = request.form.get('diagnostico', '').strip() or None
        resolucion = request.form.get('resolucion', '').strip() or None
        estados_validos = {'Nueva', 'Asignada', 'En proceso', 'Resuelta', 'Cerrada'}

        if nuevo_estado not in estados_validos:
            flash('Estado de incidencia no válido.', 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('editar_incidencia', id=id))

        cursor.execute(
            """
            UPDATE incidencias
            SET estado = %s,
                diagnostico = %s,
                resolucion = %s,
                fecha_cierre = CASE
                    WHEN %s IN ('Resuelta', 'Cerrada') THEN COALESCE(fecha_cierre, NOW())
                    ELSE NULL
                END
            WHERE id = %s
            """,
            (nuevo_estado, diagnostico, resolucion, nuevo_estado, id),
        )

        recalcular_estado_activo(cursor, incidencia['activo_id'])
        registrar_historial(
            cursor,
            incidencia['activo_id'],
            'Incidencia actualizada',
            f'Estado: {nuevo_estado}. Resolución: {resolucion or "sin resolución"}.',
        )
        registrar_auditoria(
            cursor,
            'Editar',
            'Incidencia',
            id,
            f'Estado: {nuevo_estado}',
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash('Incidencia actualizada correctamente.', 'success')
        return redirect(url_for('incidencias'))

    cursor.close()
    conn.close()

    return render_template('sate/editar_incidencia.html', incidencia=incidencia)



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=app.config['DEBUG'])