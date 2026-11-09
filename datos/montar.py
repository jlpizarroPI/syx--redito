"""Monta index.html desde index.src.html: menús (datos/menu.py), gráficos (datos/graficos.json)
e imágenes con srcset (img/<nombre>-<ancho>.webp).  python3 datos/montar.py"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "datos"))
import menu  # noqa: E402

g = json.loads((RAIZ / "datos" / "graficos.json").read_text(encoding="utf-8"))


def img(nombre, sizes):
    return (f'src="img/{nombre}-800.webp" srcset="img/{nombre}-480.webp 480w, img/{nombre}-800.webp 800w, '
            f'img/{nombre}-1200.webp 1200w" sizes="{sizes}"')


def fichas():
    out = []
    for f in g["fichas"]:
        sentido = "sube" if f["sube"] else "cae"
        out.append(f'<li class="haber-ficha haber-ficha--{sentido}"><a class="haber-ficha__enlace" href="#mercados">'
                   f'<span class="haber-ficha__nombre">{f["nombre"]}</span>'
                   f'<span class="haber-ficha__valor">{f["valor"]}</span>'
                   f'<span class="haber-ficha__delta">{f["delta"]}</span>{f["svg"]}</a></li>')
    return "".join(out)


html = (RAIZ / "index.src.html").read_text(encoding="utf-8")
html = html.replace("{{NAV}}", menu.nav_escritorio()).replace("{{CAJON}}", menu.cajon())
html = html.replace("{{MEGA}}", menu.megamenus(img)).replace("{{SECCIONES}}", menu.secciones_fila())
html = html.replace("{{TEMAS}}", menu.temas()).replace("{{PIE}}", menu.pie()).replace("{{FICHAS}}", fichas())
for k in ("bono", "ibex", "eurusd"):
    html = html.replace(f"{{{{GRAF:{k}}}}}", g[k][0]).replace(f"{{{{TABLA:{k}}}}}", g[k][1])
html = html.replace("{{GRAF:subastas}}", g["subastas"]).replace("{{GRAF:sectores}}", g["sectores"])
html = html.replace("{{TABLA:sectores}}", g["sectores_tabla"])
html = re.sub(r"\{\{IMG:([a-z]+)\|([^}]+)\}\}", lambda m: img(m.group(1), m.group(2)), html)
assert "{{" not in html, re.findall(r"\{\{[^}]+\}\}", html)
# ortotipografía: la cifra y su signo no se separan al partir la línea («60 %», «2,5 %», «12 €»).
# Solo en texto (fuera de etiquetas, <script> y <style>), con espacio de no separación.
def _sin_corte(m):
    return m.group(0) if m.group(1) else re.sub(r"(\d) (%|€|‰|p\. ?b\.)", "\\1\u00a0\\2", m.group(0))
html = re.sub(r"(<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)|[^<]+", _sin_corte, html, flags=re.S)
(RAIZ / "index.html").write_text(html, encoding="utf-8")
print("index.html", len(html))
