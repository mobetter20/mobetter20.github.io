/* World Metros Atlas — prototype (D8 gate 2).
   Vanilla JS. Diagram mode inlines the unmodified Commons SVG and drives its
   viewBox (the D11 spike's approach); True Shape renders our OSM-derived
   per-city JSON (built by _scripts/world_metros/build_page_geometry.py). */
'use strict';

// ------------------------------------------------------------------ config

const CITIES = {
  seoul: {
    name: 'SEOUL', sub: 'SEOUL METROPOLITAN SUBWAY', opened: '1974',
    scopeNote: '2–9 · L1 scope: Method',
    diagram: {
      file: 'assets/seoul-diagram.svg', tappable: true,
      credit: '“Seoul Metropolitan Subway network map” by Satellizer, Wikimedia Commons, CC BY-SA 4.0',
      commons: 'https://commons.wikimedia.org/wiki/File:Seoul_Metropolitan_Subway_network_map.svg',
      license: 'CC BY-SA 4.0',
      sub: 'community recreation in the official idiom · bilingual · 2023 base',
      note: 'diagram dated 2023, future lines as then planned',
    },
    official: 'https://www.seoulmetro.co.kr',
    why: [
      '<b>why it’s here:</b> the densest reach of any metro on earth. The green Line 2 loop orbits the core while seven siblings lace a city of ten million into one grid.',
      'Full underground cell coverage, heated winter seats, and a circle line so central that “inside Line 2” is shorthand for downtown.',
    ],
  },
  paris: {
    name: 'PARIS', sub: 'MÉTRO DE PARIS · RATP', opened: '1900',
    scopeNote: '1–14 + 3bis/7bis',
    diagram: {
      file: 'assets/paris-diagram.svg', tappable: true,
      credit: '“Carte Métro de Paris” by Rigil, Wikimedia Commons, CC BY 3.0',
      commons: 'https://commons.wikimedia.org/wiki/File:Carte_M%C3%A9tro_de_Paris.svg',
      license: 'CC BY 3.0',
      sub: 'community recreation in the RATP idiom · current to mid-2026',
    },
    official: 'https://www.ratp.fr/plans',
    why: [
      '<b>why it’s here:</b> the tightest station mesh anywhere. Almost no point in the city proper is more than about 500 m from a Métro entrance, on a network first opened in 1900.',
      'Rubber-tyred trains, the driverless Line 14, and a map so settled it has been graphic-design canon for a century.',
    ],
  },
  tokyo: {
    name: 'TOKYO', sub: 'TOKYO METRO + TOEI SUBWAY', opened: '1927',
    scopeNote: 'Tokyo Metro + Toei',
    diagram: {
      file: 'assets/tokyo-diagram.svg', tappable: false,
      credit: '“Tokyo Subway Linemap” by Yveltal, Wikimedia Commons, CC BY-SA 4.0',
      commons: 'https://commons.wikimedia.org/wiki/File:Tokyo_Subway_Linemap_en.svg',
      license: 'CC BY-SA 4.0',
      sub: 'community recreation in the official idiom · bilingual · 2020 base, network unchanged since',
    },
    official: 'https://www.tokyometro.jp/en/subwaymap/',
    why: [
      '<b>why it’s here:</b> Asia’s first subway (the Ginza Line, 1927) grew into the planet’s busiest rail city. Two operators run thirteen lines that riders treat as one system.',
      'Many trains continue past the subway’s edges onto suburban railways; the atlas draws the subway proper and truncates the through-running there.',
    ],
  },
};

// city strip order matches the mock boards; only three are live at this gate
const STRIP = ['shanghai', 'tokyo', 'seoul', 'hong kong', 'singapore', 'delhi',
               'moscow', 'london', 'paris', 'nyc', 'mexico city', 'cairo'];
const LIVE = new Set(['seoul', 'paris', 'tokyo']);

const ODBL = 'geometry © OpenStreetMap contributors (ODbL)';
const PAD_KM = 2;

const $ = (sel) => document.querySelector(sel);
const esc = (s) => s.replace(/[&<>"']/g,
  (ch) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[ch]));

let META = null; // assets/meta.json — per-city stats for cards + footer as-of

// ------------------------------------------------------------- asset cache

const diagramCache = {};
function getDiagramText(city) {
  if (!diagramCache[city]) {
    diagramCache[city] = fetch(CITIES[city].diagram.file)
      .then((r) => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.text(); })
      .then((t) => t.slice(t.search(/<svg[\s>]/i)))
      .catch((err) => { delete diagramCache[city]; throw err; });
  }
  return diagramCache[city];
}

const shapeCache = {};
function getShape(city) {
  if (!shapeCache[city]) {
    shapeCache[city] = fetch('assets/' + city + '-shape.json')
      .then((r) => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .catch((err) => { delete shapeCache[city]; throw err; });
  }
  return shapeCache[city];
}

// --------------------------------------------------------- pan/zoom engine
// From the D11 interactivity spike: viewBox-driven wheel zoom, pointer pan,
// two-finger pinch; plus zoom clamping, drag-vs-tap discrimination, and
// keyboard support on the focusable viewport.

function makePanZoom(viewport, svg, opts = {}) {
  const vb0 = svg.viewBox.baseVal;
  const home = { x: vb0.x, y: vb0.y, w: vb0.width, h: vb0.height };
  let vb = { ...home };
  const minW = home.w / (opts.maxZoom || 40);
  const maxW = home.w * 3;

  const apply = () => {
    svg.setAttribute('viewBox', vb.x + ' ' + vb.y + ' ' + vb.w + ' ' + vb.h);
    if (opts.onChange) opts.onChange(vb);
  };

  function zoomAt(cx, cy, f) {
    if (vb.w * f < minW) f = minW / vb.w;
    if (vb.w * f > maxW) f = maxW / vb.w;
    const r = svg.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const mx = vb.x + (cx - r.left) / r.width * vb.w;
    const my = vb.y + (cy - r.top) / r.height * vb.h;
    vb = { x: mx - (mx - vb.x) * f, y: my - (my - vb.y) * f, w: vb.w * f, h: vb.h * f };
    apply();
  }

  svg.addEventListener('wheel', (e) => {
    e.preventDefault();
    zoomAt(e.clientX, e.clientY, e.deltaY > 0 ? 1.18 : 1 / 1.18);
  }, { passive: false });

  const pts = new Map();
  let lastMid = null, lastDist = null, dragDist = 0;
  svg.addEventListener('pointerdown', (e) => {
    svg.setPointerCapture(e.pointerId);
    pts.set(e.pointerId, [e.clientX, e.clientY]);
    lastMid = null; lastDist = null; dragDist = 0;
    viewport.classList.add('dragging');
  });
  svg.addEventListener('pointermove', (e) => {
    if (!pts.has(e.pointerId)) return;
    pts.set(e.pointerId, [e.clientX, e.clientY]);
    const r = svg.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const ps = [...pts.values()];
    if (ps.length === 1) {
      if (lastMid) {
        dragDist += Math.hypot(ps[0][0] - lastMid[0], ps[0][1] - lastMid[1]);
        vb.x -= (ps[0][0] - lastMid[0]) / r.width * vb.w;
        vb.y -= (ps[0][1] - lastMid[1]) / r.height * vb.h;
        apply();
      }
      lastMid = ps[0];
    } else if (ps.length === 2) {
      const mid = [(ps[0][0] + ps[1][0]) / 2, (ps[0][1] + ps[1][1]) / 2];
      const dist = Math.hypot(ps[0][0] - ps[1][0], ps[0][1] - ps[1][1]);
      dragDist += 10; // a pinch is never a tap
      if (lastDist) zoomAt(mid[0], mid[1], lastDist / dist);
      if (lastMid) {
        vb.x -= (mid[0] - lastMid[0]) / r.width * vb.w;
        vb.y -= (mid[1] - lastMid[1]) / r.height * vb.h;
        apply();
      }
      lastMid = mid; lastDist = dist;
    }
  });
  ['pointerup', 'pointercancel'].forEach((t) => svg.addEventListener(t, (e) => {
    pts.delete(e.pointerId);
    lastMid = null; lastDist = null;
    if (!pts.size) viewport.classList.remove('dragging');
  }));

  if (opts.onTap) {
    svg.addEventListener('click', (e) => {
      if (dragDist > 6) return;
      opts.onTap(e);
    });
  }

  viewport.addEventListener('keydown', (e) => {
    const r = svg.getBoundingClientRect();
    const step = vb.w * 0.08;
    if (e.key === 'ArrowLeft') vb.x -= step;
    else if (e.key === 'ArrowRight') vb.x += step;
    else if (e.key === 'ArrowUp') vb.y -= step;
    else if (e.key === 'ArrowDown') vb.y += step;
    else if (e.key === '+' || e.key === '=') {
      return e.preventDefault(), zoomAt(r.left + r.width / 2, r.top + r.height / 2, 1 / 1.3);
    } else if (e.key === '-' || e.key === '_') {
      return e.preventDefault(), zoomAt(r.left + r.width / 2, r.top + r.height / 2, 1.3);
    } else if (e.key === '0' || e.key === 'Home') { vb = { ...home }; }
    else return;
    e.preventDefault();
    apply();
  });

  apply();
  return {
    get vb() { return vb; },
    reset() { vb = { ...home }; apply(); },
    zoomCenter(f) {
      const r = svg.getBoundingClientRect();
      zoomAt(r.left + r.width / 2, r.top + r.height / 2, f);
    },
    refresh: apply,
    svg,
  };
}

// ------------------------------------------------------ true-shape renderer

const SVG_NS = 'http://www.w3.org/2000/svg';

function buildShapeSVG(shape, opts = {}) {
  const svg = document.createElementNS(SVG_NS, 'svg');
  const w = shape.w_km + 2 * PAD_KM, h = shape.h_km + 2 * PAD_KM;
  svg.setAttribute('viewBox', `${-PAD_KM} ${-PAD_KM} ${w} ${h}`);
  svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');

  if (opts.grid) {
    const g = document.createElementNS(SVG_NS, 'g');
    const lo = -Math.ceil(2 * Math.max(w, h) / 10) * 10;
    const hi = -lo + Math.ceil(Math.max(w, h) / 10) * 10;
    for (let v = lo; v <= hi; v += 10) {
      const vl = document.createElementNS(SVG_NS, 'line');
      vl.setAttribute('x1', v); vl.setAttribute('x2', v);
      vl.setAttribute('y1', lo); vl.setAttribute('y2', hi);
      const hl = document.createElementNS(SVG_NS, 'line');
      hl.setAttribute('y1', v); hl.setAttribute('y2', v);
      hl.setAttribute('x1', lo); hl.setAttribute('x2', hi);
      for (const ln of [vl, hl]) {
        ln.setAttribute('stroke', '#ecece6');
        ln.setAttribute('vector-effect', 'non-scaling-stroke');
        ln.setAttribute('stroke-width', '1');
        g.appendChild(ln);
      }
    }
    svg.appendChild(g);
  }

  for (const line of shape.lines) {
    const g = document.createElementNS(SVG_NS, 'g');
    g.setAttribute('class', 'metroline');
    g.dataset.ref = line.ref;
    for (const path of line.paths) {
      const pl = document.createElementNS(SVG_NS, 'polyline');
      pl.setAttribute('points', path.map((p) => p[0] + ',' + p[1]).join(' '));
      pl.setAttribute('fill', 'none');
      pl.setAttribute('stroke', line.color);
      pl.setAttribute('stroke-width', '3');
      pl.setAttribute('stroke-linecap', 'round');
      pl.setAttribute('stroke-linejoin', 'round');
      pl.setAttribute('vector-effect', 'non-scaling-stroke');
      g.appendChild(pl);
    }
    svg.appendChild(g);
  }

  if (opts.stations) {
    const g = document.createElementNS(SVG_NS, 'g');
    g.setAttribute('class', 'stations');
    g.setAttribute('fill', '#ffffff');
    g.setAttribute('stroke', '#17171c');
    g.setAttribute('stroke-width', '0.95');
    g.setAttribute('opacity', '0.92');
    for (const [x, y] of shape.stations) {
      const c = document.createElementNS(SVG_NS, 'circle');
      c.setAttribute('cx', x); c.setAttribute('cy', y); c.setAttribute('r', '0.2');
      c.setAttribute('vector-effect', 'non-scaling-stroke');
      g.appendChild(c);
    }
    svg.appendChild(g);
  }
  return svg;
}

// station dots keep a constant on-screen radius across zoom levels
function updateDots(svg, vb) {
  const g = svg.querySelector('g.stations');
  if (!g) return;
  const rect = svg.getBoundingClientRect();
  if (!rect.width) return;
  const r = 2.4 * vb.w / rect.width;
  for (const c of g.children) c.setAttribute('r', r);
}

function setScalebar(el, pxPerKm, panelPx) {
  const maxPx = Math.min(170, (panelPx || 500) * 0.32);
  let km = 0.5;
  for (const k of [200, 100, 50, 20, 10, 5, 2, 1, 0.5]) {
    if (k * pxPerKm <= maxPx) { km = k; break; }
  }
  el.querySelector('.bar').style.width = (km * pxPerKm).toFixed(0) + 'px';
  el.querySelector('.km').textContent = km + ' km';
}

// ----------------------------------------------------------------- explore

const explore = { city: 'seoul', mode: 'diagram', pz: null, token: 0, selectedRef: null };

function showLoading(el, on, failed) {
  el.hidden = !on;
  el.textContent = failed ? 'could not load · tap to retry' : 'loading…';
  el.style.pointerEvents = failed ? 'auto' : 'none';
}

let chipTimer = null;
function showStationChip(name) {
  const chip = $('#station-chip');
  chip.innerHTML = '<b>' + esc(name) + '</b> · station data card lands in the next stage';
  chip.hidden = false;
  clearTimeout(chipTimer);
  chipTimer = setTimeout(() => { chip.hidden = true; }, 6000);
}

let tappedLabel = null;
function onDiagramTap(e) {
  const t = e.target.closest('text');
  if (!t) return;
  const name = t.textContent.trim().replace(/\s+/g, ' ');
  if (!name) return;
  if (tappedLabel) tappedLabel.classList.remove('tapped');
  t.classList.add('tapped');
  tappedLabel = t;
  showStationChip(name);
}

function onShapeTap(e) {
  const g = e.target.closest('g.metroline');
  selectLine(g && g.dataset.ref !== explore.selectedRef ? g.dataset.ref : null);
}

function selectLine(ref) {
  explore.selectedRef = ref;
  const svg = explore.pz && explore.pz.svg;
  if (svg) {
    for (const g of svg.querySelectorAll('g.metroline')) {
      g.classList.toggle('dim', ref !== null && g.dataset.ref !== ref);
      if (g.dataset.ref === ref) g.parentNode.appendChild(g); // draw on top
    }
  }
  for (const b of document.querySelectorAll('.linechips button')) {
    b.setAttribute('aria-pressed', String(b.dataset.ref === ref));
  }
  const meta = META && META.cities[explore.city];
  $('#map-sub').textContent = ref !== null
    ? 'line ' + ref + ' selected · tap again to clear'
    : trueShapeSub(meta);
}

function trueShapeSub(meta) {
  return (meta ? meta.lines.length + ' lines' : 'lines') +
    ' in their official colours · true geometry · north-up';
}

async function renderExplore() {
  const token = ++explore.token;
  const c = CITIES[explore.city];
  const meta = META && META.cities[explore.city];
  const isDiagram = explore.mode === 'diagram';
  explore.selectedRef = null;

  $('#map-label').textContent = c.name + (isDiagram
    ? ' · DIAGRAM · THE FAMILIAR MAP' : ' · TRUE GEOMETRY · NORTH-UP');
  $('#map-sub').textContent = isDiagram ? c.diagram.sub : trueShapeSub(meta);
  $('#mode-diagram').setAttribute('aria-pressed', String(isDiagram));
  $('#mode-shape').setAttribute('aria-pressed', String(!isDiagram));
  renderCard();
  updateFooter();

  const mapEl = $('#explore-map');
  mapEl.innerHTML = '';
  explore.pz = null;
  $('#explore-scalebar').hidden = true;
  $('#map-note').hidden = true;
  $('#station-chip').hidden = true;
  $('#map-hint').textContent = '';
  if (tappedLabel) tappedLabel = null;
  const loading = $('#map-loading');
  showLoading(loading, true);

  try {
    if (isDiagram) {
      const text = await getDiagramText(explore.city);
      if (token !== explore.token) return;
      mapEl.innerHTML = text;
      const svg = mapEl.querySelector('svg');
      svg.removeAttribute('width');
      svg.removeAttribute('height');
      explore.pz = makePanZoom(mapEl, svg, {
        onTap: c.diagram.tappable ? onDiagramTap : null,
      });
      $('#map-note').hidden = c.diagram.tappable;
      $('#map-hint').textContent = c.diagram.tappable
        ? 'drag · scroll · pinch · tap a station name' : 'drag · scroll · pinch';
    } else {
      const shape = await getShape(explore.city);
      if (token !== explore.token) return;
      const svg = buildShapeSVG(shape, { stations: true });
      mapEl.appendChild(svg);
      explore.pz = makePanZoom(mapEl, svg, {
        onTap: onShapeTap,
        onChange: (vb) => {
          updateDots(svg, vb);
          const rect = svg.getBoundingClientRect();
          if (rect.width) setScalebar($('#explore-scalebar'), rect.width / vb.w, rect.width);
        },
      });
      $('#explore-scalebar').hidden = false;
      explore.pz.refresh();
      $('#map-hint').textContent = 'drag · scroll · pinch · tap a line to isolate it';
    }
    showLoading(loading, false);
  } catch (err) {
    if (token !== explore.token) return;
    showLoading(loading, true, true);
  }
}

function factRow(dt, dd) {
  return '<div><span class="dt">' + dt + '</span><span class="dd">' + dd + '</span></div>';
}

function renderCard() {
  const c = CITIES[explore.city];
  const meta = META && META.cities[explore.city];
  const isDiagram = explore.mode === 'diagram';
  const pipeline = '<span class="ev">pipeline · dated at build</span>';
  const rows = [
    factRow('opened', c.opened),
    factRow('lines drawn', (meta ? meta.lines.length : '…') +
      ' <span class="ev">(' + c.scopeNote + ')</span>'),
    factRow('stations plotted', meta ? meta.stations : '…'),
    factRow('furthest-stations span', meta
      ? meta.span_km.toFixed(0) + ' km <span class="ev">computed</span>' : '…'),
    factRow('reported route-km', pipeline),
    factRow('annual ridership', pipeline),
    factRow('diagram source', '<a href="' + c.diagram.commons +
      '" target="_blank" rel="noopener">Commons · ' + c.diagram.license + '</a>'),
    factRow('the map riders see', '<a href="' + c.official +
      '" target="_blank" rel="noopener">official map ↗</a>'),
  ].join('');

  const chips = meta ? meta.lines.map((l) =>
    '<button style="background:' + esc(l.color) + '" data-ref="' + esc(l.ref) +
    '" aria-pressed="false"' + (isDiagram ? ' aria-disabled="true" tabindex="-1"' : '') +
    ' aria-label="line ' + esc(l.ref) + '">' + esc(l.ref) + '</button>').join('') : '';

  $('#citycard').innerHTML =
    '<div class="cityname">' + c.name + '<small>' + c.sub + '</small></div>' +
    '<div class="facts">' + rows + '</div>' +
    (isDiagram && c.diagram.note
      ? '<div class="diagramnote">' + c.diagram.note + '</div>' : '') +
    '<div class="why">' + c.why.map((p) => '<p>' + p + '</p>').join('') + '</div>' +
    '<div class="linechips">' + chips + '</div>';

  if (!isDiagram) {
    for (const b of document.querySelectorAll('.linechips button')) {
      b.addEventListener('click', () =>
        selectLine(explore.selectedRef === b.dataset.ref ? null : b.dataset.ref));
    }
  }
}

// ------------------------------------------------------------------- shape
// One shared px-per-km across both panes: a single view state (zoom width W
// plus a pan offset from each network's own centre) drives both viewBoxes.

const pair = {
  inited: false, initing: null,
  panes: [], // {el, svg, wkm, hkm, scalebar}
  state: null, w0: 0,
};

function paneVB(pane) {
  const r = pane.el.getBoundingClientRect();
  const W = pair.state.w;
  const H = W * (r.height || 1) / (r.width || 1);
  return {
    x: pane.wkm / 2 + pair.state.offX - W / 2,
    y: pane.hkm / 2 + pair.state.offY - H / 2,
    w: W, h: H,
  };
}

function applyPair() {
  for (const pane of pair.panes) {
    const vb = paneVB(pane);
    pane.svg.setAttribute('viewBox', vb.x + ' ' + vb.y + ' ' + vb.w + ' ' + vb.h);
    const r = pane.el.getBoundingClientRect();
    if (r.width) setScalebar(pane.scalebar, r.width / pair.state.w, r.width);
  }
}

function pairZoomAt(pane, cx, cy, f) {
  const minW = pair.w0 / 30, maxW = pair.w0 * 2.5;
  if (pair.state.w * f < minW) f = minW / pair.state.w;
  if (pair.state.w * f > maxW) f = maxW / pair.state.w;
  const r = pane.svg.getBoundingClientRect();
  if (!r.width || !r.height) return;
  const vb = paneVB(pane);
  const px = vb.x + (cx - r.left) / r.width * vb.w;
  const py = vb.y + (cy - r.top) / r.height * vb.h;
  const nx = px - (px - vb.x) * f;
  const ny = py - (py - vb.y) * f;
  pair.state.w *= f;
  pair.state.offX = nx + pair.state.w / 2 - pane.wkm / 2;
  pair.state.offY = ny + (vb.h * f) / 2 - pane.hkm / 2;
  applyPair();
}

function wirePane(pane) {
  const { el, svg } = pane;
  svg.addEventListener('wheel', (e) => {
    e.preventDefault();
    pairZoomAt(pane, e.clientX, e.clientY, e.deltaY > 0 ? 1.18 : 1 / 1.18);
  }, { passive: false });

  const pts = new Map();
  let lastMid = null, lastDist = null;
  svg.addEventListener('pointerdown', (e) => {
    svg.setPointerCapture(e.pointerId);
    pts.set(e.pointerId, [e.clientX, e.clientY]);
    lastMid = null; lastDist = null;
    el.classList.add('dragging');
  });
  svg.addEventListener('pointermove', (e) => {
    if (!pts.has(e.pointerId)) return;
    pts.set(e.pointerId, [e.clientX, e.clientY]);
    const r = svg.getBoundingClientRect();
    if (!r.width || !r.height) return;
    const ps = [...pts.values()];
    const kmPerPx = pair.state.w / r.width;
    if (ps.length === 1) {
      if (lastMid) {
        pair.state.offX -= (ps[0][0] - lastMid[0]) * kmPerPx;
        pair.state.offY -= (ps[0][1] - lastMid[1]) * kmPerPx;
        applyPair();
      }
      lastMid = ps[0];
    } else if (ps.length === 2) {
      const mid = [(ps[0][0] + ps[1][0]) / 2, (ps[0][1] + ps[1][1]) / 2];
      const dist = Math.hypot(ps[0][0] - ps[1][0], ps[0][1] - ps[1][1]);
      if (lastDist) pairZoomAt(pane, mid[0], mid[1], lastDist / dist);
      if (lastMid) {
        pair.state.offX -= (mid[0] - lastMid[0]) * kmPerPx;
        pair.state.offY -= (mid[1] - lastMid[1]) * kmPerPx;
        applyPair();
      }
      lastMid = mid; lastDist = dist;
    }
  });
  ['pointerup', 'pointercancel'].forEach((t) => svg.addEventListener(t, (e) => {
    pts.delete(e.pointerId);
    lastMid = null; lastDist = null;
    if (!pts.size) el.classList.remove('dragging');
  }));

  el.addEventListener('keydown', (e) => {
    const step = pair.state.w * 0.08;
    const r = svg.getBoundingClientRect();
    if (e.key === 'ArrowLeft') pair.state.offX -= step;
    else if (e.key === 'ArrowRight') pair.state.offX += step;
    else if (e.key === 'ArrowUp') pair.state.offY -= step;
    else if (e.key === 'ArrowDown') pair.state.offY += step;
    else if (e.key === '+' || e.key === '=') {
      return e.preventDefault(), pairZoomAt(pane, r.left + r.width / 2, r.top + r.height / 2, 1 / 1.3);
    } else if (e.key === '-' || e.key === '_') {
      return e.preventDefault(), pairZoomAt(pane, r.left + r.width / 2, r.top + r.height / 2, 1.3);
    } else if (e.key === '0' || e.key === 'Home') {
      pair.state = { offX: 0, offY: 0, w: pair.w0 };
    } else return;
    e.preventDefault();
    applyPair();
  });
}

function initShapeTab() {
  if (pair.inited || pair.initing) return pair.initing;
  const loading = $('#shape-loading');
  showLoading(loading, true);
  pair.initing = Promise.all([getShape('seoul'), getShape('paris')]).then(([seoul, paris]) => {
    const defs = [
      { id: 'pane-seoul', shape: seoul, city: 'seoul' },
      { id: 'pane-paris', shape: paris, city: 'paris' },
    ];
    for (const d of defs) {
      const el = document.getElementById(d.id);
      const svg = buildShapeSVG(d.shape, { grid: true });
      el.appendChild(svg);
      const meta = META && META.cities[d.city];
      if (meta) {
        $('#' + d.id + '-sub').textContent =
          'furthest stations ' + meta.span_km.toFixed(0) + ' km · ' +
          meta.lines.length + ' lines';
      }
      const pane = {
        el, svg, wkm: d.shape.w_km, hkm: d.shape.h_km,
        scalebar: $('#' + d.id + '-scalebar'),
      };
      pair.panes.push(pane);
      wirePane(pane);
    }
    // shared scale: the width (km) at which both networks fit their panes
    pair.w0 = Math.max(...pair.panes.map((p) => {
      const r = p.el.getBoundingClientRect();
      const aspect = (r.width || 1) / (r.height || 1);
      return Math.max(p.wkm + 2 * PAD_KM, (p.hkm + 2 * PAD_KM) * aspect);
    }));
    pair.state = { offX: 0, offY: 0, w: pair.w0 };
    applyPair();
    pair.inited = true;
    showLoading(loading, false);
  }).catch(() => {
    pair.initing = null;
    showLoading(loading, true, true);
  });
  return pair.initing;
}

// ----------------------------------------------------------- chrome wiring

let activeTab = 'tab-explore';
const TABS = ['tab-explore', 'tab-shape', 'tab-rankings', 'tab-method'];

function selectTab(id) {
  activeTab = id;
  for (const tid of TABS) {
    const tab = document.getElementById(tid);
    const on = tid === id;
    tab.setAttribute('aria-selected', String(on));
    tab.tabIndex = on ? 0 : -1;
    document.getElementById(tab.getAttribute('aria-controls')).hidden = !on;
  }
  updateFooter();
  if (id === 'tab-shape') initShapeTab();
  if (id === 'tab-explore' && explore.pz) explore.pz.refresh();
}

function wireTabs() {
  for (const tid of TABS) {
    const tab = document.getElementById(tid);
    tab.addEventListener('click', () => selectTab(tid));
    tab.addEventListener('keydown', (e) => {
      const i = TABS.indexOf(tid);
      let next = null;
      if (e.key === 'ArrowRight') next = TABS[(i + 1) % TABS.length];
      else if (e.key === 'ArrowLeft') next = TABS[(i + TABS.length - 1) % TABS.length];
      else if (e.key === 'Home') next = TABS[0];
      else if (e.key === 'End') next = TABS[TABS.length - 1];
      if (next) {
        e.preventDefault();
        selectTab(next);
        document.getElementById(next).focus();
      }
    });
  }
}

function renderCityStrip() {
  const strip = $('#citystrip');
  strip.innerHTML = '';
  for (const label of STRIP) {
    const live = LIVE.has(label);
    const b = document.createElement('button');
    b.textContent = label;
    if (live) {
      b.classList.toggle('on', label === explore.city);
      b.addEventListener('click', () => {
        if (explore.city === label) return;
        explore.city = label;
        for (const x of strip.children) x.classList.toggle('on', x.textContent === label);
        renderExplore();
      });
    } else {
      b.className = 'soon';
      b.title = 'soon';
      b.setAttribute('aria-disabled', 'true');
      b.tabIndex = -1;
    }
    strip.appendChild(b);
  }
}

function updateFooter() {
  const parts = [];
  if (activeTab === 'tab-explore' && explore.mode === 'diagram') {
    parts.push('diagram: ' + CITIES[explore.city].diagram.credit);
  }
  parts.push(ODBL + (META ? ' · OSM snapshot ' + META.as_of : ''));
  $('#attribution').textContent = parts.join(' · ');
}

function wireChrome() {
  wireTabs();
  $('#mode-diagram').addEventListener('click', () => {
    if (explore.mode !== 'diagram') { explore.mode = 'diagram'; renderExplore(); }
  });
  $('#mode-shape').addEventListener('click', () => {
    if (explore.mode !== 'shape') { explore.mode = 'shape'; renderExplore(); }
  });
  $('#zoom-in').addEventListener('click', () => explore.pz && explore.pz.zoomCenter(1 / 1.4));
  $('#zoom-out').addEventListener('click', () => explore.pz && explore.pz.zoomCenter(1.4));
  $('#zoom-reset').addEventListener('click', () => explore.pz && explore.pz.reset());
  $('#map-loading').addEventListener('click', () => renderExplore());
  $('#shape-loading').addEventListener('click', () => initShapeTab());

  let raf = null;
  window.addEventListener('resize', () => {
    if (raf) return;
    raf = requestAnimationFrame(() => {
      raf = null;
      if (explore.pz) explore.pz.refresh();
      if (pair.inited) applyPair();
    });
  });
}

async function init() {
  renderCityStrip();
  wireChrome();
  try {
    META = await fetch('assets/meta.json').then((r) => r.json());
  } catch (err) { /* cards fall back to ellipses; footer omits the as-of */ }
  renderExplore();
}

init();
