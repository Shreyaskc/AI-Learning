/* Native modal dialog enhancement; ordinary glossary links remain the fallback. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory;
  else factory(document, window);
}(this, function mount(doc, win) {
  const dialog = doc.getElementById('term-dialog');
  const data = doc.getElementById('term-data');
  if (!dialog || !data || typeof dialog.showModal !== 'function') return null;
  let entries;
  try { entries = JSON.parse(data.textContent); } catch (_) { return null; }
  let active = null;
  const closeButton = doc.getElementById('term-close');
  function cleanup() {
    const previous = active;
    active = null;
    if (previous) previous.setAttribute('aria-expanded', 'false');
    const target = previous && previous.isConnected && !previous.closest('[hidden]') ? previous : doc.getElementById('main');
    if (target) target.focus({preventScroll: true});
  }
  function close() {
    if (dialog.open) dialog.close();
    if (active) cleanup();
  }
  function open(trigger) {
    const entry = entries[trigger.dataset.term];
    if (!entry || !entry.definition || !entry.example || trigger.closest('[hidden]')) return false;
    for (let parent = trigger.parentElement; parent; parent = parent.parentElement) {
      if (parent.tagName === 'DETAILS' && !parent.open && !parent.querySelector('summary')?.contains(trigger)) return false;
    }
    if (active) active.setAttribute('aria-expanded', 'false');
    doc.getElementById('term-title').textContent = entry.name;
    doc.getElementById('term-definition').textContent = entry.definition;
    doc.getElementById('term-example-text').textContent = entry.example;
    doc.getElementById('term-glossary').setAttribute('href', trigger.getAttribute('href'));
    active = trigger;
    if (!dialog.open) dialog.showModal();
    trigger.setAttribute('aria-expanded', 'true');
    closeButton.focus({preventScroll: true});
    return true;
  }
  doc.addEventListener('click', event => {
    const trigger = event.target.closest?.('a[data-term]');
    if (trigger && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey && open(trigger)) event.preventDefault();
  });
  closeButton.addEventListener('click', close);
  dialog.addEventListener('cancel', event => { event.preventDefault(); close(); });
  dialog.addEventListener('close', () => { if (active) cleanup(); });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const r = dialog.getBoundingClientRect();
    if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) close();
  });
  win.addEventListener('popstate', close);
  win.addEventListener('hashchange', close);
  win.addEventListener('pagehide', close);
  return {open, close};
}));
