(function () {
  "use strict";

  const stage = document.querySelector(".hero-stage");
  if (!stage) return;

  const placeholder = stage.querySelector(".hero-stage-placeholder");
  if (placeholder) placeholder.remove();

  const labelEl = document.querySelector("[data-hero-label]");
  const countEl = document.querySelector("[data-hero-count]");

  const canvas = document.createElement("canvas");
  canvas.style.cssText =
    "position:absolute;inset:0;width:100%;height:100%;display:block;";
  stage.insertBefore(canvas, stage.firstChild);

  const ctx = canvas.getContext("2d");
  const DPR = Math.min(window.devicePixelRatio || 1, 2);
  let W = 0,
    H = 0;

  function resize() {
    const rect = stage.getBoundingClientRect();
    W = rect.width;
    H = rect.height;
    canvas.width = Math.round(W * DPR);
    canvas.height = Math.round(H * DPR);
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }

  const PHASES = [
    { id: "waiting", t: 0.0 },
    { id: "trickle", t: 0.07 },
    { id: "arriving", t: 0.22 },
    { id: "gathering", t: 0.42 },
    { id: "about to go off", t: 0.63 },
    { id: "gone off", t: 0.82 },
  ];

  const MAX = () => (window.innerWidth < 768 ? 140 : 220);
  const DURATION_MS = 9000;

  const prefersReduced =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  class Runner {
    constructor() {
      this.scale = 0.85 + Math.random() * 0.3;
      this.gaitPhase = Math.random() * Math.PI * 2;
      this.gaitSpeed = 0.22 + Math.random() * 0.08;
      this.opacity = 0;
      this.opacityTarget = 0.88;
      this.spawn();
    }
    spawn() {
      const edge = Math.floor(Math.random() * 4);
      const pad = 30;
      if (edge === 0) {
        this.x = Math.random() * W;
        this.y = -pad;
        this.angle = Math.PI / 2 + (Math.random() - 0.5) * 1.2;
      } else if (edge === 1) {
        this.x = W + pad;
        this.y = Math.random() * H;
        this.angle = Math.PI + (Math.random() - 0.5) * 1.2;
      } else if (edge === 2) {
        this.x = Math.random() * W;
        this.y = H + pad;
        this.angle = -Math.PI / 2 + (Math.random() - 0.5) * 1.2;
      } else {
        this.x = -pad;
        this.y = Math.random() * H;
        this.angle = (Math.random() - 0.5) * 1.2;
      }
      this.speed = 1.1 + Math.random() * 0.7;
    }
    update(alignStrength) {
      this.gaitPhase += this.gaitSpeed;
      this.opacity += (this.opacityTarget - this.opacity) * 0.04;

      if (alignStrength > 0.001) {
        let delta = 0 - this.angle;
        while (delta > Math.PI) delta -= Math.PI * 2;
        while (delta < -Math.PI) delta += Math.PI * 2;
        this.angle += delta * 0.03 * Math.min(1.3, alignStrength * 2.2);
      }

      const vx = Math.cos(this.angle) * this.speed;
      const vy = Math.sin(this.angle) * this.speed;
      this.x += vx;
      this.y += vy;

      const aligned = alignStrength > 0.7;
      if (aligned) {
        if (this.x > W + 40) {
          this.x = -40;
          this.y = Math.random() * H;
          this.opacity = 0;
        }
      } else {
        if (
          this.x < -60 ||
          this.x > W + 60 ||
          this.y < -60 ||
          this.y > H + 60
        ) {
          this.spawn();
          this.opacity = 0;
        }
      }
    }
    draw(ctx) {
      const s = this.scale * 10;
      const p = this.gaitPhase;
      const swing = 0.55;

      const legR = Math.sin(p) * swing;
      const legL = -Math.sin(p) * swing;
      const armR = -Math.sin(p) * swing * 0.8;
      const armL = Math.sin(p) * swing * 0.8;
      const bob = Math.abs(Math.sin(p * 2)) * 0.08 * s;

      const a = Math.max(0, Math.min(1, this.opacity));

      ctx.save();
      ctx.translate(this.x, this.y);
      ctx.rotate(this.angle + Math.PI / 2);
      ctx.translate(0, -bob);

      ctx.strokeStyle = `rgba(244, 242, 237, ${a * 0.92})`;
      ctx.fillStyle = `rgba(244, 242, 237, ${a * 0.92})`;
      ctx.lineWidth = Math.max(1.2, 0.18 * s);
      ctx.lineCap = "round";
      ctx.lineJoin = "round";

      const headR = 0.28 * s;
      const shoulderY = -0.55 * s;
      const hipY = 0.15 * s;
      const armLen = 0.5 * s;
      const legLen = 0.75 * s;

      ctx.beginPath();
      ctx.arc(0, -1.05 * s, headR, 0, Math.PI * 2);
      ctx.fill();

      ctx.beginPath();
      ctx.moveTo(0, -0.75 * s);
      ctx.lineTo(0, hipY);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(0, shoulderY);
      ctx.lineTo(Math.sin(armR) * armLen, shoulderY + Math.cos(armR) * armLen);
      ctx.moveTo(0, shoulderY);
      ctx.lineTo(Math.sin(armL) * armLen, shoulderY + Math.cos(armL) * armLen);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(0, hipY);
      ctx.lineTo(Math.sin(legR) * legLen, hipY + Math.cos(legR) * legLen);
      ctx.moveTo(0, hipY);
      ctx.lineTo(Math.sin(legL) * legLen, hipY + Math.cos(legL) * legLen);
      ctx.stroke();

      ctx.restore();
    }
  }

  const runners = [];
  let progress = 0;
  let alignStrength = 0;
  let peakCount = 0;

  let startTime = null;
  let hasStarted = false;

  function currentPhase(p) {
    let phase = PHASES[0];
    for (const ph of PHASES) {
      if (p >= ph.t) phase = ph;
    }
    return phase;
  }

  function tick(now) {
    requestAnimationFrame(tick);

    if (hasStarted && startTime !== null) {
      const elapsed = now - startTime;
      progress = Math.max(0, Math.min(1, elapsed / DURATION_MS));
    }

    const rect = stage.getBoundingClientRect();
    const offscreen =
      rect.bottom < -50 || rect.top > window.innerHeight + 50;
    if (offscreen) return;

    const target = Math.floor(progress * MAX());
    peakCount = Math.max(peakCount, target);
    while (runners.length < peakCount) runners.push(new Runner());

    const alignT = PHASES[4].t;
    const alignFull = PHASES[5].t + 0.04;
    const targetAlign = Math.max(
      0,
      Math.min(1, (progress - alignT) / (alignFull - alignT))
    );
    alignStrength += (targetAlign - alignStrength) * 0.06;

    ctx.fillStyle = "#141110";
    ctx.fillRect(0, 0, W, H);

    for (const r of runners) {
      r.update(alignStrength);
      r.draw(ctx);
    }

    const phase = currentPhase(progress);
    if (labelEl) labelEl.textContent = phase.id;
    if (countEl) countEl.textContent = runners.length;
  }

  function start() {
    if (hasStarted) return;
    hasStarted = true;
    if (prefersReduced) {
      startTime = performance.now() - DURATION_MS;
    } else {
      startTime = performance.now();
    }
  }

  resize();
  window.addEventListener("resize", resize);

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
      { threshold: 0.35 }
    );
    io.observe(stage);
  } else {
    start();
  }

  requestAnimationFrame(tick);
})();
