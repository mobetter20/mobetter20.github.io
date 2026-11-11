/* No real share sheet or clipboard is used. Run: node --test _scripts/test_share.js */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const SOURCE = fs.readFileSync(path.join(__dirname, '..', 'assets', 'paper', 'share.js'), 'utf8');
const FIRST = { title: 'First cartoon', url: 'https://ajin.im/is/writing/first/' };
const SECOND = { title: 'Second cartoon', url: 'https://ajin.im/is/writing/second/' };

function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}
const failure = name => Object.assign(new Error(name), { name });

function harness({ share, canShare, writeText, data = FIRST } = {}) {
  const h = { shares: [], copies: [], capabilities: [], timers: new Map(), groups: [], inputs: [], focus: [] };
  let timerID = 0, mutationCallback;
  const handlers = new Map();
  class Node {
    constructor(className = '', group = null) {
      this.className = className;
      this.group = group;
      this.attrs = {};
      this.nodeType = 1;
      this.textContent = '';
    }
    get isConnected() { return !!this.group?.connected; }
    getAttribute(name) { return this.attrs[name] ?? null; }
    setAttribute(name, value) { this.attrs[name] = String(value); }
    removeAttribute(name) { delete this.attrs[name]; }
    matches(selector) { return selector === `.${this.className}`; }
    closest(selector) {
      if (this.matches(selector)) return this;
      return selector === '.piece-share' ? this.group : null;
    }
    querySelectorAll() { return []; }
    remove() { if (this.group) this.group.children = this.group.children.filter(node => node !== this); this.group = null; }
    focus() { assert.equal(this.isConnected, true, 'must not focus a detached control'); h.focus.push(this); }
    select() { this.selected = true; }
  }
  class Group extends Node {
    constructor(piece) {
      super('piece-share');
      this.group = this;
      this.connected = true;
      this.hidden = true;
      this.button = new Node('share-button', this);
      this.button.hidden = true;
      this.button.disabled = false;
      this.button.textContent = 'Share';
      this.button.setAttribute('data-share-title', piece.title);
      this.button.setAttribute('data-share-url', piece.url);
      this.status = new Node('share-status', this);
      this.children = [this.button, this.status];
    }
    querySelector(selector) { return this.children.find(node => node.matches(selector)) || null; }
    contains(node) { return this.children.includes(node); }
    append(node) { node.group = this; this.children.push(node); }
  }
  h.group = new Group(data);
  h.groups.push(h.group);
  const navigator = {};
  if (share) navigator.share = payload => { h.shares.push({ ...payload }); return share(payload); };
  if (canShare) navigator.canShare = payload => { h.capabilities.push({ ...payload }); return canShare(payload); };
  if (writeText) navigator.clipboard = { writeText: text => { h.copies.push(text); return writeText(text); } };
  const document = {
    body: {},
    querySelectorAll: selector => { assert.equal(selector, '.piece-share'); return h.groups.filter(group => group.connected); },
    addEventListener: (name, handler) => handlers.set(name, handler),
    createElement: name => { assert.equal(name, 'input'); const field = new Node(); h.inputs.push(field); return field; },
  };
  vm.runInNewContext(SOURCE, {
    document, navigator, URL,
    MutationObserver: class {
      constructor(callback) { mutationCallback = callback; }
      observe(target, options) {
        assert.equal(target, document.body);
        assert.equal(options.childList, true);
        assert.equal(options.subtree, true);
      }
    },
    setTimeout: (fn, delay) => { const id = ++timerID; h.timers.set(id, { fn, delay }); return id; },
    clearTimeout: id => h.timers.delete(id),
  });
  h.click = (group = h.group) => handlers.get('click')({
    target: group.button, defaultPrevented: false,
    preventDefault() { this.defaultPrevented = true; },
  });
  h.add = (piece = SECOND, clonedFrom = null) => {
    const group = new Group(piece);
    if (clonedFrom) {
      group.hidden = clonedFrom.hidden;
      group.button.hidden = clonedFrom.button.hidden;
      group.button.disabled = clonedFrom.button.disabled;
      group.button.attrs = { ...clonedFrom.button.attrs, 'data-share-title': piece.title, 'data-share-url': piece.url };
      group.status.textContent = clonedFrom.status.textContent;
      const sourceField = clonedFrom.querySelector('.share-url');
      if (sourceField) {
        const clonedField = new Node('share-url');
        clonedField.value = sourceField.value;
        group.append(clonedField);
      }
    }
    h.groups.push(group);
    mutationCallback([{ addedNodes: [group] }]);
    return group;
  };
  h.repeatMutation = group => mutationCallback([{ addedNodes: [group] }]);
  h.resetFeedback = () => {
    for (const [id, timer] of [...h.timers]) { h.timers.delete(id); timer.fn(); }
  };
  return h;
}

test('native sharing uses only the canonical URL and actual title, then returns quietly', async () => {
  const h = harness({ share: async () => {}, canShare: () => true });
  assert.equal(h.group.hidden, false);
  assert.equal(h.group.button.hidden, false);
  assert.equal(h.group.button.textContent, 'Share');
  await h.click();
  assert.deepEqual(h.shares, [FIRST]);
  assert.ok(h.capabilities.every(payload => payload.title === FIRST.title && payload.url === FIRST.url));
  assert.deepEqual(h.copies, []);
  assert.equal(h.group.status.textContent, '');
  assert.equal(h.group.button.disabled, false);
  assert.equal(h.group.button.getAttribute('aria-busy'), null);
});

test('native cancellation stays silent and never copies the link', async () => {
  const h = harness({ share: async () => { throw failure('AbortError'); }, writeText: async () => {} });
  await h.click();
  assert.equal(h.shares.length, 1);
  assert.deepEqual(h.copies, []);
  assert.equal(h.group.status.textContent, '');
  assert.equal(h.inputs.length, 0);
  assert.equal(h.group.button.disabled, false);
});

test('native denial falls back to clipboard without claiming a successful share', async () => {
  const h = harness({ share: async () => { throw failure('NotAllowedError'); }, writeText: async () => {} });
  await h.click();
  assert.deepEqual(h.shares, [FIRST]);
  assert.deepEqual(h.copies, [FIRST.url]);
  assert.equal(h.group.status.textContent, 'Copied');
  assert.equal(h.group.button.textContent, 'Share');
});

for (const capability of [() => false, () => { throw failure('TypeError'); }]) {
  test(`unavailable native payload support exposes Copy link (${capability.toString()})`, async () => {
    const h = harness({ share: async () => {}, canShare: capability, writeText: async () => {} });
    assert.equal(h.group.button.textContent, 'Copy link');
    await h.click();
    assert.deepEqual(h.shares, []);
    assert.deepEqual(h.copies, [FIRST.url]);
    assert.deepEqual(h.capabilities[0], FIRST);
  });
}

test('Copy link appears without native sharing and reports Copied only after the write resolves', async () => {
  const copy = deferred();
  const h = harness({ writeText: () => copy.promise });
  assert.equal(h.group.button.textContent, 'Copy link');
  const pending = h.click();
  assert.equal(h.group.button.disabled, true);
  assert.equal(h.group.status.textContent, '');
  assert.equal(h.timers.size, 0);
  copy.resolve();
  await pending;
  assert.equal(h.group.status.textContent, 'Copied');
  assert.equal(h.group.button.disabled, false);
  assert.equal(h.timers.size, 1);
  h.resetFeedback();
  assert.equal(h.group.status.textContent, '');
  assert.equal(h.group.button.textContent, 'Copy link');
});

for (const writeText of [undefined, async () => { throw failure('NotAllowedError'); }]) {
  test(`unavailable or denied clipboard reveals an accessible manual-copy field (${writeText ? 'denied' : 'missing'})`, async () => {
    const h = harness({ writeText });
    await h.click();
    const field = h.group.querySelector('.share-url');
    assert.ok(field);
    assert.equal(field.type, 'text');
    assert.equal(field.readOnly, true);
    assert.equal(field.value, FIRST.url);
    assert.equal(field.getAttribute('aria-label'), 'Link to this piece');
    assert.equal(field.selected, true);
    assert.equal(h.focus.at(-1), field);
    assert.equal(h.group.status.textContent, 'Copy this link:');
    assert.equal(h.group.button.disabled, false);
  });
}

test('rapid clicks share only once and capture the original data before any async completion', async () => {
  const native = deferred();
  const h = harness({ share: () => native.promise });
  const first = h.click();
  h.group.button.setAttribute('data-share-title', SECOND.title);
  h.group.button.setAttribute('data-share-url', SECOND.url);
  await h.click();
  assert.deepEqual(h.shares, [FIRST]);
  assert.equal(h.group.button.disabled, true);
  native.resolve();
  await first;
  assert.equal(h.group.status.textContent, '');
});

test('new slide controls use their own canonical data and initialize once', async () => {
  const copy = deferred();
  const h = harness({ writeText: () => copy.promise });
  const second = h.add();
  const pending = h.click(second);
  h.repeatMutation(second);
  assert.equal(second.button.disabled, true, 'a repeated mutation must not unlock an active operation');
  assert.deepEqual(h.copies, [SECOND.url]);
  copy.resolve();
  await pending;
  assert.equal(second.status.textContent, 'Copied');
  assert.equal(h.group.status.textContent, '');
});

test('late clipboard completion on a detached slide does not affect its replacement', async () => {
  const copy = deferred();
  const h = harness({ writeText: () => copy.promise });
  const pending = h.click();
  h.group.connected = false;
  const second = h.add();
  copy.resolve();
  await pending;
  assert.equal(second.status.textContent, '');
  assert.equal(second.button.disabled, false);
  assert.equal(h.timers.size, 0);
  assert.equal(h.focus.length, 0);
});

test('late native failure or clipboard denial on a detached slide neither copies nor focuses another slide', async () => {
  const native = deferred();
  const h = harness({ share: () => native.promise, writeText: async () => {} });
  const pending = h.click();
  h.group.connected = false;
  const second = h.add();
  native.reject(failure('NotAllowedError'));
  await pending;
  assert.deepEqual(h.copies, []);
  assert.equal(second.status.textContent, '');
  assert.equal(h.focus.length, 0);

  const copy = deferred();
  const rejected = harness({ writeText: () => copy.promise });
  const copying = rejected.click();
  rejected.group.connected = false;
  rejected.add();
  copy.reject(failure('NotAllowedError'));
  await copying;
  assert.equal(rejected.inputs.length, 0);
  assert.equal(rejected.focus.length, 0);
});

test('cloned busy or feedback markup resets to a fresh enabled control', async () => {
  const native = deferred();
  const h = harness({ share: () => native.promise });
  const pending = h.click();
  h.group.status.textContent = 'Copied';
  const clone = h.add(SECOND, h.group);
  assert.equal(clone.hidden, false);
  assert.equal(clone.button.hidden, false);
  assert.equal(clone.button.disabled, false);
  assert.equal(clone.button.getAttribute('aria-busy'), null);
  assert.equal(clone.status.textContent, '');
  native.resolve();
  await pending;

  const manual = harness();
  await manual.click();
  assert.ok(manual.group.querySelector('.share-url'));
  const manualClone = manual.add(SECOND, manual.group);
  assert.equal(manualClone.querySelector('.share-url'), null);
  assert.equal(manualClone.status.textContent, '');
  assert.equal(manualClone.button.textContent, 'Copy link');
});

test('invalid or off-origin URLs cannot reach any sharing or clipboard API', async () => {
  for (const url of [
    'http://ajin.im/is/writing/first/', 'https://ajin.im.evil.example/first/',
    'https://www.ajin.im/first/', 'https://ajin.im:8745/first/',
    'https://name@ajin.im/first/', '/is/writing/first/', 'javascript:alert(1)',
  ]) {
    const h = harness({ data: { ...FIRST, url }, share: async () => {}, writeText: async () => {} });
    await h.click();
    assert.equal(h.group.hidden, true, url);
    assert.equal(h.group.button.hidden, true, url);
    assert.deepEqual(h.shares, []);
    assert.deepEqual(h.copies, []);
  }
  const h = harness({ share: async () => {}, writeText: async () => {} });
  h.group.button.setAttribute('data-share-url', 'https://evil.example/');
  await h.click();
  assert.deepEqual(h.shares, []);
  assert.deepEqual(h.copies, []);
});
