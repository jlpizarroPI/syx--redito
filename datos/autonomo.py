"""dist/index.html autónomo: CSS de SYX (sin sus @font-face) y de la app en línea, fuentes,
imágenes (variante de 800 px) y scripts incrustados. Es lo que se publica como artefacto."""
import base64
import re
from pathlib import Path

R = Path(__file__).resolve().parent.parent
html = (R / "index.html").read_text(encoding="utf-8")
syx = re.sub(r"@font-face\s*\{[^}]*\}", "", (R / "css/syx.css").read_text(encoding="utf-8"))
haber = (R / "css/haber.css").read_text(encoding="utf-8")
for f in ("newsreader.woff2", "newsreader-italic.woff2", "hito-v1.woff2", "hito-italic-v1.woff2"):
    b = base64.b64encode((R / "fonts" / f).read_bytes()).decode()
    haber = haber.replace(f'url("../fonts/{f}")', f'url("data:font/woff2;base64,{b}")')
html = re.sub(r'\s*<link rel="preload"[^>]*>', "", html)
html = html.replace('<link rel="stylesheet" href="css/syx.css">', "<style>" + syx + "</style>")
html = html.replace('<link rel="stylesheet" href="css/haber.css">', "<style>" + haber + "</style>")


def img(m):
    nombre = m.group(1)
    b = base64.b64encode((R / "img" / f"{nombre}-800.webp").read_bytes()).decode()
    return f'src="data:image/webp;base64,{b}"'


html = re.sub(r'src="img/([a-z]+)-800\.webp" srcset="[^"]*" sizes="[^"]*"', img, html)
assert 'src="img/' not in html
for js, tipo in (("syx-site-nav.js", "module"), ("syx-tabs.js", "module"), ("haber.js", None), ("redito-pub.js", None)):
    codigo = (R / "js" / js).read_text(encoding="utf-8").replace("</script", "<\\/script")
    patron = f'<script type="module" src="js/{js}"></script>' if tipo else f'<script src="js/{js}" defer></script>'
    nuevo = f'<script type="module">{codigo}</script>' if tipo else f'<script type="module">{codigo}</script>'
    assert patron in html, patron
    html = html.replace(patron, nuevo)
(R / "dist" / "index.html").write_text(html, encoding="utf-8")
print("dist/index.html", len(html) // 1024, "KB")
