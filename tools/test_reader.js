'use strict';
// Behavioral smoke tests of our script against small DOM/storage doubles.
// This does not substitute for rendered desktop/mobile browser inspection.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
function element(textContent = '', dataset = {}) {
  const classes = new Set();
  return { textContent, dataset, hidden: false, checked: false, handlers: {}, attributes: {},
    addEventListener(type, fn) { this.handlers[type] = fn; },
    setAttribute(key, value) { this.attributes[key] = value; },
    classList: { toggle(name, force) { const next = force === undefined ? !classes.has(name) : force; if (next) classes.add(name); else classes.delete(name); return next; } } };
}
const lesson = element('08 · Tokens, embeddings and transformers', { lesson: '08-transformers' });
const security = element('16 · Security, privacy and responsible AI', { lesson: '16-security-responsibility' });
const extra = element('Glossary', { lesson: 'glossary' });
const controls = { '#completed': element('', { id: '08-transformers' }), '#search': element(), '#menu': element(), '#progress': element() };
let stored = '{invalid JSON';
const body = element();
vm.runInNewContext(fs.readFileSync('app.js', 'utf8'), {
  document: { body, querySelector: s => controls[s], querySelectorAll: () => [lesson, security, extra] },
  localStorage: { getItem: () => stored, setItem: (key, value) => { stored = value; } },
});
assert.match(controls['#progress'].textContent, /0 of 2/);
controls['#completed'].checked = true;
controls['#completed'].handlers.change();
assert.deepEqual(JSON.parse(stored), ['08-transformers']);
assert.match(controls['#progress'].textContent, /1 of 2/);
controls['#search'].handlers.input({ target: { value: 'security privacy' } });
assert.equal(lesson.hidden, true); assert.equal(security.hidden, false); assert.equal(extra.hidden, true);
controls['#menu'].handlers.click({ currentTarget: controls['#menu'] });
assert.equal(controls['#menu'].attributes['aria-expanded'], 'true');

const handlers = {}, deleted = []; let unregisters = 0;
vm.runInNewContext(fs.readFileSync('sw.js', 'utf8'), {
  caches: { keys: async () => ['ai-fluency-v2', 'unrelated-app-cache'], delete: async key => deleted.push(key) },
  self: { addEventListener: (name, fn) => { handlers[name] = fn; }, skipWaiting: async () => {},
    registration: { unregister: async () => { unregisters += 1; } },
    clients: { matchAll: async () => [] } },
});
(async () => {
  let activated;
  handlers.activate({ waitUntil(promise) { activated = promise; } });
  await activated;
  assert.deepEqual(deleted, ['ai-fluency-v2']); assert.equal(unregisters, 1);
  console.log('PASS: reader progress/search/menu and scoped legacy-worker retirement smoke tests (DOM doubles)');
})().catch(error => { console.error(error); process.exitCode = 1; });
