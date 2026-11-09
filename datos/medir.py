"""Comprobaciones de la portada v4 en Chrome (barrido 320 → 1600 px de 8 en 8).
C2 desborde · C6 columna en uso / gutter · C7 objetivos táctiles · Q5 caída de columna ·
CLS (layout shift al cargar, imágenes y huecos de publicidad reservados) · publicidad:
número de bloques y que ninguno toque a otro · C5 en los textos de tarjeta (medida)."""
import json
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/index.html"
JS = """() => {
  const de = document.documentElement;
  const g = document.querySelector('.haber-zona');
  const cs = getComputedStyle(g);
  const cols = cs.gridTemplateColumns.split(' ').map(parseFloat);
  const gap = parseFloat(cs.columnGap);
  const visibles = sel => [...document.querySelectorAll(sel)].filter(e => e.offsetParent !== null && getComputedStyle(e).visibility !== 'hidden');
  const objetivos = visibles('main a, main button, .org-site-header a, .org-site-header button, .haber-secciones a, .haber-temas a, .haber-pie a')
      .map(e => { const b = e.getBoundingClientRect(); return {h: b.height, w: b.width, t: e.textContent.trim().slice(0, 30)}; });
  const minimo = objetivos.reduce((m, o) => Math.min(m, o.h), 99);
  const bajo = objetivos.filter(o => o.h < 24).map(o => o.t);
  const piezas = visibles('.haber-zona > *, .haber-entrada > *, .haber-banda .layout-grid > *').map(e => e.getBoundingClientRect().width);
  return {col: cols[0], gap, en_uso: Math.min(...piezas), desborde: de.scrollWidth > de.clientWidth, objetivo_min: minimo, bajo24: bajo};
}"""
res = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(viewport={"width": 320, "height": 800})
    pg.goto(URL); pg.wait_for_timeout(400)
    for w in range(320, 1601, 8):
        pg.set_viewport_size({"width": w, "height": 800}); pg.wait_for_timeout(15)
        d = pg.evaluate(JS); d["w"] = w; res.append(d)
    # CLS en carga, móvil y escritorio, recorriendo toda la página
    cls = {}
    for w in (375, 1440):
        q = b.new_page(viewport={"width": w, "height": 800})
        q.add_init_script("""window.__cls = 0; new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({type: 'layout-shift', buffered: true});""")
        q.goto(URL); q.wait_for_timeout(300)
        q.evaluate("""async () => { for (let y = 0; y < document.body.scrollHeight; y += 500) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } }""")
        q.wait_for_timeout(500)
        cls[w] = q.evaluate("window.__cls")
        if w == 1440:
            anuncios = q.evaluate("""() => { const a = [...document.querySelectorAll('.haber-anuncio, .haber-tarjeta--patrocinada')];
              return {n: a.length, en_entrada: a.filter(x => x.closest('.haber-entrada')).length,
                      contiguos: a.some((x, i) => i && x.previousElementSibling === a[i - 1])}; }""")
            medida = q.evaluate("""() => [...document.querySelectorAll('.haber-tarjeta__texto, .haber-noticia__texto, .haber-abre__entradilla')].map(p => {
              const t = p.firstChild; if (!t || !t.length) return 0; const r = document.createRange(); let y = null, n = 0, mx = 0;
              for (let i = 0; i < t.length; i++) { r.setStart(t, i); r.setEnd(t, i + 1); const bb = r.getClientRects()[0]; if (!bb) continue;
                if (y === null || Math.abs(bb.top - y) > 2) { mx = Math.max(mx, n); y = bb.top; n = 0; } n++; }
              return Math.max(mx, n); })""")
        q.close()
    b.close()
caida = max((max(0.0, (res[i-1]["col"] - res[i]["col"]) / res[i-1]["col"]) for i in range(1, len(res))), default=0)
print("C2 desborde en algún ancho:", any(r["desborde"] for r in res))
print("C6 columna EN USO / gutter mínima: %.2f" % min(r["en_uso"] / r["gap"] for r in res))
print("Q5 mayor caída de columna al ensanchar: %.2f %%" % (100 * caida))
print("C7 alto mínimo de objetivo táctil: %.1f px · por debajo de 24 px: %s" % (min(r["objetivo_min"] for r in res), sorted({t for r in res for t in r["bajo24"]})[:8]))
print("CLS en carga y desplazamiento:", {k: round(v, 4) for k, v in cls.items()})
print("Publicidad:", anuncios)
print("C5 línea más larga de los textos de tarjeta a 1440 px:", max(medida), "caracteres")
