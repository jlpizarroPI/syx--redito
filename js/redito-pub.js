/* Rédito · publicidad trazable — sticky de carril y visibilidad según el estándar MRC.
 *
 * El HTML lo declara todo con data-*; este módulo solo observa y anota:
 *
 *   data-pub              tipo de bloque: robapaginas · faldon · patrocinado
 *   data-pub-id           identificador único y estable del hueco (para el servidor de anuncios y analítica)
 *   data-pub-formato      formato IAB: «300x250», o por punto de corte: «320x50 md:728x90 lg:970x90»
 *   data-pub-zona         zona del atlas SYX 06.2 en la que vive
 *   data-pub-posicion     orden en la página (1…3; el atlas 06.3 permite 3 como máximo)
 *   data-pub-anunciante   solo en patrocinado
 *   data-pub-sticky       «carril» (se pega dentro de su columna) · «no»
 *   data-pub-sticky-desde punto de corte desde el que se pega (md · lg · xl); la regla es CSS puro
 *
 * Y escribe el estado, para estilos, depuración y pruebas:
 *
 *   data-pub-estado       reservado → en-vista → visible (impresión visible MRC cumplida)
 *   data-pub-pegado       true / false mientras el carril lo mantiene pegado
 *
 * Eficiencia: ningún listener de scroll. Un IntersectionObserver para todos los bloques y otro para los
 * centinelas de los carriles; el pegado lo hace el navegador con position: sticky (sin layout en JS).
 *
 * Trazabilidad: cada cambio emite un CustomEvent «redito:pub» en document y, si existe, un push en
 * window.dataLayer. Al salir de la página se emite el resumen (tiempo en vista y tiempo pegado por hueco).
 * Con data-pub-depurar en <html> (o ?pub-depurar en la URL) cada bloque enseña su id y su estado.
 */
(() => {
  'use strict';

  const bloques = [...document.querySelectorAll('[data-pub][data-pub-id]')];
  if (!bloques.length || !('IntersectionObserver' in window)) return;

  if (new URLSearchParams(location.search).has('pub-depurar')) {
    document.documentElement.setAttribute('data-pub-depurar', '');
  }

  // MRC Viewable Impression Guidelines: 50 % de los píxeles durante 1 s continuo, en una pestaña visible;
  // en anuncios de 242.500 px² o más, el 30 %.
  const MRC_MS = 1000;
  const MRC_GRANDE = 242500;
  const estado = new Map();   // elemento → { umbral, desde, vistaMs, temporizador, pegadoDesde, pegadoMs }

  const emitir = (el, tipo, extra = {}) => {
    const d = el.dataset;
    const detalle = {
      evento: 'redito_pub_' + tipo,
      pub_id: d.pubId, pub_tipo: d.pub, pub_formato: d.pubFormato, pub_zona: d.pubZona,
      pub_posicion: Number(d.pubPosicion), pub_anunciante: d.pubAnunciante || null,
      ...extra,
    };
    document.dispatchEvent(new CustomEvent('redito:pub', { detail: detalle }));
    if (Array.isArray(window.dataLayer)) window.dataLayer.push(detalle);
  };

  const umbralDe = (el) => {
    const r = el.getBoundingClientRect();
    return r.width * r.height >= MRC_GRANDE ? 0.3 : 0.5;
  };

  const pararReloj = (s) => {
    if (s.desde !== null) { s.vistaMs += performance.now() - s.desde; s.desde = null; }
    clearTimeout(s.temporizador); s.temporizador = null;
  };

  const vista = new IntersectionObserver((entradas) => {
    for (const e of entradas) {
      const el = e.target, s = estado.get(el);
      const dentro = e.intersectionRatio >= s.umbral && document.visibilityState === 'visible';
      if (dentro && s.desde === null) {
        s.desde = performance.now();
        if (el.dataset.pubEstado === 'reservado') el.dataset.pubEstado = 'en-vista';
        if (el.dataset.pubEstado !== 'visible') {
          s.temporizador = setTimeout(() => {
            el.dataset.pubEstado = 'visible';
            emitir(el, 'impresion_visible', { umbral: s.umbral, ms: MRC_MS });
          }, MRC_MS);
        }
      } else if (!dentro) {
        pararReloj(s);
        if (el.dataset.pubEstado === 'en-vista') el.dataset.pubEstado = 'reservado';
      }
    }
  }, { threshold: [0, 0.3, 0.5, 1] });

  // Pegado: dos centinelas de alto cero, uno justo encima del bloque y otro al final de su carril.
  // Está pegado cuando el de arriba ya ha cruzado la línea de pegado (su «top» calculado) y el de abajo
  // todavía no ha subido hasta el borde inferior del bloque pegado (si lo hace, el carril lo empuja).
  const vigilarCarril = (el, carril) => {
    const s = estado.get(el);
    const top = Math.ceil(parseFloat(getComputedStyle(el).top) || 0);
    const alto = Math.ceil(el.getBoundingClientRect().height);
    const centinela = (donde) => {
      const c = document.createElement('div');
      c.setAttribute('aria-hidden', 'true');
      c.setAttribute('data-pub-centinela', donde);
      return c;
    };
    const arriba = centinela('arriba'), abajo = centinela('abajo');
    el.before(arriba); carril.append(abajo);
    const pasado = { arriba: false, abajo: false };
    const decidir = () => {
      const valor = String(pasado.arriba && !pasado.abajo && getComputedStyle(el).position === 'sticky');
      if (el.dataset.pubPegado === valor) return;
      el.dataset.pubPegado = valor;
      if (valor === 'true') s.pegadoDesde = performance.now();
      else if (s.pegadoDesde !== null) { s.pegadoMs += performance.now() - s.pegadoDesde; s.pegadoDesde = null; }
      emitir(el, valor === 'true' ? 'pegado' : 'despegado');
    };
    // La raíz es el propio documento (root: document): así los márgenes se respetan también dentro de
    // un iframe de otro origen. Arriba se recorta hasta la línea; abajo se amplía muchísimo, para que
    // «fuera» solo pueda significar «ya ha pasado la línea» y un salto brusco también cruce el borde.
    const observar = (nodo, clave, margen) => new IntersectionObserver(([e]) => {
      pasado[clave] = !e.isIntersecting;
      decidir();
    }, { root: document, rootMargin: `-${margen}px 0px 100000px 0px` }).observe(nodo);
    observar(arriba, 'arriba', top + 1);
    observar(abajo, 'abajo', top + alto + 1);
    el.dataset.pubPegado = 'false';
  };

  for (const el of bloques) {
    estado.set(el, { umbral: umbralDe(el), desde: null, vistaMs: 0, temporizador: null, pegadoDesde: null, pegadoMs: 0 });
    vista.observe(el);
    const carril = el.closest('[data-pub-carril]');
    if (el.dataset.pubSticky === 'carril' && carril) vigilarCarril(el, carril);
  }

  // El formato cambia con el ancho (faldón): se recalcula el umbral MRC sin volver a observar.
  let pendiente = 0;
  addEventListener('resize', () => {
    cancelAnimationFrame(pendiente);
    pendiente = requestAnimationFrame(() => { for (const [el, s] of estado) s.umbral = umbralDe(el); });
  }, { passive: true });

  // Pestaña oculta: el reloj MRC se detiene (exige pestaña en primer plano).
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState !== 'visible') for (const s of estado.values()) pararReloj(s);
    else for (const el of bloques) { vista.unobserve(el); vista.observe(el); }   // reevalúa al volver
  });

  // Resumen al salir: tiempo en vista y tiempo pegado por hueco.
  addEventListener('pagehide', () => {
    for (const [el, s] of estado) {
      pararReloj(s);
      if (s.pegadoDesde !== null) { s.pegadoMs += performance.now() - s.pegadoDesde; s.pegadoDesde = null; }
      emitir(el, 'resumen', { estado: el.dataset.pubEstado, vista_ms: Math.round(s.vistaMs), pegado_ms: Math.round(s.pegadoMs) });
    }
  });

  const listos = { evento: 'redito_pub_listos', total: bloques.length, ids: bloques.map((b) => b.dataset.pubId) };
  document.dispatchEvent(new CustomEvent('redito:pub', { detail: listos }));
  if (Array.isArray(window.dataLayer)) window.dataLayer.push(listos);
})();
