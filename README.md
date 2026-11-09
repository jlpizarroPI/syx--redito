# Rédito · Diario de mercados

Prototipo de portada de un diario económico digital, construido sobre el sistema de diseño **SYX v5.1**. Usa Newsreader para el texto y **Hito**, una letra propia, solo para las cifras de mercado.

Lo que lo distingue es que **cada decisión de maquetación contra la fatiga de lectura está respaldada por un estudio**. Este README cuenta cuál, qué dice y cómo se ha traducido a código.

> Estado: prototipo (v0.5). Datos, noticias y anunciantes son ficticios. Las ilustraciones están generadas por código.

---

## Índice

1. [Arranque rápido](#arranque-rápido)
2. [Estructura del proyecto](#estructura-del-proyecto)
3. [Arquitectura SCSS](#arquitectura-scss)
4. [Tipografía](#tipografía)
5. [Publicidad trazable y sticky de carril](#publicidad-trazable-y-sticky-de-carril)
6. [Reglas contra la fatiga, de un vistazo](#reglas-contra-la-fatiga-de-un-vistazo)
7. [Por qué: la psicología detrás de cada decisión](#por-qué-la-psicología-detrás-de-cada-decisión)
8. [Lo que la ciencia no dice](#lo-que-la-ciencia-no-dice)
9. [Ideas para contarlo](#ideas-para-contarlo)
10. [Verificación](#verificación)
11. [Créditos y licencias](#créditos-y-licencias)
12. [Fuentes](#fuentes)

---

## Arranque rápido

```bash
npm install            # instala sass (dev) y syx-design-system
npm run build          # scss → css/haber.css → index.html → dist/index.html
npm run servir         # http://127.0.0.1:8765 (los módulos JS no cargan desde file://)
```

| Script | Qué hace |
|---|---|
| `npm run css` | Compila `scss/haber.scss` en `css/haber.css` |
| `npm run css:vigilar` | Igual, recompilando en cada cambio |
| `npm run html` | Monta `index.html` desde `index.src.html` y `datos/menu.py` |
| `npm run dist` | Genera `dist/index.html`, un único archivo autónomo de unos 1,1 MB con fuentes e imágenes incrustadas |
| `npm run scan` | `syx-scan` sobre `index.html` y **todos los parciales SCSS** (la fuente es lo que se audita) |
| `npm run pub` | Prueba del sistema de publicidad: atributos `data-pub`, carril sticky, impresión MRC y eventos |
| `npm run vertical` | Auditoría vertical: líneas base compartidas (sonda) y controles centrados en las mayúsculas (tinta real a 4×) |
| `npm run alinear` | Auditoría de alineación: los bordes de inicio o fin de cada bloque caen en una línea de columna |
| `npm run medir` | Barrido de 320 a 1600 px con las comprobaciones de retícula, CLS y publicidad |
| `npm run capturas` | Capturas de móvil, tableta, escritorio y móvil oscuro en `datos/` |

Para `medir` y `capturas` hacen falta Python 3 y Playwright, y el servidor en marcha.

---

## Estructura del proyecto

```
rédito/
├── index.src.html        plantilla con marcadores {{NAV}}, {{GRAF:x}}, {{IMG:x}}…
├── index.html            generado (npm run html)
├── dist/index.html       generado, autónomo: es lo que se publica
├── scss/                 ← fuente de estilos (ver abajo)
├── css/haber.css         generado (npm run css); no editar a mano
├── js/
│   ├── haber.js          modo oscuro, control «Aa», cruz de lectura de los gráficos
│   ├── redito-pub.js     publicidad: estado, pegado, visibilidad MRC y eventos (data-pub-*)
│   ├── syx-site-nav.js   copiado de SYX (cabecera, cajón)
│   └── syx-tabs.js       copiado de SYX (pestañas)
├── fonts/                Newsreader (OFL) y Hito v0.5 en woff2
├── img/                  ilustraciones en duotono, en WebP de 480, 800 y 1200 px
├── datos/
│   ├── menu.py           arquitectura de la información: una sola fuente para nav, cajón, megamenú y pie
│   ├── graficos.py       datos ficticios a graficos.json
│   ├── imagenes.py       genera las ilustraciones
│   ├── montar.py         index.src.html a index.html
│   ├── autonomo.py       index.html a dist/index.html
│   ├── medir.py          comprobaciones C2 · C5 · C6 · C7 · Q5 · CLS · publicidad
│   ├── capturas.py       capturas en cuatro vistas
│   ├── comparar_css.py   compara dos CSS por equivalencia
│   ├── pub.py            prueba de publicidad (sticky, MRC, eventos, sin sticky en móvil)
│   ├── alinear.py        auditoría de alineación contra las líneas de columna
│   ├── vertical.py       auditoría vertical: línea base y centro óptico (tinta)
│   └── partir_scss.py    registro de cómo se partió el CSS original (se ejecutó una vez)
├── GRID-SPEC.md          especificación de la retícula (gridcalc)
├── AGENTS.md / CLAUDE.md reglas de SYX para agentes
└── SYX-VOCABULARY.md     vocabulario de clases y tokens de SYX
```

---

## Arquitectura SCSS

### Principios

1. **Primero SYX.** Rédito no repinta componentes de SYX. Cuando necesita otro aspecto, escribe los tokens del componente en su propio contenedor; por ejemplo, `--component-button-font-family` en la barra. Cada bloque propio lleva encima un comentario `/* syx-reuse: checked … — por qué no sirve */` que deja constancia de qué se consultó en SYX.
2. **Mixins de SYX para posición y movimiento.** Los parciales usan `@use "syx-design-system/scss/abstracts/mixins/mixins" as syx;` (por eso `sass` se llama con `--load-path=node_modules`). `@include syx.transition(…)` emite la transición y su salida de `prefers-reduced-motion`, y `@include syx.sticky(…)` deja el posicionamiento declarado como deliberado.
3. **Los tokens son propiedades personalizadas de CSS, no variables de Sass.** El modo oscuro, el tamaño de letra del lector y el contraste alto cambian en el navegador, en tiempo de ejecución. Si fueran variables de Sass quedarían congeladas al compilar. Sass se usa solo para lo que sí se decide al compilar: puntos de corte, mixins y organización.
4. **Mobile first.** Solo hay `min-width`. Los puntos de corte viven en un único mapa: `abstracts/_puntos.scss`.
5. **El orden de `haber.scss` es la cascada.** Los parciales se cargan con `meta.load-css()` en el orden exacto del documento. Reordenar cambia el resultado.
6. **Capas.** Todo lo de la aplicación va en `@layer syx.app`, entre los organismos y las utilidades de SYX. Solo las fuentes y los tokens quedan fuera de capa, porque tienen que ganar a los valores por defecto de SYX.

### Árbol

```
scss/
├── haber.scss                    punto de entrada: orden de capas + orden de carga
│
├── abstracts/                    herramientas; no emiten CSS
│   ├── _index.scss               @forward de todo lo de abajo
│   ├── _puntos.scss              $puntos (md 48em · lg 64em · xl 80em), desde(), entre()
│   └── _preferencias.scss        sin-movimiento (prefers-reduced-motion)
│
├── base/
│   ├── _fuentes.scss             @font-face: Newsreader + «Hito Cifras» (unicode-range)
│   └── _base.scss                cuerpo, rótulos, titulares, firma            [syx.app]
│
├── tokens/                       fuera de capa
│   ├── _syx.scss                 sobrescritura de tokens semánticos: claro · oscuro del sistema · oscuro elegido
│   ├── _proyecto.scss            tokens --haber-*: medidas de gridcalc, ritmo, pesos, colores de gráfico
│   └── _preferencias.scss        data-letra (control «Aa») y prefers-contrast: more
│
├── componentes/                  piezas reutilizables dentro de la portada    [syx.app]
│   ├── _marca.scss               cabecera de marca (≥ 64em)
│   ├── _barra.scss               barra fija: org-site-header, cajón, megamenús, búsqueda
│   ├── _secciones-temas.scss     filas de secciones y temas con desplazamiento horizontal
│   ├── _fichas.scss              fichas de mercado (stat tile + sparkline)
│   ├── _graficos.scss            gráficos SVG: línea, columnas, divergente, cruz de lectura
│   ├── _publicidad.scss          huecos publicitarios rotulados con aspect-ratio
│   ├── _boletines.scss           formulario de boletines
│   └── _lectura.scss             «Las claves» y tiempo de lectura
│
├── zonas/                        franjas de la portada, en orden de aparición [syx.app]
│   ├── _entrada.scss             5 · apertura (N1 + N2 + Lo último), sin publicidad
│   ├── _secciones.scss           ritmo común de las secciones
│   ├── _mercados.scss            6 · banda densa de mercados
│   ├── _desarrollo.scss          7 · tarjetas con imagen y lateral
│   ├── _opinion.scss             8 · bloque de respiro
│   ├── _profundidad.scss         9 · Empresas y Tecnología
│   └── _pie.scss                 pie con el índice completo
│
└── utilidades/
    └── _movimiento-foco.scss     movimiento reducido, foco visible, ::selection
```

`componentes/` frente a `zonas/`: un componente se puede mover de sitio sin romperse. Una zona describe una franja concreta de la portada y depende de su posición en la página (atlas SYX 06.2).

### Centrado óptico: `.haber-optico`

SYX centra casillas, iconos y botones en la **caja de línea** del texto. Con Newsreader, que tiene ascendentes muy altos, esa caja no está centrada en las mayúsculas, y el texto queda más alto que su control: medido con la tinta real, entre 1,3 y 3 px en las casillas del boletín.

La corrección no usa números mágicos ni repinta clases de SYX. Basta envolver el texto en un elemento propio:

```html
<span class="atom-check__label"><span class="haber-optico">La apertura, cada mañana</span></span>
```

```scss
.haber-optico { display: block; text-box: trim-both cap alphabetic; }
```

Así la caja del texto va exactamente de la línea base a la altura de las mayúsculas, y cualquier centrado (flex, botón) cae en el centro óptico. Se usa en las casillas, la marca de la barra, la navegación, «Buscar», «Aa» y «Suscríbete».

Los iconos de lucide se dimensionan a `1cap × 1,2`, porque su trazo ocupa 20/24 del cuadro, centrado. Así la lupa y la luna miden lo mismo que las mayúsculas vecinas. Resultado: todo queda a menos de 0,62 px del centro de las mayúsculas, en 5 anchos y en los dos modos (la medición tiene una resolución de 0,25 px).

### Puntos de corte

```scss
@use "../abstracts" as *;

.haber-tarjeta {
  // móvil: fila compacta (por defecto)
  @include desde(md) { /* ≥ 48em: tarjeta con subgrid */ }
}

.haber-nav {
  @include entre(md, xl) { /* 48em – 79,99em */ }
}
```

Un nombre que no existe en el mapa detiene la compilación con un `@error` que lista los válidos.

> **Cuidado con los nombres.** En `layout-grid` de SYX, las clases `col-lg-*` se ponen lado a lado desde **80em**. En el mapa de Rédito ese punto se llama **`xl`**, porque nuestro `lg` (64em) es donde aparece la marca. Cualquier regla que dependa de que el lateral esté **al lado** (el carril publicitario, por ejemplo) va en `desde(xl)`.

### Añadir un parcial

1. Créalo en `componentes/` o en `zonas/`, con un comentario de una línea arriba que diga qué es.
2. Si usa puntos de corte, pon `@use "../abstracts" as *;` al principio.
3. Encima de su primera regla, escribe el comentario `syx-reuse`.
4. Añádelo a `haber.scss` en el punto de la cascada que le toque.
5. Ejecuta `npm run css && npm run scan`. El escaneo tiene que dar 0 hallazgos.

`syx-scan` se pasa sobre **la fuente**: `index.html` y todos los parciales. Hoy da 0 hallazgos. Cada parcial lleva su propio `syx-reuse` o `syx-reuse-file`, porque el escáner lee archivo por archivo. Sobre el CSS compilado solo quedan avisos leves de `position: sticky`, que vienen del mixin de SYX.

---

## Tipografía

| Uso | Letra | Detalle |
|---|---|---|
| Texto y titulares | **Newsreader** (Production Type, OFL) | Ejes `opsz` y `wght`. Cuerpo de 18 a 20 px, interlineado de 1,556 y medida de 31,3 em. Titular a 400 con opsz 72 |
| Cifras de mercado | **Hito Cifras** (propia, v0.5) | `unicode-range` limitado a 0–9, + − % , y . con `size-adjust` del 94,9 %. El navegador solo descarga Hito cuando aparece una cifra |
| Rótulos | Newsreader en versalitas espaciadas | — |

Las medidas salen de `gridcalc` (skill de retícula) aplicado al archivo de Newsreader, peso a peso. Ver `GRID-SPEC.md`.

---

## Publicidad trazable y sticky de carril

### Qué se pega y qué no

| Bloque | `data-pub-sticky` | Por qué |
|---|---|---|
| Robapáginas 300 × 250 (lateral de Economía) | `carril`, desde `xl` (80em) | Se pega **dentro de su columna** mientras se lee la zona (unos 650 a 690 px de recorrido) y se suelta al final. No tapa contenido |
| Faldón 970 × 90 · 728 × 90 · 320 × 50 | `no` | Está entre dos zonas: pegarlo taparía el contenido. El atlas 06.3 §5 lo prohíbe salvo acuerdo con negocio y con cierre al desplazar |
| Patrocinado (molde N3) | `no` | Es una pieza de contenido marcada como «Publicidad» |
| Cualquier bloque en **móvil y tableta** | — | El atlas 06.3 §14 pide reducir el impacto en móvil. Además, el lateral está apilado y no hay carril |

**Por qué cumple las reglas.**
- **CP-01 de SYX:** nada de `absolute` ni `fixed`. `position: sticky` mantiene el bloque como hijo de la retícula, con su hueco reservado, y no provoca saltos de maquetación (CLS 0,0001).
- **Better Ads Standards:** consideran inaceptables los anuncios pegajosos grandes, los que ocupan más del 30 % de la pantalla. Un 300 × 250 en el lateral ocupa alrededor del 6 % del área de una pantalla de 1440 × 900.
- **Pantallas bajas:** el sticky solo se activa si la ventana mide al menos 36rem de alto. Por debajo, no se pega.
- **Móvil:** el robapáginas sube al principio de la zona, tras su cabecera (solo cambia el orden visual). Así no queda pegado al faldón (§7) ni entre dos noticias (§5).

### El contrato en el HTML

```html
<div class="haber-pub-carril" data-pub-carril>
  <div class="haber-anuncio haber-anuncio--robapaginas" role="complementary" aria-label="Publicidad"
       data-pub="robapaginas" data-pub-id="rdt-portada-lat-1" data-pub-formato="300x250"
       data-pub-zona="desarrollo" data-pub-posicion="1"
       data-pub-sticky="carril" data-pub-sticky-desde="xl" data-pub-estado="reservado">
    <p class="haber-anuncio__etiqueta">Publicidad</p>
    <div class="haber-anuncio__hueco" data-formato="300 × 250"></div>
  </div>
</div>
```

| Atributo | Lo escribe | Para qué |
|---|---|---|
| `data-pub` | HTML | Tipo de bloque: `robapaginas`, `faldon` o `patrocinado` |
| `data-pub-id` | HTML | Identificador único y estable del hueco: lo usan el servidor de anuncios, la analítica y las pruebas |
| `data-pub-formato` | HTML | Formato IAB. Si cambia con el ancho, va por punto de corte: `320x50 md:728x90 lg:970x90` |
| `data-pub-zona`, `data-pub-posicion` | HTML | Zona del atlas 06.2 y orden en la página (3 como máximo) |
| `data-pub-anunciante` | HTML | Solo en el patrocinado |
| `data-pub-sticky`, `data-pub-sticky-desde` | HTML | Modo (`carril` o `no`) y punto de corte. El pegado es **CSS puro**: el SCSS genera un selector por cada punto del mapa con `@each $puntos` |
| `data-pub-estado` | JS | `reservado` → `en-vista` → `visible` (impresión visible según el MRC) |
| `data-pub-pegado` | JS | `true` mientras el carril lo mantiene pegado |

### Eficiencia

- **No hay ningún listener de `scroll`.** Un solo IntersectionObserver vigila todos los bloques. El pegado lo hace el navegador con `position: sticky`: el JS no toca la maquetación.
- **El pegado se detecta con dos centinelas de alto cero**, uno encima del anuncio y otro al final del carril, observados con `root: document`. Así funcionan también dentro de un iframe de otro origen, como el visor del artefacto, y con saltos bruscos de desplazamiento.
- **Impresión visible según el MRC:**
  - el 50 % de los píxeles a la vista durante 1 s continuo (el 30 % en anuncios de 242.500 px² o más);
  - el reloj se para si la pestaña pasa a segundo plano.

### Trazabilidad

Cada cambio emite un `CustomEvent("redito:pub")` en `document` y, si existe, un `push` a `window.dataLayer`:

```js
{ evento: "redito_pub_impresion_visible", pub_id: "rdt-portada-lat-1", pub_tipo: "robapaginas",
  pub_formato: "300x250", pub_zona: "desarrollo", pub_posicion: 1, umbral: 0.5, ms: 1000 }
```

| Evento | Cuándo |
|---|---|
| `redito_pub_listos` | Al iniciar, con el total de bloques y sus ids |
| `redito_pub_impresion_visible` | Cuando se cumple el criterio MRC |
| `redito_pub_pegado` / `redito_pub_despegado` | Al entrar y salir del pegado en el carril |
| `redito_pub_resumen` | Al salir de la página (`pagehide`), por hueco: estado final, `vista_ms` y `pegado_ms` |

**Depuración:** con `?pub-depurar` en la URL, o el atributo `data-pub-depurar` en `<html>`, cada bloque muestra su id, su estado y si está pegado.

---

## Reglas contra la fatiga, de un vistazo

| # | Regla | Evidencia principal | Cómo se aplica en Rédito |
|---|---|---|---|
| 1 | Lo esencial, en el titular y las primeras líneas | Weinreich et al. 2008; Nielsen 2008, 2018 | Pirámide invertida; entradilla que resume la noticia |
| 2 | «Las claves» arriba | Cowan 2001; Ackerman y Goldsmith 2011 | Tres viñetas bajo la firma de la apertura |
| 3 | Bloques cortos con rótulo | Pernice 2017 (patrón F); Pirolli y Card 1999 | Cada sección con rótulo; textos de tarjeta de 74 caracteres por línea como máximo |
| 4 | Cifras en gráficos, no en párrafos | Carga cognitiva (Sweller 1988) | Sparklines, líneas y columnas, cada uno con su tabla equivalente |
| 5 | Tiempo de lectura visible | Pirolli y Card 1999; Brysbaert 2019 | Clase `.haber-lectura` en la apertura y en las 10 piezas, en cifras Hito y sin cortes de línea |
| 6 | El móvil baja menos | Nielsen 2018; Haile 2014 | Módulo vertical de 28 px en móvil y 32 px en escritorio; secciones 3/4u en móvil y 5/7u desde 64em |
| 7 | Letra grande y ajustable | Rello, Pielot y Marcos 2016 | Cuerpo de 18 a 20 px; control «Aa» al 100, 112,5 o 125 % que recuerda la elección |
| 8 | Medida contenida | Dyson y Haselgrove 2001 | Entre 47 y 73 caracteres de media por línea |
| 9 | Claro por defecto; oscuro opcional | Piepenbrock, Mayr y Buchner 2013, 2014 | Fondo marfil por defecto; el modo oscuro es una elección del lector |
| 10 | Contraste y movimiento a demanda | Sheppard y Wolffsohn 2018 | `prefers-contrast: more` y `prefers-reduced-motion` |
| 11 | Publicidad honesta y apartada | Benway y Lane 1998 | Tres bloques como máximo, ninguno en la apertura ni seguidos, siempre rotulados «Publicidad» |
| 12 | Color apto para daltónicos | Birch 2012 | Subidas en azul y bajadas en teja, nunca verde y rojo |

---

## Por qué: la psicología detrás de cada decisión

### 1. En pantalla no leemos: escaneamos y recolectamos

**El estudio.** Weinreich, Obendorf, Herder y Mayer registraron durante meses la navegación real de 25 personas, sin tareas impuestas. Concluyeron que se navega deprisa incluso en páginas con mucho contenido, y que eso pide diseños pensados para una lectura somera. Jakob Nielsen reanalizó esos datos (unas 45.000 páginas vistas). Por cada 100 palabras más, la visita solo dura unos 4,4 segundos más. En una página media de 593 palabras da tiempo a leer como mucho el 28 %, y lo realista es alrededor del 20 %. Solo en páginas de 111 palabras o menos se llega a leer la mitad.

**La psicología.** La teoría del forrajeo de información (*information foraging*) de Pirolli y Card, de Xerox PARC, explica esa conducta. Buscamos información como un animal busca comida: maximizamos lo que ganamos por unidad de esfuerzo. Seguimos el «olor» de la información, que son las pistas cercanas, como títulos, rótulos o la disposición de la página, y abandonamos una «parcela» cuando deja de rendir.

**Qué hace Rédito.** Asume que se leerá el 20 % y decide **cuál** 20 % será: el titular, la entradilla y las claves. Los rótulos de sección y el tiempo de lectura son pistas de olor. Dicen qué hay y cuánto cuesta antes de que el lector invierta su atención.

### 2. La atención se gasta arriba

**El estudio.** En 2018, los estudios de seguimiento ocular de Nielsen Norman Group midieron que el 57 % del tiempo de mirada cae en la primera pantalla. La segunda recibe alrededor del 17 % y el resto se reparte en una cola larga. En 2010, la primera pantalla recibía el 80 %: hoy desplazamos más, pero la caída sigue siendo abrupta. Desde la industria, el análisis de Chartbeat sobre 2.000 millones de visitas (Tony Haile, *Time*, 2014) encontró que el 55 % de las páginas vistas recibe menos de 15 segundos de atención activa.

**La psicología.** Desplazar la página tiene un coste de interacción. Además, lo que queda arriba actúa de criba: el lector decide si sigue o no según lo que ve primero.

**Qué hace Rédito.** La apertura no lleva publicidad y concentra la jerarquía. En móvil, los respiros verticales son más cortos, para que bajar cueste menos. No por ello se meten más cosas en la primera pantalla.

### 3. La memoria de trabajo admite unas cuatro piezas: por eso las claves son tres

**El estudio.** Nelson Cowan revisó la literatura sobre memoria a corto plazo. El famoso «siete más o menos dos» de Miller (1956) era más una estimación aproximada y un recurso retórico que un límite real. La capacidad pura ronda **cuatro unidades** (*chunks*).

**Qué hace Rédito.** «Las claves» son tres frases de una idea cada una, con una cifra por frase como mucho. Caben en la memoria de trabajo y dejan margen para el titular.

### 4. En pantalla creemos haber entendido más de lo que entendemos

**Los estudios.**
- El metaanálisis de **Delgado, Vargas, Ackerman y Salmerón (2018)**, de la Universidad de Valencia, reúne 54 estudios con más de 171.000 participantes. Encuentra una ventaja del papel sobre la pantalla en comprensión, con un efecto pequeño pero consistente: g de Hedges = −0,21. La ventaja **crece con prisa**, se da en textos informativos (no en narrativos) y **ha ido aumentando con los años**.
- **Ackerman y Goldsmith (2011)** dieron con el mecanismo. Con tiempo fijo, pantalla y papel rinden igual. Cuando cada uno gestiona su tiempo, la pantalla rinde peor, porque predecimos peor lo que vamos a recordar y regulamos el estudio de forma más errática. El problema no es cognitivo, es **metacognitivo**: exceso de confianza.

**Por qué importa en un diario económico.** Las noticias económicas son textos informativos y se leen con prisa, que es justo donde la desventaja de la pantalla es mayor.

**Qué hace Rédito.** «Las claves» funcionan como una autoevaluación implícita: si las tres frases no te dicen nada, no has entendido la noticia. El tiempo de lectura ayuda a calibrar el esfuerzo antes de empezar.

### 5. El tiempo de lectura como pista honesta

**El estudio.** El metaanálisis de **Marc Brysbaert (2019)**, con 190 estudios y unos 18.500 participantes, sitúa la lectura silenciosa de un adulto en inglés en **238 palabras por minuto** en no ficción. Es bastante menos que las 300 que se citan a menudo. La velocidad en otros idiomas se predice por cuántas palabras necesitan para decir lo mismo que el inglés.

**Qué hace Rédito.** Calcula el tiempo en el **peor caso**: minutos = palabras / 200, redondeando hacia arriba. Es mejor prometer 4 minutos y que sean 3 que al revés. En este prototipo las cifras son de ejemplo, porque los artículos no existen.

> Hipótesis de diseño, no resultado probado: que mostrar el tiempo reduzca el abandono no está demostrado en un estudio controlado que conozcamos. Se apoya en la teoría del olor de la información (punto 1). Merece una prueba A/B.

### 6. El tamaño de la letra importa más que el interlineado

**El estudio.** **Rello, Pielot y Marcos (CHI 2016)** midieron con seguimiento ocular legibilidad y comprensión en artículos de Wikipedia. Legibilidad y comprensión mejoraron de forma continua hasta 18 puntos (unos 24 px). Con 10 y 12 puntos la comprensión empeoró. El interlineado apenas influyó, salvo en valores extremos.

**Qué hace Rédito.** El cuerpo va de 18 a 20 px, más que los 16 px habituales en la prensa digital. El control «Aa» deja subir al 112,5 % o al 125 %, en una pulsación y sin tocar el navegador. Como todo va en `rem`, escala la página entera.

### 7. La medida de línea: un compromiso declarado

**El estudio.** **Dyson y Haselgrove (2001)** midieron que unos **55 caracteres por línea** favorecen la lectura eficaz en pantalla, tanto a velocidad normal como rápida. Leer deprisa reduce la comprensión.

**Qué hace Rédito.** Sus líneas tienen entre 47 y 73 caracteres de media. Rondan el óptimo de comprensión, pero se permiten algo más de densidad, como corresponde a un diario. No se ha cambiado la medida en esta versión porque ya estaba en rango.

### 8. Claro por defecto: el modo oscuro es una preferencia

**El estudio.** Un programa de investigación de la Universidad de Düsseldorf (**Buchner, Mayr y Piepenbrock**) encuentra una **ventaja de la polaridad positiva**: texto oscuro sobre fondo claro. Se lee y se corrige mejor, a cualquier edad. La explicación propuesta es óptica: la pantalla clara contrae la pupila y la imagen en la retina sale más nítida. La ventaja crece con letra pequeña.

**Qué hace Rédito.** El fondo marfil es el predeterminado. El modo oscuro existe porque hay quien lo prefiere o lee de noche, pero es una elección, no la norma. Tiene sus propios valores, no es una inversión automática de colores. En oscuro se sube ligeramente el grosor de la letra (`--haber-grado`) para compensar el efecto de irradiación.

### 9. La fatiga visual digital es mayoritaria

**El estudio.** La revisión de **Sheppard y Wolffsohn (2018)** estima que la fatiga visual digital, también llamada síndrome visual informático, puede afectar al **50 % o más** de los usuarios de ordenador. Los síntomas se agrupan en dos tipos: los del esfuerzo de enfoque y visión binocular, y los del ojo seco.

**Qué hace Rédito.** El diseño no puede curar el ojo seco, pero sí evitar sumar esfuerzo. Respeta `prefers-contrast: more`, que acerca el texto secundario al principal, y `prefers-reduced-motion`. Sus objetivos táctiles miden 24 px o más.

### 10. La ceguera a los banners y la publicidad honesta

**El estudio.** **Benway y Lane (1998)**, de la Universidad Rice, acuñaron el término *banner blindness*. Al buscar algo concreto, los usuarios pasaban por alto precisamente lo más llamativo: el banner que contenía la respuesta. El efecto aparecía tanto con banners gráficos como con textos destacados. Estudios posteriores lo matizan: depende de la tarea, y fuera de la navegación orientada el reconocimiento de anuncios es mayor (Bayles 2000).

**Qué hace Rédito.** Sigue la norma 06.3 del atlas SYX: tres bloques publicitarios como máximo, ninguno en la apertura, nunca dos seguidos, siempre rotulados «Publicidad» y con hueco reservado, sin saltos de página (CLS de 0,0001). El contenido patrocinado usa el mismo molde que una noticia, pero está **rotulado y marcado con `rel="sponsored"`**: la integración visual nunca oculta qué es.

### 11. Color para todos

**El estudio.** Según la revisión de **Birch (2012)**, la deficiencia de color rojo-verde afecta a cerca del **8 % de los hombres** de ascendencia europea y a menos del 0,5 % de las mujeres.

**Qué hace Rédito.** El validador de la skill dataviz dio una distancia de color ΔE de 3,8 al par verde/rojo en protanopía, que es ilegible. El par azul/teja da 22,1. Además, la subida y la bajada nunca dependen solo del color: llevan signo (+ / −) y la tabla de datos está disponible.

### 12. La atención sostenida decae, y es el lector quien lo nota

**La literatura.** El «decremento de vigilancia» es la caída del rendimiento con el tiempo dedicado a una tarea de atención sostenida, y está ampliamente replicado. Trabajos recientes (Zanesco et al. 2024a, 2024b; Schwartzman et al. 2025) lo asocian a un aumento de la mente errante a medida que avanza la tarea.

**Cautela.** Son tareas de laboratorio, no lectura de prensa: se citan como **analogía razonable**, no como prueba directa.

**Qué hace Rédito.** Alterna bandas densas (Mercados) con bloques de respiro (Opinión). Es la «alternancia de densidad» del atlas SYX 06.2, que da al lector un descanso cada pocos pantallazos.

---

## Lo que la ciencia no dice

Contarlo con honestidad lo hace más creíble:

- **Weinreich et al.** estudiaron a 25 personas con un nivel educativo alto, con datos de 2005. Nielsen sostiene que su conducta anticipa la del público general, pero es una muestra pequeña.
- **Chartbeat** son datos de la industria, no un estudio revisado por pares, aunque la muestra sea enorme.
- **El patrón F** no es una ley: es lo que ocurre **cuando no hay pistas visuales fuertes** (Pernice 2017). Un buen diseño lo evita, no lo explota.
- **El efecto papel frente a pantalla** es pequeño (g = −0,21). Importa porque es consistente y crece con la prisa, no porque sea dramático.
- **Que el tiempo de lectura reduzca el abandono** es una hipótesis. Habría que medirlo.
- **La ceguera a los banners** depende de la tarea; no es universal.

---

## Ideas para contarlo

Hilos que se pueden desarrollar en una publicación, cada uno con su dato:

1. **«Tus lectores van a leer el 20 %. Tú decides cuál.»** Weinreich/Nielsen, más la pirámide invertida y «Las claves».
2. **«En pantalla creemos haber entendido más de lo que entendemos.»** Ackerman y Goldsmith: el problema es metacognitivo, no visual. Por eso un resumen de tres líneas no es pereza, es calibración.
3. **«El número mágico no es 7, es 4.»** Cowan 2001 y por qué las claves son tres.
4. **«El modo oscuro no es más descansado.»** La ventaja de la polaridad positiva y por qué Rédito lo ofrece sin imponerlo.
5. **«Letra de 16 px es poca para leer.»** Rello et al.: la comprensión mejora hasta unos 24 px.
6. **«Verde sube, rojo baja… para el 92 % de los hombres.»** Birch 2012 y el par azul/teja.
7. **«Diseñar con evidencia también es decir lo que no sabes.»** La sección anterior como argumento de credibilidad.

---

## Verificación

Última pasada (v0.5, con la arquitectura SCSS):

| Comprobación | Resultado |
|---|---|
| CSS compilado frente a CSS original | Reglas equivalentes; capturas **idénticas píxel a píxel** en móvil, tableta, escritorio y móvil oscuro |
| C2 · desbordamiento horizontal de 320 a 1600 px (también con «Aa» al 125 %) | Ninguno |
| C5 · línea más larga en textos de tarjeta | 74 caracteres |
| C6 · columna en uso / calle mínima | 8,69 |
| C7 · objetivo táctil mínimo | 24 px |
| Q5 · mayor caída de columna al ensanchar | 0,03 % |
| CLS al cargar y al desplazar | 0,0001 |
| Publicidad | 3 bloques, 0 en la apertura, ninguno seguido (también en móvil, con el robapáginas al principio de la zona) |
| Carril sticky (`npm run pub`) | Pegado a 91–92 px, bajo la barra, en 1280 y 1440; se suelta al final; sin sticky por debajo de 80em ni en ventanas de menos de 36rem de alto; funciona dentro de un iframe de otro origen |
| Impresión MRC y eventos | `visible` tras 1 s; eventos en `document` y en `dataLayer` |
| Alineación vertical (`npm run vertical`) | 0 fuera de tolerancia (0,75 px) de 320 a 1440 px. Casillas, hamburguesa, lupa, luna y botones a ≤ 0,62 px del centro de las mayúsculas; líneas base compartidas en cabeceras, temas, fichas, «Lo último», pestañas y firma |
| Alineación (`npm run alinear`) | Bordes en línea de columna. Excepciones intencionadas: el panel patrocinado (su texto va dentro del relleno) y la etiqueta «Publicidad», centrada sobre la creatividad |
| Barra | Sin solapes de 1280 a 1920 px con el texto al 100, 112,5 y 125 %; con la letra ampliada, la navegación se retira hasta que cabe |
| `syx-scan` sobre la fuente | 0 hallazgos |

---

## Créditos y licencias

- **Newsreader**: Production Type, SIL Open Font License 1.1 (`fonts/newsreader-OFL.txt`).
- **Hito**: letra propia generada paramétricamente (proyecto `syx--typography`). Están pendientes la comprobación de marca y la licencia definitiva.
- **SYX v5.1**: sistema de diseño de base.
- **Ilustraciones**: generadas por código (`datos/imagenes.py`). No hay fotografías de terceros.
- **Datos, noticias, firmas y anunciantes**: ficticios.

---

## Fuentes

**Lectura en la web y atención**
- Weinreich, H., Obendorf, H., Herder, E. y Mayer, M. (2008). Not quite the average: An empirical study of Web use. *ACM Transactions on the Web*, 2(1), art. 5. https://doi.org/10.1145/1326561.1326566
- Nielsen, J. (2008). How little do users read? Nielsen Norman Group. https://www.nngroup.com/articles/how-little-do-users-read/
- Fessenden, T. (2018). Scrolling and attention. Nielsen Norman Group. https://www.nngroup.com/articles/scrolling-and-attention/
- Pernice, K. (2017). F-shaped pattern of reading on the web: Misunderstood, but still relevant (even on mobile). Nielsen Norman Group. https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/
- Haile, T. (2014). What you think you know about the web is wrong. *Time*. https://time.com/12933/what-you-think-you-know-about-the-web-is-wrong/
- Pirolli, P. y Card, S. (1999). Information foraging. *Psychological Review*, 106(4), 643–675. https://doi.org/10.1037/0033-295X.106.4.643

**Memoria, carga y metacognición**
- Cowan, N. (2001). The magical number 4 in short-term memory: A reconsideration of mental storage capacity. *Behavioral and Brain Sciences*, 24(1), 87–114. https://doi.org/10.1017/S0140525X01003922
- Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. *Cognitive Science*, 12(2), 257–285. https://doi.org/10.1207/s15516709cog1202_4
- Ackerman, R. y Goldsmith, M. (2011). Metacognitive regulation of text learning: On screen versus on paper. *Journal of Experimental Psychology: Applied*, 17(1), 18–32. https://doi.org/10.1037/a0022086
- Ackerman, R. y Lauterman, T. (2012). Taking reading comprehension exams on screen or on paper? A metacognitive analysis of learning texts under time pressure. *Computers in Human Behavior*, 28(5), 1816–1828. https://doi.org/10.1016/j.chb.2012.04.023
- Delgado, P., Vargas, C., Ackerman, R. y Salmerón, L. (2018). Don't throw away your printed books: A meta-analysis on the effects of reading media on reading comprehension. *Educational Research Review*, 25, 23–38. https://doi.org/10.1016/j.edurev.2018.09.003

**Velocidad de lectura y tipografía**
- Brysbaert, M. (2019). How many words do we read per minute? A review and meta-analysis of reading rate. *Journal of Memory and Language*, 109, 104047. https://doi.org/10.1016/j.jml.2019.104047
- Rello, L., Pielot, M. y Marcos, M.-C. (2016). Make it big! The effect of font size and line spacing on online readability. *Proceedings of CHI 2016*, 3637–3648. https://doi.org/10.1145/2858036.2858204
- Dyson, M. C. y Haselgrove, M. (2001). The influence of reading speed and line length on the effectiveness of reading from screen. *International Journal of Human-Computer Studies*, 54(4), 585–612.

**Visión y color**
- Piepenbrock, C., Mayr, S., Mund, I. y Buchner, A. (2013). Positive display polarity is advantageous for both younger and older adults. *Ergonomics*, 56(7), 1116–1124. https://doi.org/10.1080/00140139.2013.790485
- Piepenbrock, C., Mayr, S. y Buchner, A. (2014). Positive display polarity is particularly advantageous for small character sizes. *Human Factors*, 56(5), 942–951. https://doi.org/10.1177/0018720813515509
- Sheppard, A. L. y Wolffsohn, J. S. (2018). Digital eye strain: Prevalence, measurement and amelioration. *BMJ Open Ophthalmology*, 3(1), e000146. https://doi.org/10.1136/bmjophth-2018-000146
- Birch, J. (2012). Worldwide prevalence of red-green color deficiency. *Journal of the Optical Society of America A*, 29(3), 313–320. https://doi.org/10.1364/JOSAA.29.000313

**Publicidad**
- Media Rating Council (2015). *MRC Viewable Ad Impression Measurement Guidelines*, v2.0. https://mediaratingcouncil.org/sites/default/files/Standards/081815%20Viewable%20Ad%20Impression%20Guideline_v2.0_Final.pdf
- Coalition for Better Ads. *Better Ads Standards* (escritorio y móvil). Interpretación de Google: https://support.google.com/webtools/answer/7129127
- Benway, J. P. y Lane, D. M. (1998). Banner blindness: Web searchers often miss "obvious" links. *Internetworking*, ITG Newsletter, 1(3). Rice University.
- Bayles, M. (2000). Just how "blind" are we to advertising banners on the web? *Usability News*, 2(2). Software Usability Research Laboratory, Wichita State University.

**Atención sostenida**
- Zanesco, A. P., Denkova, E., Barry, J. y Jha, A. P. (2024a). Mind wandering is associated with worsening attentional vigilance. *Journal of Experimental Psychology: Human Perception and Performance*, 50, 1049–1066. https://doi.org/10.1037/xhp0001233
- Zanesco, A. P., Denkova, E. y Jha, A. P. (2024b). Mind-wandering increases in frequency over time during task performance: An individual-participant meta-analytic review. *Psychological Bulletin*, 150. https://doi.org/10.1037/bul0000424
- Schwartzman, B., Zanesco, A. P., Denkova, E., Tsukahara, J. S. y Jha, A. P. (2025). Examining the association between vigilance and mind wandering. *Frontiers in Cognition*. https://doi.org/10.3389/fcogn.2025.1577053
