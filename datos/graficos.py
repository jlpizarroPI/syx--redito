"""Gráficos de Rédito en SVG, con datos ficticios y verosímiles (skill dataviz).

Reglas de la skill aplicadas: forma por la tarea (sparkline en las fichas, línea para la
tendencia, columnas con énfasis para comparar, barras divergentes para la polaridad);
una sola serie = sin leyenda (el título la nombra); trazo de 2 px que no escala; barras de
24 px como máximo con el extremo de dato redondeado 4 px y recto en la línea base; rejilla
de 1 px recesiva; etiquetas selectivas (extremo y final), nunca un número en cada punto;
texto con tokens de texto, nunca con el color de la serie; vista de tabla para todo.
Las medidas de texto y marcas se escriben en px de pantalla: haber-graficos.js fija
--k = unidades del viewBox por px reales, así el texto mide lo mismo a cualquier ancho.
  python3 datos/graficos.py   → datos/graficos.json (fragmentos que inserta montar.py)
"""
import json
import math
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RNG = np.random.default_rng(2026)
MESES = ["dic", "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov"]


def es(v, dec=1, miles=True):
    s = f"{abs(v):,.{dec}f}" if miles else f"{abs(v):.{dec}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if v < 0 else "") + s


def paseo(n, ini, fin, vol, seed):
    r = np.random.default_rng(seed)
    pasos = r.normal(0, vol, n)
    x = np.cumsum(pasos)
    x = x - np.linspace(0, x[-1], n)          # puente: empieza y acaba donde se pide
    return ini + (fin - ini) * np.linspace(0, 1, n) + x


# ── sparkline ────────────────────────────────────────────────────────────────────────
def sparkline(serie, sube):
    W, H, m = 120, 32, 4
    lo, hi = min(serie), max(serie)
    pts = [(m + i * (W - 2 * m) / (len(serie) - 1), H - m - (v - lo) / (hi - lo or 1) * (H - 2 * m)) for i, v in enumerate(serie)]
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    x, y = pts[-1]
    return (f'<svg class="haber-ficha__linea" viewBox="0 0 {W} {H}" aria-hidden="true" focusable="false">'
            f'<polyline points="{d}" />'
            f'<circle class="haber-ficha__punto haber-ficha__punto--{"sube" if sube else "cae"}" cx="{x:.1f}" cy="{y:.1f}" r="4" /></svg>')


def semana(i):
    import datetime as dt
    d = dt.date(2025, 11, 17) + dt.timedelta(weeks=i)
    return f"semana del {d.day} {MESES[(d.month) % 12]}"


# ── línea con cruz de lectura ──────────────────────────────────────────────────────────
def linea(id_, titulo, serie, fmt_dec, unidad, ticks):
    W, H = 640, 300
    ml, mr, mt, mb = 0, 64, 20, 30
    n = len(serie)
    lo, hi = ticks[0], ticks[-1]
    X = lambda i: ml + i * (W - ml - mr) / (n - 1)
    Y = lambda v: mt + (hi - v) / (hi - lo) * (H - mt - mb)
    pts = [(X(i), Y(v)) for i, v in enumerate(serie)]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = d + f" L{pts[-1][0]:.1f},{Y(lo):.1f} L{pts[0][0]:.1f},{Y(lo):.1f} Z"
    g = []
    for t in ticks:
        g.append(f'<line class="haber-graf__rejilla" x1="{ml}" x2="{W - mr + 8}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" />'
                 f'<text class="haber-graf__eje" x="{W}" y="{Y(t):.1f}" dy="0.32em" text-anchor="end">{es(t, fmt_dec)}</text>')
    for k, mes in enumerate(MESES):
        i = round(k * (n - 1) / 11)
        if k % 2 == 0:
            g.append(f'<text class="haber-graf__eje" x="{X(i):.1f}" y="{H - 8}" text-anchor="middle">{mes}</text>')
    ix, iy = pts[-1]
    imin = int(np.argmin(serie)); imax = int(np.argmax(serie))
    ext = imin if abs(imin - n) > 6 else imax
    datos = json.dumps({"x": [round(p[0], 1) for p in pts], "y": [round(p[1], 1) for p in pts],
                        "v": [es(v, fmt_dec) + unidad for v in serie],
                        "f": [semana(i) for i in range(n)]}, ensure_ascii=False)
    svg = (f'<svg class="haber-graf haber-graf--linea" id="{id_}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="{titulo}. Último valor: {es(serie[-1], fmt_dec)}{unidad}." tabindex="0" data-haber-linea=\'{datos}\'>'
           + "".join(g) +
           f'<path class="haber-graf__area" d="{area}" /><path class="haber-graf__trazo" d="{d}" />'
           f'<circle class="haber-graf__marca haber-graf__marca--ext" cx="{pts[ext][0]:.1f}" cy="{pts[ext][1]:.1f}" />'
           f'<text class="haber-graf__nota" x="{pts[ext][0]:.1f}" y="{pts[ext][1]:.1f}" dy="{"1.4em" if ext == imin else "-0.8em"}" text-anchor="{"start" if ext < n * 0.15 else "end" if ext > n * 0.85 else "middle"}">{"mínimo" if ext == imin else "máximo"} {es(serie[ext], fmt_dec)}{unidad}</text>'
           f'<circle class="haber-graf__marca" cx="{ix:.1f}" cy="{iy:.1f}" />'
           f'<g class="haber-graf__cruz" aria-hidden="true"><line class="haber-graf__cruz-linea" y1="{mt}" y2="{H - mb}" />'
           f'<circle class="haber-graf__cruz-punto" /><g class="haber-graf__burbuja"><rect rx="4" /><text class="haber-graf__burbuja-valor" /><text class="haber-graf__burbuja-fecha" /></g></g>'
           '</svg>')
    filas = "".join(f'<tr><th class="atom-table__td" scope="row">{MESES[k]}</th><td class="atom-table__td haber-tabla__num">{es(serie[round(k * (n - 1) / 11)], fmt_dec)}{unidad}</td></tr>' for k in range(12))
    tabla = (f'<details class="mol-disclosure haber-graf__datos"><summary class="mol-disclosure__summary">Ver los datos</summary>'
             f'<div class="mol-disclosure__content atom-table__container"><table class="atom-table haber-tabla"><caption class="haber-tabla__pie">{titulo}: cierre de cada mes</caption>'
             f'<thead><tr><th class="atom-table__th" scope="col">Mes</th><th class="atom-table__th haber-tabla__num" scope="col">Valor</th></tr></thead><tbody>{filas}</tbody></table></div></details>')
    return svg, tabla


# ── columnas con énfasis ───────────────────────────────────────────────────────────────
def columnas(id_, titulo, etiquetas, valores, unidad):
    W, H, mb, mt = 320, 220, 30, 30
    n = len(valores)
    banda = W / n
    ancho = 24
    hi = max(valores) * 1.0
    out = []
    for i, (e, v) in enumerate(zip(etiquetas, valores)):
        cx = banda * (i + 0.5)
        h = v / hi * (H - mb - mt)
        x, y = cx - ancho / 2, H - mb - h
        r = 4
        path = (f"M{x:.1f},{H - mb} L{x:.1f},{y + r:.1f} Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f} "
                f"L{x + ancho - r:.1f},{y:.1f} Q{x + ancho:.1f},{y:.1f} {x + ancho:.1f},{y + r:.1f} L{x + ancho:.1f},{H - mb} Z")
        clase = "haber-graf__col haber-graf__col--enfasis" if i == n - 1 else "haber-graf__col"
        out.append(f'<g class="haber-graf__pieza" tabindex="0" role="listitem" aria-label="{e}: {es(v, 0)} {unidad}" data-valor="{es(v, 0)} {unidad}" data-nombre="{e}">'
                   f'<rect class="haber-graf__blanco" x="{cx - banda / 2 + 2:.1f}" y="{mt - 24}" width="{banda - 4:.1f}" height="{H - mt - mb + 24}" />'
                   f'<path class="{clase}" d="{path}" />'
                   f'<text class="haber-graf__valor" x="{cx:.1f}" y="{y - 8:.1f}" text-anchor="middle">{es(v, 0)}</text>'
                   f'<text class="haber-graf__eje" x="{cx:.1f}" y="{H - 8}" text-anchor="middle">{e}</text></g>')
    svg = (f'<svg class="haber-graf haber-graf--columnas" id="{id_}" viewBox="0 0 {W} {H}" role="list" aria-label="{titulo}">'
           f'<line class="haber-graf__base" x1="0" x2="{W}" y1="{H - mb + 0.5}" y2="{H - mb + 0.5}" />' + "".join(out) + "</svg>")
    return svg


# ── barras divergentes ─────────────────────────────────────────────────────────────────
def divergente(id_, titulo, filas):
    """Nombres en su columna; el cero se coloca para que la barra negativa más larga y su
    etiqueta quepan sin pisar los nombres."""
    W, fila_h, ancho = 420, 34, 20
    H = fila_h * len(filas) + 8
    nombres, etq = 136, 48              # ancho de la columna de nombres y de una etiqueta
    neg = max([-v for _, v in filas if v < 0] or [0]); pos = max([v for _, v in filas if v > 0] or [0])
    esc = (W - nombres - 2 * etq) / (neg + pos)
    x0 = nombres + etq + neg * esc
    out = [f'<line class="haber-graf__base" x1="{x0 + 0.5:.1f}" x2="{x0 + 0.5:.1f}" y1="0" y2="{H}" />']
    for i, (nombre, v) in enumerate(filas):
        y = 4 + i * fila_h + (fila_h - ancho) / 2
        L = abs(v) * esc
        r = 4
        if v >= 0:
            p = (f"M{x0:.1f},{y:.1f} L{x0 + L - r:.1f},{y:.1f} Q{x0 + L:.1f},{y:.1f} {x0 + L:.1f},{y + r:.1f} "
                 f"L{x0 + L:.1f},{y + ancho - r:.1f} Q{x0 + L:.1f},{y + ancho:.1f} {x0 + L - r:.1f},{y + ancho:.1f} L{x0:.1f},{y + ancho:.1f} Z")
            tx, anc = x0 + L + 6, "start"
        else:
            p = (f"M{x0:.1f},{y:.1f} L{x0 - L + r:.1f},{y:.1f} Q{x0 - L:.1f},{y:.1f} {x0 - L:.1f},{y + r:.1f} "
                 f"L{x0 - L:.1f},{y + ancho - r:.1f} Q{x0 - L:.1f},{y + ancho:.1f} {x0 - L + r:.1f},{y + ancho:.1f} L{x0:.1f},{y + ancho:.1f} Z")
            tx, anc = x0 - L - 6, "end"
        txt = f"{'+' if v > 0 else ''}{es(v, 1)} %"
        out.append(f'<g class="haber-graf__pieza" tabindex="0" role="listitem" aria-label="{nombre}: {txt}">'
                   f'<rect class="haber-graf__blanco" x="0" y="{4 + i * fila_h:.1f}" width="{W}" height="{fila_h}" />'
                   f'<text class="haber-graf__nombre" x="0" y="{y + ancho / 2:.1f}" dy="0.32em">{nombre}</text>'
                   f'<path class="haber-graf__barra haber-graf__barra--{"sube" if v >= 0 else "cae"}" d="{p}" />'
                   f'<text class="haber-graf__valor" x="{tx:.1f}" y="{y + ancho / 2:.1f}" dy="0.32em" text-anchor="{anc}">{txt}</text></g>')
    return (f'<svg class="haber-graf haber-graf--divergente" id="{id_}" viewBox="0 0 {W} {H}" role="list" aria-label="{titulo}">'
            + "".join(out) + "</svg>")


def main():
    g = {}
    fichas = [("Ibex 35", paseo(20, 11702, 11842.6, 18, 1), "11.842,6", "+1,2 %", True),
              ("Bancos", paseo(20, 1067, 1094.3, 4, 2), "1.094,3", "+2,5 %", True),
              ("Euro/dólar", paseo(20, 1.0875, 1.0842, 0.0012, 3), "1,0842", "−0,3 %", False),
              ("Brent (dólares)", paseo(20, 75.0, 74.20, 0.25, 4), "74,20", "−1,1 %", False),
              ("Oro (dólares)", paseo(20, 2400, 2412, 4, 5), "2.412", "+0,5 %", True),
              ("Bono a 10 años", paseo(20, 3.12, 3.08, 0.006, 6), "3,08 %", "−0,04", False)]
    g["fichas"] = [dict(nombre=n, valor=v, delta=dl, sube=s, svg=sparkline(list(serie), s)) for n, serie, v, dl, s in fichas]
    bono = paseo(52, 3.46, 3.08, 0.035, 11)
    ibex = paseo(52, 10380, 11842.6, 120, 12)
    eurusd = paseo(52, 1.081, 1.0842, 0.007, 13)
    g["bono"] = linea("graf-bono", "Rentabilidad del bono español a 10 años, último año", list(bono), 2, " %", [3.0, 3.2, 3.4, 3.6])
    g["ibex"] = linea("graf-ibex", "Ibex 35, último año", list(ibex), 0, "", [10000, 10750, 11500, 12250])
    g["eurusd"] = linea("graf-eurusd", "Euro/dólar, último año", list(eurusd), 3, "", [1.05, 1.07, 1.09, 1.11])
    g["subastas"] = columnas("graf-subastas", "Demanda en las cuatro subastas de letras de noviembre, en millones de euros",
                             ["1.ª", "2.ª", "3.ª", "4.ª"], [6240, 8310, 9870, 10500], "millones")
    sectores = [("Bancos", 3.4), ("Seguros", 1.8), ("Telecomunicaciones", 0.9), ("Construcción", 0.4),
                ("Consumo", -0.6), ("Inmobiliario", -1.2), ("Energía", -2.1), ("Tecnología", -2.8)]
    g["sectores"] = divergente("graf-sectores", "Variación semanal por sector del Ibex 35, en porcentaje", sectores)
    g["sectores_tabla"] = ('<details class="mol-disclosure haber-graf__datos"><summary class="mol-disclosure__summary">Ver los datos</summary>'
                           '<div class="mol-disclosure__content atom-table__container"><table class="atom-table haber-tabla"><caption class="haber-tabla__pie">Variación semanal por sector</caption>'
                           '<thead><tr><th class="atom-table__th" scope="col">Sector</th><th class="atom-table__th haber-tabla__num" scope="col">Variación</th></tr></thead><tbody>'
                           + "".join(f'<tr><th class="atom-table__td" scope="row">{n}</th><td class="atom-table__td haber-tabla__num">{"+" if v > 0 else ""}{es(v, 1)} %</td></tr>' for n, v in sectores)
                           + '</tbody></table></div></details>')
    (AQUI / "graficos.json").write_text(json.dumps(g, ensure_ascii=False, indent=0), encoding="utf-8")
    print("ok", list(g))


if __name__ == "__main__":
    main()
