(function () {
  "use strict";

  const section = document.querySelector('[data-boom="pc"]');
  if (!section) return;
  const stage = section.querySelector(".case-viz");
  if (!stage) return;

  const placeholder = stage.querySelector(".case-viz-placeholder");
  if (placeholder) placeholder.remove();

  const yearEl = stage.querySelector(".case-viz-readout.is-year");
  const countEl = stage.querySelector(".case-viz-readout.is-count");

  const canvas = document.createElement("canvas");
  canvas.style.cssText =
    "position:absolute;inset:0;width:100%;height:100%;display:block;";
  stage.insertBefore(canvas, stage.firstChild);
  const ctx = canvas.getContext("2d");
  const DPR = Math.min(window.devicePixelRatio || 1, 2);
  let W = 0,
    H = 0;

  const PURPLE = "#8b5cf6";
  const UNIT = 100;

  const KEY = [
    { year: 1998, count: 100, phase: "just a few rooms" },
    { year: 2001, count: 15000, phase: "one on every corner" },
    { year: 2009, count: 21549, phase: "critical mass" },
    { year: 2015, count: 16000, phase: "the air has changed" },
    { year: 2021, count: 9265, phase: "what remains" },
  ];
  const PEAK_DOTS = Math.ceil(KEY[2].count / UNIT);

  const DURATION_MS = 8500;
  const prefersReduced =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  let cells = [];
  let cols = 0,
    rows = 0,
    cellW = 0,
    cellH = 0,
    padX = 0,
    padY = 0,
    dotSize = 0;

  function layout() {
    const rect = stage.getBoundingClientRect();
    W = rect.width;
    H = rect.height;
    canvas.width = Math.round(W * DPR);
    canvas.height = Math.round(H * DPR);
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);

    const topInset = Math.min(72, H * 0.22);
    const sideInset = Math.min(32, W * 0.04);
    const bottomInset = Math.min(28, H * 0.08);

    const innerW = W - sideInset * 2;
    const innerH = H - topInset - bottomInset;

    const targetRatio = innerW / innerH;
    cols = Math.max(
      12,
      Math.round(Math.sqrt(PEAK_DOTS * targetRatio))
    );
    rows = Math.ceil(PEAK_DOTS / cols);

    cellW = innerW / cols;
    cellH = innerH / rows;
    padX = sideInset;
    padY = topInset;
    dotSize = Math.max(3, Math.min(cellW, cellH) * 0.52);

    cells = [];
    for (let i = 0; i < PEAK_DOTS; i++) {
      const r = Math.floor(i / cols);
      const c = i % cols;
      cells.push({
        x: padX + c * cellW + cellW / 2,
        y: padY + r * cellH + cellH / 2,
        onOrder: i,
        offOrder: 0,
      });
    }

    const shuffleOn = cells.map((_, i) => i);
    for (let i = shuffleOn.length - 1; i > 0; i--) {
      const j = Math.floor(seededRand(i) * (i + 1));
      [shuffleOn[i], shuffleOn[j]] = [shuffleOn[j], shuffleOn[i]];
    }
    shuffleOn.forEach((idx, order) => {
      cells[idx].onOrder = order;
    });

    const offPool = cells.map((_, i) => i);
    for (let i = offPool.length - 1; i > 0; i--) {
      const j = Math.floor(seededRand(i + 9999) * (i + 1));
      [offPool[i], offPool[j]] = [offPool[j], offPool[i]];
    }
    offPool.forEach((idx, order) => {
      cells[idx].offOrder = order;
    });
  }

  function seededRand(seed) {
    const x = Math.sin(seed * 9301 + 49297) * 233280;
    return x - Math.floor(x);
  }

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function countForProgress(p) {
    const stops = [
      { p: 0.0, c: KEY[0].count },
      { p: 0.12, c: KEY[0].count },
      { p: 0.32, c: KEY[1].count },
      { p: 0.52, c: KEY[2].count },
      { p: 0.7, c: KEY[2].count },
      { p: 0.82, c: KEY[3].count },
      { p: 1.0, c: KEY[4].count },
    ];
    for (let i = 0; i < stops.length - 1; i++) {
      const a = stops[i],
        b = stops[i + 1];
      if (p >= a.p && p <= b.p) {
        const t = (p - a.p) / (b.p - a.p);
        const eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
        return lerp(a.c, b.c, eased);
      }
    }
    return stops[stops.length - 1].c;
  }

  function yearForProgress(p) {
    const stops = [
      { p: 0.0, y: 1998 },
      { p: 0.12, y: 1998 },
      { p: 0.32, y: 2001 },
      { p: 0.52, y: 2009 },
      { p: 0.7, y: 2009 },
      { p: 0.82, y: 2015 },
      { p: 1.0, y: 2021 },
    ];
    for (let i = 0; i < stops.length - 1; i++) {
      const a = stops[i],
        b = stops[i + 1];
      if (p >= a.p && p <= b.p) {
        const t = (p - a.p) / (b.p - a.p);
        return Math.round(lerp(a.y, b.y, t));
      }
    }
    return stops[stops.length - 1].y;
  }

  let startTime = null;
  let hasStarted = false;
  let peakReached = 0;

  function start() {
    if (hasStarted) return;
    hasStarted = true;
    startTime = prefersReduced
      ? performance.now() - DURATION_MS
      : performance.now();
  }

  function drawField(p) {
    ctx.clearRect(0, 0, W, H);

    const currentCount = countForProgress(p);
    const targetDots = currentCount / UNIT;
    peakReached = Math.max(peakReached, targetDots);

    for (const cell of cells) {
      let alpha = 0;
      if (cell.onOrder < targetDots) {
        alpha = Math.min(1, targetDots - cell.onOrder);
      }

      if (peakReached > targetDots) {
        const decayAmount = peakReached - targetDots;
        if (cell.offOrder < decayAmount) {
          alpha = 0;
        } else if (cell.offOrder < decayAmount + 1) {
          alpha *= decayAmount + 1 - cell.offOrder;
        }
      }

      if (alpha <= 0) continue;

      ctx.fillStyle = `rgba(139, 92, 246, ${alpha * 0.9})`;
      ctx.fillRect(
        cell.x - dotSize / 2,
        cell.y - dotSize / 2,
        dotSize,
        dotSize
      );
    }
  }

  function tick(now) {
    requestAnimationFrame(tick);

    let progress = 0;
    if (hasStarted && startTime !== null) {
      const elapsed = now - startTime;
      progress = Math.max(0, Math.min(1, elapsed / DURATION_MS));
    }

    const rect = stage.getBoundingClientRect();
    if (rect.bottom < -100 || rect.top > window.innerHeight + 100) return;

    drawField(progress);

    const year = yearForProgress(progress);
    const count = Math.round(countForProgress(progress));
    if (yearEl) yearEl.textContent = year;
    if (countEl) countEl.textContent = count.toLocaleString();
  }

  let resizeTimeout;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
      peakReached = 0;
      layout();
    }, 120);
  });

  layout();

  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            start();
            io.disconnect();
            break;
          }
        }
      },
      { threshold: 0.3 }
    );
    io.observe(stage);
  } else {
    start();
  }

  requestAnimationFrame(tick);
})();
