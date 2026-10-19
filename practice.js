'use strict';
// State is exported for zero-dependency behavioral tests; the same state drives the UI.
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.AIPractice = api;
  if (typeof document !== 'undefined' && document.querySelector('#practice-app')) api.mount(document, window);
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  const KEY = 'ai-fluency-qa-v1';
  function create(bank, storage) {
    const byId = new Map(bank.map(q => [q.id, q]));
    let saved = {}, warning = '', topic = 'all', search = '', selected = null, shown = false;
    const attempts = new Map();
    try {
      const raw = storage.getItem(KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (!parsed || parsed.version !== 1 || typeof parsed.ratings !== 'object' || !parsed.ratings) throw new Error('invalid progress');
        saved = parsed;
      }
    } catch (_) { warning = 'Saved progress is unavailable. Practice still works for this session.'; }
    let lastByTopic = Object.fromEntries(Object.entries(saved.lastByTopic || {}).filter(([key, id]) => byId.has(id) && (key === 'all' || byId.get(id).topic === key)));
    let ratings = Object.fromEntries(Object.entries(saved.ratings || {}).filter(([id, value]) => byId.has(id) && ['got-it', 'partly', 'need-practice'].includes(value)));
    selected = byId.has(saved.last) ? saved.last : (bank[0] || {}).id || null;
    function list() {
      const words = search.toLowerCase().trim().split(/\s+/).filter(Boolean);
      return bank.filter(q => (topic === 'all' || q.topic === topic) && words.every(word => `${q.question} ${q.topicTitle}`.toLowerCase().includes(word)));
    }
    function persist() {
      if (selected) lastByTopic[topic] = selected;
      try { storage.setItem(KEY, JSON.stringify({ version: 1, ratings, last: selected, lastByTopic })); }
      catch (_) { warning = 'Progress could not be saved. Your self-checks still work for this session.'; }
    }
    function ensure(preferred) {
      const visible = list();
      const next = visible.some(q => q.id === preferred) ? preferred : (visible[0] || {}).id || null;
      if (next !== selected) shown = false;
      selected = next;
    }
    return {
      view() {
        const visible = list(); const question = byId.get(selected) || null;
        return { question, visible, topic, search, shown, warning,
          index: visible.findIndex(q => q.id === selected), rating: ratings[selected] || null,
          attempt: attempts.get(selected) || '', reviewed: Object.keys(ratings).length,
          needsReview: Object.values(ratings).filter(value => value !== 'got-it').length, total: bank.length };
      },
      filter(nextTopic, nextSearch) {
        topic = nextTopic === 'all' || bank.some(q => q.topic === nextTopic) ? nextTopic : 'all';
        search = String(nextSearch || '').slice(0, 300); ensure(lastByTopic[topic] || selected); shown = false; persist();
      },
      route(hash) {
        const params = new URLSearchParams(String(hash || '').replace(/^#/, ''));
        topic = params.get('topic') || 'all';
        if (topic !== 'all' && !bank.some(q => q.topic === topic)) topic = 'all';
        search = (params.get('search') || '').slice(0, 300);
        ensure(params.get('q') || lastByTopic[topic] || selected); shown = false; persist();
      },
      hash() {
        const params = new URLSearchParams(); if (topic !== 'all') params.set('topic', topic);
        if (search) params.set('search', search); if (selected) params.set('q', selected);
        return '#' + params.toString();
      },
      select(id) { if (list().some(q => q.id === id)) { selected = id; shown = false; persist(); } },
      move(delta) {
        const visible = list(); const index = visible.findIndex(q => q.id === selected);
        if (index >= 0 && visible[index + delta]) { selected = visible[index + delta].id; shown = false; persist(); }
      },
      reveal() { if (selected) shown = true; },
      hide() { shown = false; },
      attempt(text) { if (selected) attempts.set(selected, String(text)); },
      rate(value) { if (selected && shown && ['got-it', 'partly', 'need-practice'].includes(value)) { ratings[selected] = value; persist(); } },
      reset() { ratings = {}; lastByTopic = {}; selected = (list()[0] || {}).id || null; shown = false; persist(); },
    };
  }
  function mount(doc, win) {
    const $ = id => doc.getElementById(id);
    const bank = JSON.parse($('practice-data').textContent);
    let storage;
    // Accessing the localStorage property itself can fail in private/restricted contexts.
    try { storage = win.localStorage; } catch (_) { storage = { getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); } }; }
    const state = create(bank, storage);
    $('practice-interactive').hidden = false;
    if (win.location.hash) state.route(win.location.hash);
    function setRich(id, value) {
      const node = $(id); node.replaceChildren();
      String(value).split(/(`[^`]+`)/g).forEach(part => {
        if (part.startsWith('`') && part.endsWith('`')) { const code = doc.createElement('code'); code.textContent = part.slice(1, -1); node.appendChild(code); }
        else node.appendChild(doc.createTextNode(part));
      });
    }
    function render(focus) {
      const view = state.view(), q = view.question;
      $('practice-topic').value = view.topic; $('practice-search').value = view.search;
      $('practice-results').textContent = `${view.visible.length} questions in these results. Topic and search filter the questions, not the hidden answers.`;
      $('practice-count').textContent = `${view.reviewed} of ${view.total} self-checked · ${view.needsReview} marked for review`;
      $('practice-storage').hidden = !view.warning; $('practice-storage').textContent = view.warning;
      $('practice-card').hidden = !q; $('practice-empty').hidden = !!q;
      if (!q) return;
      $('practice-topic-name').textContent = q.topicTitle;
      $('practice-position').textContent = `Question ${view.index + 1} of ${view.visible.length}`;
      setRich('practice-question', q.question);
      $('practice-attempt').value = view.attempt;
      $('practice-answer').hidden = !view.shown;
      $('practice-reveal').textContent = view.shown ? 'Hide answer' : 'Show answer';
      $('practice-reveal').setAttribute('aria-expanded', String(view.shown));
      setRich('practice-answer-text', q.answer);
      setRich('practice-explanation', q.explanation || 'The source gives a concise answer here. Revisit the lesson’s worked examples to check your reasoning.');
      $('practice-lesson').setAttribute('href', q.lesson);
      $('practice-read-before').setAttribute('href', q.lesson);
      ['got-it', 'partly', 'need-practice'].forEach(value => $('practice-' + value).setAttribute('aria-pressed', String(view.rating === value)));
      $('practice-rating').textContent = view.rating ? ({'got-it': 'Got it — revisit later to check retention.', 'partly': 'Partly — keep this question in your review list.', 'need-practice': 'Need practice — revisit the lesson and try again.'}[view.rating] + ' This is your self-assessment, not a test score.') : 'Choose a self-check after comparing your reasoning.';
      $('practice-previous').disabled = view.index <= 0;
      $('practice-next').disabled = view.index >= view.visible.length - 1;
      $('practice-nav-status').textContent = `${view.index + 1} / ${view.visible.length}`;
      $('practice-end').hidden = view.index !== view.visible.length - 1;
      if (focus === 'question') $('practice-question').focus();
      if (focus === 'answer') $('practice-answer-title').focus();
    }
    function navigate(action, focus = 'question', replace = false) {
      action(); const hash = state.hash();
      if (win.location.hash !== hash) win.history[replace ? 'replaceState' : 'pushState'](null, '', hash);
      render(focus);
    }
    $('practice-topic').addEventListener('change', () => navigate(() => state.filter($('practice-topic').value, $('practice-search').value)));
    $('practice-search').addEventListener('input', () => navigate(() => state.filter($('practice-topic').value, $('practice-search').value), null, true));
    function clear() { navigate(() => state.filter('all', '')); $('practice-topic').focus(); }
    $('practice-clear').addEventListener('click', clear); $('practice-empty-clear').addEventListener('click', clear);
    $('practice-attempt').addEventListener('input', () => state.attempt($('practice-attempt').value));
    $('practice-reveal').addEventListener('click', () => { const shown = state.view().shown; shown ? state.hide() : state.reveal(); render(shown ? null : 'answer'); if (shown) $('practice-reveal').focus(); });
    $('practice-previous').addEventListener('click', () => navigate(() => state.move(-1)));
    $('practice-next').addEventListener('click', () => navigate(() => state.move(1)));
    ['got-it', 'partly', 'need-practice'].forEach(value => $('practice-' + value).addEventListener('click', () => { state.rate(value); render(); }));
    $('practice-reset').addEventListener('click', () => { $('practice-reset-confirm').hidden = false; $('practice-reset-yes').focus(); });
    $('practice-reset-no').addEventListener('click', () => { $('practice-reset-confirm').hidden = true; $('practice-reset').focus(); });
    $('practice-reset-yes').addEventListener('click', () => { $('practice-reset-confirm').hidden = true; navigate(() => state.reset()); });
    win.addEventListener('popstate', () => { state.route(win.location.hash); render('question'); });
    win.addEventListener('hashchange', () => { state.route(win.location.hash); render('question'); });
    win.history.replaceState(null, '', state.hash()); render();
    return state;
  }
  return { create, mount, KEY };
});
