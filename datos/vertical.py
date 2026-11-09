"""Auditoría de alineación VERTICAL.

Dos métodos, cada uno donde es fiable:

  · LÍNEA BASE (sonda inline de alto cero): los textos que comparten fila — cabeceras, temas, fichas,
    listas con hora, pestañas, firma — deben tener la misma línea base.
  · TINTA (captura a 4×): los controles junto a texto — casillas, hamburguesa, lupa, luna, botones de la
    barra — deben tener su centro en el centro de las MAYÚSCULAS del texto vecino. Se mide la tinta real
    de la primera letra (mayúscula) y del control; la canvas no sirve aquí porque Newsreader cambia de
    proporciones con opsz y el cálculo exageraba el desfase.

Uso: python3 datos/vertical.py [url] [anchos…]   ·   tolerancia: 0,75 px
"""
import json, sys
from playwright.sync_api import sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].startswith("http") else "http://127.0.0.1:8765/index.html"
ANCHOS = [int(a) for a in sys.argv[1:] if a.isdigit()] or [375, 1440]
TOL = 0.75

J = r"""() => {
const cv = document.createElement('canvas').getContext('2d');
function texto(el){ // primer nodo de texto visible dentro de el
  const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, {acceptNode:n=>n.textContent.trim()?1:3});
  return w.nextNode();
}
function metr(el){
  const n = texto(el); if(!n) return null;
  const p = n.parentElement, cs = getComputedStyle(p);
  const s = document.createElement('span'); s.style.cssText='display:inline-block;width:0;height:0;vertical-align:baseline';
  n.parentNode.insertBefore(s, n); const base = s.getBoundingClientRect().bottom; s.remove();
  cv.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
  const cap = cv.measureText('H').actualBoundingBoxAscent, x = cv.measureText('x').actualBoundingBoxAscent;
  return {base, cap, x, centro: base - cap/2, centroX: base - x/2, fs: parseFloat(cs.fontSize)};
}
const vis = e => e && e.getClientRects().length && getComputedStyle(e).visibility!=='hidden';
const r1 = v => Math.round(v*100)/100;
const out = [];
function control(nombre, ctrlCentro, el){
  const m = metr(el); if(!m) return;
  out.push({tipo:'centro', nombre, dif:r1(ctrlCentro - m.centro), difX:r1(ctrlCentro - m.centroX), cap:r1(m.cap), x:r1(m.x)});
}
function base(nombre, els){
  const ms = els.filter(vis).map(e=>[e, metr(e)]).filter(([,m])=>m);
  if(ms.length<2) return;
  const bs = ms.map(([,m])=>m.base); const ref = bs[0];
  out.push({tipo:'base', nombre, dif:r1(Math.max(...bs)-Math.min(...bs)), detalle: ms.map(([e,m])=>[(e.className.baseVal??e.className).split(' ').pop()||e.tagName, r1(m.base-ref)])});
}
// 3 · cabeceras con enlace
document.querySelectorAll('.haber-fichas__cabeza, .haber-seccion__cabeza').forEach((c,i)=>{
  const t=c.firstElementChild, a=c.querySelector('.haber-mas'); if(!a||!vis(t)) return;
  const rt=t.getBoundingClientRect(), ra=a.getBoundingClientRect(); if(ra.top>rt.bottom) return; // apilados
  base('cabecera '+(i+1)+' · '+t.textContent.trim().slice(0,18), [t,a]);
});
// 4 · temas
const tt=document.querySelector('.haber-temas__titulo'), t1=document.querySelector('.haber-temas__lista a');
base('temas · rótulo vs enlaces', [tt,t1]);
// 5 · fichas
document.querySelectorAll('.haber-ficha__enlace').forEach((f,i)=>{ if(i>1) return;
  base('ficha '+(i+1)+' · valor vs variación', [f.querySelector('.haber-ficha__valor'), f.querySelector('.haber-ficha__delta')]); });
// 6 · listas con hora
document.querySelectorAll('.haber-ultimo__lista > li').forEach((li,i)=>{ if(i>1) return;
  base('lo último '+(i+1)+' · hora vs titular', [li.querySelector('time'), li.querySelector('a')]); });
// 7 · pestañas
document.querySelectorAll('.mol-tabs__list').forEach((t,i)=> base('pestañas '+(i+1), [...t.querySelectorAll('.mol-tabs__tab')]));
// 8 · firma
const fi=document.querySelector('.haber-firma'); if(fi) base('firma de la apertura (1.ª línea)', [...fi.children].filter(e=>e.getBoundingClientRect().top < fi.firstElementChild.getBoundingClientRect().bottom));
// 9 · columnistas: el avatar se centra en el bloque nombre + título (no en el nombre)
document.querySelectorAll('.haber-columna').forEach((c,i)=>{ if(i) return; const av=c.querySelector('.atom-avatar').getBoundingClientRect();
  const blq=c.querySelector('div').getBoundingClientRect();
  out.push({tipo:'centro', nombre:'columnista · avatar vs bloque nombre+título', dif:r1((av.top+av.height/2)-(blq.top+blq.height/2))}); });
// 10 · lo más leído: número vs titular (::before en la misma rejilla, alineado por baseline)
const li=document.querySelector('.haber-leido__lista > li'); if(li&&vis(li)) out.push({tipo:'info', nombre:'lo más leído · align-items', dif:getComputedStyle(li).alignItems});
// 11 · campo y botón del boletín
const bt=document.querySelector('.haber-boletines__boton'), inp=document.querySelector('.haber-boletines__form input[type=email]');
if(vis(bt)&&vis(inp)){const a=bt.getBoundingClientRect(),b=inp.getBoundingClientRect(); if(Math.abs(a.top-b.top)<a.height) out.push({tipo:'base', nombre:'boletín · campo vs botón (bordes)', dif:r1(Math.max(Math.abs(a.top-b.top),Math.abs(a.bottom-b.bottom)))});}
return out;}"""


S = 4
from PIL import Image
import io, numpy as np
def _tinta(img, r, primera=True):
    x0, y0, x1, y1 = [int(round(v * S)) for v in (r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"])]
    a = np.asarray(img.crop((x0, y0, x1, y1)).convert("L")).astype(int); ink = np.abs(a - np.median(a)) > 70
    cols = np.where(ink.any(0))[0]
    if not len(cols): return None
    if primera:
        g = np.where(np.diff(cols) > S // 2)[0]; cols = cols[: g[0] + 1] if len(g) else cols
    rows = np.where(ink[:, cols].any(1))[0]
    return ((y0 + rows[0]) / S + (y0 + rows[-1] + 1) / S) / 2
def _casilla(pg, i):
    png = pg.locator(".atom-check").nth(i).screenshot(); im = np.asarray(Image.open(io.BytesIO(png)).convert("L")).astype(int)
    ink = np.abs(im - np.median(im)) > 60; cols = np.where(ink.any(0))[0]; g = np.where(np.diff(cols) > 3 * S)[0]
    caja, letra = cols[: g[0] + 1], cols[g[0] + 1:]
    g2 = np.where(np.diff(letra) > S)[0]; letra = letra[: g2[0] + 1] if len(g2) else letra
    rc = np.where(ink[:, caja].any(1))[0]; rl = np.where(ink[:, letra].any(1))[0]
    return ((rc[0] + rc[-1]) / 2 - (rl[0] + rl[-1]) / 2) / S
def tinta(pg):
    img = Image.open(io.BytesIO(pg.screenshot())); res = []
    bb = lambda sel: (lambda e: e.first.bounding_box() if e.count() and e.first.is_visible() else None)(pg.locator(sel))
    ref = None
    for sel in (".haber-nav__boton .haber-optico", ".haber-barra__letra .haber-optico"):
        r = bb(sel)
        if r: ref = _tinta(img, r); break
    for nombre, sel, prim in (("barra · hamburguesa", ".haber-barra__menu", False), ("barra · «Buscar»", ".haber-barra__texto", True),
                              ("barra · lupa", ".haber-barra__boton .atom-icon", False), ("barra · «Aa»", ".haber-barra__letra .haber-optico", True),
                              ("barra · luna", ".haber-barra__modo .atom-icon", False), ("barra · «Suscríbete»", ".haber-barra__suscripcion .haber-optico", True)):
        r = bb(sel)
        if r and ref is not None:
            v = _tinta(img, r, prim)
            if v is not None: res.append({"tipo": "centro", "nombre": nombre + " (tinta, frente a las mayúsculas)", "dif": round(v - ref, 2)})
    for i in range(pg.locator(".atom-check").count()):
        res.append({"tipo": "centro", "nombre": f"casilla {i+1} (tinta, cuadro frente a la mayúscula)", "dif": round(_casilla(pg, i), 2)})
    return res

fallos = 0
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    for w in ANCHOS:
        pg = b.new_page(viewport={"width": w, "height": 900}, device_scale_factor=S); pg.goto(URL); pg.wait_for_timeout(500)
        print(f"── {w} px")
        for r in pg.evaluate(J) + tinta(pg):
            mal = r["tipo"] != "info" and isinstance(r["dif"], (int, float)) and abs(r["dif"]) > TOL
            fallos += mal
            extra = f"  (frente a la x: {r['difX']:+} px · mayúscula {r['cap']} px, x {r['x']} px)" if "difX" in r else ""
            det = f"  {r['detalle']}" if mal and "detalle" in r else ""
            print(f"  {'✗' if mal else '✓'} {r['nombre']}: {r['dif']}{' px' if r['tipo']!='info' else ''}{extra}{det}")
    b.close()
print("fuera de tolerancia:", fallos)
