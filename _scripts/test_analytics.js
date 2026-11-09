/* Run with: node --test _scripts/test_analytics.js */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const SOURCE = fs.readFileSync(path.join(__dirname, '..', 'analytics.js'), 'utf8');
const ID = 'G-60PV5XGMSX';

function link(href, { target = '', rel = '' } = {}) {
  return {
    target, rel,
    getAttribute: name => name === 'href' ? href : null,
  };
}

function storage(seed = {}, throws = false) {
  const values = new Map(Object.entries(seed));
  const check = () => { if (throws) throw new Error('storage denied'); };
  return {
    values,
    getItem(key) { check(); return values.has(key) ? values.get(key) : null; },
    setItem(key, value) { check(); values.set(key, String(value)); },
    removeItem(key) { check(); values.delete(key); },
  };
}

function run({ origin = 'https://ajin.im', search = '', webdriver = false, store, links = [] } = {}) {
  const appended = [];
  const listeners = new Map();
  const document = {
    readyState: 'complete',
    querySelectorAll: selector => {
      assert.equal(selector, 'a[href]');
      return links;
    },
    addEventListener: (name, handler) => listeners.set(name, handler),
    createElement: tag => ({ tagName: tag }),
    head: { appendChild: node => appended.push(node) },
  };
  const window = { location: { origin, search } };
  const context = {
    window, document, navigator: { webdriver }, localStorage: store || storage(),
    URLSearchParams, Date, encodeURIComponent,
  };
  vm.runInNewContext(SOURCE, context);
  return { window, appended, store: context.localStorage, links, listeners };
}

test('normal production browser loads the existing GA4 property and configuration', () => {
  for (const origin of ['https://ajin.im', 'http://ajin.im']) {
    const result = run({ origin });
    assert.equal(result.appended.length, 1);
    assert.equal(result.appended[0].src, `https://www.googletagmanager.com/gtag/js?id=${ID}`);
    const calls = result.window.dataLayer.map(call => Array.from(call));
    assert.equal(calls[0][0], 'js');
    assert.equal(calls[1][0], 'config');
    assert.equal(calls[1][1], ID);
    assert.equal(calls[1][2].allow_google_signals, false);
    assert.equal(calls[1][2].allow_ad_personalization_signals, false);
  }
});

test('manual opt-out wins over track and track only reverses stored manual opt-out', () => {
  const optedOut = storage({ _notrack: '1' });
  assert.equal(run({ store: optedOut }).appended.length, 0);

  const tracked = storage({ _notrack: '1' });
  assert.equal(run({ search: '?track', store: tracked }).appended.length, 1);
  assert.equal(tracked.values.has('_notrack'), false);

  const both = storage({ _notrack: '1' });
  assert.equal(run({ search: '?notrack&track', store: both }).appended.length, 0);
  assert.equal(both.values.get('_notrack'), '1');
});

test('local, preview, file, port and automation contexts never load GA4', () => {
  for (const origin of [
    'https://ajin.im.evil.example', 'https://ajin.im:8745', 'http://localhost:8745',
    'http://127.0.0.1:8745', 'http://[::1]:8745', 'https://preview.ajin.im', 'null',
  ]) assert.equal(run({ origin }).appended.length, 0, origin);
  assert.equal(run({ webdriver: true }).appended.length, 0);
  assert.equal(run({ origin: 'http://localhost:8745', search: '?track' }).appended.length, 0);
});

test('storage denial fails closed, including the current ?notrack visit', () => {
  assert.equal(run({ store: storage({}, true) }).appended.length, 0);
  assert.equal(run({ search: '?notrack', store: storage({}, true) }).appended.length, 0);
  assert.equal(run({ search: '?track', store: storage({}, true) }).appended.length, 0);
});

test('navigation retargeting remains active when analytics is blocked', () => {
  const ordinary = link('/is/writing/');
  const explicit = link('/is/running/', { target: '_self', rel: 'author' });
  const anchor = link('#all');
  const result = run({ origin: 'http://localhost:8745', links: [ordinary, explicit, anchor] });
  assert.equal(result.appended.length, 0);
  assert.equal(ordinary.target, '_blank');
  assert.equal(ordinary.rel, 'noopener noreferrer');
  assert.equal(explicit.target, '_self');
  assert.equal(explicit.rel, 'author');
  assert.equal(anchor.target, '');
});
