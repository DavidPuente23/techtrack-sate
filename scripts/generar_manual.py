"""Genera el Manual de Usuario de SATE en PDF.

El manual cubre el sitio publico de TechTrack Solutions y los seis modulos
del sistema privado. Usa FPDF con fuentes core (Helvetica, latin-1), por lo
que todo el texto pasa por `txt()` antes de dibujarse.

Uso:
    python scripts/generar_manual.py

Requiere Pillow solo para leer las dimensiones de las capturas (herramienta
de build; no es una dependencia de ejecucion de la aplicacion).
"""

from __future__ import annotations

import os
import sys

from fpdf import FPDF
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAPTURAS = os.path.join(RAIZ, "docs", "capturas")
SALIDA = os.path.join(RAIZ, "docs", "Manual_Usuario_SATE.pdf")

ANCHO = 210.0
ALTO = 297.0
MARGEN = 18.0
CONTENIDO = ANCHO - 2 * MARGEN

AZUL = (37, 99, 235)
INDIGO = (79, 70, 229)
OSCURO = (15, 23, 42)
GRIS = (71, 85, 105)
GRIS_CLARO = (148, 163, 184)
FONDO_SUAVE = (248, 250, 252)
BORDE = (226, 232, 240)
VERDE = (16, 185, 129)
AMBAR = (217, 119, 6)
ROJO = (220, 38, 38)

REEMPLAZOS = {
    "\u2192": "->",
    "\u2190": "<-",
    "\u2013": "-",
    "\u2014": "-",
    "\u2026": "...",
    "\u2022": "-",
    "\u201c": '"',
    "\u201d": '"',
    "\u2018": "'",
    "\u2019": "'",
    "\u00d7": "x",
    "\u2265": ">=",
    "\u2264": "<=",
    "\u2713": "OK",
    "\u2714": "OK",
    "\u26a0": "!",
    "\u00a0": " ",
    "\u20ac": "EUR",
}


def txt(valor) -> str:
    """Normaliza cualquier texto a latin-1 para las fuentes core de FPDF."""
    cadena = str(valor if valor is not None else "")
    for origen, destino in REEMPLAZOS.items():
        cadena = cadena.replace(origen, destino)
    return "".join(caracter if ord(caracter) < 256 else "?" for caracter in cadena)


class Manual(FPDF):
    def __init__(self, registrar: bool = True):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(True, margin=MARGEN)
        self.set_margins(MARGEN, 20, MARGEN)
        self.registrar = registrar
        self.toc: list[tuple[int, str, int]] = []
        self.n1 = 0
        self.n2 = 0
        self.figura = 0
        self.tabla_num = 0
        self.seccion = ""
        self.ocultar_cabecera = True

    # ------------------------------------------------------------------
    # Estructura de pagina
    # ------------------------------------------------------------------
    def header(self):
        if self.ocultar_cabecera:
            return
        self.set_y(9)
        self.set_font("Helvetica", "", 7.4)
        self.set_text_color(*GRIS_CLARO)
        self.cell(0, 4, txt(self.seccion), 0, 0, "L")
        self.cell(0, 4, "Manual de Usuario · SATE", 0, 1, "R")
        self.set_draw_color(*BORDE)
        self.set_line_width(0.2)
        self.line(MARGEN, 15, ANCHO - MARGEN, 15)
        self.set_y(22)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-13)
        self.set_font("Helvetica", "", 7.4)
        self.set_text_color(*GRIS_CLARO)
        self.cell(0, 4, "TechTrack Solutions · Documento de uso interno y académico", 0, 0, "L")
        self.cell(0, 4, txt(f"Página {self.page_no()} de {{nb}}"), 0, 0, "R")

    def necesita(self, alto: float):
        if self.get_y() + alto > 275:
            self.add_page()

    # ------------------------------------------------------------------
    # Titulos
    # ------------------------------------------------------------------
    def h1(self, titulo: str):
        self.n1 += 1
        self.n2 = 0
        numero = str(self.n1)
        self.seccion = f"{numero}. {titulo}"
        self.add_page()
        if self.registrar:
            self.toc.append((1, f"{numero}. {titulo}", self.page_no()))
        self.set_font("Helvetica", "B", 19)
        self.set_text_color(*OSCURO)
        self.cell(0, 9, txt(f"{numero}. {titulo}"), 0, 1, "L")
        self.set_draw_color(*INDIGO)
        self.set_line_width(0.9)
        self.line(MARGEN, self.get_y() + 1, MARGEN + 32, self.get_y() + 1)
        self.ln(7)

    def h2(self, titulo: str):
        self.necesita(24)
        self.n2 += 1
        numero = f"{self.n1}.{self.n2}"
        if self.registrar:
            self.toc.append((2, f"{numero}. {titulo}", self.page_no()))
        self.set_font("Helvetica", "B", 12.4)
        self.set_text_color(30, 41, 59)
        self.multi_cell(0, 6, txt(f"{numero}. {titulo}"), 0, "L")
        self.ln(1.6)

    def subtitulo(self, texto: str):
        self.necesita(14)
        self.set_font("Helvetica", "B", 10.4)
        self.set_text_color(*OSCURO)
        self.multi_cell(0, 5.2, txt(texto), 0, "L")
        self.ln(1.2)

    # ------------------------------------------------------------------
    # Texto
    # ------------------------------------------------------------------
    def p(self, texto: str, size: float = 10.0, lh: float = 5.4, color=GRIS, align="J"):
        self.set_font("Helvetica", "", size)
        self.set_text_color(*color)
        self.multi_cell(0, lh, txt(texto), 0, align)
        self.ln(1.8)

    def vinetas(self, items, size: float = 9.8, lh: float = 5.1):
        self.set_font("Helvetica", "", size)
        total = sum(
            len(self.multi_cell(CONTENIDO - 5.5, lh, txt(item), split_only=True)) * lh + 0.7
            for item in items
        )
        if total <= 130 and self.get_y() + total > 275:
            self.add_page()
        self.set_font("Helvetica", "", size)
        self.set_text_color(55, 65, 81)
        for item in items:
            self.necesita(9)
            y = self.get_y()
            self.set_fill_color(*INDIGO)
            self.rect(MARGEN + 1.4, y + 2.1, 1.5, 1.5, "F")
            self.set_x(MARGEN + 5.5)
            self.multi_cell(CONTENIDO - 5.5, lh, txt(item), 0, "L")
            self.ln(0.7)
        self.ln(1.4)

    def numerada(self, items, size: float = 9.8, lh: float = 5.1):
        self.set_font("Helvetica", "", size)
        total = sum(
            len(self.multi_cell(CONTENIDO - 8, lh, txt(item), split_only=True)) * lh + 0.9
            for item in items
        )
        if total <= 130 and self.get_y() + total > 275:
            self.add_page()
        self.set_font("Helvetica", "", size)
        self.set_text_color(55, 65, 81)
        for indice, item in enumerate(items, start=1):
            self.necesita(10)
            y = self.get_y()
            self.set_fill_color(*INDIGO)
            self.rect(MARGEN + 0.5, y + 0.6, 5.4, 4.6, "F")
            self.set_font("Helvetica", "B", 8.2)
            self.set_text_color(255, 255, 255)
            self.set_xy(MARGEN + 0.5, y + 0.9)
            self.cell(5.4, 4.0, str(indice), 0, 0, "C")
            self.set_font("Helvetica", "", size)
            self.set_text_color(55, 65, 81)
            self.set_xy(MARGEN + 8, y)
            self.multi_cell(CONTENIDO - 8, lh, txt(item), 0, "L")
            self.ln(0.9)
        self.ln(1.2)

    def nota(self, titulo: str, texto: str, color=AZUL, fondo=(239, 246, 255)):
        self.necesita(28)
        ancho_texto = CONTENIDO - 12
        self.set_font("Helvetica", "", 9)
        lineas = self.multi_cell(ancho_texto, 4.7, txt(texto), split_only=True)
        alto = 10.5 + len(lineas) * 4.7 + 3
        y = self.get_y()
        if y + alto > 275:
            self.add_page()
            y = self.get_y()
        self.set_fill_color(*fondo)
        self.rect(MARGEN, y, CONTENIDO, alto, "F")
        self.set_fill_color(*color)
        self.rect(MARGEN, y, 2.2, alto, "F")
        self.set_xy(MARGEN + 6, y + 3.6)
        self.set_font("Helvetica", "B", 9.4)
        self.set_text_color(*color)
        self.cell(0, 4.4, txt(titulo), 0, 1)
        self.set_x(MARGEN + 6)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(55, 65, 81)
        self.multi_cell(ancho_texto, 4.7, txt(texto), 0, "L")
        self.set_y(y + alto + 4)

    # ------------------------------------------------------------------
    # Tablas
    # ------------------------------------------------------------------
    def _cabecera_tabla(self, headers, anchos, size=8.3):
        self.set_font("Helvetica", "B", size)
        self.set_fill_color(30, 41, 59)
        self.set_text_color(255, 255, 255)
        x = MARGEN
        y = self.get_y()
        alto = 7.2
        for header, ancho in zip(headers, anchos):
            self.set_xy(x, y)
            self.cell(ancho, alto, txt(header), 0, 0, "L", True)
            x += ancho
        self.set_y(y + alto)

    def tabla(self, headers, filas, anchos, size=8.3, lh=4.15, padding=3.2):
        self.tabla_num += 1
        # Medir todas las filas para no partir tablas pequenas y evitar filas huerfanas.
        alturas_filas = []
        for fila in filas:
            self.set_font("Helvetica", "", size)
            lineas = [
                len(self.multi_cell(ancho - 3, lh, txt(valor), split_only=True))
                for valor, ancho in zip(fila, anchos)
            ]
            alturas_filas.append(max(lineas) * lh + padding)
        alto_total = 7.2 + sum(alturas_filas)
        if alto_total <= 150 and self.get_y() + alto_total > 275:
            self.add_page()
        self.necesita(22)
        self._cabecera_tabla(headers, anchos, size)
        for indice, (fila, alto) in enumerate(zip(filas, alturas_filas)):
            self.set_font("Helvetica", "", size)
            if self.get_y() + alto > 275:
                self.add_page()
                self._cabecera_tabla(headers, anchos, size)
            y = self.get_y()
            if indice % 2 == 0:
                self.set_fill_color(*FONDO_SUAVE)
                self.rect(MARGEN, y, sum(anchos), alto, "F")
            x = MARGEN
            for valor, ancho in zip(fila, anchos):
                self.set_xy(x + 1.5, y + padding / 2)
                self.set_text_color(45, 55, 72)
                self.multi_cell(ancho - 3, lh, txt(valor), 0, "L")
                x += ancho
            self.set_draw_color(*BORDE)
            self.set_line_width(0.15)
            self.line(MARGEN, y + alto, MARGEN + sum(anchos), y + alto)
            self.set_y(y + alto)
        self.ln(4.2)

    # ------------------------------------------------------------------
    # Imagenes
    # ------------------------------------------------------------------
    def imagen(self, archivo: str, leyenda: str, ancho: float = 152.0, minimo: float = 112.0):
        ruta = os.path.join(CAPTURAS, archivo)
        if not os.path.exists(ruta):
            raise FileNotFoundError(ruta)
        with Image.open(ruta) as imagen:
            ancho_px, alto_px = imagen.size
        alto = ancho * alto_px / ancho_px
        reserva = 12.0
        espacio = 275 - self.get_y()
        if alto + reserva > espacio:
            ancho_ajustado = (espacio - reserva) * ancho_px / alto_px
            if ancho_ajustado >= minimo:
                ancho = ancho_ajustado
                alto = ancho * alto_px / ancho_px
            else:
                self.add_page()
                alto = ancho * alto_px / ancho_px
        self.figura += 1
        x = (ANCHO - ancho) / 2
        y = self.get_y()
        self.set_draw_color(*BORDE)
        self.set_line_width(0.25)
        self.rect(x - 1.2, y - 1.2, ancho + 2.4, alto + 2.4)
        self.image(ruta, x, y, ancho)
        self.set_y(y + alto + 2.2)
        self.set_font("Helvetica", "I", 8.2)
        self.set_text_color(110, 120, 135)
        self.multi_cell(0, 4.2, txt(f"Figura {self.figura}. {leyenda}"), 0, "C")
        self.ln(4.4)

    def h2_imagen(self, titulo: str, archivo: str, leyenda: str, ancho: float = 152.0):
        """Titulo de seccion con su figura: evita dejar el titulo huerfano."""
        ruta = os.path.join(CAPTURAS, archivo)
        with Image.open(ruta) as imagen:
            ancho_px, alto_px = imagen.size
        alto = ancho * alto_px / ancho_px
        if self.get_y() + 12 + alto + 12 > 275:
            self.add_page()
        self.h2(titulo)
        self.imagen(archivo, leyenda, ancho)

    # ------------------------------------------------------------------
    # Portada, ficha e indice
    # ------------------------------------------------------------------
    def portada(self):
        self.add_page()
        self.set_fill_color(9, 14, 28)
        self.rect(0, 0, ANCHO, ALTO, "F")
        self.set_fill_color(24, 33, 58)
        self.ellipse(120, -55, 150, 150, "F")
        self.set_fill_color(49, 46, 129)
        self.ellipse(-70, 190, 170, 170, "F")
        self.set_fill_color(30, 41, 59)
        self.ellipse(150, 205, 90, 90, "F")

        self.set_xy(20, 30)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(129, 140, 248)
        self.cell(0, 5, "TECHTRACK SOLUTIONS", 0, 1, "L")
        self.set_xy(20, 44)
        self.set_font("Helvetica", "B", 30)
        self.set_text_color(248, 250, 252)
        self.cell(0, 12, "Manual de Usuario", 0, 1, "L")
        self.set_xy(20, 60)
        self.set_font("Helvetica", "B", 46)
        self.set_text_color(129, 140, 248)
        self.cell(0, 18, "SATE", 0, 1, "L")
        self.set_xy(20, 82)
        self.set_font("Helvetica", "", 12.5)
        self.set_text_color(203, 213, 225)
        self.cell(0, 7, "Sistema de Administración y Trazabilidad de Equipos", 0, 1, "L")
        self.set_xy(20, 92)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(148, 163, 184)
        self.cell(0, 5, "Guía completa del sitio público y del sistema privado", 0, 1, "L")

        self.set_draw_color(129, 140, 248)
        self.set_line_width(0.8)
        self.line(20, 104, 62, 104)

        ruta = os.path.join(CAPTURAS, "01-inicio.png")
        self.image(ruta, 20, 114, 170)
        self.set_draw_color(71, 85, 105)
        self.set_line_width(0.4)
        self.rect(19, 113, 172, 117.3)

        self.set_xy(20, 244)
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(226, 232, 240)
        self.cell(0, 6, "Versión 1.0 · Octubre de 2026", 0, 1, "L")
        self.set_xy(20, 251)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(148, 163, 184)
        self.cell(0, 5, "Elaborado para la presentación del Proyecto Integrador de Aplicaciones", 0, 1, "L")
        self.set_xy(20, 258)
        self.cell(0, 5, "TechTrack Solutions · SIT, Redes, Desarrollo y Soporte", 0, 1, "L")

    def ficha(self):
        self.add_page()
        self.set_y(20)
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*OSCURO)
        self.cell(0, 9, "Ficha del documento", 0, 1, "L")
        self.set_draw_color(*INDIGO)
        self.set_line_width(0.8)
        self.line(MARGEN, self.get_y() + 1, MARGEN + 28, self.get_y() + 1)
        self.ln(7)

        filas = [
            ("Título", "Manual de Usuario de SATE"),
            ("Subtítulo", "Guía completa del sitio público y del sistema privado"),
            ("Producto", "SATE - Sistema de Administración y Trazabilidad de Equipos"),
            ("Empresa", "TechTrack Solutions"),
            ("Versión", "1.0"),
            ("Fecha", "Octubre de 2026"),
            ("Público", "Usuarios solicitantes, técnicos, administradores, Dirección General y personal de TI"),
            ("Alcance", "Sitio público, acceso, panel, activos e historial, mantenimientos, incidencias, usuarios y roles, perfil"),
            ("Formato", "PDF A4, 210 x 297 mm"),
        ]
        self.tabla(["Elemento", "Detalle"], filas, [38, 136], size=8.8, lh=4.6)

        self.subtitulo("Propósito")
        self.p(
            "Este documento explica qué contiene la página de TechTrack Solutions, para qué sirve cada "
            "sección y cómo se realizan las tareas habituales dentro de SATE. Está pensado para que una "
            "persona sin experiencia previa pueda consultar el sitio público, iniciar sesión, registrar "
            "equipos, programar mantenimientos, atender incidencias y administrar cuentas sin depender de "
            "otra persona."
        )

        self.subtitulo("Cómo está organizado")
        self.vinetas(
            [
                "Capítulos 1 a 3: presentación de la empresa, del producto y del sitio público.",
                "Capítulos 4 y 5: conceptos, roles y permisos que explican el comportamiento del sistema.",
                "Capítulos 6 a 11: uso detallado de cada módulo de SATE, con capturas y campos.",
                "Capítulos 12 a 15: datos demo, preguntas frecuentes, glosario y anexos de consulta.",
            ]
        )

        self.subtitulo("Convenciones")
        self.vinetas(
            [
                "Las figuras muestran la interfaz real con los datos de demostración.",
                "Las rutas se escriben en formato /app/... y son relativas al dominio donde se publica SATE.",
                "Los recuadros azules señalan notas útiles; los ámbar, advertencias; los rojos, límites o riesgos.",
                "Los nombres de botones y campos se muestran entre comillas para facilitar su búsqueda.",
            ]
        )

        self.nota(
            "Alcance de esta versión",
            "SATE se limita a seis módulos: acceso, panel, activos e historial, mantenimientos, "
            "incidencias y usuarios/roles. Las políticas del sitio público mencionan otras prácticas "
            "(proveedores, cambios, continuidad, problemas, capacidad, disponibilidad o configuración), "
            "pero no existen como módulos independientes en esta versión.",
            color=AMBAR,
            fondo=(255, 251, 235),
        )

    def escribir_indice(self, entradas, offset: int) -> int:
        inicio = self.page_no()
        self.ocultar_cabecera = True
        self.set_y(20)
        self.set_font("Helvetica", "B", 20)
        self.set_text_color(*OSCURO)
        self.cell(0, 10, "Contenido", 0, 1, "L")
        self.set_draw_color(*INDIGO)
        self.set_line_width(0.8)
        self.line(MARGEN, self.get_y() + 1, MARGEN + 26, self.get_y() + 1)
        self.ln(8)

        for nivel, titulo, pagina in entradas:
            if self.get_y() > 267:
                self.add_page()
                self.set_y(20)
            if nivel == 1:
                self.ln(0.8)
                self.set_font("Helvetica", "B", 10.0)
                self.set_text_color(*OSCURO)
                x = MARGEN
                ancho_titulo = 180 - x
            else:
                self.set_font("Helvetica", "", 9.0)
                self.set_text_color(55, 65, 81)
                x = MARGEN + 6
                ancho_titulo = 180 - x

            y = self.get_y()
            texto = txt(titulo)
            while self.get_string_width(texto) > ancho_titulo and len(texto) > 5:
                texto = texto[:-2]
            self.set_xy(x, y)
            self.cell(self.get_string_width(texto) + 0.5, 4.2, texto, 0, 0, "L")

            espacio = 180 - (x + self.get_string_width(texto))
            if espacio > 4:
                puntos = "." * max(1, int(espacio / 1.3))
                self.set_font("Helvetica", "", 7.2)
                self.set_text_color(203, 213, 225)
                self.cell(espacio, 4.2, puntos, 0, 0, "L")
            self.set_font("Helvetica", "B" if nivel == 1 else "", 9.0 if nivel == 2 else 10.0)
            self.set_text_color(*OSCURO if nivel == 1 else GRIS)
            self.cell(12, 4.2, str(pagina + offset), 0, 1, "R")

        return self.page_no() - inicio + 1


def cuerpo(doc: Manual):
    # ==================================================================
    # 1. INTRODUCCION
    # ==================================================================
    doc.h1("Introducción")
    doc.p(
        "TechTrack Solutions es una empresa de tecnología dedicada al desarrollo de software para la "
        "gestión y trazabilidad de activos tecnológicos. Su producto principal, SATE, concentra en una "
        "sola plataforma el inventario de equipos, los responsables, las ubicaciones, los mantenimientos "
        "y las incidencias. Este manual acompaña ese recorrido: primero presenta el sitio público y "
        "después explica, módulo por módulo, el sistema privado."
    )

    doc.h2("La empresa y su propuesta")
    doc.p(
        "La propuesta de TechTrack Solutions es pasar de un control reactivo, en el que los problemas se "
        "atienden cuando ya ocurrieron, a un control preventivo basado en información completa, alertas "
        "y reportes. Sus clientes son organizaciones que administran equipos de cómputo, redes y otros "
        "activos tecnológicos y necesitan saber dónde está cada equipo, quién lo tiene y cuándo le toca "
        "mantenimiento."
    )
    doc.tabla(
        ["Aspecto", "Descripción"],
        [
            ("Giro", "Tecnología: desarrollo de software para la gestión y trazabilidad de activos tecnológicos."),
            ("Producto", "SATE, Sistema de Administración y Trazabilidad de Equipos."),
            ("Propuesta de valor", "Control preventivo con historial completo, alertas y reportes."),
            ("Clientes", "Organizaciones que administran equipos de cómputo, redes y activos tecnológicos."),
            ("Cobertura del sitio", "Empresa, departamentos, políticas, perfiles, producto SATE y contacto."),
        ],
        [42, 132],
        size=8.7,
        lh=4.5,
    )

    doc.h2("Qué es SATE")
    doc.p(
        "SATE significa Sistema de Administración y Trazabilidad de Equipos. Es una aplicación web que "
        "registra cada activo con un identificador único, conserva su historial y permite programar "
        "mantenimientos y atender incidencias con prioridad, responsable, diagnóstico y solución. Con "
        "ello, la organización deja de depender de hojas de cálculo dispersas y obtiene una fuente "
        "única de consulta."
    )
    doc.p(
        "El problema que resuelve es concreto: cuando la información de los equipos está repartida entre "
        "correos, archivos y memoria del personal, nadie sabe con certeza qué se tiene, dónde está, quién "
        "lo usa o qué fallas se repiten. Eso provoca compras duplicadas, pérdida de tiempo y decisiones "
        "sin datos."
    )
    doc.subtitulo("Beneficios principales")
    doc.vinetas(
        [
            "Inventario centralizado con un identificador único por equipo.",
            "Trazabilidad de responsables, ubicaciones y cambios de estado.",
            "Mantenimientos programados y alertas de vencimiento.",
            "Incidencias con prioridad, responsable, diagnóstico y solución.",
            "Indicadores reales para Dirección General y jefaturas.",
            "Acceso controlado por roles y registro de auditoría.",
        ]
    )

    doc.h2("A quién va dirigido este manual")
    doc.p(
        "El manual puede leerse completo o consultarse por tareas. La siguiente tabla orienta a cada "
        "perfil sobre los capítulos que más le convienen."
    )
    doc.tabla(
        ["Perfil", "Uso recomendado del manual"],
        [
            ("Usuario Solicitante", "Capítulos 2, 3, 6, 7 y 9. Consulta activos de su área y reporta sus incidencias."),
            ("Técnico de Soporte", "Capítulos 6 a 9. Atiende incidencias y mantenimientos, y actualiza equipos."),
            ("Administrador de Activos", "Capítulos 6 a 8. Gestiona inventario, asignaciones y mantenimientos."),
            ("Administrador de Redes", "Capítulos 6, 8 y 9. Atiende mantenimientos e incidencias de infraestructura."),
            ("Desarrollador", "Capítulos 6 y 9. Atiende incidencias de software y consulta el inventario."),
            ("Dirección General", "Capítulos 5, 6 y 13. Consulta indicadores y el alcance del sistema."),
            ("Administrador General", "Manual completo, con énfasis en los capítulos 10 y 11."),
        ],
        [44, 130],
        size=8.7,
        lh=4.5,
    )

    doc.h2("Cómo usar el manual")
    doc.p(
        "Cada capítulo de SATE sigue el mismo orden: para qué sirve el módulo, cómo se llega a él, qué "
        "muestra la pantalla, qué significan sus campos y cuáles son las reglas que aplica el sistema. "
        "Las capturas permiten reconocer la interfaz; el texto explica lo que no se ve a simple vista, "
        "como el cálculo automático de estados o el alcance limitado de un rol."
    )
    doc.nota(
        "Antes de empezar",
        "Si solo necesitas resolver una tarea, abre el índice y ve directamente al apartado. Si vas a "
        "usar el sistema por primera vez, lee los capítulos 2, 4 y 5: explican el acceso, los conceptos "
        "básicos y los permisos.",
    )

    doc.h2("Resumen de los módulos")
    doc.p(
        "SATE se organiza en seis módulos. Esta tabla sirve como mapa general; cada uno se desarrolla "
        "en su propio capítulo."
    )
    doc.tabla(
        ["Módulo", "Para qué sirve", "Capítulo"],
        [
            ("Acceso", "Identificar al usuario, validar su cuenta y iniciar sesión.", "2"),
            ("Panel", "Resumir el estado del inventario, los pendientes y la actividad reciente.", "6"),
            ("Activos e historial", "Registrar equipos, asignarlos, consultarlos y conservar su trazabilidad.", "7"),
            ("Mantenimientos", "Programar servicios preventivos y correctivos y cerrarlos.", "8"),
            ("Incidencias", "Reportar fallas, asignarlas, diagnosticarlas y resolverlas.", "9"),
            ("Usuarios y roles", "Crear cuentas, asignar roles y controlar el acceso.", "10"),
        ],
        [40, 116, 18],
        size=8.6,
        lh=4.5,
    )

    # ==================================================================
    # 2. ACCESO
    # ==================================================================
    doc.h1("Acceso al sistema")
    doc.p(
        "SATE es un sistema privado. El sitio público puede consultarse sin cuenta, pero el panel, el "
        "inventario, los mantenimientos, las incidencias y la administración de usuarios requieren una "
        "sesión iniciada. El acceso se controla con correo, contraseña y rol."
    )

    doc.h2("Requisitos")
    doc.vinetas(
        [
            "Navegador actualizado: Chrome, Edge, Firefox o Safari en versión reciente.",
            "Resolución mínima recomendada de 1280 x 720; en móvil la navegación se adapta.",
            "Conexión al servidor donde está publicada la aplicación.",
            "JavaScript habilitado para las tablas paginadas, el calendario y las gráficas.",
            "Una cuenta activa creada por el Administrador General.",
        ]
    )
    doc.nota(
        "Recursos externos",
        "Las tablas, el calendario y las gráficas cargan librerías desde CDN. Sin salida a internet, lo "
        "esencial de SATE sigue funcionando, pero esas mejoras visuales pueden no aparecer.",
        color=AMBAR,
        fondo=(255, 251, 235),
    )

    doc.h2_imagen(
        "Iniciar sesión",
        "02-login.png",
        "Pantalla de inicio de sesión. El texto gris de los campos es un ejemplo, no un valor escrito.",
    )
    doc.p(
        "Abre la dirección del sitio y entra a /login, o pulsa «Ir al panel» desde la navegación pública. "
        "La pantalla muestra el título TechTrack SATE, dos campos y el botón «Ingresar a SATE»."
    )
    doc.numerada(
        [
            "Escribe tu correo electrónico completo en «Correo Electrónico».",
            "Escribe tu contraseña en «Contraseña». El contenido se oculta con puntos.",
            "Pulsa «Ingresar a SATE».",
            "Si tus datos son correctos, entrarás al panel principal. Si tu contraseña es temporal, irás a Mi Perfil.",
        ]
    )
    doc.p(
        "El texto gris que aparece dentro de los campos es un marcador de ejemplo: el correo no está "
        "prellenado. Debes borrarlo mentalmente y escribir tus propios datos. La contraseña distingue "
        "mayúsculas de minúsculas."
    )
    doc.tabla(
        ["Campo", "Obligatorio", "Descripción"],
        [
            ("Correo Electrónico", "Sí", "Cuenta registrada por el administrador. No se permiten espacios."),
            ("Contraseña", "Sí", "Contraseña personal o temporal. Mínimo 8 caracteres en cuentas nuevas."),
        ],
        [46, 26, 102],
        size=8.7,
        lh=4.5,
    )
    doc.subtitulo("Mensajes de error frecuentes")
    doc.tabla(
        ["Mensaje", "Significado y acción"],
        [
            ("Correo o contraseña incorrectos.", "Los datos no coinciden. Revisa mayúsculas y vuelve a intentar."),
            ("Tu usuario está desactivado. Contacta al administrador.", "La cuenta existe pero está inactiva. Solicita su activación."),
            ("Tu contraseña es temporal. Cámbiala para continuar.", "Debes actualizarla en Mi Perfil antes de usar SATE."),
            ("Tu cuenta ya no está activa. Contacta al administrador.", "La cuenta se desactivó o eliminó durante la sesión."),
        ],
        [62, 112],
        size=8.7,
        lh=4.5,
    )

    doc.h2("Cambio obligatorio de contraseña temporal")
    doc.p(
        "Cuando el Administrador General crea una cuenta o restablece una contraseña, el sistema marca "
        "la clave como temporal. En el primer acceso, SATE redirige a Mi Perfil y bloquea el resto de "
        "los módulos hasta que la contraseña se cambie. Solo se permite consultar el perfil, cambiar el "
        "tema y cerrar sesión."
    )
    doc.imagen("22-perfil.jpg", "Mi Perfil concentra los datos de la cuenta, el tema visual y el cambio de contraseña.")
    doc.numerada(
        [
            "En «Contraseña Actual», escribe la contraseña temporal que recibiste.",
            "En «Nueva Contraseña», escribe una clave de al menos 8 caracteres.",
            "Pulsa «Guardar Cambios». El aviso de contraseña temporal desaparece.",
        ]
    )
    doc.nota(
        "Seguridad",
        "No compartas la contraseña temporal ni la reutilices. Si sospechas que alguien más la conoce, "
        "cámbiala de inmediato desde Mi Perfil.",
        color=ROJO,
        fondo=(254, 242, 242),
    )

    doc.h2("Cerrar sesión")
    doc.p(
        "El botón «Cerrar Sesión» está en la esquina superior derecha de todas las pantallas privadas. "
        "Al pulsarlo, SATE elimina la sesión y vuelve al login. Cierra siempre la sesión en equipos "
        "compartidos o de uso público."
    )

    doc.h2("Olvido de contraseña")
    doc.p(
        "Esta versión no incluye recuperación automática por correo. Si olvidaste tu contraseña, pide al "
        "Administrador General que restablezca la cuenta desde Usuarios y roles. El sistema generará una "
        "contraseña temporal y te pedirá cambiarla al entrar."
    )

    doc.h2("Sesión y seguridad")
    doc.p(
        "La sesión se guarda en una cookie firmada y se renueva con cada petición. SATE valida en cada "
        "una que la cuenta siga existiendo y esté activa, de modo que una desactivación surte efecto casi "
        "de inmediato. Los formularios incorporan un token CSRF que impide enviarlos desde otro sitio."
    )
    doc.vinetas(
        [
            "No dejes una sesión abierta en una computadora compartida: usa siempre «Cerrar Sesión».",
            "El navegador debe aceptar cookies; sin ellas no es posible mantener la sesión.",
            "Si ves un error 400 al enviar un formulario, recarga la página y vuelve a intentarlo.",
            "No dupliques pestañas con formularios abiertos durante mucho tiempo: el token puede caducar.",
            "En producción, publica SATE con HTTPS para proteger las credenciales en tránsito.",
        ]
    )

    # ==================================================================
    # 3. SITIO PUBLICO
    # ==================================================================
    doc.h1("El sitio público")
    doc.p(
        "El sitio público presenta a TechTrack Solutions, su organización y su producto. No requiere "
        "sesión y está pensado para clientes, visitantes, docentes y cualquier persona que necesite "
        "entender qué hace la empresa y cómo se relaciona SATE con sus políticas."
    )

    doc.h2("Estructura y navegación")
    doc.p(
        "La barra superior enlaza Inicio, Empresa, Departamentos, Políticas, Trabaja con nosotros, "
        "Producto SATE y Contacto. El botón «Ir al panel» aparece cuando hay una sesión iniciada; si no, "
        "se muestra «Iniciar sesión». En pantallas pequeñas el menú se reorganiza y el pie de página "
        "conserva los enlaces principales y el aviso de privacidad."
    )
    doc.tabla(
        ["Página", "Ruta", "Contenido principal"],
        [
            ("Inicio", "/", "Propuesta de valor, problema, módulos, beneficios y llamado a la acción."),
            ("Empresa", "/empresa", "Datos generales, misión, visión, objetivos, metas y organigrama."),
            ("Departamentos", "/departamentos", "SIT, Redes, Desarrollo y Soporte, con su ficha detallada."),
            ("Políticas", "/politicas", "Diez políticas de gestión de TI y matriz de responsabilidades."),
            ("Trabaja con nosotros", "/trabaja-con-nosotros", "Perfiles de puesto y formulario de postulación."),
            ("Producto SATE", "/sate", "Problema, funcionamiento, módulos y captura del panel."),
            ("Contacto", "/contacto", "Formulario de contacto y datos de la empresa."),
            ("Cumplimiento del PIA", "/cumplimiento-pia", "Matriz de evidencias entre el documento y la aplicación."),
            ("Aviso de privacidad", "/privacidad", "Tratamiento de datos personales del sitio."),
            ("Acceso", "/login", "Inicio de sesión del sistema privado."),
        ],
        [42, 46, 86],
        size=8.5,
        lh=4.4,
    )
    doc.p(
        "El sitio genera además /sitemap.xml con 27 direcciones públicas, /robots.txt con las reglas de "
        "indexación y archivos de favicon para navegadores y dispositivos móviles. Las páginas privadas "
        "y el login declaran noindex, nofollow."
    )

    doc.h2_imagen("Inicio", "01-inicio.png", "Página de inicio del sitio público de TechTrack Solutions.")
    doc.p(
        "La portada abre con el mensaje «Control total de tus activos tecnológicos» y resume el problema "
        "que atiende SATE. Después presenta los módulos, los beneficios, la estructura de la empresa y "
        "un cierre con invitación a conocer el producto. Los botones conducen a Producto SATE y a "
        "Contacto."
    )

    doc.h2_imagen("Empresa", "13-empresa.jpg", "Página de Empresa con la ficha institucional y el organigrama.")
    doc.p(
        "La página de Empresa reúne la ficha institucional: nombre, giro, descripción, propuesta de "
        "valor y clientes objetivo. También publica misión, visión, objetivos y metas, y un organigrama "
        "interactivo en el que Dirección General coordina SIT, Redes y Desarrollo, mientras Soporte "
        "depende de Desarrollo y opera con funciones propias."
    )

    doc.h2_imagen("Departamentos", "14-departamentos.jpg", "Vista general de los cuatro departamentos.")
    doc.p(
        "La vista general presenta cuatro áreas y permite entrar a cada una. La ficha de un "
        "departamento explica su función, su objetivo, sus funciones principales, las políticas que "
        "lidera, aquellas en las que participa y el perfil de puesto asociado."
    )
    doc.tabla(
        ["Departamento", "Función resumida"],
        [
            ("SIT", "Administra el ciclo de vida de los activos tecnológicos, de su alta a su baja."),
            ("Redes", "Administra, monitorea y protege la infraestructura de red."),
            ("Desarrollo", "Diseña, programa, prueba y mantiene el sistema SATE."),
            ("Soporte", "Atiende incidentes y solicitudes de los usuarios y escala lo necesario."),
        ],
        [38, 136],
        size=8.7,
        lh=4.5,
    )
    doc.imagen("28-departamento-detalle.png", "Ficha del departamento de Desarrollo con sus funciones y políticas.")

    doc.h2_imagen("Políticas", "15-politicas.jpg", "Catálogo de políticas y matriz de responsabilidades.")
    doc.p(
        "El catálogo publica diez políticas de gestión de TI. Cada ficha incluye objetivo, alcance, qué "
        "regula, reglas y lineamientos, procedimiento general, responsables por área y la relación con "
        "SATE. La página principal también muestra una matriz que indica qué área lidera (R) y cuáles "
        "participan (P) en cada política."
    )
    doc.tabla(
        ["No.", "Política", "Área responsable"],
        [
            ("1", "Gestión de activos", "SIT"),
            ("2", "Gestión de configuración", "SIT"),
            ("3", "Gestión de cambios", "Desarrollo"),
            ("4", "Gestión de capacidad", "Redes"),
            ("5", "Gestión de disponibilidad", "Redes"),
            ("6", "Gestión de incidentes", "Soporte"),
            ("7", "Gestión de problemas", "Soporte"),
            ("8", "Gestión de continuidad", "Redes"),
            ("9", "Seguridad de la información", "Redes"),
            ("10", "Gestión de proveedores", "SIT"),
        ],
        [14, 100, 60],
        size=8.7,
        lh=4.5,
    )
    doc.imagen("29-politica-detalle.png", "Detalle de la Política de gestión de activos.")

    doc.h2_imagen("Trabaja con nosotros", "16-trabaja.jpg", "Página de Trabaja con nosotros con los perfiles disponibles.")
    doc.p(
        "La página publica los cuatro perfiles de puesto del PIA: Administrador de Activos "
        "Tecnológicos, Administrador de Redes y Seguridad, Desarrollador de Software (SATE) y Técnico de "
        "Soporte. Cada perfil muestra objetivo, funciones, escolaridad, experiencia, conocimientos, "
        "competencias, herramientas y condiciones generales."
    )
    doc.p(
        "Al final de cada perfil hay un formulario con nombre, correo, teléfono, mensaje y aceptación "
        "del aviso de privacidad. La postulación se guarda en la tabla postulaciones y se confirma con "
        "un mensaje en pantalla. Esta versión no incluye una bandeja administrativa para revisar "
        "postulaciones dentro de SATE; la consulta se hace directamente en la base de datos."
    )
    doc.imagen("30-perfil-puesto.png", "Detalle de un perfil de puesto y formulario de postulación.")

    doc.h2_imagen("Producto SATE", "17-sate.jpg", "Página del producto SATE con el flujo de trabajo y los módulos.")
    doc.p(
        "La página de Producto SATE explica el problema de la información dispersa, cómo funciona la "
        "plataforma y el recorrido desde el alta de un equipo hasta el cierre de una incidencia. "
        "También resume los módulos y muestra una captura del panel principal. Es la mejor introducción "
        "para quien verá el sistema por primera vez."
    )

    doc.h2_imagen("Contacto", "18-contacto.jpg", "Formulario de contacto del sitio público.")
    doc.p(
        "El formulario solicita nombre, organización, correo, teléfono opcional, motivo, mensaje y "
        "aceptación del aviso de privacidad. Al enviarlo, el mensaje se guarda en la tabla "
        "mensajes_contacto y se muestra una confirmación. Los campos nombre, organización, correo, "
        "motivo, mensaje y aceptación son obligatorios; el correo debe contener @."
    )

    doc.h2_imagen("Cumplimiento del PIA", "12-cumplimiento.png", "Matriz de cumplimiento del PIA con evidencias publicadas e implementadas.")
    doc.p(
        "La página /cumplimiento-pia conecta los apartados del Proyecto Integrador con la página o "
        "módulo donde se demuestran. Presenta 16 evidencias y distingue entre contenido «Publicado» y "
        "funcionalidad «Implementado». Es una página de consulta para evaluación y presentación, no un "
        "módulo operativo."
    )

    doc.h2("Aviso de privacidad y páginas de error")
    doc.p(
        "El aviso de privacidad explica qué datos se recaban en los formularios, con qué finalidad y "
        "cómo se protegen. Está enlazado desde el pie de página y desde las casillas de aceptación. El "
        "sitio incluye además páginas propias para los errores 400, 403, 404 y 500, con un enlace para "
        "volver al inicio."
    )
    doc.p(
        "En conjunto, el sitio público funciona como carta de presentación institucional y como "
        "evidencia documental del PIA. No requiere base de datos para las páginas informativas; solo los "
        "formularios de contacto y postulación escriben en la base."
    )

    # ==================================================================
    # 4. CONCEPTOS
    # ==================================================================
    doc.h1("Conceptos básicos de SATE")
    doc.p(
        "Antes de recorrer los módulos conviene fijar el vocabulario. Estos conceptos aparecen en casi "
        "todas las pantallas y explican por qué el sistema se comporta de cierta manera."
    )

    doc.h2("Activo e identificador único")
    doc.p(
        "Un activo es cualquier equipo tecnológico registrado: laptop, computadora de escritorio, "
        "monitor, servidor, impresora u otro. Cada activo recibe un identificador único generado por "
        "SATE a partir del tipo y un consecutivo de tres dígitos. El identificador no se reutiliza, "
        "aunque el equipo se dé de baja."
    )
    doc.tabla(
        ["Tipo de activo", "Prefijo", "Ejemplo"],
        [
            ("Laptop", "LAP", "LAP-001"),
            ("Computadora de Escritorio", "COM", "COM-001"),
            ("Monitor", "MON", "MON-001"),
            ("Servidor", "SRV", "SRV-001"),
            ("Impresora", "IMP", "IMP-001"),
            ("Otro", "OTR", "OTR-001"),
        ],
        [70, 34, 70],
        size=8.7,
        lh=4.5,
    )

    doc.h2("Estados del activo")
    doc.p(
        "El estado resume la situación operativa del equipo. SATE lo recalcula automáticamente cuando "
        "hay mantenimientos o incidencias abiertas, salvo que el activo esté dado de baja."
    )
    doc.tabla(
        ["Estado", "Significado", "Cuándo aparece"],
        [
            ("Operativo", "El equipo funciona y está disponible.", "Sin mantenimientos abiertos ni incidencias abiertas."),
            ("En Mantenimiento", "El equipo está en servicio técnico.", "Existe un mantenimiento En proceso o Pendiente con fecha vencida."),
            ("Con Falla", "El equipo presenta una falla reportada.", "Existe una incidencia Nueva, Asignada o En proceso."),
            ("Baja", "El equipo se retiró del inventario activo.", "Se cambia manualmente; el historial se conserva."),
        ],
        [38, 62, 74],
        size=8.6,
        lh=4.5,
    )
    doc.nota(
        "Regla automática",
        "Si hay un mantenimiento abierto, el estado es En Mantenimiento. Si no lo hay pero existe una "
        "incidencia abierta, es Con Falla. Si no hay ninguno, vuelve a Operativo. La baja es la única "
        "excepción: se respeta y no se recalcula.",
    )

    doc.h2("Mantenimiento")
    doc.p(
        "Un mantenimiento es un servicio programado sobre un activo. Puede ser preventivo, para revisar "
        "y conservar el equipo, o correctivo, para reparar una falla. Se registra con descripción, fecha "
        "programada y técnico responsable, y avanza por tres estados: Pendiente, En proceso y "
        "Finalizado. Al finalizar se guarda la fecha de finalización y las observaciones."
    )

    doc.h2("Incidencia")
    doc.p(
        "Una incidencia es el reporte de una falla o solicitud sobre un equipo. Tiene prioridad, "
        "solicitante, equipo afectado, descripción, técnico o área asignada, diagnóstico y resolución. "
        "Su ciclo va de Nueva a Cerrada, pasando por Asignada, En proceso y Resuelta. El cierre registra "
        "la fecha y permite documentar qué se hizo."
    )
    doc.tabla(
        ["Prioridad", "Criterio orientativo"],
        [
            ("Baja", "No afecta el trabajo diario."),
            ("Media", "Es una molestia, pero permite trabajar."),
            ("Alta", "Impide trabajar a un usuario."),
            ("Crítica", "Afecta a todo un departamento o a un sistema completo."),
        ],
        [38, 136],
        size=8.7,
        lh=4.5,
    )

    doc.h2("Historial y auditoría")
    doc.p(
        "El historial es la línea de tiempo de un activo: altas, cambios de responsable, ubicación o "
        "estado, mantenimientos e incidencias. Cada registro guarda el tipo de movimiento, el detalle, "
        "el usuario que lo hizo y la fecha. La auditoría, por su parte, registra las acciones relevantes "
        "del sistema para trazabilidad administrativa."
    )
    doc.p(
        "El historial no se borra al dar de baja un equipo: se conserva como evidencia de su ciclo de "
        "vida. Tampoco se escribe un movimiento si una edición no cambió ningún valor."
    )

    doc.h2("Alcance por rol")
    doc.p(
        "No todos los usuarios ven la misma información. La mayoría de los roles tiene alcance global; "
        "el Usuario Solicitante tiene alcance restringido: solo consulta los activos de su departamento "
        "y únicamente sus propias incidencias. Este límite se aplica en listados, fichas, reportes y "
        "códigos QR, no solo en el menú."
    )

    doc.h2("Ciclo de vida de un activo")
    doc.p(
        "El recorrido típico de un equipo dentro de SATE sigue cinco etapas. Comprenderlas ayuda a "
        "decidir qué módulo usar en cada momento."
    )
    doc.numerada(
        [
            "Alta: se registra el equipo con tipo, marca, modelo, serie, responsable y departamento. SATE asigna el identificador.",
            "Asignación: se actualiza la ubicación y el responsable cada vez que el equipo cambia de manos o de espacio.",
            "Mantenimiento: se programa el servicio preventivo o correctivo y se documenta su cierre.",
            "Incidencia: si el equipo falla, se reporta el caso, se diagnostica y se resuelve.",
            "Baja: cuando el equipo se retira, se cambia su estado a Baja; el historial permanece disponible.",
        ]
    )

    # ==================================================================
    # 5. ROLES
    # ==================================================================
    doc.h1("Roles y permisos")
    doc.p(
        "SATE usa los siete roles de la estructura organizacional del PIA. El rol determina qué módulos "
        "aparecen en el menú y qué acciones se pueden ejecutar. El Administrador General asigna el rol "
        "al crear o editar una cuenta."
    )

    doc.h2("Los siete roles")
    doc.tabla(
        ["Rol", "Alcance"],
        [
            ("Administrador General", "Control total de SATE, incluida la gestión de usuarios y roles."),
            ("Dirección General", "Consulta de indicadores, activos, mantenimientos e incidencias."),
            ("Administrador de Activos", "Administra inventario, asignaciones y mantenimientos; consulta incidencias."),
            ("Administrador de Redes", "Atiende mantenimientos e incidencias de infraestructura; consulta activos."),
            ("Desarrollador", "Atiende incidencias de software; consulta activos y mantenimientos."),
            ("Técnico de Soporte", "Registra, atiende y cierra incidencias y mantenimientos; edita activos."),
            ("Usuario Solicitante", "Consulta activos de su área y reporta sus propias incidencias."),
        ],
        [48, 126],
        size=8.6,
        lh=4.6,
    )

    doc.h2("Matriz de permisos")
    doc.p(
        "La siguiente matriz resume las acciones por módulo. La leyenda es: V = ver, C = crear, "
        "E = editar, A = administrar cuentas. Un guion indica que el rol no tiene acceso al módulo."
    )
    doc.tabla(
        ["Rol", "Panel", "Activos", "Mantenim.", "Incidencias", "Usuarios"],
        [
            ("Administrador General", "V", "V · C · E", "V · C · E", "V · C · E", "V · C · E · A"),
            ("Dirección General", "V", "V", "V", "V", "-"),
            ("Administrador de Activos", "V", "V · C · E", "V · C · E", "V", "-"),
            ("Administrador de Redes", "V", "V", "V · C · E", "V · C · E", "-"),
            ("Desarrollador", "V", "V", "V", "V · C · E", "-"),
            ("Técnico de Soporte", "V", "V · E", "V · C · E", "V · C · E", "-"),
            ("Usuario Solicitante", "V", "V (su área)", "-", "V · C (propias)", "-"),
        ],
        [40, 18, 30, 30, 32, 24],
        size=7.9,
        lh=4.4,
    )
    doc.p(
        "Los permisos se aplican en el servidor. Ocultar un botón no es suficiente: si un usuario intenta "
        "entrar a una ruta sin permiso, SATE responde con acceso denegado. El alcance por departamento "
        "del Usuario Solicitante también se valida en cada consulta."
    )

    doc.h2("Reglas de administración de cuentas")
    doc.vinetas(
        [
            "Solo el Administrador General puede ver y administrar Usuarios y roles.",
            "No se puede desactivar la propia cuenta.",
            "No se puede desactivar ni quitar el rol al último Administrador General activo.",
            "Las cuentas nuevas y las contraseñas restablecidas son temporales.",
            "Al desactivar o eliminar una cuenta, la sesión abierta se invalida en la siguiente petición.",
            "Un cambio de rol se aplica cuando el usuario vuelve a iniciar sesión.",
        ]
    )

    # ==================================================================
    # 6. PANEL
    # ==================================================================
    doc.h1("Panel principal")
    doc.p(
        "El panel es la primera pantalla después de iniciar sesión. Resume el estado del inventario, "
        "los pendientes y la actividad reciente, y ofrece accesos directos a las tareas más frecuentes. "
        "Su contenido cambia según el rol: no muestra módulos ni acciones que el usuario no pueda usar."
    )

    doc.h2_imagen("Qué muestra el panel", "03-panel-admin.png", "Panel principal con la vista del Administrador General.")
    doc.p(
        "La cabecera saluda al usuario, muestra su nombre y su rol. Debajo aparecen las alertas, los "
        "indicadores, la actividad reciente, los accesos rápidos y las gráficas. En el rol Usuario "
        "Solicitante se agrega una nota que explica el alcance de su cuenta."
    )

    doc.h2("Alertas de atención")
    doc.p(
        "El bloque «Requiere tu atención» aparece cuando hay pendientes y enlaza a la vista ya filtrada. "
        "Puede mostrar tres tipos de alerta:"
    )
    doc.vinetas(
        [
            "Mantenimientos vencidos sin finalizar, con enlace a la vista filtrada por vencidos.",
            "Mantenimientos por vencer en los próximos 7 días, con enlace a la vista filtrada.",
            "Incidencias críticas abiertas desde hace más de 24 horas, con enlace a la prioridad Crítica.",
        ]
    )

    doc.h2("Indicadores")
    doc.tabla(
        ["Indicador", "Qué cuenta"],
        [
            ("Activos registrados", "Equipos no dados de baja. En el solicitante se titula «Activos de mi área»."),
            ("Mantenimientos pendientes", "Servicios que no están finalizados, con vencidos y próximos como pista."),
            ("Incidencias abiertas", "Casos que aún no se resuelven. En el solicitante, solo los propios."),
            ("Usuarios activos", "Cuentas habilitadas. Solo visible para quien puede gestionar usuarios."),
        ],
        [52, 122],
        size=8.7,
        lh=4.5,
    )

    doc.h2("Actividad reciente")
    doc.p(
        "Reúne tres bloques: incidencias recientes, mantenimientos próximos y movimientos de activos. "
        "Cada elemento enlaza a su ficha y muestra fecha, estado y una pista del detalle. Si no hay "
        "datos, aparece un mensaje vacío en lugar de una tabla en blanco."
    )

    doc.h2("Accesos rápidos y gráficas")
    doc.p(
        "Los accesos rápidos permiten registrar un activo, programar un mantenimiento, reportar una "
        "incidencia o abrir un listado, según el rol. Las gráficas muestran la distribución del "
        "inventario por estado y, si el rol puede ver incidencias, la distribución de incidencias por "
        "estado. Cuando todavía no hay datos, la gráfica se sustituye por un estado vacío con una "
        "acción para empezar."
    )

    doc.h2_imagen("Panel del Usuario Solicitante", "23-panel-solicitante.png", "Panel del Usuario Solicitante con el alcance de su departamento.")
    doc.p(
        "El solicitante ve «Activos de mi área» y «Mis incidencias abiertas». La nota de alcance indica "
        "su departamento y recuerda que solo puede consultar sus propios reportes. Los accesos de alta "
        "se limitan a reportar una incidencia; no puede crear activos ni mantenimientos."
    )

    doc.h2("Navegación y uso en móvil")
    doc.p(
        "En pantallas de hasta 900 px, el menú lateral se convierte en un panel deslizante. El botón "
        "«Menú» lo abre; el overlay, el botón de cierre o la tecla Escape lo cierran, y el foco vuelve "
        "al botón. Mientras está cerrado, el menú queda fuera del recorrido de teclado y de lectores de "
        "pantalla. Las tablas y tarjetas se apilan para conservar la legibilidad."
    )

    doc.h2("Buenas prácticas del panel")
    doc.p(
        "El panel es un punto de partida, no un reporte histórico. Estas rutinas ayudan a que la "
        "información mostrada siga siendo útil para todo el equipo."
    )
    doc.vinetas(
        [
            "Revisa al inicio de la jornada las alertas de vencidos, próximos y críticas.",
            "Atiende primero lo que bloquea el trabajo de un usuario o afecta a un área completa.",
            "Mantén actualizados los estados: un panel con datos viejos pierde utilidad.",
            "Usa los accesos rápidos en lugar de navegar por varios menús para registrar un pendiente.",
            "Si una gráfica aparece vacía, verifica que existan datos y que tu rol tenga alcance sobre ellos.",
            "Recuerda que el solicitante solo ve su área y sus propios reportes: no interpretes su panel como el total de la empresa.",
        ]
    )

    doc.h2("Caso práctico: inicio de jornada")
    doc.p(
        "Un técnico de Soporte abre SATE al comenzar el día y quiere saber qué atender primero. Este es "
        "el recorrido recomendado."
    )
    doc.numerada(
        [
            "Inicia sesión y observa el bloque «Requiere tu atención».",
            "Si hay incidencias críticas con más de 24 horas, ábrelas desde el enlace de la alerta.",
            "Revisa los mantenimientos vencidos y confirma si el trabajo ya se realizó.",
            "Consulta los mantenimientos de los próximos 7 días para anticipar refacciones o tiempos.",
            "Usa los accesos rápidos para registrar una incidencia o programar un servicio sin salir del panel.",
            "Al terminar, actualiza los estados: el panel del día siguiente reflejará la información real.",
        ]
    )

    # ==================================================================
    # 7. ACTIVOS
    # ==================================================================
    doc.h1("Activos e historial")
    doc.p(
        "Este módulo es el corazón de SATE. Permite registrar cada equipo, consultarlo, editarlo, "
        "imprimir su resguardo, generar un reporte de inventario y obtener su etiqueta con código QR. "
        "También conserva la línea de tiempo que explica qué le ocurrió al activo."
    )

    doc.h2_imagen("Listado y filtros", "04-activos.png", "Inventario de activos con filtros, contador y acciones por fila.")
    doc.p(
        "La vista /app/activos muestra una tabla paginada de diez filas. Los filtros se combinan entre "
        "sí y se aplican en el servidor, por lo que también afectan al reporte PDF. El botón «Limpiar» "
        "restablece todos los criterios."
    )
    doc.tabla(
        ["Filtro", "Qué busca"],
        [
            ("Buscar", "Nombre, identificador, número de serie, marca, modelo o responsable."),
            ("Estado", "Operativo, En Mantenimiento, Con Falla o Baja."),
            ("Tipo", "Laptop, Computadora de Escritorio, Monitor, Servidor, Impresora u Otro."),
            ("Departamento", "SIT, Redes, Desarrollo o Soporte."),
        ],
        [38, 136],
        size=8.7,
        lh=4.5,
    )
    doc.p(
        "La tabla muestra ID, nombre, tipo, responsable, departamento, estado y acciones. «Ver» abre la "
        "ficha; «Editar» aparece solo si el rol puede modificar activos. El contador superior indica "
        "cuántos equipos coinciden con los filtros."
    )

    doc.h2_imagen("Registrar un activo", "10-nuevo-activo.png", "Formulario de alta de un activo tecnológico.")
    doc.p(
        "El botón «+ Nuevo Activo» abre el formulario. Al guardar, SATE genera el identificador, registra "
        "el alta en el historial y en la auditoría, y abre la ficha del equipo. Los campos marcados como "
        "obligatorios son nombre, tipo, responsable y departamento."
    )
    doc.tabla(
        ["Campo", "Obligatorio", "Descripción"],
        [
            ("Nombre del Equipo", "Sí", "Descripción corta y reconocible, por ejemplo «Laptop Dell Desarrollo»."),
            ("Tipo de Activo", "Sí", "Define el prefijo del identificador."),
            ("Marca", "No", "Fabricante del equipo."),
            ("Modelo", "No", "Modelo comercial."),
            ("Número de Serie", "No", "Serie del fabricante; ayuda a conciliar el inventario físico."),
            ("Ubicación", "No", "Oficina, piso, rack o mesa donde se encuentra."),
            ("Responsable Asignado", "Sí", "Persona que resguarda el equipo."),
            ("Departamento Asignado", "Sí", "Área a la que pertenece el activo."),
        ],
        [48, 26, 100],
        size=8.5,
        lh=4.4,
    )
    doc.nota(
        "Identificador automático",
        "El identificador se forma con el prefijo del tipo y un consecutivo de tres dígitos. Si el "
        "último LAP es LAP-007, el siguiente será LAP-008. No se reutilizan números de equipos dados de "
        "baja.",
    )

    doc.h2_imagen("Ficha del activo", "05-detalle-activo.png", "Ficha del activo con datos, asignación, QR e historial.")
    doc.p(
        "La ficha reúne cuatro bloques. «Datos del equipo» muestra nombre, tipo, marca, modelo y serie. "
        "«Asignación y estado» muestra responsable, departamento, ubicación y estado actual, con los "
        "botones «Editar información» y «Acta en PDF». Después aparece la identificación por QR y, al "
        "final, el historial de movimientos."
    )

    doc.h2_imagen("Editar un activo", "26-editar-activo.png", "Edición de los datos de asignación y estado de un activo.")
    doc.p(
        "El formulario de edición permite cambiar nombre, ubicación, responsable, departamento y estado. "
        "El tipo, la marca, el modelo y el número de serie se capturan al crear y no se editan en esta "
        "versión. Cada cambio se compara con el valor anterior y se registra en el historial con el "
        "usuario y la fecha; si no hubo cambios, no se escribe nada."
    )

    doc.h2("Historial de movimientos")
    doc.p(
        "La línea de tiempo muestra altas, cambios de datos, mantenimientos programados o actualizados e "
        "incidencias reportadas. Cada elemento incluye un distintivo de tipo, la fecha, el detalle y el "
        "usuario que lo registró. Los cambios de datos se presentan como «campo: valor anterior -> valor "
        "nuevo», lo que permite reconstruir la historia del equipo."
    )
    doc.p(
        "El historial se conserva incluso si el activo se da de baja. Es la evidencia que permite "
        "responder quién tuvo el equipo, dónde estuvo y qué servicios recibió."
    )

    doc.h2("Acta de resguardo en PDF")
    doc.p(
        "El botón «Acta en PDF» genera un documento con los datos del activo y un texto de entrega "
        "formal. Incluye identificador, nombre, categoría, marca, modelo, serie y departamento, además "
        "de los compromisos del usuario y dos espacios de firma: aceptación del responsable y "
        "autorización de SIT. Es útil para entregar equipos y dejar constancia documental."
    )
    doc.nota(
        "Permiso requerido",
        "El acta está disponible para roles con permiso de edición de activos. Si solo puedes consultar "
        "el inventario, el botón no aparece.",
    )

    doc.h2("Reporte de inventario en PDF")
    doc.p(
        "El botón «Reporte PDF» genera un documento horizontal con los filtros activos. Incluye la fecha "
        "de generación, el total de activos, un resumen de filtros y una tabla con identificador, "
        "nombre, tipo, marca, modelo, serie, departamento, responsable, ubicación y estado. Respeta el "
        "alcance del rol: el Usuario Solicitante solo obtiene los equipos de su departamento."
    )

    doc.h2("Código QR y etiqueta imprimible")
    doc.p(
        "Cada ficha incluye un código QR que abre la misma ficha desde un teléfono. El QR se genera en "
        "SVG, por lo que puede imprimirse a cualquier tamaño sin perder nitidez, y no guarda datos del "
        "equipo: solo codifica la dirección de la ficha. El botón «Descargar QR» guarda el archivo SVG."
    )
    doc.p(
        "El botón «Imprimir etiqueta» abre una etiqueta de 90 x 55 mm con la marca TechTrack Solutions, "
        "el identificador, el nombre del equipo, el tipo, el departamento, el estado y el QR. La página "
        "incluye estilos de impresión para que solo se imprima la etiqueta."
    )
    doc.imagen("06-etiqueta.png", "Etiqueta imprimible de 90 x 55 mm con el código QR del activo.")
    doc.nota(
        "Uso desde un teléfono",
        "El QR codifica la dirección absoluta de la ficha. Si SATE está publicado en 127.0.0.1 o "
        "localhost, el teléfono no podrá abrirlo. Para probarlo en la red local, publica la aplicación "
        "con la IP de la computadora y vuelve a generar la etiqueta.",
        color=AMBAR,
        fondo=(255, 251, 235),
    )

    doc.h2("Buenas prácticas de inventario")
    doc.vinetas(
        [
            "Registra el activo antes de entregarlo y captura el número de serie cuando exista.",
            "Actualiza responsable y ubicación el mismo día del cambio.",
            "Usa la baja lógica en lugar de borrar el registro; así conservas el historial.",
            "Imprime la etiqueta después de cualquier cambio de identificador o departamento.",
            "Concilia periódicamente el inventario físico con el reporte PDF.",
        ]
    )

    # ==================================================================
    # 8. MANTENIMIENTOS
    # ==================================================================
    doc.h1("Mantenimientos")
    doc.p(
        "El módulo de mantenimientos organiza los servicios preventivos y correctivos. Permite ver qué "
        "equipos requieren atención, programar una fecha, asignar un técnico y cerrar el servicio con "
        "observaciones. El panel y las alertas se alimentan de esta información."
    )

    doc.h2_imagen("Listado, filtros y calendario", "07-mantenimientos.png", "Listado de mantenimientos con filtros y calendario mensual.")
    doc.p(
        "La vista /app/mantenimientos combina una tabla con un calendario mensual. La tabla muestra ID, "
        "equipo, tipo, fecha, responsable, estado y acciones. Los filtros permiten buscar por equipo, "
        "identificador, descripción o responsable, y acotar por estado, tipo y vencimiento."
    )
    doc.tabla(
        ["Filtro", "Valores"],
        [
            ("Buscar", "Equipo, identificador, descripción o responsable."),
            ("Estado", "Pendiente, En proceso o Finalizado."),
            ("Tipo", "Preventivo o Correctivo."),
            ("Vencimiento", "Próximos 7 días o Vencidos sin finalizar."),
        ],
        [38, 136],
        size=8.7,
        lh=4.5,
    )
    doc.p(
        "En el calendario, los eventos se colorean según el estado: ámbar para Pendiente, azul para En "
        "proceso y verde para Finalizado. Al pulsar un evento se muestra su título con el equipo y el "
        "tipo de servicio."
    )

    doc.h2_imagen("Programar un mantenimiento", "19-nuevo-mantenimiento.jpg", "Formulario para programar un mantenimiento preventivo o correctivo.")
    doc.p(
        "El botón «+ Programar Mantenimiento» abre el formulario. Al guardar, SATE registra el servicio, "
        "recalcula el estado del activo y agrega el movimiento al historial. No se pueden seleccionar "
        "activos dados de baja."
    )
    doc.tabla(
        ["Campo", "Obligatorio", "Descripción"],
        [
            ("Seleccionar Equipo", "Sí", "Activo que recibirá el servicio; excluye los dados de baja."),
            ("Tipo de Mantenimiento", "Sí", "Preventivo (revisión o limpieza) o Correctivo (reparación)."),
            ("Descripción del Trabajo", "Sí", "Qué se realizará, en una línea clara."),
            ("Fecha Programada", "Sí", "Fecha del servicio. Si queda en el pasado, aparecerá como vencido."),
            ("Técnico Responsable", "Sí", "Persona o área que ejecutará el trabajo."),
        ],
        [48, 26, 100],
        size=8.5,
        lh=4.4,
    )

    doc.h2_imagen("Ficha del mantenimiento", "20-detalle-mantenimiento.jpg", "Ficha de un mantenimiento con los datos del servicio y del equipo.")
    doc.p(
        "La ficha muestra los datos del servicio (tipo, estado, fecha programada, fecha de finalización "
        "y responsable) y los datos del equipo intervenido (nombre, identificador, tipo, departamento, "
        "ubicación y estado). Debajo aparecen la descripción del trabajo y las observaciones. Los "
        "botones permiten editar el mantenimiento y descargar la orden en PDF."
    )

    doc.h2_imagen("Editar y cerrar un mantenimiento", "27-editar-mantenimiento.png", "Cierre de un mantenimiento con observaciones del trabajo realizado.")
    doc.p(
        "El formulario de edición permite cambiar el estado y las observaciones. Al pasar a Finalizado, "
        "SATE guarda la fecha de finalización y recalcula el estado del activo: si no quedan "
        "mantenimientos ni incidencias abiertas, vuelve a Operativo. Si se reabre el servicio, la fecha "
        "de finalización se limpia."
    )
    doc.nota(
        "Trazabilidad",
        "Cada cambio de estado genera un movimiento en el historial del activo y un registro de "
        "auditoría. No es necesario editar el activo por separado: el mantenimiento actualiza su estado.",
    )

    doc.h2("Orden de trabajo en PDF")
    doc.p(
        "El botón «Orden en PDF» genera un documento con los datos del equipo y del servicio: tipo, "
        "fecha programada, estado, descripción y responsable. Sirve para entregar la orden al técnico o "
        "para archivar la evidencia del mantenimiento."
    )

    doc.h2("Alertas y vencimientos")
    doc.p(
        "El panel muestra dos alertas de mantenimiento: vencidos sin finalizar y próximos a vencer en "
        "los próximos 7 días. Ambas enlazan a la vista filtrada. La alerta de próximos incluye los "
        "servicios con fecha entre hoy y dentro de siete días; la de vencidos, los anteriores a hoy que "
        "siguen pendientes o en proceso."
    )

    doc.h2("Flujo recomendado")
    doc.numerada(
        [
            "Registra el mantenimiento con fecha, tipo, descripción y responsable.",
            "Verifica que el activo haya cambiado a En Mantenimiento.",
            "Cuando inicie el trabajo, cambia el estado a En proceso.",
            "Al terminar, cambia a Finalizado y documenta las observaciones.",
            "Confirma que el activo volvió a Operativo o que conserva la falla si hay una incidencia abierta.",
            "Descarga la orden en PDF si necesitas evidencia documental.",
        ]
    )

    doc.h2("Indicadores de mantenimiento")
    doc.p(
        "Aunque SATE no incluye un módulo de reportes avanzados, los filtros y el panel permiten "
        "responder las preguntas habituales de seguimiento."
    )
    doc.tabla(
        ["Pregunta", "Cómo responderla"],
        [
            ("¿Cuántos servicios están pendientes?", "Filtra por estado Pendiente o En proceso en el listado."),
            ("¿Qué equipos están vencidos?", "Usa el filtro Vencidos sin finalizar o la alerta del panel."),
            ("¿Qué vence esta semana?", "Usa el filtro Próximos 7 días."),
            ("¿Qué proporción es preventiva?", "Filtra por tipo Preventivo y compara con el total del contador."),
            ("¿Qué equipos requieren más atención?", "Revisa el historial del activo y los servicios repetidos."),
        ],
        [62, 112],
        size=8.6,
        lh=4.5,
    )

    doc.h2("Caso práctico: servicio vencido")
    doc.p(
        "Un mantenimiento preventivo quedó programado para la semana pasada y sigue pendiente. Así se "
        "regulariza sin perder la trazabilidad."
    )
    doc.numerada(
        [
            "Abre el listado con el filtro Vencidos sin finalizar.",
            "Confirma con el responsable si el servicio se realizó o debe reprogramarse.",
            "Si se realizó, cambia el estado a Finalizado y documenta el trabajo en las observaciones.",
            "Si no se realizó, edita la fecha programada y avisa al área usuaria del nuevo compromiso.",
            "Verifica que el estado del activo sea coherente: En Mantenimiento mientras esté abierto.",
            "Al cerrar, revisa el historial del activo para confirmar que el movimiento quedó registrado.",
        ]
    )
    # ==================================================================
    # 9. INCIDENCIAS
    # ==================================================================
    doc.h1("Incidencias")
    doc.p(
        "El módulo de incidencias registra fallas y solicitudes, les asigna prioridad y responsable, y "
        "documenta el diagnóstico y la solución. Es el canal formal para que un usuario reporte un "
        "problema y para que Soporte, Redes o Desarrollo lo atiendan."
    )

    doc.h2_imagen("Listado y filtros", "08-incidencias.png", "Listado de incidencias con prioridad, estado y responsables.")
    doc.p(
        "La vista /app/incidencias muestra los tickets con equipo afectado, falla reportada, prioridad, "
        "estado, solicitante, asignado y acciones. Los filtros permiten buscar por descripción, equipo, "
        "identificador o asignado, y acotar por estado y prioridad. El Usuario Solicitante ve solo sus "
        "propias incidencias y el título cambia a «Mis incidencias»."
    )

    doc.h2_imagen("Reportar una incidencia", "25-nueva-incidencia.png", "Formulario para reportar una incidencia.")
    doc.p(
        "El botón «+ Reportar Incidencia» abre el formulario. El ticket se crea en estado Nueva, con el "
        "usuario actual como solicitante y la fecha de registro actual. El equipo debe existir y no "
        "estar dado de baja."
    )
    doc.tabla(
        ["Campo", "Obligatorio", "Descripción"],
        [
            ("Equipo que presenta la falla", "Sí", "Activo afectado. El solicitante solo ve equipos de su alcance."),
            ("Descripción detallada", "Sí", "Qué ocurre, desde cuándo y qué se intentó. Evita textos vagos."),
            ("Prioridad", "Sí", "Baja, Media, Alta o Crítica, según el impacto."),
            ("Técnico o Área Asignada", "Sí", "Persona o área que atenderá el caso."),
        ],
        [52, 26, 96],
        size=8.5,
        lh=4.4,
    )

    doc.h2_imagen("Ficha de la incidencia", "21-detalle-incidencia.jpg", "Ficha de una incidencia con reporte, equipo, diagnóstico y resolución.")
    doc.p(
        "La ficha presenta el reporte (estado, prioridad, fecha de registro, fecha de cierre, "
        "solicitante y asignado), el equipo afectado y tres bloques de texto: descripción de la falla, "
        "diagnóstico y resolución. Si todavía no hay diagnóstico o resolución, se indica claramente en "
        "lugar de dejar el espacio vacío."
    )

    doc.h2_imagen("Atender y cerrar una incidencia", "24-editar-incidencia.png", "Actualización de estado, diagnóstico y resolución de una incidencia.")
    doc.p(
        "El botón «Atender incidencia» abre el formulario de actualización. Permite cambiar el estado, "
        "capturar el diagnóstico técnico y escribir la resolución o notas. Al pasar a Resuelta o "
        "Cerrada, SATE registra la fecha de cierre; si el caso vuelve a un estado abierto, la fecha se "
        "limpia."
    )
    doc.tabla(
        ["Estado", "Uso recomendado"],
        [
            ("Nueva", "El caso se registró y aún no se asigna o revisa."),
            ("Asignada", "Ya tiene responsable, pero el trabajo no ha comenzado."),
            ("En proceso", "El técnico está diagnosticando o reparando."),
            ("Resuelta", "La solución se aplicó y se documentó."),
            ("Cerrada", "El caso se confirmó con el usuario y se dio por terminado."),
        ],
        [32, 142],
        size=8.7,
        lh=4.5,
    )
    doc.nota(
        "Diagnóstico y resolución",
        "El diagnóstico explica la causa o los hallazgos; la resolución documenta qué se hizo. Ambos "
        "campos son opcionales, pero una buena práctica es no cerrar un caso sin ellos: son la memoria "
        "técnica que evita repetir el análisis en el futuro.",
    )

    doc.h2("Flujo recomendado")
    doc.numerada(
        [
            "El usuario reporta la incidencia con una descripción concreta y una prioridad justificada.",
            "Soporte revisa el caso y lo asigna al área o técnico correspondiente.",
            "El responsable cambia el estado a En proceso al comenzar la atención.",
            "Se registra el diagnóstico con la causa probable o confirmada.",
            "Se documenta la resolución y se cambia el estado a Resuelta.",
            "Se confirma con el usuario y se cierra el caso.",
            "Si el problema se repite, se reporta como problema recurrente según la política 7.",
        ]
    )

    doc.h2("Buenas prácticas")
    doc.vinetas(
        [
            "No uses «Media» por defecto: la prioridad debe reflejar el impacto real.",
            "Describe el equipo, la falla y el contexto; evita «no sirve» o «falla mucho».",
            "Actualiza el estado el mismo día en que cambia la situación.",
            "Cierra solo cuando la solución esté verificada con el usuario.",
            "Consulta el historial del activo antes de diagnosticar una falla recurrente.",
        ]
    )

    doc.h2("Indicadores de incidencias")
    doc.p(
        "Los filtros del listado y los datos de la ficha permiten dar seguimiento sin salir del módulo. "
        "La tabla resume las consultas más frecuentes."
    )
    doc.tabla(
        ["Pregunta", "Cómo responderla"],
        [
            ("¿Cuántos casos están abiertos?", "Filtra por Nueva, Asignada o En proceso."),
            ("¿Qué casos son críticos?", "Filtra por prioridad Crítica y revisa la alerta del panel."),
            ("¿Qué casos están sin asignar?", "Busca los que muestran «Sin asignar» en la columna Asignado a."),
            ("¿Cuánto tardó un caso?", "Compara la fecha de registro con la fecha de cierre en la ficha."),
            ("¿Qué fallas se repiten?", "Revisa el historial del equipo y las incidencias con la misma descripción."),
        ],
        [62, 112],
        size=8.6,
        lh=4.5,
    )

    doc.h2("Caso práctico: incidencia crítica")
    doc.p(
        "Un área completa reporta que no puede acceder al sistema. La prioridad es Crítica y el caso "
        "debe atenderse con un orden claro."
    )
    doc.numerada(
        [
            "Confirma el alcance: cuántos usuarios y qué servicios están afectados.",
            "Verifica que la incidencia esté en estado Asignada y con un responsable concreto.",
            "Cambia a En proceso al iniciar el diagnóstico y registra la hora en las notas.",
            "Documenta el diagnóstico con la causa probable y las pruebas realizadas.",
            "Aplica la solución, verifica con el usuario y escribe la resolución.",
            "Cambia a Resuelta y, tras la confirmación, a Cerrada.",
            "Si el caso se repite, abre un análisis de problema recurrente según la política 7.",
        ]
    )

    # ==================================================================
    # 10. USUARIOS
    # ==================================================================
    doc.h1("Usuarios y roles")
    doc.p(
        "Este módulo, visible solo para el Administrador General, permite crear cuentas, asignar rol y "
        "departamento, activar o desactivar usuarios y restablecer contraseñas. Es la puerta de entrada "
        "a SATE y, por tanto, una de las áreas más sensibles del sistema."
    )

    doc.h2_imagen("Listado de usuarios", "09-usuarios.png", "Listado de usuarios con rol, estado y último acceso.")
    doc.p(
        "La vista /app/usuarios muestra usuario, departamento, rol de acceso, estado y último acceso. "
        "Desde aquí se abre la edición de cada cuenta y se activa o desactiva con confirmación. El "
        "listado incluye una tarjeta final con las reglas de administración."
    )

    doc.h2_imagen("Crear un usuario", "11-nuevo-usuario.png", "Formulario de alta de una cuenta con rol y departamento.")
    doc.p(
        "El botón «+ Nuevo Usuario» abre el formulario. Todos los campos son obligatorios. El correo "
        "debe contener @ y ser único; la contraseña temporal debe tener al menos 8 caracteres. Al "
        "guardar, la cuenta queda activa y marcada para cambiar la contraseña en el primer acceso."
    )
    doc.tabla(
        ["Campo", "Obligatorio", "Descripción"],
        [
            ("Nombre completo", "Sí", "Nombre que se mostrará en la interfaz y en el historial."),
            ("Correo electrónico", "Sí", "Será el usuario de acceso. Debe ser único."),
            ("Contraseña temporal", "Sí", "Mínimo 8 caracteres. Se cambia en el primer acceso."),
            ("Departamento", "Sí", "Área a la que pertenece la cuenta."),
            ("Rol en SATE", "Sí", "Determina módulos y permisos."),
        ],
        [48, 26, 100],
        size=8.5,
        lh=4.4,
    )

    doc.h2("Editar un usuario")
    doc.p(
        "La edición permite cambiar nombre, correo, departamento y rol. No cambia la contraseña: para "
        "eso existe la sección «Restablecer contraseña». Un cambio de rol no altera la sesión abierta; "
        "el usuario debe volver a iniciar sesión para recibir el nuevo menú y los nuevos permisos."
    )

    doc.h2("Activar y desactivar cuentas")
    doc.p(
        "El botón «Desactivar» cambia el estado de la cuenta y pide confirmación. La sesión abierta se "
        "invalida en la siguiente petición: el usuario es enviado al login con el aviso «Tu cuenta ya no "
        "está activa». El botón «Activar» revierte la situación. No se puede desactivar la propia cuenta "
        "ni dejar el sistema sin un Administrador General activo."
    )

    doc.h2("Restablecer contraseña")
    doc.p(
        "En la edición de la cuenta, la sección «Restablecer contraseña» solicita una nueva contraseña "
        "temporal de al menos 8 caracteres. Al guardarla, la cuenta se marca para cambio obligatorio y "
        "el usuario deberá actualizarla al entrar. No se puede restablecer la propia contraseña desde "
        "aquí: para eso se usa Mi Perfil."
    )

    doc.h2("Reglas de administración")
    doc.vinetas(
        [
            "Solo el Administrador General accede al módulo.",
            "No se puede desactivar la propia cuenta.",
            "No se puede desactivar ni cambiar el rol al último Administrador General activo.",
            "Las cuentas nuevas y las contraseñas restablecidas son temporales.",
            "El correo debe ser único y contener @.",
            "El rol Usuario Solicitante limita el alcance a su departamento y a sus propias incidencias.",
        ]
    )

    doc.h2("Buenas prácticas de administración")
    doc.p(
        "La gestión de cuentas no termina al crear un usuario. Estas rutinas mantienen el acceso "
        "controlado y facilitan una auditoría ordenada."
    )
    doc.vinetas(
        [
            "Crea las cuentas con el rol mínimo necesario y amplía permisos solo si la función lo exige.",
            "Revisa cada mes la lista de usuarios activos y el último acceso; desactiva las cuentas sin uso.",
            "Al cambiar el rol de una persona, avísale que debe cerrar sesión y volver a entrar.",
            "Restablece la contraseña por un canal seguro y no envíes la clave temporal junto con el correo de la cuenta.",
            "Mantén al menos dos Administradores Generales activos para no depender de una sola persona.",
            "Documenta quién solicitó cada alta, baja o cambio de rol para responder ante una auditoría.",
        ]
    )

    doc.h2("Caso práctico: alta de un técnico")
    doc.p(
        "Ingresa una persona nueva al área de Soporte y necesita acceso a SATE desde el primer día. "
        "Este orden evita permisos de más y retrabajos."
    )
    doc.numerada(
        [
            "Confirma con la jefatura el rol y el departamento que corresponden, sin conceder permisos de más.",
            "Crea la cuenta con el correo institucional y un departamento válido.",
            "Entrega la contraseña temporal por un canal seguro y pide el cambio en el primer acceso.",
            "Verifica con la persona que puede iniciar sesión y que ve los módulos esperados.",
            "Revisa a la semana que el último acceso corresponde y que no hay cuentas duplicadas.",
            "Cuando la persona cambie de área, actualiza departamento y rol, y avisa que debe reiniciar sesión.",
        ]
    )

    # ==================================================================
    # 11. PERFIL
    # ==================================================================
    doc.h1("Mi perfil")
    doc.p(
        "Mi Perfil está disponible para todos los usuarios con sesión. Reúne los datos de la cuenta, la "
        "personalización visual y el cambio de contraseña. Es también la pantalla a la que SATE redirige "
        "cuando la contraseña es temporal."
    )

    doc.h2("Datos de la cuenta")
    doc.p(
        "La ficha muestra nombre, correo, departamento y rol. Estos datos no se editan aquí: el nombre, "
        "el correo, el departamento y el rol los administra el Administrador General. Si algo es "
        "incorrecto, solicita la corrección."
    )

    doc.h2("Tema visual")
    doc.p(
        "El selector «Tema Visual de SATE» permite elegir entre Azul Neón (predeterminado), Esmeralda "
        "(verde), Fuego (naranja) y Amatista (morado). El cambio se guarda en la cuenta y se aplica al "
        "guardar el formulario. También puede cambiarse desde el selector de la cabecera."
    )
    doc.tabla(
        ["Tema", "Color dominante", "Uso sugerido"],
        [
            ("Azul Neón", "Azul eléctrico", "Opción predeterminada; buena legibilidad en pantallas y proyecciones."),
            ("Esmeralda", "Verde", "Para quien prefiere un contraste más suave y tonos fríos."),
            ("Fuego", "Naranja", "Para distinguir visualmente un entorno de pruebas o demostración."),
            ("Amatista", "Morado", "Alternativa de alto contraste para uso prolongado."),
        ],
        [36, 40, 98],
        size=8.6,
        lh=4.5,
    )

    doc.h2("Cambiar contraseña")
    doc.p(
        "Para cambiar la contraseña se escribe la actual y la nueva. La nueva debe tener al menos 8 "
        "caracteres. Si la cuenta tiene contraseña temporal, el cambio es obligatorio y desbloquea el "
        "resto de SATE. Si se deja la nueva contraseña en blanco, solo se actualiza el tema."
    )
    doc.nota(
        "Recomendación",
        "Usa una contraseña distinta a la de otros servicios, con mayúsculas, minúsculas, números y "
        "símbolos. No la compartas por correo ni por mensajería.",
        color=ROJO,
        fondo=(254, 242, 242),
    )

    doc.h2("Buenas prácticas de la cuenta")
    doc.vinetas(
        [
            "Cambia la contraseña temporal en el primer acceso y no la reutilices en otros servicios.",
            "Cierra sesión al terminar, sobre todo en equipos compartidos o de laboratorio.",
            "Verifica que tu departamento y tu rol sean correctos; si no, solicita la corrección.",
            "No compartas tu cuenta para que otra persona reporte una incidencia: cada quien debe usar la suya.",
            "Si sospechas un acceso ajeno, cambia la contraseña y avisa al Administrador General.",
        ]
    )

    # ==================================================================
    # 12. DEMO
    # ==================================================================
    doc.h1("Datos de demostración")
    doc.p(
        "Para presentar el sistema con información realista existe un conjunto de datos demo. Se cargan "
        "con un script y se eliminan sin tocar la información real. Son útiles para probar roles, "
        "alertas, reportes y capturas."
    )

    doc.h2("Cargar los datos")
    doc.p(
        "Desde la carpeta del proyecto, con el entorno virtual activo y la base configurada, ejecuta:"
    )
    doc.nota(
        "Comando",
        "python scripts/seed_demo.py",
        color=OSCURO,
        fondo=(241, 245, 249),
    )
    doc.p(
        "El script es idempotente: puede ejecutarse varias veces y refresca solo sus propios registros. "
        "Crea siete usuarios, doce activos, seis mantenimientos, cinco incidencias y cinco movimientos "
        "de historial."
    )

    doc.h2("Cuentas demo")
    doc.tabla(
        ["Correo", "Rol", "Nombre"],
        [
            ("admin@demo.techtrack.com", "Administrador General", "Administrador Demo"),
            ("direccion@demo.techtrack.com", "Dirección General", "Laura Méndez"),
            ("activos@demo.techtrack.com", "Administrador de Activos", "Carlos Ramírez"),
            ("redes@demo.techtrack.com", "Administrador de Redes", "Ana Torres"),
            ("desarrollo@demo.techtrack.com", "Desarrollador", "Luis Herrera"),
            ("soporte@demo.techtrack.com", "Técnico de Soporte", "María López"),
            ("solicitante@demo.techtrack.com", "Usuario Solicitante", "Jorge Salinas"),
        ],
        [62, 54, 58],
        size=8.4,
        lh=4.5,
    )
    doc.p("La contraseña de todas las cuentas demo es Demo123!")
    doc.nota(
        "No usar en producción",
        "Las cuentas demo tienen contraseñas conocidas y no deben quedar activas en un entorno real. "
        "Cárgalas solo en desarrollo, pruebas o presentación.",
        color=ROJO,
        fondo=(254, 242, 242),
    )

    doc.h2("Qué incluyen los datos")
    doc.vinetas(
        [
            "Doce activos con identificadores DEMO-001 a DEMO-012 en los cuatro departamentos.",
            "Mantenimientos vencidos, próximos y finalizados para probar alertas y calendario.",
            "Incidencias en estados Nueva, Asignada, En proceso y Resuelta, con prioridades variadas.",
            "Movimientos de alta, asignación, mantenimiento y baja para probar el historial.",
        ]
    )

    doc.h2("Eliminar los datos demo")
    doc.p(
        "Para retirar solo los registros de demostración, ejecuta el script con la opción de limpieza. "
        "Se identifican por el dominio @demo.techtrack.com y el prefijo DEMO-, por lo que no afectan a "
        "los datos reales."
    )
    doc.nota(
        "Comando",
        "python scripts/seed_demo.py --limpiar",
        color=OSCURO,
        fondo=(241, 245, 249),
    )

    doc.h2("Verificación después de cargar")
    doc.p(
        "Después de ejecutar el script conviene comprobar que los datos quedaron completos y que las "
        "cuentas pueden iniciar sesión. Esta lista sirve como prueba rápida."
    )
    doc.vinetas(
        [
            "Entra con admin@demo.techtrack.com y confirma que el panel muestra 12 activos y 7 usuarios.",
            "Abre el inventario y verifica que existen registros DEMO-001 a DEMO-012.",
            "Revisa que el panel muestre alertas de mantenimientos vencidos y próximos.",
            "Filtra incidencias por prioridad Crítica y confirma que hay al menos un caso.",
            "Entra con solicitante@demo.techtrack.com y comprueba que solo ve su departamento.",
            "Abre la ficha de un activo demo y revisa que el historial tenga movimientos.",
        ]
    )

    doc.h2("Caso práctico: presentación con datos demo")
    doc.p(
        "Para una demostración académica conviene recorrer el sistema en un orden que muestre el valor "
        "de la trazabilidad, no solo las pantallas."
    )
    doc.numerada(
        [
            "Inicia sesión como Administrador General y presenta el panel con las alertas.",
            "Abre el inventario y muestra los filtros y el identificador único de un equipo.",
            "Entra a la ficha de un activo y explica el QR, la etiqueta y el historial.",
            "Presenta un mantenimiento vencido y muestra cómo se cierra con observaciones.",
            "Abre una incidencia crítica y explica el diagnóstico y la resolución.",
            "Cierra la sesión y entra como Usuario Solicitante para mostrar el alcance restringido.",
            "Finaliza con la página de Cumplimiento del PIA como evidencia del proyecto.",
        ]
    )

    # ==================================================================
    # 13. PROBLEMAS
    # ==================================================================
    doc.h1("Preguntas frecuentes y solución de problemas")
    doc.p(
        "Esta sección reúne las situaciones más habituales. Antes de escalar un problema, revisa la "
        "tabla y confirma que la sesión, el rol y los filtros sean los esperados."
    )

    doc.h2("Problemas de acceso")
    doc.tabla(
        ["Síntoma", "Causa probable", "Solución"],
        [
            ("No puedo entrar y el mensaje dice correo o contraseña incorrectos.", "Datos mal escritos o contraseña cambiada.", "Revisa mayúsculas y espacios. Si persiste, pide un restablecimiento."),
            ("Mi cuenta aparece desactivada.", "El administrador la desactivó.", "Solicita la activación al Administrador General."),
            ("SATE me lleva siempre a Mi Perfil.", "Contraseña temporal pendiente.", "Cambia la contraseña en Mi Perfil."),
            ("Mi sesión se cerró sola.", "La cuenta se desactivó o eliminó.", "Contacta al administrador."),
            ("El navegador muestra un error 400.", "Token CSRF vencido o formulario viejo.", "Recarga la página y vuelve a enviar."),
        ],
        [52, 50, 72],
        size=8.2,
        lh=4.4,
    )

    doc.h2("Problemas de operación")
    doc.tabla(
        ["Síntoma", "Causa probable", "Solución"],
        [
            ("No veo un módulo en el menú.", "El rol no tiene permiso de ver.", "Solicita revisión del rol al administrador."),
            ("No veo activos de otro departamento.", "Alcance del Usuario Solicitante.", "Es el comportamiento esperado; pide apoyo a tu área."),
            ("No puedo crear o editar.", "El rol solo permite consulta.", "Solicita el permiso correspondiente."),
            ("No encuentro una incidencia ajena.", "El solicitante solo ve las propias.", "Pide el número de ticket al área responsable."),
            ("El activo sigue En Mantenimiento.", "Hay un mantenimiento abierto o vencido.", "Finaliza el mantenimiento o revisa su fecha."),
            ("El activo sigue Con Falla.", "Hay una incidencia abierta.", "Resuelve o cierra la incidencia."),
            ("No aparece un mantenimiento en próximos 7 días.", "Está fuera de la ventana o ya finalizó.", "Revisa la fecha programada y el estado."),
            ("No puedo desactivar a un administrador.", "Es el último Administrador General activo.", "Crea o activa otro administrador antes."),
        ],
        [56, 48, 70],
        size=8.2,
        lh=4.4,
    )

    doc.h2("Problemas de impresión y visualización")
    doc.tabla(
        ["Síntoma", "Causa probable", "Solución"],
        [
            ("El QR no abre en el teléfono.", "La URL apunta a 127.0.0.1 o localhost.", "Publica SATE con la IP de la red y regenera la etiqueta."),
            ("La etiqueta no mide 90 x 55 mm.", "La impresora escala el PDF.", "Imprime al 100 %, sin ajustar a la página."),
            ("El calendario o las gráficas no aparecen.", "No hay acceso a los CDN.", "Verifica la conexión o publica las librerías localmente."),
            ("La tabla no muestra todas las filas.", "Paginación de diez registros.", "Usa los filtros o avanza de página."),
            ("La interfaz se ve cortada en móvil.", "Zoom del navegador o resolución muy baja.", "Restablece el zoom y usa el menú desplegable."),
        ],
        [52, 50, 72],
        size=8.2,
        lh=4.4,
    )

    doc.h2("Errores del servidor")
    doc.p(
        "Si aparece un error 403, la cuenta no tiene permiso para esa ruta. Un 404 indica que el activo, "
        "mantenimiento, incidencia o usuario no existe. Un 500 es un fallo interno: anota la hora, la "
        "acción realizada y el mensaje, y repórtalo al equipo de Desarrollo. No reintentes una y otra vez "
        "sobre el mismo formulario sin recargar."
    )

    doc.h2("Cómo escalar un caso")
    doc.p(
        "Cuando el problema no se resuelve con las tablas anteriores, reúne la evidencia antes de "
        "contactar al soporte técnico. Un reporte completo ahorra varias rondas de preguntas."
    )
    doc.numerada(
        [
            "Anota el correo de la cuenta y el rol con el que estabas trabajando.",
            "Indica la ruta o el módulo donde ocurrió y la acción exacta que realizaste.",
            "Registra la hora aproximada y el texto del mensaje de error.",
            "Adjunta una captura de pantalla si el problema es visual.",
            "Si el caso afecta a un activo, incluye su identificador; si afecta a una incidencia, su número de ticket.",
            "Envía la información al Administrador General o al área de Desarrollo según el canal definido.",
        ]
    )

    # ==================================================================
    # 14. GLOSARIO
    # ==================================================================
    doc.h1("Glosario")
    doc.p("Los términos siguientes se usan a lo largo del manual y de la interfaz.")
    doc.tabla(
        ["Término", "Definición"],
        [
            ("Activo", "Equipo tecnológico registrado en SATE con identificador único."),
            ("Alcance", "Conjunto de datos que un rol puede consultar. Puede ser global o por departamento."),
            ("API", "Interfaz de programación que permite integrar SATE con otros sistemas."),
            ("Auditoría", "Registro de acciones administrativas relevantes del sistema."),
            ("Baja", "Estado que retira un activo del inventario activo sin borrar su historial."),
            ("Base de datos", "Repositorio donde se guardan usuarios, activos, mantenimientos e incidencias."),
            ("Campo", "Cada dato que se captura en un formulario."),
            ("CSRF", "Protección que impide enviar formularios desde otro sitio."),
            ("Dashboard", "Panel visual con indicadores; en SATE, el panel principal."),
            ("Diagnóstico", "Causa o hallazgos técnicos de una incidencia."),
            ("Endpoint", "Dirección o ruta del servidor que responde a una petición."),
            ("Flask", "Marco de desarrollo web en Python con el que está construido SATE."),
            ("Formulario", "Pantalla con campos que se envían al servidor para crear o actualizar datos."),
            ("Historial", "Línea de tiempo de los movimientos de un activo."),
            ("Identificador", "Código único del activo, formado por prefijo y consecutivo."),
            ("Incidencia", "Reporte de una falla o solicitud sobre un equipo."),
            ("Mantenimiento", "Servicio preventivo o correctivo programado sobre un activo."),
            ("Matriz R/P", "Tabla que indica qué área lidera (R) y cuál participa (P) en una política."),
            ("MySQL", "Sistema gestor de base de datos relacional usado por SATE."),
            ("Permiso", "Autorización para ver, crear, editar o administrar un módulo."),
            ("PIA", "Proyecto Integrador de Aplicaciones que documenta la empresa y SATE."),
            ("QR", "Código bidimensional que abre la ficha del activo."),
            ("RBAC", "Control de acceso basado en roles."),
            ("Resolución", "Documentación de la solución aplicada a una incidencia."),
            ("Rol", "Conjunto de permisos asignado a una cuenta."),
            ("SATE", "Sistema de Administración y Trazabilidad de Equipos."),
            ("Script", "Programa auxiliar que ejecuta una tarea, como cargar datos demo."),
            ("Sesión", "Periodo durante el cual el usuario permanece autenticado."),
            ("SVG", "Formato de imagen vectorial usado para el código QR."),
            ("Ticket", "Número que identifica una incidencia."),
            ("Usuario Solicitante", "Rol con alcance limitado a su departamento y a sus propias incidencias."),
            ("Validación", "Comprobación de que los datos cumplen las reglas antes de guardarse."),
        ],
        [42, 132],
        size=8.0,
        lh=3.9,
        padding=2.0,
    )

    # ==================================================================
    # 15. ANEXOS
    # ==================================================================
    doc.h1("Anexos")
    doc.p(
        "Los anexos concentran información de consulta rápida: rutas, checklist de puesta en marcha y "
        "recomendaciones de seguridad. No sustituyen a los capítulos anteriores, pero facilitan el "
        "trabajo diario."
    )

    doc.h2("Rutas principales")
    doc.tabla(
        ["Ruta", "Método", "Función"],
        [
            ("/", "GET", "Inicio del sitio público."),
            ("/empresa", "GET", "Ficha institucional y organigrama."),
            ("/departamentos", "GET", "Vista general de las cuatro áreas."),
            ("/departamentos/<slug>", "GET", "Ficha de SIT, Redes, Desarrollo o Soporte."),
            ("/politicas", "GET", "Catálogo y matriz de políticas."),
            ("/politicas/<slug>", "GET", "Detalle de una política."),
            ("/trabaja-con-nosotros", "GET", "Perfiles de puesto."),
            ("/trabaja-con-nosotros/<slug>", "GET/POST", "Detalle y postulación."),
            ("/sate", "GET", "Página del producto."),
            ("/contacto", "GET/POST", "Formulario de contacto."),
            ("/cumplimiento-pia", "GET", "Matriz de evidencias del PIA."),
            ("/privacidad", "GET", "Aviso de privacidad."),
            ("/login", "GET/POST", "Inicio de sesión."),
            ("/logout", "POST", "Cierre de sesión."),
            ("/app/dashboard", "GET", "Panel principal."),
            ("/app/activos", "GET", "Inventario y filtros."),
            ("/app/activos/nuevo", "GET/POST", "Alta de activo."),
            ("/app/activos/<id>", "GET", "Ficha del activo."),
            ("/app/activos/<id>/editar", "GET/POST", "Edición del activo."),
            ("/app/activos/<id>/resguardo", "GET", "Acta de resguardo en PDF."),
            ("/app/activos/<id>/qr.svg", "GET", "Código QR en SVG."),
            ("/app/activos/<id>/etiqueta", "GET", "Etiqueta imprimible."),
            ("/app/activos/reporte", "GET", "Reporte de inventario en PDF."),
            ("/app/mantenimientos", "GET", "Listado y calendario."),
            ("/app/mantenimientos/nuevo", "GET/POST", "Programar mantenimiento."),
            ("/app/mantenimientos/<id>", "GET", "Ficha del mantenimiento."),
            ("/app/mantenimientos/<id>/editar", "GET/POST", "Editar o cerrar."),
            ("/app/mantenimientos/<id>/orden", "GET", "Orden de trabajo en PDF."),
            ("/app/incidencias", "GET", "Listado de incidencias."),
            ("/app/incidencias/nueva", "GET/POST", "Reportar incidencia."),
            ("/app/incidencias/<id>", "GET", "Ficha de la incidencia."),
            ("/app/incidencias/<id>/editar", "GET/POST", "Atender o cerrar."),
            ("/app/usuarios", "GET", "Listado de usuarios."),
            ("/app/usuarios/nuevo", "GET/POST", "Crear usuario."),
            ("/app/usuarios/<id>/editar", "GET/POST", "Editar usuario."),
            ("/app/usuarios/<id>/estado", "POST", "Activar o desactivar."),
            ("/app/usuarios/<id>/password", "POST", "Restablecer contraseña."),
            ("/app/perfil", "GET/POST", "Perfil, tema y contraseña."),
        ],
        [64, 22, 88],
        size=7.8,
        lh=4.0,
    )

    doc.h2("Checklist de puesta en marcha")
    doc.p("Antes de usar SATE con información real, verifica los siguientes puntos.")
    doc.vinetas(
        [
            "La base de datos está creada y las migraciones aplicadas.",
            "El archivo .env tiene una SECRET_KEY propia y credenciales válidas.",
            "El Administrador General cambió la contraseña inicial.",
            "Los departamentos y roles están cargados.",
            "Los activos iniciales tienen identificador, responsable y departamento.",
            "Los mantenimientos vencidos están programados o cerrados.",
            "Las cuentas demo se eliminaron del entorno de producción.",
            "Los respaldos de la base de datos están configurados.",
            "El sitio se publica con HTTPS y SESSION_COOKIE_SECURE=1.",
        ]
    )

    doc.h2("Recomendaciones de seguridad")
    doc.vinetas(
        [
            "Aplica el principio de mínimo privilegio: asigna solo el rol necesario.",
            "Desactiva de inmediato las cuentas de personas que dejan la organización.",
            "No compartas contraseñas ni las envíes por canales inseguros.",
            "Revisa periódicamente la lista de usuarios activos y el último acceso.",
            "Conserva los respaldos de la base y prueba la restauración.",
            "Reporta cualquier acceso extraño o cambio no reconocido en el historial.",
        ]
    )

    doc.h2("Soporte")
    doc.p(
        "Para dudas funcionales, consulta primero este manual y la página de Cumplimiento del PIA. Para "
        "problemas técnicos, contacta al área de Desarrollo o al Administrador General de SATE e incluye "
        "el correo de la cuenta, la ruta donde ocurrió el problema, la hora aproximada y el mensaje de "
        "error. Esa información reduce el tiempo de diagnóstico."
    )
    doc.p(
        "TechTrack Solutions · SATE · Manual de Usuario · Versión 1.0 · Octubre de 2026",
        size=9,
        color=GRIS_CLARO,
        align="C",
    )


def main():
    if not os.path.isdir(CAPTURAS):
        print(f"No existe la carpeta de capturas: {CAPTURAS}", file=sys.stderr)
        return 1

    # Primera pasada: cuerpo con numeracion relativa y entradas del indice.
    borrador = Manual(registrar=True)
    borrador.ocultar_cabecera = False
    cuerpo(borrador)
    entradas = list(borrador.toc)
    paginas_cuerpo = borrador.page_no()

    # Medir cuantas paginas ocupa el indice con el mismo formato.
    medidor = Manual(registrar=False)
    medidor.add_page()
    paginas_indice = medidor.escribir_indice(entradas, 0)

    offset = 2 + paginas_indice  # portada + ficha + indice

    # Segunda pasada: documento final.
    doc = Manual(registrar=False)
    doc.portada()
    doc.ficha()
    doc.add_page()
    usado = doc.escribir_indice(entradas, offset)
    if usado != paginas_indice:
        print(
            f"Aviso: el indice ocupa {usado} paginas y se midieron {paginas_indice}.",
            file=sys.stderr,
        )
    doc.ocultar_cabecera = False
    cuerpo(doc)
    doc.alias_nb_pages()

    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    pdf = doc.output(dest="S")
    if isinstance(pdf, str):
        pdf = pdf.encode("latin-1")
    with open(SALIDA, "wb") as archivo:
        archivo.write(pdf)

    print(f"Manual generado: {SALIDA}")
    print(f"Paginas: {doc.page_no()} (cuerpo de borrador: {paginas_cuerpo})")
    print(f"Indice: {paginas_indice} pagina(s), offset {offset}")
    print(f"Figuras: {doc.figura}; tablas: {doc.tabla_num}; entradas de indice: {len(entradas)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
