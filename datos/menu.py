"""Arquitectura de la información de Rédito: una sola fuente para el cajón (móvil y
escritorio), los megamenús (≥ 80em), la fila de secciones y el pie. montar.py la usa."""

SECCIONES = [
    ("mercados", "Mercados", ["Bolsa", "Renta fija", "Divisas", "Materias primas", "Cotizaciones", "Calendario"],
     ("Las letras a doce meses bajan al 2,15 %, el tipo más bajo desde enero", "bolsa")),
    ("economia", "Economía", ["Macroeconomía", "Fiscalidad", "Empleo", "Vivienda", "Unión Europea", "Internacional"],
     ("El Gobierno prorroga los presupuestos por tercera vez", "vivienda")),
    ("empresas", "Empresas", ["Banca", "Energía", "Industria", "Telecomunicaciones", "Distribución", "Pymes"],
     ("La banca encadena su mejor semana del año en bolsa", "industria")),
    ("finanzas", "Finanzas personales", ["Ahorro", "Inversión", "Hipotecas", "Pensiones", "Impuestos", "Calculadoras"],
     ("Qué hacer con los depósitos si el BCE vuelve a bajar los tipos", "tesoro")),
    ("tecnologia", "Tecnología", ["Startups", "Inteligencia artificial", "Ciberseguridad", "Fintech"],
     ("Los centros de datos disparan la demanda eléctrica del norte", "tecnologia")),
    ("opinion", "Opinión", ["Editoriales", "Tribunas", "Columnistas", "Cartas al director"],
     ("El presupuesto no puede esperar", None)),
]
SERVICIOS = ["Boletines", "Pódcasts", "Hemeroteca", "Edición impresa", "Aplicación"]
CORPORATIVO = ["Quiénes somos", "Contacto", "Trabaja con nosotros", "Publicidad"]
LEGAL = ["Aviso legal", "Privacidad", "Cookies", "Accesibilidad"]
TEMAS = ["Subastas del Tesoro", "BCE", "Presupuestos 2027", "Vivienda", "Aranceles", "Resultados del tercer trimestre"]


def slug(t):
    import unicodedata
    s = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return "-".join("".join(c if c.isalnum() else " " for c in s).split())


def cajon():
    """Cajón: acordeón exclusivo (details con el mismo name) por sección + servicios."""
    out = ['<nav class="org-site-nav-drawer haber-cajon" id="menu-cajon" aria-label="Todas las secciones">',
           '<form class="haber-busca" role="search" action="#"><label class="atom-label" for="busca-cajon">Buscar en Rédito</label>'
           '<input class="atom-input" id="busca-cajon" type="search" name="q" autocomplete="off" placeholder="Empresas, índices, autores…"></form>',
           '<a class="org-site-nav-drawer__link haber-cajon__portada" href="#principal" aria-current="page">Portada</a>']
    for i, (id_, nombre, subs, _) in enumerate(SECCIONES):
        enlaces = "".join(f'<li><a class="haber-cajon__sub" href="#{id_}-{slug(s)}">{s}</a></li>' for s in subs)
        out.append(f'<details class="mol-disclosure haber-cajon__seccion" name="cajon">'
                   f'<summary class="mol-disclosure__summary"><span class="haber-cajon__titulo">{nombre}</span></summary>'
                   f'<div class="mol-disclosure__content"><ul class="haber-cajon__lista">'
                   f'<li><a class="haber-cajon__sub haber-cajon__sub--todo" href="#{id_}">Toda la sección</a></li>{enlaces}</ul></div></details>')
    out.append('<div class="haber-cajon__extra"><p class="haber-rotulo">Servicios</p><ul class="haber-cajon__lista haber-cajon__lista--dos">'
               + "".join(f'<li><a class="haber-cajon__sub" href="#{slug(s)}">{s}</a></li>' for s in SERVICIOS) + '</ul></div>')
    out.append('<div class="haber-cajon__extra haber-cajon__cuenta"><a class="atom-btn atom-btn--primary atom-btn--filled" href="#suscripcion">Suscríbete</a>'
               '<a class="atom-btn atom-btn--secondary" href="#entrar">Iniciar sesión</a></div>')
    out.append('</nav>')
    return "".join(out)


def nav_escritorio():
    """Botones de la barra (≥ 80em): cada uno abre su megamenú (Popover API, nativo)."""
    return "".join(f'<button class="haber-nav__boton" type="button" popovertarget="mega-{id_}" '
                   f'aria-controls="mega-{id_}"><span class="haber-optico">{nombre}</span></button>' for id_, nombre, _, _ in SECCIONES)


def megamenus(img):
    out = []
    for id_, nombre, subs, (dest, foto) in SECCIONES:
        cols = "".join(f'<li><a class="haber-mega__enlace" href="#{id_}-{slug(s)}">{s}</a></li>' for s in subs)
        media = (f'<img class="haber-mega__img" {img(foto, "(min-width: 80em) 20rem, 1px")} alt="" width="480" height="320" loading="lazy" decoding="async">'
                 if foto else '<span class="atom-avatar atom-avatar--lg" role="img" aria-label="Ernesto Ibarra">EI</span>')
        out.append(f'<div class="haber-mega" id="mega-{id_}" popover aria-label="{nombre}">'
                   f'<div class="layout-grid haber-mega__rejilla">'
                   f'<div class="layout-grid__col-xs-12 layout-grid__col-lg-3 haber-mega__cabeza"><p class="haber-rotulo">{nombre}</p>'
                   f'<a class="haber-mega__todo" href="#{id_}">Ver toda la sección</a></div>'
                   f'<ul class="layout-grid__col-xs-12 layout-grid__col-lg-5 haber-mega__lista">{cols}</ul>'
                   f'<a class="layout-grid__col-xs-12 layout-grid__col-lg-4 haber-mega__destacado" href="#{id_}">{media}'
                   f'<span class="haber-mega__titular">{dest}</span></a>'
                   f'</div></div>')
    return "".join(out)


def secciones_fila():
    return ('<li><a class="haber-secciones__enlace" href="#principal" aria-current="page">Portada</a></li>'
            + "".join(f'<li><a class="haber-secciones__enlace" href="#{id_}">{nombre}</a></li>' for id_, nombre, _, _ in SECCIONES))


def temas():
    return "".join(f'<li><a class="haber-temas__enlace" href="#tema-{slug(t)}">{t}</a></li>' for t in TEMAS)


def pie():
    col = lambda titulo, items, pref="": (f'<div class="layout-grid__col-xs-6 layout-grid__col-md-3 haber-pie__col"><p class="haber-rotulo">{titulo}</p>'
                                          f'<ul class="haber-pie__lista">' + "".join(f'<li><a class="haber-pie__enlace" href="#{pref}{slug(i)}">{i}</a></li>' for i in items) + '</ul></div>')
    return (col("Secciones", [n for _, n, _, _ in SECCIONES]) + col("Servicios", SERVICIOS)
            + col("Rédito", CORPORATIVO) + col("Legal", LEGAL))
