"""Parte css/haber.css (v5) en la arquitectura SCSS de scss/. Se ejecutó una vez; queda como registro."""
import re, pathlib
L = pathlib.Path('css/haber.css').read_text().split('\n')
def rango(a, b): return L[a-1:b]          # 1-based, inclusivo
def sin_sangria(ls): return [l[2:] if l.startswith('  ') else l for l in ls]
MQ = [
  ('@media (min-width: 48em) and (max-width: 79.99em)', '@include entre(md, xl)'),
  ('@media (min-width: 48em)', '@include desde(md)'),
  ('@media (min-width: 64em)', '@include desde(lg)'),
  ('@media (min-width: 80em)', '@include desde(xl)'),
  ('@media (prefers-reduced-motion: reduce)', '@include sin-movimiento'),
]
def mq(t):
  for a, b in MQ: t = t.replace(a, b)
  return t
def escribe(ruta, cabecera, lineas, usa=True):
  p = pathlib.Path('scss')/ruta; p.parent.mkdir(parents=True, exist_ok=True)
  cuerpo = mq('\n'.join(lineas)).strip('\n')
  pre = '@use "../abstracts" as *;\n\n' if usa and '@include' in cuerpo else ''
  p.write_text(f'// {cabecera}\n{pre}{cuerpo}\n')
# — fuera de capa —
escribe('base/_fuentes.scss', 'Newsreader (texto y titulares) y Hito solo para cifras (unicode-range).', rango(12, 46))
escribe('tokens/_syx.scss', 'Sobrescritura de tokens semánticos de SYX: claro, oscuro del sistema y oscuro elegido.', rango(48, 132))
escribe('tokens/_proyecto.scss', 'Tokens --haber-*: leen roles semánticos; las longitudes salen de gridcalc (GRID-SPEC.md).',
        rango(134, 232) + [''] + rango(245, 250))
escribe('tokens/_preferencias.scss', 'Preferencias del lector: tamaño de letra (control «Aa») y más contraste.', rango(234, 243))
# — capa syx.app —
capa = [
  ('base/_base.scss', 'Base de la portada: cuerpo, rótulos, titulares, firma, tipografía común.', 258, 402),
  ('componentes/_marca.scss', 'Cabecera de marca (≥ 64em).', 403, 448),
  ('componentes/_barra.scss', 'Barra fija: org-site-header de SYX, cajón, megamenús y búsqueda.', 449, 678),
  ('componentes/_secciones-temas.scss', 'Fila de secciones y temas con desplazamiento horizontal.', 679, 748),
  ('componentes/_fichas.scss', 'Fichas de mercado: stat tile con sparkline (skill dataviz).', 749, 850),
  ('zonas/_entrada.scss', 'Zona 5 · entrada (N1 + N2 + Lo último + Las claves). Sin publicidad (atlas 06.3).', 851, 999),
  ('zonas/_secciones.scss', 'Encabezado y ritmo común de las secciones.', 1000, 1015),
  ('zonas/_mercados.scss', 'Zona 6 · mercados: banda densa (alternancia de densidad, atlas 06.2).', 1016, 1071),
  ('componentes/_graficos.scss', 'Gráficos SVG (skill dataviz): --k = unidades del viewBox por px.', 1072, 1242),
  ('zonas/_desarrollo.scss', 'Zona 7 · desarrollo: tarjetas con imagen y lateral.', 1243, 1377),
  ('componentes/_publicidad.scss', 'Publicidad (atlas 06.3): bloque del grid, rotulado, con hueco reservado.', 1378, 1430),
  ('zonas/_opinion.scss', 'Zona 8 · opinión: bloque de respiro.', 1431, 1499),
  ('zonas/_profundidad.scss', 'Zona 9 · profundidad: Empresas y Tecnología.', 1500, 1526),
  ('componentes/_boletines.scss', 'Zona 10 · boletines.', 1527, 1572),
  ('zonas/_pie.scss', 'Pie con el índice completo.', 1573, 1620),
  ('componentes/_lectura.scss', 'Reglas contra la fatiga: Las claves y tiempo de lectura (ver README).', 1621, 1662),
  ('utilidades/_movimiento-foco.scss', 'Movimiento reducido, foco visible y selección.', 1663, 1684),
]
for ruta, cab, a, b in capa:
  escribe(ruta, cab, sin_sangria(rango(a, b)))
print('cabecera de capa:', rango(253, 257))
