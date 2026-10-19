'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { create, mount, KEY } = require('../practice.js');
const html = fs.readFileSync('practice.html', 'utf8');
const bank = JSON.parse(html.match(/id="practice-data">([\s\S]*?)<\/script>/)[1]);
let checks = 0;
function test(name, fn) { fn(); checks++; console.log('PASS:', name); }
function memory(initial = null) {
  const values = new Map(initial === null ? [] : [[KEY, initial]]);
  return { getItem: key => values.get(key) || null, setItem: (key, value) => values.set(key, value), values };
}

test('69 source-derived questions, including diagnostic and transformer groups', () => {
  assert.equal(bank.length, 69); assert.equal(bank.filter(q => q.topic === '00-start').length, 10);
  assert.equal(bank.filter(q => q.topic === '01-foundations').length, 3);
  assert.equal(bank.filter(q => q.topic === '08-transformers').length, 7);
});
test('reveal is idempotent; only explicit self-rating counts and overwrites', () => {
  const state = create(bank, memory());
  state.rate('got-it'); assert.equal(state.view().reviewed, 0);
  state.reveal(); state.reveal(); assert.equal(state.view().reviewed, 0);
  state.rate('got-it'); state.rate('got-it'); assert.equal(state.view().reviewed, 1);
  state.rate('partly'); assert.equal(state.view().reviewed, 1); assert.equal(state.view().needsReview, 1);
  state.rate('need-practice'); assert.equal(state.view().reviewed, 1);
  state.hide(); assert.equal(state.view().shown, false);
});
test('next/previous hide answers, retain session notes and do not overrun boundaries', () => {
  const storage = memory(); const state = create(bank, storage); const first = state.view().question.id;
  state.attempt('private session notes'); state.reveal(); state.move(1);
  assert.equal(state.view().shown, false); assert.equal(state.view().attempt, '');
  state.move(-1); assert.equal(state.view().question.id, first); assert.equal(state.view().attempt, 'private session notes');
  state.move(-1); assert.equal(state.view().question.id, first);
  assert.ok(!storage.getItem(KEY).includes('private session notes'));
});
test('per-topic resume survives reload; explicit deep link wins', () => {
  const storage = memory(), state = create(bank, storage);
  state.filter('08-transformers', ''); state.move(3); const transformer = state.view().question.id;
  state.filter('01-foundations', ''); state.move(1); const foundations = state.view().question.id;
  state.filter('08-transformers', ''); assert.equal(state.view().question.id, transformer);
  const resumed = create(bank, storage); resumed.route('#topic=01-foundations');
  assert.equal(resumed.view().question.id, foundations);
  resumed.route('#topic=08-transformers&q=' + bank.find(q => q.topic === '08-transformers').id);
  assert.notEqual(resumed.view().question.id, transformer);
});
test('search matches prompts and topics; empty results recover; no hidden-answer search', () => {
  const state = create(bank, memory()); state.filter('all', 'not-a-real-match');
  assert.equal(state.view().question, null); assert.equal(state.view().visible.length, 0);
  state.filter('all', ''); assert.equal(state.view().visible.length, 69);
  state.filter('08-transformers', 'causal'); assert.ok(state.view().visible.length > 0);
  assert.ok(state.view().visible.every(q => q.topic === '08-transformers'));
});
test('reset clears self-checks/resume but leaves course study key and notes alone', () => {
  const storage = memory(); storage.setItem('ai-fluency-course-v2-progress', '["01-foundations"]');
  const state = create(bank, storage); state.reveal(); state.rate('got-it'); state.attempt('notes'); state.reset();
  assert.equal(state.view().reviewed, 0); assert.equal(state.view().shown, false);
  assert.equal(storage.getItem('ai-fluency-course-v2-progress'), '["01-foundations"]');
});
test('corrupt, inaccessible and quota-full storage keep practice usable', () => {
  for (const storage of [memory('{broken'), memory('{"version":1,"ratings":null}'),
    { getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); } },
    { getItem() { return null; }, setItem() { throw new Error('quota'); } }]) {
    const state = create(bank, storage); state.reveal(); state.rate('got-it'); state.move(1);
    assert.ok(state.view().question); assert.equal(state.view().reviewed, 1); assert.ok(state.view().warning);
  }
});
test('unknown/stale URL state cannot select a missing question or expose an answer', () => {
  const state = create(bank, memory()); state.reveal(); state.route('#topic=missing&q=missing');
  assert.equal(state.view().topic, 'all'); assert.ok(state.view().question); assert.equal(state.view().shown, false);
});

// Minimal DOM doubles exercise bindings and history, not browser layout or screen readers.
function harness(storage = memory(), initialHash = '', inaccessibleProperty = false) {
  const nodes = new Map(); const events = {};
  function node(id) {
    if (nodes.has(id)) return nodes.get(id);
    const value = { id, textContent: '', value: '', hidden: false, disabled: false, children: [], attributes: {}, events: {},
      addEventListener(name, fn) { (this.events[name] ||= []).push(fn); },
      emit(name) { (this.events[name] || []).forEach(fn => fn({ target: this })); },
      setAttribute(key, value) { this.attributes[key] = value; },
      replaceChildren() { this.children = []; }, appendChild(child) { this.children.push(child); },
      focus() { doc.activeElement = this; } };
    nodes.set(id, value); return value;
  }
  for (const [, id] of html.matchAll(/id="([^"]+)"/g)) node(id);
  node('practice-data').textContent = JSON.stringify(bank);
  const doc = { activeElement: null, getElementById: node, querySelector: () => node('practice-app'), createElement: tag => ({ tag, textContent: '' }), createTextNode: text => ({ textContent: text }) };
  const stack = [initialHash]; let index = 0;
  const win = { localStorage: storage, location: { hash: initialHash }, addEventListener(name, fn) { (events[name] ||= []).push(fn); },
    history: { replaceState(_state, _unused, hash) { win.location.hash = hash; stack[index] = hash; },
      pushState(_state, _unused, hash) { stack.splice(index + 1); stack.push(hash); index++; win.location.hash = hash; },
      back() { if (index) { index--; win.location.hash = stack[index]; (events.popstate || []).forEach(fn => fn()); } },
      forward() { if (index < stack.length - 1) { index++; win.location.hash = stack[index]; (events.popstate || []).forEach(fn => fn()); } } } };
  if (inaccessibleProperty) Object.defineProperty(win, 'localStorage', { get() { throw new Error('property blocked'); } });
  const state = mount(doc, win); return { node, doc, win, state, storage };
}
test('UI attempt → reveal → self-check → next has explicit focus and hidden-state changes', () => {
  const h = harness(); assert.equal(h.node('practice-answer').hidden, true);
  h.node('practice-reveal').emit('click'); assert.equal(h.node('practice-answer').hidden, false);
  assert.equal(h.node('practice-reveal').attributes['aria-expanded'], 'true'); assert.equal(h.doc.activeElement.id, 'practice-answer-title');
  h.node('practice-partly').emit('click'); assert.equal(h.state.view().reviewed, 1);
  h.node('practice-reveal').emit('click'); assert.equal(h.node('practice-answer').hidden, true); assert.equal(h.doc.activeElement.id, 'practice-reveal');
  h.node('practice-next').emit('click'); assert.equal(h.doc.activeElement.id, 'practice-question'); assert.equal(h.node('practice-answer').hidden, true);
});
test('browser back/forward restore exact question and keep answers hidden', () => {
  const h = harness(); const first = h.state.view().question.id; h.node('practice-next').emit('click');
  const second = h.state.view().question.id; h.node('practice-reveal').emit('click'); h.win.history.back();
  assert.equal(h.state.view().question.id, first); assert.equal(h.node('practice-answer').hidden, true);
  h.win.history.forward(); assert.equal(h.state.view().question.id, second); assert.equal(h.node('practice-answer').hidden, true);
});
test('UI empty search, clear filters and reset confirmation/cancel work', () => {
  const h = harness(); h.node('practice-reveal').emit('click'); h.node('practice-got-it').emit('click');
  h.node('practice-reset').emit('click'); assert.equal(h.node('practice-reset-confirm').hidden, false);
  h.node('practice-reset-no').emit('click'); assert.equal(h.state.view().reviewed, 1);
  h.node('practice-reset').emit('click'); h.node('practice-reset-yes').emit('click'); assert.equal(h.state.view().reviewed, 0);
  h.node('practice-search').value = 'unmatchable-phrase'; h.node('practice-search').emit('input');
  assert.equal(h.node('practice-empty').hidden, false); assert.equal(h.node('practice-card').hidden, true);
  h.node('practice-empty-clear').emit('click'); assert.equal(h.node('practice-card').hidden, false); assert.equal(h.doc.activeElement.id, 'practice-topic');
});
test('UI localStorage property denial is handled before the first render', () => {
  const h = harness(memory(), '', true); assert.equal(h.node('practice-interactive').hidden, false);
  assert.equal(h.node('practice-storage').hidden, false); h.node('practice-reveal').emit('click');
  h.node('practice-need-practice').emit('click'); assert.equal(h.state.view().reviewed, 1);
});
test('UI topic changes resume each topic and respect a direct question link', () => {
  const chosen = bank.find(q => q.topic === '08-transformers');
  const h = harness(memory(), '#topic=08-transformers&q=' + chosen.id);
  assert.equal(h.state.view().question.id, chosen.id); h.node('practice-next').emit('click');
  const second = h.state.view().question.id;
  h.node('practice-topic').value = '01-foundations'; h.node('practice-topic').emit('change');
  assert.equal(h.state.view().question.topic, '01-foundations');
  h.node('practice-topic').value = '08-transformers'; h.node('practice-topic').emit('change');
  assert.equal(h.state.view().question.id, second); assert.equal(h.node('practice-answer').hidden, true);
  assert.equal(h.doc.activeElement.id, 'practice-question');
});
console.log(`PASS: ${checks} Q&A state/UI behavioral groups (DOM doubles; no rendered/mobile QA claim)`);
