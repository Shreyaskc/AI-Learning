'use strict';
(() => {
  const key = 'ai-fluency-course-v2-progress';
  let studied = [];
  try {
    const value = JSON.parse(localStorage.getItem(key) || '[]');
    if (Array.isArray(value)) studied = value.filter(x => typeof x === 'string');
  } catch (_) { /* Reading still works if storage is unavailable. */ }
  const links = [...document.querySelectorAll('nav [data-lesson]')];
  const coreIds = links.map(a => a.dataset.lesson).filter(id => /^\d{2}-/.test(id));
  const checkbox = document.querySelector('#completed');
  function update() {
    links.forEach(a => a.classList.toggle('done', studied.includes(a.dataset.lesson)));
    const count = coreIds.filter(id => studied.includes(id)).length;
    document.querySelector('#progress').textContent = `${count} of ${coreIds.length} lessons marked studied. Mastery requires the exercises.`;
  }
  if (checkbox) {
    checkbox.checked = studied.includes(checkbox.dataset.id);
    checkbox.addEventListener('change', () => {
      studied = studied.filter(id => id !== checkbox.dataset.id);
      if (checkbox.checked) studied.push(checkbox.dataset.id);
      try { localStorage.setItem(key, JSON.stringify(studied)); } catch (_) { /* No persistence. */ }
      update();
    });
  }
  update();
  document.querySelector('#search').addEventListener('input', event => {
    const words = event.target.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    links.forEach(a => { a.hidden = !words.every(word => a.textContent.toLowerCase().includes(word)); });
  });
  document.querySelector('#menu').addEventListener('click', event => {
    const open = document.body.classList.toggle('menu-open');
    event.currentTarget.setAttribute('aria-expanded', String(open));
  });
})();
