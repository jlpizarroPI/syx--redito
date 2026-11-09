"""Auditoría de alineación: los bordes de inicio de titulares, rótulos, textos, imágenes y controles
deben empezar o terminar en una línea de columna de su layout-grid (±1 px). Lista los que no, agrupados."""
import json, sys
from collections import Counter
from playwright.sync_api import sync_playwright
J = r"""()=>{
 const res=[]; const sel='h1,h2,h3,p,.haber-rotulo,img,input.atom-input,.atom-btn,.haber-tabla,figure,ul,ol,.mol-tabs,svg.haber-graf__svg';
 for(const g of document.querySelectorAll('.layout-grid')){
  if(!g.offsetParent) continue;
  const cs=getComputedStyle(g); const cols=cs.gridTemplateColumns.split(' ').map(parseFloat); const gap=parseFloat(cs.columnGap)||0;
  const r=g.getBoundingClientRect(); let x=r.left+parseFloat(cs.paddingLeft)+parseFloat(cs.borderLeftWidth); const lines=[];
  for(const c of cols){lines.push(x); x+=c; lines.push(x); x+=gap;}
  for(const e of g.querySelectorAll(sel)){
   if(e.closest('.layout-grid')!==g) continue;
   const b=e.getBoundingClientRect(); if(!b.width||!b.height) continue;
   if(e.closest('.haber-claves,.haber-ficha,.haber-pub,.haber-graf,.mol-tabs__panel,.haber-cajon,.haber-mega,[popover],.haber-tarjeta__media,.haber-avatar,.atom-check')) continue;
   const st=getComputedStyle(e); if(st.position==='fixed'||st.visibility==='hidden') continue;
   const dl=Math.min(...lines.map(l=>Math.abs(l-b.left))), dr=Math.min(...lines.map(l=>Math.abs(l-b.right)));
   if(e.matches('.haber-abre__titulo')&&dl<3) continue; /* alineación óptica intencionada del titular de apertura */
   const d=Math.min(dl,dr);
   if(d>1) res.push({cls:(e.className&&e.className.baseVal!==undefined?e.className.baseVal:e.className)||e.tagName, tag:e.tagName, d:Math.round(d*10)/10, x:Math.round(b.left), y:Math.round(b.top+scrollY), txt:(e.textContent||'').trim().slice(0,30)});
  }
 } return res;}"""
with sync_playwright() as p:
  b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
  for w in [int(a) for a in (sys.argv[1:] or [375, 768, 1024, 1440])]:
    pg = b.new_page(viewport={"width": w, "height": 900}); pg.goto("http://127.0.0.1:8765/index.html"); pg.wait_for_timeout(400)
    r = pg.evaluate(J)
    c = Counter((x['tag'], x['cls'].split(' ')[-1] if x['cls'] else x['tag'], x['d']) for x in r)
    print(f"{w}px · {len(r)} fuera de línea")
    for k, n in c.most_common(25): print("   ", n, k, next(x['txt'] for x in r if (x['tag'], x['cls'].split(' ')[-1] if x['cls'] else x['tag'], x['d']) == k))
  b.close()
