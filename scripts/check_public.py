"""Valida el sitio público del Bloque 5: rutas, contenido y enlaces.

No necesita base de datos: todas las páginas públicas son contenido estático.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app
from contenido import DEPARTAMENTOS, PERFILES, POLITICAS

app.config.update(TESTING=True)

fallos = []


def revisar(ruta, esperado=200):
    respuesta = cliente.get(ruta)
    ok = respuesta.status_code == esperado
    print(f"{'OK ' if ok else 'FALLO'} GET {ruta} -> {respuesta.status_code}")
    if not ok:
        fallos.append((ruta, respuesta.status_code))
    return respuesta


with app.test_client() as cliente:
    # Páginas principales
    for ruta in [
        "/",
        "/empresa",
        "/departamentos",
        "/politicas",
        "/trabaja-con-nosotros",
        "/sate",
        "/contacto",
        "/privacidad",
        "/cumplimiento-pia",
    ]:
        revisar(ruta)

    # Departamentos
    for slug, departamento in DEPARTAMENTOS.items():
        respuesta = revisar(f"/departamentos/{slug}")
        html = respuesta.get_data(as_text=True)
        for texto in [departamento["nombre"], departamento["objetivo"], "Políticas"]:
            if texto not in html:
                print(f"FALLO contenido /departamentos/{slug}: falta {texto!r}")
                fallos.append((f"/departamentos/{slug}", f"falta {texto}"))

    # Políticas
    for slug, politica in POLITICAS.items():
        respuesta = revisar(f"/politicas/{slug}")
        html = respuesta.get_data(as_text=True)
        for texto in [politica["nombre"], politica["objetivo"], "Relación con el producto", "Reglas y lineamientos"]:
            if texto not in html:
                print(f"FALLO contenido /politicas/{slug}: falta {texto!r}")
                fallos.append((f"/politicas/{slug}", f"falta {texto}"))

    # Perfiles
    for slug, perfil in PERFILES.items():
        respuesta = revisar(f"/trabaja-con-nosotros/{slug}")
        html = respuesta.get_data(as_text=True)
        for texto in [perfil["nombre"], "Jefe inmediato", "Jornada", "Herramientas que utiliza", "Competencias profesionales"]:
            if texto not in html:
                print(f"FALLO contenido /trabaja-con-nosotros/{slug}: falta {texto!r}")
                fallos.append((f"/trabaja-con-nosotros/{slug}", f"falta {texto}"))

    # Rutas antiguas: redirección permanente
    for vieja, nueva in [
        ("/vacantes", "/trabaja-con-nosotros"),
        ("/vacantes/tecnico-soporte", "/trabaja-con-nosotros/tecnico-soporte"),
    ]:
        respuesta = cliente.get(vieja, follow_redirects=False)
        ok = respuesta.status_code in (301, 308) and nueva in respuesta.headers.get("Location", "")
        print(f"{'OK ' if ok else 'FALLO'} GET {vieja} -> {respuesta.status_code} {respuesta.headers.get('Location', '')}")
        if not ok:
            fallos.append((vieja, respuesta.status_code))

    # Slugs inexistentes
    for ruta in ["/departamentos/no-existe", "/politicas/no-existe", "/trabaja-con-nosotros/no-existe"]:
        revisar(ruta, 404)

    # Página de cumplimiento del PIA
    respuesta = revisar("/cumplimiento-pia")
    html = respuesta.get_data(as_text=True)
    for texto in ["Cumplimiento del PIA", "Matriz de evidencia", "Políticas generales", "Implementado", "Organigrama"]:
        if texto not in html:
            print(f"FALLO contenido /cumplimiento-pia: falta {texto!r}")
            fallos.append(("/cumplimiento-pia", f"falta {texto}"))

    # Enlaces vacíos en las páginas públicas
    for ruta in ["/", "/empresa", "/departamentos", "/politicas", "/trabaja-con-nosotros", "/sate", "/contacto", "/cumplimiento-pia"]:
        html = cliente.get(ruta).get_data(as_text=True)
        if 'href="#"' in html:
            print(f"FALLO enlace vacío href=# en {ruta}")
            fallos.append((ruta, "href=#"))

    # El pie debe enlazar al aviso de privacidad real
    html = cliente.get("/").get_data(as_text=True)
    if 'href="/privacidad"' not in html:
        print("FALLO el pie no enlaza a /privacidad")
        fallos.append(("/", "footer privacidad"))

    # SEO técnico: favicon, robots, sitemap y metadatos sociales
    respuesta = cliente.get("/favicon.ico")
    ok = respuesta.status_code == 200 and "icon" in respuesta.headers.get("Content-Type", "")
    print(f"{'OK ' if ok else 'FALLO'} GET /favicon.ico -> {respuesta.status_code}")
    if not ok:
        fallos.append(("/favicon.ico", respuesta.status_code))

    respuesta = cliente.get("/robots.txt")
    robots = respuesta.get_data(as_text=True)
    ok = (
        respuesta.status_code == 200
        and "Disallow: /app/" in robots
        and "Sitemap:" in robots
    )
    print(f"{'OK ' if ok else 'FALLO'} GET /robots.txt -> {respuesta.status_code}")
    if not ok:
        fallos.append(("/robots.txt", "contenido incompleto"))

    respuesta = cliente.get("/sitemap.xml")
    sitemap = respuesta.get_data(as_text=True)
    esperadas = 9 + len(DEPARTAMENTOS) + len(POLITICAS) + len(PERFILES)
    ok = (
        respuesta.status_code == 200
        and sitemap.count("<url>") == esperadas
        and "/cumplimiento-pia" in sitemap
        and "/app/" not in sitemap
    )
    print(
        f"{'OK ' if ok else 'FALLO'} GET /sitemap.xml -> {respuesta.status_code} "
        f"({sitemap.count('<url>')}/{esperadas} URLs)"
    )
    if not ok:
        fallos.append(("/sitemap.xml", f"{sitemap.count('<url>')} URLs"))

    html = cliente.get("/").get_data(as_text=True)
    for etiqueta in [
        'property="og:title"',
        'property="og:description"',
        'property="og:image"',
        'name="twitter:card"',
        'rel="canonical"',
        'application/ld+json',
        "favicon.ico",
    ]:
        if etiqueta not in html:
            print(f"FALLO metadatos: falta {etiqueta}")
            fallos.append(("/", f"falta {etiqueta}"))

print()
if fallos:
    print(f"FALLOS: {len(fallos)}")
    for fallo in fallos:
        print(" -", fallo)
    raise SystemExit(1)
print("SITIO PÚBLICO: TODAS LAS VALIDACIONES PASARON")
