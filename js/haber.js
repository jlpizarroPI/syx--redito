/* Rédito · comportamiento de la portada (sin dependencias).
   1. modo oscuro (data-theme), 2. barra fija con sombra al desplazar (.is-scrolled de
   org-site-header), 3. escala de los gráficos (--k = unidades del viewBox por px reales,
   para que texto y marcas midan lo mismo a cualquier ancho), 4. cruz de lectura de los
   gráficos de línea (ratón, tacto y teclado: flechas, Inicio, Fin), 5. el formulario de
   ejemplo no envía nada. Los textos de las burbujas se escriben con textContent. */
(function () {
  'use strict';
  var raiz = document.documentElement;

  // 1 · modo oscuro
  var boton = document.querySelector('[data-haber-modo]');
  function oscuro() {
    var t = raiz.getAttribute('data-theme');
    return t ? t === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  function pintarModo() {
    if (!boton) return;
    var o = oscuro();
    boton.setAttribute('aria-pressed', String(o));
  }
  if (boton) {
    boton.addEventListener('click', function () {
      raiz.setAttribute('data-theme', oscuro() ? 'light' : 'dark');
      pintarModo();
    });
    pintarModo();
  }

  // 1b · tamaño del texto: normal → 112,5 % → 125 %; se recuerda en este navegador
  var letra = document.querySelector('[data-haber-letra]');
  var NOMBRES = ['normal', 'grande', 'muy grande'];
  function ponerLetra(n) {
    if (n) raiz.setAttribute('data-letra', String(n)); else raiz.removeAttribute('data-letra');
    var estado = letra && letra.querySelector('[data-haber-letra-estado]');
    if (estado) estado.textContent = ', tamaño del texto: ' + NOMBRES[n];
  }
  var guardada = 0;
  try { guardada = parseInt(localStorage.getItem('redito-letra') || '0', 10) || 0; } catch (e) {}
  ponerLetra(Math.min(2, Math.max(0, guardada)));
  if (letra) {
    letra.addEventListener('click', function () {
      var n = ((parseInt(raiz.getAttribute('data-letra') || '0', 10) || 0) + 1) % 3;
      ponerLetra(n);
      try { localStorage.setItem('redito-letra', String(n)); } catch (e) {}
    });
  }

  // 2 · barra fija
  var barra = document.querySelector('.org-site-header');
  if (barra) {
    var marca = document.querySelector('.haber-marca');
    var umbral = function () { return marca ? marca.offsetHeight : 0; };
    var alDesplazar = function () { barra.classList.toggle('is-scrolled', window.scrollY > umbral()); };
    window.addEventListener('scroll', alDesplazar, { passive: true });
    alDesplazar();
  }

  // 3 · escala de los gráficos
  var graficos = document.querySelectorAll('svg.haber-graf');
  function escalar(svg) {
    var vb = svg.viewBox.baseVal, w = svg.getBoundingClientRect().width;
    if (vb && w) svg.style.setProperty('--k', (vb.width / w).toFixed(4));
  }
  if ('ResizeObserver' in window) {
    var ro = new ResizeObserver(function (es) { es.forEach(function (e) { escalar(e.target); }); });
    graficos.forEach(function (s) { ro.observe(s); });
  } else {
    graficos.forEach(escalar);
  }

  // 4 · cruz de lectura
  document.querySelectorAll('svg[data-haber-linea]').forEach(function (svg) {
    var d = JSON.parse(svg.getAttribute('data-haber-linea'));
    var cruz = svg.querySelector('.haber-graf__cruz');
    var linea = cruz.querySelector('.haber-graf__cruz-linea');
    var punto = cruz.querySelector('.haber-graf__cruz-punto');
    var burbuja = cruz.querySelector('.haber-graf__burbuja');
    var caja = burbuja.querySelector('rect');
    var tv = burbuja.querySelector('.haber-graf__burbuja-valor');
    var tf = burbuja.querySelector('.haber-graf__burbuja-fecha');
    var vb = svg.viewBox.baseVal;
    var actual = d.x.length - 1;

    function mostrar(i) {
      actual = Math.max(0, Math.min(d.x.length - 1, i));
      var x = d.x[actual], y = d.y[actual];
      var k = parseFloat(getComputedStyle(svg).getPropertyValue('--k')) || 1;
      linea.setAttribute('x1', x); linea.setAttribute('x2', x);
      punto.setAttribute('cx', x); punto.setAttribute('cy', y);
      tv.textContent = d.v[actual];
      tf.textContent = d.f[actual];
      var pad = 8 * k, ancho = Math.max(tv.getComputedTextLength(), tf.getComputedTextLength()) + 2 * pad;
      var alto = 44 * k;
      var bx = x + 12 * k + ancho > vb.width - 64 ? x - 12 * k - ancho : x + 12 * k;
      var by = Math.max(0, Math.min(y - alto - 10 * k, vb.height - alto - 30));
      if (by < 0) by = y + 10 * k;
      caja.setAttribute('x', bx); caja.setAttribute('y', by);
      caja.setAttribute('width', ancho); caja.setAttribute('height', alto);
      tv.setAttribute('x', bx + pad); tv.setAttribute('y', by + 19 * k);
      tf.setAttribute('x', bx + pad); tf.setAttribute('y', by + 35 * k);
      svg.classList.add('is-leyendo');
    }
    function ocultar() { svg.classList.remove('is-leyendo'); }
    function indice(ev) {
      var p = svg.createSVGPoint(); p.x = ev.clientX; p.y = ev.clientY;
      var q = p.matrixTransform(svg.getScreenCTM().inverse());
      var mejor = 0, dist = Infinity;
      d.x.forEach(function (x, i) { var dd = Math.abs(x - q.x); if (dd < dist) { dist = dd; mejor = i; } });
      return mejor;
    }
    svg.addEventListener('pointermove', function (ev) { mostrar(indice(ev)); });
    svg.addEventListener('pointerdown', function (ev) { mostrar(indice(ev)); });
    svg.addEventListener('pointerleave', ocultar);
    svg.addEventListener('focus', function () { mostrar(actual); });
    svg.addEventListener('blur', ocultar);
    svg.addEventListener('keydown', function (ev) {
      var paso = { ArrowLeft: -1, ArrowRight: 1, ArrowDown: -1, ArrowUp: 1 }[ev.key];
      if (paso) { mostrar(actual + paso); ev.preventDefault(); }
      if (ev.key === 'Home') { mostrar(0); ev.preventDefault(); }
      if (ev.key === 'End') { mostrar(d.x.length - 1); ev.preventDefault(); }
    });
  });

  // 5 · formularios de ejemplo
  document.querySelectorAll('form[action^="#"]').forEach(function (f) {
    f.addEventListener('submit', function (ev) { ev.preventDefault(); });
  });
})();
