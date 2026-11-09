# GRID SPEC — Rédito v4 (portada completa)

```
Contexto       : web mobile first · portada de diario económico ficticio · prestigio + densidad informativa
Tipografía     : Newsreader (texto y titulares, opsz auto) · cifras de datos en Hito v0.5 (unicode-range) — ver v3
Retícula       : layout-grid de SYX, 12 col · gutter 16 → 42 · margen 16 → 120 · máx. 90rem (1200 de contenido)
Ritmo          : u = 28 → 32 px; espacios en múltiplos de u/4; sección 3u en móvil → 5u desde 64em;
                 respiro 4u → 7u (06.2 §18: en móvil, menos vacío)
Zonas (06.2)   : marca · barra · secciones/temas · fichas de mercado · ENTRADA (N1 + N2 + lo último, 0 anuncios)
                 · MERCADOS (banda densa en papel 2) · DESARROLLO (Economía 8 + lateral 4) · faldón
                 · RESPIRO (Opinión) · PROFUNDIDAD (Empresas, Tecnología) · boletines · pie
Publicidad     : 3 bloques (máx. de 06.3): robapáginas 300×250 en el lateral de desarrollo; faldón entre desarrollo
                 y profundidad (320×50 → 728×90 desde 48em → 970×90 desde 64em); contenido patrocinado como N3,
                 rotulado «Publicidad», rel="sponsored". Huecos con aspect-ratio: CLS 0,0001
Navegación     : org-site-header fijo (hamburguesa en todos los anchos) · cajón = índice completo en acordeón
                 exclusivo (mol-disclosure name) con búsqueda, servicios y cuenta · ≥ 80em: 6 botones con megamenú
                 (Popover API + anchor positioning) · < 80em: fila de secciones desplazable · fila de temas
Imágenes       : 7 ilustraciones duotono generadas por código (datos/imagenes.py), webp 480/800/1200 con srcset;
                 proporciones 3:2 (abre, tarjetas ≥ 48em) y 1:1 (miniaturas); hueco reservado con aspect-ratio
Gráficos       : skill dataviz — 6 fichas con sparkline · línea con cruz de lectura (3 series en mol-tabs) ·
                 columnas con énfasis · barras divergentes; vista de tabla en mol-disclosure; par sube/cae azul/teja
                 validado (ΔE CVD 22,1 claro · 23,1 oscuro)
Transformación : < 48em una columna; tarjetas en fila compacta (titular + miniatura) · 48–80em tarjetas 2 por fila
                 con subgrid, lateral bajo las tarjetas · ≥ 80em 8 + 4, tecnología 3 por fila (cards/row de compose)
Validación     : C2 ✓ (320 → 1600) · C6 ✓ 8,7 · C7 ✓ ≥ 24 px (navegación 44 px) · Q5 0,03 % · CLS 0,0001 ·
                 C5 ✓ textos de tarjeta ≤ 74 car. · 3 anuncios, 0 en la entrada, ninguno contiguo · syx-scan 0
```

---

## v5 · Rédito — reglas contra la fatiga de lectura

Base: Weinreich et al. 2008 / Nielsen (se lee ~20–28 % del texto de una página), Chartbeat (la atención cae tras el primer pantallazo), metaanálisis de síndrome visual informático, Delgado et al. 2018 (comprensión en pantalla frente a papel).

1. Lo esencial en titular, entradilla y primeras líneas (pirámide invertida).
2. «Las claves»: 3 viñetas bajo la firma de la apertura, ≤ 70 caracteres cada una.
3. Bloques cortos con rótulo de sección; textos de tarjeta ≤ 74 caracteres por línea (C5).
4. Cifras en gráficos con su tabla equivalente, no en párrafos.
5. Tiempo de lectura visible en la apertura y en cada tarjeta (`.haber-lectura`, cifras Hito, sin corte de línea).
6. El móvil baja menos: módulo u = 28 px en móvil y 32 px en escritorio; secciones 3/4 → 5/7.
7. Control «Aa»: 100 / 112,5 / 125 %, guardado por lector; `prefers-contrast: more`; modo oscuro propio.
8. Sin cambios en la medida (31,3 em) ni en el interlineado (1,556), que ya están en el rango óptimo.

Verificación: C2 sin desborde 320–1600 · C6 8,69 · C7 ≥ 24 px · Q5 0,03 % · CLS 0,0001 · 3 anuncios, ninguno en la apertura · C5 máx. 74.

## Versión anterior (v3)

# GRID SPEC — Rédito v3 (Newsreader + cifras en Hito)

```
Contexto       : web mobile first · diario económico ficticio · prestigio (perception-of-prestige de SYX)
Tipografía     : Newsreader (Production Type, OFL), redonda y cursiva variables wght 200–800 · opsz 6–72,
                 opsz = cuerpo (auto). Cuerpo 18 → 20 px / 1,556 (x 0,426) · char 0,3974 → 0,3991 em · medida 31,3 em
                 Cifras de datos: Hito v0.5 por unicode-range (0–9 + − % , .), size-adjust 94,9 % (versal 0,67 / cifra 0,706)
Densidad       : uso reading · spacious · razón de cadena 2
Cadena         : micro 4 · inner 8→10 · padding 16→18 · gutter 16→42 · margen 16→120 · sección 5u (140→160) · respiro 7u (196→224)
Retícula base  : u = 28 → 32 px; espacios verticales en múltiplos de u/4, de tinta a tinta (text-box: trim-both cap alphabetic)
Operadores     : O3 desplazamiento (tribuna) · O14 vacío activo (columna 8 y bloque de respiro)
Validación     : C2 ✓ · C5 ✓ desde ~380 px (45–77 car. de media, máx. 80) · C6 ✓ 8,3 · C7 ✓ 44 px · Q5 0,03 % · syx-scan 0
```

| Pieza | Tamaño (360 → 1440) | Interlineado | Peso / opsz | Tracking |
|---|---|---|---|---|
| Cabecera «Rédito» | +4 → +6 · 56,8 → 112 px | 63 → 120 | 500 · 72 | −0,02 em |
| Titular de abre | +3 → +5 · 42,6 → 84 px | 49 → 96 (1,15 → 1,14) | 400 · 72 | −0,015 em |
| Cita de tribuna (cursiva) | +2 → +4 · 32 → 63 px | 42 → 72 (1,31 → 1,14) | 350 · auto | −0,01 em; «» colgada (−0,432 em) |
| Titular de pieza | +1½ · 27,7 → 30,8 px | 35 → 40 (1,26 → 1,3) | 500 · auto | −0,008 em |
| Entradilla (cursiva) | +1 · 24 → 26,7 px | 35 → 40 | 400 · auto | 0 |
| Cuerpo | 18 → 20 px | 28 → 32 (1,556) | 400 (380 en oscuro) · auto | 0 |
| Rótulos (versal) | −1 · 13,5 → 15 px | u | 600 | +0,1 em |
| Firma, pie, datos | 15 → 16 px | u | 400 / 600 | +0,01 em |

Alineación óptica (start_white de gridcalc): abre −0,0292 em · pieza −0,0285 em · cita −0,0066 em.

---

## Versión anterior (v2)

# GRID SPEC — Rédito v2 «edición de prestigio»

```
Contexto       : web mobile first · diario económico ficticio · prestigio (perception-of-prestige de SYX)
Tipografía     : Ticker medida por peso (gridcalc font --axes wght=…): char 0,4289 em @300 · 0,4422 @400 ·
                 0,4656 @600 · 0,4885 @800 · start_white 0,0347 / 0,0318 / 0,0277 / 0,0229 em
                 cuerpo 16 → 18 px / 1,5 · medida 32,795 em · escala de cuarta 1,333 con medios pasos
Densidad       : uso reading · densidad spacious · razón de cadena 2
Cadena         : micro 4 · inner 8→10 · padding 16→18 · gutter 16→38 · margen 16→120 · sección 5u (120→140)
                 · respiro 7u (168→196) px
Retícula base  : u = 24→28 px; todo espacio vertical en múltiplos de u/4, de tinta a tinta (text-box: trim-both cap alphabetic)
Proporciones   : abre 10/12 · texto 7 + vacío 1 + lateral 4 desde 80em (8 + 4 desde 64em) · tribuna 8 desplazada 2 · piezas 3 × 4
Operadores     : O3 desplazamiento (tribuna) · O14 vacío activo (columna 8 y bloque de respiro)
Validación     : C2 ✓ · C5 ✓ desde 376 px (47–73 car. de media, máx. 75) · C6 ✓ 9,1 · C7 ✓ · Q5 0 % · syx-scan 0
```

| Pieza | Tamaño (360 → 1440) | Interlineado | Peso | Tracking |
|---|---|---|---|---|
| Cabecera «Rédito» | +4 → +6 · 50,5 → 101 px | 54 → 105 | 300 | −0,04 em |
| Titular de abre | +3 → +5 · 37,9 → 75,8 px | 42 → 84 (1,11) | 300 | −0,03 em |
| Cita de tribuna (cursiva) | +2 → +4 · 28,4 → 56,8 px | 36 → 70 (1,27 → 1,23) | 300 | −0,02 em |
| Titular de pieza | +1½ · 24,6 → 27,7 px | 30 → 35 (1,22 → 1,26) | 400 | −0,015 em |
| Entradilla (cursiva) | +1 · 21,3 → 24 px | 30 → 35 | 300 | 0 |
| Cuerpo | 16 → 18 px | 24 → 28 | 400 (380 en oscuro) | 0 |
| Rótulo, firma, datos | −½ · 13,9 → 15,6 px | u | 500 | +0,02 em |

---

## Versión anterior (v1)

# GRID SPEC — Rédito (portada de prueba de Ticker v0.3)

```
Contexto       : web mobile first · diario económico ficticio · texto + datos · expresividad editorial (canónica)
Tipografía     : cuerpo Ticker Regular (x 0,53, char 0,4422 em con el texto real) · 16 → 18 px / 1,5 · medida 32,795 em
Densidad       : uso reading · densidad default · razón de cadena 2
Cadena         : micro 4 · inner 6→8 · padding 12→14 · gutter 16→28 · margen 16→120 · sección 96→112 (= 4u) px
Retícula base  : layout-grid de SYX · 12 columnas · gutter clamp(1rem, 0.75rem + 1.1111vw, 1.75rem)
                 · margen clamp(1rem, -1.1667rem + 9.6296vw, 7.5rem) · máx. 90rem · filas auto
Proporciones   : principal 8 : lateral 4 (2:1) desde 64em · piezas 2 por fila desde 48em y 3 desde 80em
                 (cards/row de compose) · escala tipográfica 1,25 (heading-steps 7)
Operadores     : ninguno (canónica)
Invariantes    : medida de 71 caracteres reales; interlineados en múltiplos de u/4; filetes de 1 y 3 px
Ruptura        : ninguna
Validación     : C1–C13 (ver abajo) · Q 13/16
```

## De dónde sale cada número

| Valor | Comando |
|---|---|
| char 0,4422 em, line box 0,978/0,272 (igual en web y Windows), cifras tabulares 0,536 em | `gridcalc font fonts/ticker-v1.woff2 --sample datos/textos.txt --lang es --save` |
| interlineado 1,5, u 24→28, cadena, columnas en uso, tarjetas por fila, escala de titulares | `gridcalc compose --font fonts/ticker-v1.woff2 --sample datos/textos.txt --use reading --max 1440 --heading-steps 7` |
| medida 32,795 em (media 71 car., la más larga 74) | `gridcalc lines --typeface fonts/ticker-v1.woff2 --sample datos/textos.txt --measure 71` |
| todos los `clamp()` de letra e interlineado (360 → 1440 px) | `gridcalc clamp --min … --max … --vmin 360 --vmax 1440` |

| Pieza | Tamaño | Interlineado | Paso |
|---|---|---|---|
| Cabecera «Rédito» | 39,1 → 85,8 px | 42 → 84 | +4 → +7 |
| Titular de abre | 31,3 → 68,7 px | 30 → 70 | +3 → +6 |
| Rótulo de sección | 25 → 35,2 px | 24 → 35 | +2 → +3 |
| Entradilla (cursiva) | 20 → 28,1 px | 30 → 42 | +1 → +2 |
| Titular de pieza | 20 → 22,5 px | 24 → 28 | +1 |
| Cuerpo | 16 → 18 px | 24 → 28 (1,5) | 0 |

Valores de oficio, fuera de la retícula: tracking de la cabecera −0,02 em y del antetítulo +0,04 em; ancho mínimo de cada dato de cierre 10rem (≥ el dato más largo, «tipos a 12 meses 2,21 % cae», ≈ 9,2rem a 0,8 em).

## Transformación

| Rango | Columnas en uso | Cambio estructural |
|---|---|---|
| < 48em | 1 (spans de 12) | todo apilado; la franja de cierre se reparte sola (auto-fill, mínimo 10rem) |
| 48–64em | 2 en piezas | piezas de 6 + 6 |
| 64–80em | 8 + 4 | abre en 8, lateral en 4 |
| ≥ 80em | 8 + 4 · piezas de 4 | tres piezas por fila |

Margen y gutter son continuos (un `clamp()` por token, igualando los cinco escalones `--layout-pad-*` y `--layout-gap-*` de SYX).

## Validación (Chrome 1.63 / Playwright, barrido 320 → 1600 px en pasos de 8)

| # | Resultado |
|---|---|
| C1 | ✓ cada valor sale de un comando gridcalc o de un token de SYX (excepciones de oficio declaradas arriba) |
| C2 | ✓ sin desbordamiento horizontal en ningún ancho |
| C3 | ✓ orden visual = orden del DOM (sin `order` ni colocación) |
| C4 | ✓ filas `auto`, sin altura fija |
| C5 | ✓ desde 376 px: líneas llenas de 47–74 caracteres de media, la más larga 75 (≤ 80). **Excepción declarada:** de 320 a ~350 px la media baja a 39 caracteres; llegar a 45 exigiría un cuerpo menor de 16 px |
| C6 | ✓ columna en uso / gutter ≥ 11,6 (la pista suelta de 12 en móvil mide 0,58, pero allí solo se usan spans de 12) |
| C7 | ✓ objetivo mínimo 40 px (enlaces de sección 44 px) |
| C8 · C9 | no aplican (pantalla) |
| C10 | ✓ medida en em × char_em medido con el texto real |
| C11 | ✓ micro < inner < padding < gutter ≤ margen < sección en todo el rango |
| C12 | ✓ todo espacio vertical en u, u/2, u/4 o `lh` |
| C13 | ✓ métricas leídas del archivo (perfil con SHA-1 c3a5df60a3); aviso abierto: idioma no cubierto (faltan glifos del español), que es la limitación de Ticker v0.3 |

Calidad: Q1 2 · Q2 2 · Q3 2 · Q4 2 · Q5 2 · Q6 0 (sin ruptura, por diseño) · Q7 2 · Q8 1 (solo pantalla) → **13/16**.
