// URL migration must retain puzzle selection, anchors and browser history.
const test = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const script = readFileSync(path.join(root, 'is/building/bird-to-bird/redirect.js'), 'utf8');
const pages = [
  ['index.html', '/is/building/b2b/'],
  ['daily/index.html', '/is/building/b2b/daily/'],
  ['credits.html', '/is/building/b2b/credits.html'],
];
for (const [file, targetPath] of pages) {
  test(`old ${file} keeps its route, query and fragment without adding history`, () => {
    const html = readFileSync(path.join(root, 'is/building/bird-to-bird', file), 'utf8');
    const href = html.match(/id="new-url" href="([^"]+)"/)[1];
    assert.equal(href, targetPath);
    assert.match(html, /src="\/is\/building\/bird-to-bird\/redirect\.js" defer/);
    assert.match(html, /name="robots" content="noindex"/);
    assert.ok(html.includes(`<noscript><meta http-equiv="refresh" content="0;url=${targetPath}"></noscript>`));
    for (const [search, hash] of [
      ['', ''],
      ['?mode=playtest&puzzle=bird-023&v=daily-4', '#bird-detail'],
      ['?date=2026-11-18', '#history'],
      ['?date=2026-11-18&date=2026-11-19&note=a%20b', '#a%20b'],
    ]) {
      const link = {href: new URL(href, 'https://ajin.im').href};
      const replacements = [];
      vm.runInNewContext(script, {
        URL,
        document: {getElementById(id) { assert.equal(id, 'new-url'); return link; }},
        location: {search, hash, replace(url) { replacements.push(url); }},
      });
      assert.deepEqual(replacements, [`https://ajin.im${targetPath}${search}${hash}`]);
      assert.equal(link.href, replacements[0]);
    }
  });
}
test('old manifest is retired and current release still has its integrity record', () => {
  const {existsSync} = require('node:fs');
  assert.equal(existsSync(path.join(root, 'is/building/bird-to-bird/manifest.json')), false);
  assert.equal(existsSync(path.join(root, 'is/building/b2b/manifest.json')), true);
});
