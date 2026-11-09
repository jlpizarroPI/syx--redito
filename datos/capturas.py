import sys, json
from playwright.sync_api import sync_playwright
url = "http://127.0.0.1:8765/" + (sys.argv[1] if len(sys.argv) > 1 else "index.html")
out = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    for nombre, w, h, oscuro in (("movil", 375, 812, False), ("tablet", 834, 1112, False), ("escritorio", 1440, 900, False), ("movil-oscuro", 375, 812, True)):
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=2 if w < 800 else 1, color_scheme="dark" if oscuro else "light")
        errores = []
        pg.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errores.append(str(e)))
        pg.goto(url); pg.wait_for_timeout(300)
        pg.evaluate("""async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 40)); } window.scrollTo(0, 0); }""")
        pg.wait_for_timeout(500)
        pg.screenshot(path=f"datos/{nombre}.png", full_page=True)
        out[nombre] = pg.evaluate("""() => ({desborde: document.documentElement.scrollWidth > document.documentElement.clientWidth,
            fuentes: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.style)})""")
        out[nombre]["errores"] = errores
    b.close()
print(json.dumps(out, ensure_ascii=False, indent=1))
