/* Async navigation contracts. Real layout, decoding and native-link behavior are browser-checked. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const SCRIPT = fs.readFileSync(path.join(__dirname, '..', 'assets', 'paper', 'cartoons.js'), 'utf8');
const ORIGIN = 'https://ajin.im';
const BASE = '/is/writing/cartoons/slides/';
const SLUGS = ['a', 'b', 'c', 'd', 'e'];
const route = slug => `${ORIGIN}${BASE}${slug}/#cartoon`;
const imageURL = slug => `${ORIGIN}/assets/${slug}.webp`;
const flush = () => new Promise(resolve => setImmediate(resolve));

function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

// The harness models only the DOM operations used to present an already-built slide.
// Fetches and image decoding are separately controlled to exercise real races.
function harness({ initial = 'b', entryAlias = false, readyState = 'complete', connection, ignoreFetchAbort = false } = {}) {
  const h = { requests: [], images: [], assigned: [], replaced: [], pushes: [], swaps: [], focus: [], timers: new Map() };
  let currentURL = new URL(entryAlias ? `${ORIGIN}${BASE}#cartoon` : route(initial));
  let timerId = 0;
  const documentListeners = new Map(), windowListeners = new Map();
  const listen = (registry, name, handler, options) => {
    if (!registry.has(name)) registry.set(name, []);
    registry.get(name).push({ handler, capture: options === true || options?.capture });
  };

  class Element {
    constructor(attrs = {}, text = '') { this.attrs = { ...attrs }; this.textContent = text; }
    getAttribute(name) { return this.attrs[name] ?? null; }
    hasAttribute(name) { return Object.hasOwn(this.attrs, name); }
    setAttribute(name, value) { this.attrs[name] = value; }
    removeAttribute(name) { delete this.attrs[name]; }
    cloneNode() { return new Element(this.attrs, this.textContent); }
    remove() { if (this.parent) this.parent.nodes = this.parent.nodes.filter(node => node !== this); }
    getClientRects() { return [{}]; }
    focus() { h.focus.push(this); }
    matches(selector) { return selector === '.slide-arrow' && this.isArrow; }
    closest() { return null; }
  }
  class Head {
    constructor(slug) {
      this.nodes = [
        new Element({ rel: 'canonical', href: `${ORIGIN}/is/writing/${slug}/` }),
        new Element({ property: 'og:title', content: `Cartoon ${slug}` }),
        new Element({ property: 'og:image', content: imageURL(slug) }),
      ];
      this.nodes.forEach(node => { node.parent = this; });
    }
    querySelectorAll() { return this.nodes.slice(); }
    append(node) { node.parent = this; this.nodes.push(node); }
  }
  class Arrow extends Element {
    constructor(shell, direction, area) {
      const offset = direction === 'next' ? 1 : -1;
      super({ [`data-slide-${direction}`]: '', target: '_self' });
      this.shell = shell;
      this.direction = direction;
      this.area = area;
      this.href = route(SLUGS[SLUGS.indexOf(shell.slug) + offset]);
      this.target = '_self';
      this.isArrow = true;
    }
    closest(selector) {
      if (selector === '.slide-pagination') return this.area === 'pagination' ? {} : null;
      if (selector.includes('data-slide-') || selector === '.slide-arrow') return this;
      return null;
    }
  }
  class Shell extends Element {
    constructor(slug) {
      super({ 'data-first-slide': `${BASE}a/#cartoon` });
      this.slug = slug;
      this.title = new Element({ id: 'slide-title' }, `Cartoon ${slug}`);
      this.image = new Element({ src: `/assets/${slug}.webp` });
      this.position = new Element({ 'aria-label': `Cartoon ${SLUGS.indexOf(slug) + 1} of ${SLUGS.length}` });
      this.arrows = {};
      for (const area of ['stage', 'pagination']) {
        for (const direction of ['previous', 'next']) {
          const index = SLUGS.indexOf(slug) + (direction === 'next' ? 1 : -1);
          if (index >= 0 && index < SLUGS.length) this.arrows[`${area}-${direction}`] = new Arrow(this, direction, area);
        }
      }
      this.stage = {
        contains: node => this.contains(node),
        querySelector: selector => this.arrows[`stage-${selector.includes('next') ? 'next' : 'previous'}`] || null,
      };
    }
    querySelector(selector) {
      if (selector === '.slide-image') return this.image;
      if (selector === '#slide-title') return this.title;
      if (selector === '.slide-position') return this.position;
      if (selector === '.slide-stage') return this.stage;
      if (selector.includes('data-slide-')) return this.arrows[`${selector.includes('pagination') ? 'pagination' : 'stage'}-${selector.includes('next') ? 'next' : 'previous'}`] || null;
      return null;
    }
    querySelectorAll(selector) { return selector === 'img' ? [this.image] : Object.values(this.arrows); }
    contains(node) { return node?.shell === this || node === this.image; }
    cloneNode() { const clone = new Shell(this.slug); clone.attrs = { ...this.attrs }; return clone; }
    replaceWith(next) { assert.equal(this, h.shell); h.shell = next; h.swaps.push(next.slug); }
    after(status) { h.status = status; }
    scrollIntoView() { h.scrolled = this.slug; }
  }
  function parsedDocument(slug) {
    const shell = SLUGS.includes(slug) ? new Shell(slug) : null;
    return { title: `Cartoon ${slug} · Cartoons · ajin.im`, head: new Head(slug), querySelector: selector => selector === 'main.slide-shell' ? shell : null };
  }
  h.shell = new Shell(initial);
  const document = {
    title: `Cartoon ${initial} · Cartoons · ajin.im`, head: new Head(initial), readyState,
    querySelector: selector => selector === '.slide-stage' ? h.shell.stage : selector === 'main.slide-shell' ? h.shell : null,
    createElement: () => new Element(),
    addEventListener: (name, handler, options) => listen(documentListeners, name, handler, options),
  };
  const location = {
    get href() { return currentURL.href; }, get origin() { return currentURL.origin; },
    assign: href => h.assigned.push(href), replace: href => h.replaced.push(href),
  };
  class Image {
    constructor() { this.gate = deferred(); h.images.push(this); }
    decode() { return this.gate.promise; }
    removeAttribute(name) { if (name === 'src') this.cancelled = true; }
  }
  const fetch = (href, { signal }) => {
    const gate = deferred();
    const request = { href, signal, gate, replied: false };
    h.requests.push(request);
    if (!ignoreFetchAbort) signal.addEventListener('abort', () => gate.reject(new Error('Aborted')), { once: true });
    return gate.promise;
  };
  const history = { pushState(_state, _title, href) {
    h.pushes.push({ href, title: document.title, canonical: document.head.nodes.find(node => node.attrs.rel === 'canonical')?.attrs.href });
    currentURL = new URL(href);
  } };
  vm.runInNewContext(SCRIPT, {
    document, location, history, fetch, Image, URL, AbortController,
    DOMParser: class { parseFromString(text) { return parsedDocument(text); } },
    navigator: { connection },
    window: { addEventListener: (name, handler, options) => listen(windowListeners, name, handler, options) },
    setTimeout: (fn, delay) => { const id = ++timerId; h.timers.set(id, { fn, delay }); return id; },
    clearTimeout: id => h.timers.delete(id),
  });
  h.document = document;
  h.location = location;
  h.request = slug => h.requests.findLast(request => new URL(request.href).pathname === `${BASE}${slug}/` && !request.replied);
  h.respond = (slug, { ok = true, body = slug, url } = {}) => {
    const request = h.request(slug);
    assert.ok(request, `No pending fetch for ${slug}`);
    request.replied = true;
    request.gate.resolve({ ok, url: url || request.href, text: async () => body });
    return request;
  };
  h.rejectFetch = slug => { const request = h.request(slug); request.replied = true; request.gate.reject(new Error('Network failed')); };
  h.decode = (slug, fail = false) => {
    const pendingImages = h.images.filter(image => image.src === imageURL(slug) && !image.settled);
    assert.ok(pendingImages.length, `No pending decode for ${slug}`);
    pendingImages.forEach(image => { image.settled = true; if (fail) image.gate.reject(new Error('Decode failed')); else image.gate.resolve(); });
  };
  h.finish = async slug => { h.respond(slug); await flush(); h.decode(slug); await flush(); };
  h.ready = async () => { h.decode(initial); await flush(); };
  h.click = (direction = 'next', options = {}) => {
    const target = options.target || h.shell.arrows[`stage-${direction}`];
    assert.ok(target, `Missing ${direction} arrow`);
    const event = { target, button: 0, defaultPrevented: false, stopped: false,
      preventDefault() { this.defaultPrevented = true; }, stopImmediatePropagation() { this.stopped = true; }, ...options };
    const handlers = documentListeners.get('click') || [];
    for (const { handler } of [...handlers.filter(item => item.capture), ...handlers.filter(item => !item.capture)]) {
      handler(event);
      if (event.stopped) break;
    }
    return event;
  };
  h.pointer = (name, options = {}) => {
    const event = { target: h.shell.image, pointerType: 'touch', pointerId: 1, isPrimary: true,
      clientX: 100, clientY: 100, defaultPrevented: false,
      preventDefault() { this.defaultPrevented = true; }, ...options };
    for (const { handler } of documentListeners.get(name) || []) handler(event);
    return event;
  };
  h.emit = (name, event = {}) => { for (const { handler } of windowListeners.get(name) || []) handler(event); };
  h.popURL = href => { currentURL = new URL(href); h.emit('popstate'); };
  h.pop = slug => h.popURL(route(slug));
  h.nativeLink = href => ({ href, target: '_self', closest: () => null });
  return h;
}

test('destination decode gates the swap and updates title, URL and metadata together', async () => {
  const h = harness({ initial: 'a' });
  assert.equal(h.requests.length, 0, 'warming must wait for the visible artwork');
  await h.ready();
  h.respond('b');
  await flush();
  const click = h.click();
  assert.equal(click.defaultPrevented, true);
  assert.equal(h.shell.slug, 'a');
  assert.equal(h.shell.getAttribute('aria-busy'), 'true');
  assert.equal(h.pushes.length, 0);
  h.decode('b');
  await flush();
  assert.equal(h.shell.slug, 'b');
  assert.equal(h.location.href, route('b'));
  assert.deepEqual(h.assigned, []);
  assert.equal(h.pushes.length, 1);
  assert.deepEqual(h.pushes[0], { href: route('b'), title: 'Cartoon b · Cartoons · ajin.im', canonical: `${ORIGIN}/is/writing/b/` });
  assert.match(h.status.textContent, /Cartoon b.*Cartoon 2 of 5/);
  assert.equal(h.shell.getAttribute('aria-busy'), null);
});

test('a warmed transition, Back and Forward reuse decoded slides without extra history entries', async () => {
  const h = harness({ initial: 'a' });
  await h.ready();
  await h.finish('b');
  h.click();
  await flush();
  h.pop('a');
  await flush();
  assert.equal(h.shell.slug, 'a');
  h.pop('b');
  await flush();
  assert.equal(h.shell.slug, 'b');
  assert.equal(h.pushes.length, 1);
  assert.equal(h.requests.filter(request => request.href.endsWith('/a/')).length, 0);
  assert.equal(h.requests.filter(request => request.href.endsWith('/b/')).length, 1);
  assert.deepEqual(h.assigned, []);
  assert.deepEqual(h.replaced, []);
});

test('the entry alias and first slide URL share the same cached artwork on Back and arrow navigation', async () => {
  const h = harness({ initial: 'a', entryAlias: true });
  const alias = `${ORIGIN}${BASE}#cartoon`;
  await h.ready();
  await h.finish('b');
  h.click();
  await flush();
  h.popURL(alias);
  await flush();
  assert.equal(h.shell.slug, 'a');
  assert.equal(h.location.href, alias);
  assert.equal(h.pushes.length, 1, 'Back must preserve the entry URL without adding history');
  h.click();
  await flush();
  h.click('previous');
  await flush();
  assert.equal(h.shell.slug, 'a');
  assert.equal(h.location.href, route('a'));
  assert.equal(h.requests.filter(request => new URL(request.href).pathname === BASE || request.href.endsWith('/a/')).length, 0);
  assert.equal(h.images.filter(image => image.src === imageURL('a')).length, 1, 'the first image must not be decoded into a second cache entry');
  assert.deepEqual(h.assigned, []);
  assert.deepEqual(h.replaced, []);
});

test('focus stays on the matching arrow, with a heading fallback at the sequence boundary', async () => {
  const h = harness({ initial: 'c' });
  await h.ready();
  await h.finish('d');
  h.click();
  await flush();
  assert.equal(h.focus.at(-1), h.shell.arrows['stage-next']);
  await h.finish('e');
  h.click();
  await flush();
  assert.equal(h.focus.at(-1), h.shell.title);
  assert.equal(h.shell.title.tabIndex, -1);
});

test('fast opposing clicks commit only the last intent, even when both destinations are ready', async () => {
  const h = harness();
  await h.ready();
  await h.finish('a');
  await h.finish('c');
  h.click('next');
  h.click('previous');
  await flush();
  assert.deepEqual(h.swaps, ['a']);
  assert.deepEqual(h.pushes.map(push => push.href), [route('a')]);
});

test('a touch gesture begun on the previous stage cannot advance the newly swapped slide', async () => {
  const h = harness({ connection: { saveData: true } });
  await h.ready();
  h.click();
  const oldImage = h.shell.image;
  h.pointer('pointerdown', { target: oldImage });
  await h.finish('c');
  const up = h.pointer('pointerup', { target: oldImage, clientX: 20 });
  await flush();
  assert.equal(up.defaultPrevented, false);
  assert.equal(h.requests.length, 1, 'releasing an old gesture must not request another cartoon');
  assert.deepEqual(h.swaps, ['c']);
  assert.deepEqual(h.pushes.map(push => push.href), [route('c')]);
  assert.deepEqual(h.assigned, []);
});

test('changing direction aborts obsolete downloads and a late response cannot replace the winner', async () => {
  const h = harness({ ignoreFetchAbort: true });
  await h.ready();
  const obsolete = h.request('c');
  h.click('next');
  h.click('previous');
  assert.equal(obsolete.signal.aborted, true);
  await h.finish('a');
  h.respond('c');
  await flush();
  assert.equal(h.shell.slug, 'a');
  assert.deepEqual(h.swaps, ['a']);
  assert.deepEqual(h.assigned, []);
});

test('only displayed neighbours warm, and old slides are evicted rather than the whole collection retained', async () => {
  const h = harness();
  await h.ready();
  assert.deepEqual(h.requests.map(request => new URL(request.href).pathname).sort(), [`${BASE}a/`, `${BASE}c/`]);
  await h.finish('a');
  await h.finish('c');
  assert.equal(h.requests.length, 2, 'warming a neighbour must not recursively warm its neighbours');
  h.click();
  await flush();
  await h.finish('d');
  h.click();
  await flush();
  h.pop('c');
  await flush();
  assert.equal(h.requests.filter(request => request.href.endsWith('/b/')).length, 1, 'b was evicted after moving to d, then warmed after returning to c');
});

for (const connection of [{ saveData: true }, { effectiveType: '2g' }, { effectiveType: 'slow-2g' }]) {
  test(`data-saving connection skips speculation but still loads an explicitly requested slide: ${JSON.stringify(connection)}`, async () => {
    const h = harness({ connection });
    await h.ready();
    assert.equal(h.requests.length, 0);
    h.click();
    assert.equal(h.requests.length, 1);
    await h.finish('c');
    assert.equal(h.shell.slug, 'c');
    assert.equal(h.requests.length, 1);
  });
}

test('modified, middle-button, download, new-tab, external and full-size links stay native', async () => {
  const h = harness({ connection: { saveData: true } });
  await h.ready();
  for (const options of [{ metaKey: true }, { ctrlKey: true }, { shiftKey: true }, { altKey: true }, { button: 1 }, { defaultPrevented: true }]) {
    const event = h.click('next', options);
    if (!options.defaultPrevented) assert.equal(event.defaultPrevented, false);
  }
  const arrow = h.shell.arrows['stage-next'];
  arrow.setAttribute('download', '');
  assert.equal(h.click().defaultPrevented, false);
  arrow.removeAttribute('download');
  arrow.target = '_blank';
  assert.equal(h.click().defaultPrevented, false);
  arrow.target = '_self';
  arrow.href = 'https://example.com/is/writing/cartoons/slides/c/';
  assert.equal(h.click().defaultPrevented, false);
  assert.equal(h.click('next', { target: h.nativeLink(imageURL('b')) }).defaultPrevented, false);
  assert.equal(h.click('next', { target: h.nativeLink(`${ORIGIN}/is/writing/cartoons/`) }).defaultPrevented, false);
  assert.equal(h.requests.length, 0);
  assert.deepEqual(h.pushes, []);
});

for (const failure of ['network', 'status', 'redirect', 'markup', 'image']) {
  test(`${failure} failure retains the current artwork and falls back to the requested native page`, async () => {
    const h = harness({ connection: { saveData: true } });
    await h.ready();
    h.click();
    if (failure === 'network') h.rejectFetch('c');
    else h.respond('c', { ok: failure !== 'status', body: failure === 'markup' ? 'invalid' : 'c', url: failure === 'redirect' ? `${ORIGIN}/unrelated/` : undefined });
    await flush();
    if (failure === 'image') { h.decode('c', true); await flush(); }
    assert.equal(h.shell.slug, 'b');
    assert.deepEqual(h.assigned, [route('c')]);
    assert.deepEqual(h.pushes, []);
    assert.equal(h.shell.getAttribute('aria-busy'), null);
  });
}

test('an unresolved destination fetch times out, aborts and falls back with the old artwork retained', async () => {
  const h = harness({ connection: { saveData: true } });
  await h.ready();
  h.click();
  const request = h.request('c');
  const timeouts = [...h.timers.values()].filter(timer => timer.delay === 8000);
  assert.equal(timeouts.length, 1);
  timeouts[0].fn();
  await flush();
  assert.equal(request.signal.aborted, true);
  assert.equal(h.shell.slug, 'b');
  assert.equal(h.shell.getAttribute('aria-busy'), null);
  assert.deepEqual(h.assigned, [route('c')]);
  assert.deepEqual(h.swaps, []);
  assert.deepEqual(h.pushes, []);
});

test('a failed Back/Forward load replaces the URL rather than adding a history entry', async () => {
  const h = harness({ connection: { saveData: true } });
  await h.ready();
  h.pop('a');
  h.rejectFetch('a');
  await flush();
  assert.deepEqual(h.replaced, [route('a')]);
  assert.deepEqual(h.assigned, []);
  assert.deepEqual(h.pushes, []);
});

test('leaving the document aborts pending fetches and prevents a late navigation', async () => {
  const h = harness({ ignoreFetchAbort: true });
  await h.ready();
  h.click();
  const request = h.request('c');
  h.emit('pagehide');
  assert.equal(request.signal.aborted, true);
  h.respond('c');
  await flush();
  assert.equal(h.shell.slug, 'b');
  assert.deepEqual(h.pushes, []);
  assert.deepEqual(h.assigned, []);
});

test('leaving before the first image decodes must not start fresh neighbour requests', async () => {
  const h = harness();
  h.emit('pagehide');
  await flush();
  assert.equal(h.requests.length, 0, 'the initial load cleanup must not restart warming after pagehide');
  assert.deepEqual(h.pushes, []);
});

test('persisted pageshow resumes only the cancelled neighbour warming after pagehide', async () => {
  const h = harness();
  await h.ready();
  await h.finish('a');
  const cancelled = h.request('c');
  h.emit('pagehide');
  await flush();
  assert.equal(cancelled.signal.aborted, true);
  assert.equal(h.requests.length, 2);
  h.emit('pageshow', { persisted: false });
  await flush();
  assert.equal(h.requests.length, 2);
  h.emit('pageshow', { persisted: true });
  await flush();
  assert.equal(h.requests.filter(request => request.href.endsWith('/a/')).length, 1, 'a decoded neighbour remains cached');
  assert.equal(h.requests.filter(request => request.href.endsWith('/c/')).length, 2, 'the cancelled neighbour should resume');
  assert.equal(h.request('c').signal.aborted, false);
  await h.finish('c');
  h.emit('pageshow', { persisted: true });
  await flush();
  assert.equal(h.requests.length, 3, 'restoring or finishing warming must not fetch beyond the displayed neighbours');
  assert.equal(h.shell.slug, 'b');
  assert.deepEqual(h.pushes, []);
});

test('neighbour warming waits for window load even when the initial artwork is already decoded', async () => {
  const h = harness({ readyState: 'interactive' });
  await h.ready();
  assert.equal(h.requests.length, 0, 'speculative images must not delay the first window load');
  h.document.readyState = 'complete';
  h.emit('load');
  await flush();
  assert.deepEqual(h.requests.map(request => new URL(request.href).pathname).sort(), [`${BASE}a/`, `${BASE}c/`]);
  assert.deepEqual(h.swaps, []);
});
