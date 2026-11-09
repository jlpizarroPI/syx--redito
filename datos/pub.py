"""Prueba del sistema de publicidad: atributos data-pub completos, carril sticky (se pega bajo la barra,
no pisa «Lo más leído» ni sale de su columna), visibilidad MRC, eventos y sin sticky en móvil."""
import json, sys
from playwright.sync_api import sync_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/index.html"
REQ = ["pub", "pubId", "pubFormato", "pubZona", "pubPosicion", "pubSticky", "pubEstado"]
fallos = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    for w, h in ((375, 812), (1024, 768), (1280, 800), (1440, 900), (1440, 560)):
        pg = b.new_page(viewport={"width": w, "height": h}); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.add_init_script("window.dataLayer=[];window.__ev=[];document.addEventListener('redito:pub',e=>__ev.push(e.detail))")
        pg.goto(URL); pg.wait_for_timeout(400)
        datos = pg.evaluate("()=>[...document.querySelectorAll('[data-pub]')].map(e=>({...e.dataset}))")
        ids = [d.get("pubId") for d in datos]
        for d in datos:
            falta = [k for k in REQ if k not in d]
            if falta: fallos.append(f"{w}: {d.get('pubId')} sin {falta}")
        if len(set(ids)) != len(ids): fallos.append(f"{w}: ids repetidos {ids}")
        # recorrer la zona de desarrollo
        res = pg.evaluate("""async()=>{
          const ad=document.querySelector('[data-pub-sticky=carril]'), lat=ad.closest('.haber-lateral'),
                barra=document.querySelector('.haber-barra'), linea=parseFloat(getComputedStyle(ad).top);
          const z=lat.parentElement.getBoundingClientRect(); const top0=z.top+scrollY; const fin=z.bottom+scrollY;
          const out={sticky:getComputedStyle(ad).position, muestras:[]};
          for(let y=top0-200;y<fin+200;y+=60){ scrollTo(0,y); await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
            const a=ad.getBoundingClientRect(), L=lat.getBoundingClientRect(), B=barra.getBoundingClientRect();
            out.muestras.push({y, top:Math.round(a.top), barra:Math.round(B.bottom), linea:Math.round(linea),
              bajoBarra: ad.dataset.pubPegado==='true' && a.top < B.bottom-0.5, saleCol:a.bottom>L.bottom+0.5||a.top<L.top-0.5,
              mal: ad.dataset.pubPegado==='true' && Math.abs(a.top-linea)>1.5, pegado:ad.dataset.pubPegado});}
          out.recorrido=Math.round(lat.getBoundingClientRect().height-ad.getBoundingClientRect().height);
          out.altoAd=ad.getBoundingClientRect().height; out.vh=innerHeight;
          // quedarse 1,3 s con el robapáginas a la vista para la impresión MRC
          ad.scrollIntoView({block:'center'}); await new Promise(r=>setTimeout(r,1400));
          out.estado=ad.dataset.pubEstado; return out}""")
        ev = pg.evaluate("()=>__ev.map(e=>e.evento+':'+(e.pub_id||e.total))")
        dl = pg.evaluate("()=>dataLayer.length")
        peg = [m for m in res["muestras"] if m["pegado"] == "true"]
        sol = [m for m in res["muestras"] if m["bajoBarra"] or m["saleCol"] or m["mal"]]
        pct = round(100 * res["altoAd"] / res["vh"], 1)
        print(f"{w}×{h}: position={res['sticky']} · pegado en {len(peg)}/{len(res['muestras'])} muestras"
              f" · top al pegar {sorted({m['top'] for m in peg})} (barra {sorted({m['barra'] for m in peg})})"
              f" · recorrido {res['recorrido']} px · fallos de posición {len(sol)} · alto {pct}% de pantalla · estado {res['estado']} · eventos {len(ev)} · dataLayer {dl} · errores {errs}")
        print("   ", ev[:8])
        if sol: fallos.append(f"{w}×{h}: el carril pisa o se sale {sol[:2]}")
        if w < 1280 and res["sticky"] == "sticky": fallos.append(f"{w}: sticky en móvil")
        if res["estado"] != "visible": fallos.append(f"{w}×{h}: sin impresión visible")
        if errs: fallos.append(f"{w}: {errs}")
    b.close()
print("FALLOS:", fallos or "ninguno")
sys.exit(bool(fallos))
