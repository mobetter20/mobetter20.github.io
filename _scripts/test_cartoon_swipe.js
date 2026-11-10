/* Gesture contract for assets/paper/cartoons.js. Run: node _scripts/test_cartoon_swipe.js */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const SCRIPT = fs.readFileSync(path.join(__dirname, '..', 'assets', 'paper', 'cartoons.js'), 'utf8');

function event({ pointerId = 1, pointerType = 'touch', isPrimary = true, x = 0, y = 0, target } = {}) {
  return {
    pointerId, pointerType, isPrimary, clientX: x, clientY: y, target,
    prevented: false, stopped: false,
    preventDefault() { this.prevented = true; },
    stopImmediatePropagation() { this.stopped = true; },
  };
}

function harness({ previous = false, next = false } = {}) {
  const documentListeners = new Map();
  const stageListeners = new Map();
  const assigned = [];
  const art = { closest: () => null };
  const arrows = {
    previous: previous ? { href: '/previous/' } : null,
    next: next ? { href: '/next/' } : null,
  };
  const stage = {
    contains: target => target === art,
    querySelector: selector => selector.includes('previous') ? arrows.previous : arrows.next,
    addEventListener: (name, handler) => stageListeners.set(name, handler),
  };
  const document = {
    querySelector: selector => selector === '.slide-stage' ? stage : null,
    addEventListener: (name, handler) => documentListeners.set(name, handler),
  };
  vm.runInNewContext(SCRIPT, {
    document,
    location: { assign: href => assigned.push(href) },
    setTimeout: () => 1,
  });
  return {
    art, arrows, assigned,
    fire(name, options) {
      const e = event({ ...options, target: options?.target || art });
      documentListeners.get(name)(e);
      return e;
    },
    click(options = {}) {
      const e = event({ ...options, target: options.target || art });
      documentListeners.get('click')(e);
      return e;
    },
  };
}

function swipe(h, { id = 1, from = [100, 100], to = [20, 100] } = {}) {
  h.fire('pointerdown', { pointerId: id, x: from[0], y: from[1] });
  return h.fire('pointerup', { pointerId: id, x: to[0], y: to[1] });
}

test('requires a 60px, strongly horizontal touch gesture', () => {
  const h = harness({ next: true });
  for (const to of [[41, 100], [0, 167], [20, 154]]) {
    const up = swipe(h, { to });
    assert.equal(up.prevented, false);
    assert.deepEqual(h.assigned, []);
  }
});

test('vertical and diagonal gestures preserve native scrolling', () => {
  const h = harness({ next: true });
  for (const to of [[95, 210], [35, 150]]) {
    h.fire('pointerdown', { x: 100, y: 100 });
    const move = h.fire('pointermove', { x: to[0], y: to[1] });
    const up = h.fire('pointerup', { x: to[0], y: to[1] });
    assert.equal(move.prevented, false);
    assert.equal(up.prevented, false);
  }
  assert.deepEqual(h.assigned, []);
});

test('a second touch or pointer cancellation cancels the gesture', () => {
  const h = harness({ next: true });
  h.fire('pointerdown', { pointerId: 1, x: 100, y: 100 });
  h.fire('pointerdown', { pointerId: 2, isPrimary: false, x: 90, y: 100 });
  h.fire('pointerup', { pointerId: 1, x: 20, y: 100 });
  assert.deepEqual(h.assigned, []);

  h.fire('pointerdown', { pointerId: 3, x: 100, y: 100 });
  h.fire('pointercancel', { pointerId: 3 });
  h.fire('pointerup', { pointerId: 3, x: 20, y: 100 });
  assert.deepEqual(h.assigned, []);
});

test('a first/last bound swipe suppresses the image click, then allows a new swipe', () => {
  const h = harness();
  const up = swipe(h);
  assert.equal(up.prevented, true);
  assert.deepEqual(h.assigned, []);
  const click = h.click();
  assert.equal(click.prevented, true);
  assert.equal(click.stopped, true);

  h.arrows.next = { href: '/next/' };
  const next = swipe(h, { id: 2 });
  assert.equal(next.prevented, true);
  assert.deepEqual(h.assigned, ['/next/']);
});

test('normal taps remain native and non-touch pointers are ignored', () => {
  const h = harness({ next: true });
  const mouseDown = h.fire('pointerdown', { pointerType: 'mouse', x: 100, y: 100 });
  const mouseUp = h.fire('pointerup', { pointerType: 'mouse', x: 20, y: 100 });
  const tap = h.click();
  assert.equal(mouseDown.prevented, false);
  assert.equal(mouseUp.prevented, false);
  assert.equal(tap.prevented, false);
  assert.deepEqual(h.assigned, []);
});
