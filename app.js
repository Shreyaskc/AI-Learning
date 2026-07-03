// ─── AI Fluency app: router, progress, quiz, flashcards, glossary ──────────

const STORE_KEY = "ai-fluency-v1";
let store = JSON.parse(localStorage.getItem(STORE_KEY) || "{}");
store.done = store.done || {};      // lessonId -> true
store.quiz = store.quiz || {};      // moduleId -> best score
store.cards = store.cards || {};    // term -> { box, last }
store.last = store.last || null;    // last visited lesson route
store.theme = store.theme || "dark"; // "dark" | "light"
function save() { localStorage.setItem(STORE_KEY, JSON.stringify(store)); }

const $main = () => document.querySelector(".main");
const $side = () => document.querySelector(".sidebar");

// ─── theme ───
function applyTheme(theme) {
  store.theme = theme;
  save();
  if (theme === "light") document.documentElement.setAttribute("data-theme", "light");
  else document.documentElement.removeAttribute("data-theme");
  document.querySelectorAll(".theme-toggle").forEach((btn) => { btn.textContent = theme === "light" ? "☀️" : "🌙"; });
}
function toggleTheme() { applyTheme(store.theme === "light" ? "dark" : "light"); }
document.addEventListener("click", (e) => { if (e.target.closest(".theme-toggle")) toggleTheme(); });
applyTheme(store.theme);

// ─── helpers ───
function moduleProgress(m) {
  const total = m.lessons.length + 1; // +1 for quiz
  let done = m.lessons.filter((l) => store.done[l.id]).length;
  if (store.quiz[m.id] !== undefined && store.quiz[m.id] / m.quiz.length >= 0.8) done += 1;
  return { done, total, pct: Math.round((done / total) * 100) };
}
function overallProgress() {
  let d = 0, t = 0;
  MODULES.forEach((m) => { const p = moduleProgress(m); d += p.done; t += p.total; });
  return { d, t, pct: Math.round((d / t) * 100) };
}
function findNext() {
  for (const m of MODULES) {
    for (const l of m.lessons) if (!store.done[l.id]) return { type: "lesson", m, l };
    if (!(store.quiz[m.id] !== undefined && store.quiz[m.id] / m.quiz.length >= 0.8)) return { type: "quiz", m };
  }
  return null;
}

// ─── sidebar ───
function renderSidebar() {
  const route = location.hash;
  $side().innerHTML = `
    <div class="brand-row">
      <div class="brand" onclick="location.hash='#/'">🧭 AI Fluency<small>from tokens to agents</small></div>
      <button class="theme-toggle" aria-label="Toggle light/dark theme">${store.theme === "light" ? "☀️" : "🌙"}</button>
    </div>
    <div class="nav-part nav-part-first">Part 1 — Fluency Foundations</div>
    ${MODULES.map((m) => {
      const p = moduleProgress(m);
      const section = `<div class="nav-section">
        <div class="nav-mod" onclick="location.hash='#/lesson/${m.id}/${m.lessons[0].id}'">
          <span>${m.emoji}</span> ${m.title} <span class="prog">${p.done}/${p.total}</span>
        </div>
        <div class="nav-lessons">
          ${m.lessons.map((l) => `
            <div class="nav-lesson ${route === `#/lesson/${m.id}/${l.id}` ? "on" : ""}" onclick="location.hash='#/lesson/${m.id}/${l.id}'">
              <span class="tick ${store.done[l.id] ? "done-tick" : ""}">${store.done[l.id] ? "✔" : "○"}</span> ${l.title}
            </div>`).join("")}
          <div class="nav-lesson ${route === `#/quiz/${m.id}` ? "on" : ""}" onclick="location.hash='#/quiz/${m.id}'">
            <span class="tick ${store.quiz[m.id] !== undefined && store.quiz[m.id] / m.quiz.length >= 0.8 ? "done-tick" : ""}">${store.quiz[m.id] !== undefined && store.quiz[m.id] / m.quiz.length >= 0.8 ? "✔" : "🏁"}</span>
            Quiz${store.quiz[m.id] !== undefined ? ` — best ${store.quiz[m.id]}/${m.quiz.length}` : ""}
          </div>
        </div>
      </div>`;
      return m.id === "m7" ? `<div class="nav-part">Part 2 — Under the Hood</div>${section}` : section;
    }).join("")}
    <div class="nav-extra">
      <div class="nav-mod" onclick="location.hash='#/cards'">🃏 Flashcards <span class="prog">${dueCards().length} due</span></div>
      <div class="nav-mod" onclick="location.hash='#/glossary'">📖 Glossary <span class="prog">${GLOSSARY.length}</span></div>
    </div>`;
}

// ─── dashboard ───
function renderDashboard() {
  const o = overallProgress();
  const next = findNext();
  const mastered = Object.values(store.cards).filter((c) => c.box >= 3).length;
  $main().innerHTML = `
    <div class="hero">
      <h1>🧭 AI Fluency</h1>
      <p>${MODULES.length} modules, from "what even is a token" to the real attention math and how inference gets engineered fast. Interactive demos, quizzes, flashcards. Your progress saves automatically.</p>
    </div>
    ${next ? `
    <div class="continue-card" onclick="location.hash='${next.type === "lesson" ? `#/lesson/${next.m.id}/${next.l.id}` : `#/quiz/${next.m.id}`}'">
      <span style="font-size:1.8em">${next.m.emoji}</span>
      <div><b>${o.d === 0 ? "Start here" : "Continue"}:</b> ${next.type === "lesson" ? next.l.title : `${next.m.title} quiz`}<br>
      <span style="color:var(--muted);font-size:0.85em">${next.m.title}</span></div>
      <span class="spacer"></span><span style="font-size:1.4em">→</span>
    </div>` : `
    <div class="continue-card"><span style="font-size:1.8em">🎓</span><div><b>Course complete!</b> You passed every quiz. Keep the flashcards warm and go have opinions.</div></div>`}
    <div class="stat-row">
      <div class="stat"><b>${o.pct}%</b><span>course complete</span></div>
      <div class="stat"><b>${Object.keys(store.done).length}</b><span>lessons finished</span></div>
      <div class="stat"><b>${mastered}/${GLOSSARY.length}</b><span>terms mastered</span></div>
      <div class="stat"><b>${dueCards().length}</b><span>flashcards due</span></div>
    </div>
    <div class="part-label">Part 1 — Fluency Foundations</div>
    <div class="dash-grid">
      ${MODULES.map((m) => {
        const p = moduleProgress(m);
        const card = `<div class="mod-card" onclick="location.hash='#/lesson/${m.id}/${m.lessons[0].id}'">
          <span class="mod-emoji">${m.emoji}</span>
          <h3>${m.title}</h3>
          <div class="sub">${m.subtitle}</div>
          <div class="pbar"><div style="width:${p.pct}%"></div></div>
          <div class="mod-meta"><span>${m.lessons.length} lessons + quiz</span><span>${p.pct}%</span></div>
        </div>`;
        return m.id === "m7" ? `</div><div class="part-label">Part 2 — Under the Hood</div><div class="dash-grid">${card}` : card;
      }).join("")}
    </div>`;
}

// ─── lesson ───
function renderLesson(mid, lid) {
  const m = MODULES.find((x) => x.id === mid);
  const li = m.lessons.findIndex((x) => x.id === lid);
  const l = m.lessons[li];
  store.last = `#/lesson/${mid}/${lid}`; save();
  const isDone = !!store.done[l.id];
  $main().innerHTML = `
    <div class="crumb">${m.emoji} ${m.title} · Lesson ${li + 1} of ${m.lessons.length}</div>
    <h1 class="lesson-title">${l.title}</h1>
    <div class="lesson-body">${l.body}</div>
    ${l.demo ? `<div class="demo" id="demo-root"></div>` : ""}
    ${l.terms.length ? `<div class="termbox"><b>🔑 Key terms:</b><br>${l.terms.map((t) => `<span class="term-pill">${t}</span>`).join("")}</div>` : ""}
    <div class="takeaways"><b>💡 Remember this:</b><ul>${l.takeaways.map((t) => `<li>${t}</li>`).join("")}</ul></div>
    <div class="lesson-nav">
      ${li > 0 ? `<button class="btn btn-ghost" onclick="location.hash='#/lesson/${mid}/${m.lessons[li - 1].id}'">← Previous</button>` : `<button class="btn btn-ghost" onclick="location.hash='#/'">← Home</button>`}
      <span class="spacer"></span>
      <button class="btn ${isDone ? "btn-done" : "btn-ghost"}" id="mark-done">${isDone ? "✔ Completed" : "Mark complete"}</button>
      ${li < m.lessons.length - 1
        ? `<button class="btn" id="next-btn">Next lesson →</button>`
        : `<button class="btn" id="next-btn">Take the ${m.title} quiz 🏁</button>`}
    </div>`;
  linkifyGlossary(document.querySelector(".lesson-body"));
  linkifyGlossary(document.querySelector(".takeaways"));
  if (l.demo && DEMOS[l.demo]) DEMOS[l.demo](document.getElementById("demo-root"));
  document.getElementById("mark-done").addEventListener("click", () => {
    store.done[l.id] = !store.done[l.id];
    if (!store.done[l.id]) delete store.done[l.id];
    save(); renderSidebar(); renderLesson(mid, lid);
  });
  document.getElementById("next-btn").addEventListener("click", () => {
    if (!store.done[l.id]) { store.done[l.id] = true; save(); }
    location.hash = li < m.lessons.length - 1 ? `#/lesson/${mid}/${m.lessons[li + 1].id}` : `#/quiz/${mid}`;
  });
}

// ─── quiz ───
function renderQuiz(mid) {
  const m = MODULES.find((x) => x.id === mid);
  let qi = 0, score = 0, answered = false;
  function draw() {
    if (qi >= m.quiz.length) {
      const best = Math.max(score, store.quiz[mid] ?? 0);
      store.quiz[mid] = best; save(); renderSidebar();
      const pct = Math.round((score / m.quiz.length) * 100);
      const mi = MODULES.indexOf(m);
      $main().innerHTML = `
        <div class="crumb">${m.emoji} ${m.title} · Quiz</div>
        <div class="quiz-score">
          <div class="big">${pct >= 80 ? "🎉" : "📚"} ${score}/${m.quiz.length}</div>
          <p>${pct >= 80 ? "Passed! This module is locked in." : "Below 80% — skim the lessons and retake. Repetition is the point, not a punishment."}</p>
          <button class="btn btn-ghost" onclick="renderQuiz('${mid}')">↺ Retake</button>
          ${mi < MODULES.length - 1 ? `<button class="btn" onclick="location.hash='#/lesson/${MODULES[mi + 1].id}/${MODULES[mi + 1].lessons[0].id}'">Next module: ${MODULES[mi + 1].title} →</button>` : `<button class="btn" onclick="location.hash='#/cards'">🃏 Drill the flashcards</button>`}
        </div>`;
      return;
    }
    const q = m.quiz[qi];
    $main().innerHTML = `
      <div class="crumb">${m.emoji} ${m.title} · Quiz</div>
      <div class="quiz-progress">Question ${qi + 1} of ${m.quiz.length} · Score ${score}</div>
      <div class="quiz-q">${q.q}</div>
      <div id="opts">${q.options.map((o, i) => `<button class="quiz-opt" data-i="${i}">${String.fromCharCode(65 + i)}. ${o}</button>`).join("")}</div>
      <div id="feedback"></div>`;
    document.querySelectorAll(".quiz-opt").forEach((b) => b.addEventListener("click", () => {
      if (answered) return;
      answered = true;
      const i = +b.dataset.i;
      document.querySelectorAll(".quiz-opt").forEach((x) => (x.disabled = true));
      document.querySelector(`.quiz-opt[data-i="${q.answer}"]`).classList.add("right");
      if (i === q.answer) score++;
      else b.classList.add("wrong");
      document.getElementById("feedback").innerHTML = `
        <div class="quiz-explain">${i === q.answer ? "✅ Correct." : "❌ Not quite."} ${q.explain}</div>
        <button class="btn" id="q-next">${qi + 1 < m.quiz.length ? "Next question →" : "See results 🏁"}</button>`;
      linkifyGlossary(document.getElementById("feedback"));
      document.getElementById("q-next").addEventListener("click", () => { qi++; answered = false; draw(); });
    }));
  }
  draw();
}

// ─── flashcards (Leitner boxes: 1 = always due, 2 = due after 1 day, 3 = after 3 days) ───
function dueCards() {
  const now = Date.now(), DAY = 86400000;
  return GLOSSARY.filter((g) => {
    const c = store.cards[g.term];
    if (!c) return true;
    if (c.box <= 1) return true;
    if (c.box === 2) return now - c.last > DAY;
    return now - c.last > 3 * DAY;
  });
}
function renderCards() {
  let deck = dueCards().sort(() => Math.random() - 0.5);
  let flipped = false;
  function draw() {
    const mastered = Object.values(store.cards).filter((c) => c.box >= 3).length;
    if (!deck.length) {
      $main().innerHTML = `
        <div class="crumb">🃏 Flashcards</div>
        <div class="quiz-score"><div class="big">✨</div>
        <p>No cards due right now. ${mastered}/${GLOSSARY.length} terms mastered. Come back tomorrow — spacing out reviews is literally the trick.</p>
        <button class="btn btn-ghost" onclick="location.hash='#/'">← Home</button></div>`;
      return;
    }
    const g = deck[0];
    const c = store.cards[g.term] || { box: 1 };
    $main().innerHTML = `
      <div class="crumb">🃏 Flashcards · ${deck.length} due · ${mastered}/${GLOSSARY.length} mastered</div>
      <div class="fc-card" id="fc">${flipped ? `<span class="fc-def">${g.def}</span>` : `<b>${g.term}</b>`}</div>
      ${flipped ? `
      <div class="fc-buttons">
        <button class="btn btn-ghost" id="fc-again">😅 Again</button>
        <button class="btn" id="fc-got">✅ Got it</button>
      </div>` : `<div class="fc-meta">Think of the definition, then click the card to flip.</div>`}
      <div class="fc-meta">Box ${c.box}/3 — “Got it” moves it up; box 3 = mastered (reviewed every 3 days).</div>`;
    linkifyGlossary(document.querySelector(".fc-def"), new Set([g.term]));
    document.getElementById("fc").addEventListener("click", () => { flipped = !flipped; draw(); });
    if (flipped) {
      document.getElementById("fc-again").addEventListener("click", () => {
        store.cards[g.term] = { box: 1, last: Date.now() }; save();
        deck.push(deck.shift()); flipped = false; draw(); renderSidebar();
      });
      document.getElementById("fc-got").addEventListener("click", () => {
        store.cards[g.term] = { box: Math.min(3, c.box + 1), last: Date.now() }; save();
        deck.shift(); flipped = false; draw(); renderSidebar();
      });
    }
  }
  draw();
}

// ─── glossary ───
function renderGlossary() {
  const modNames = Object.fromEntries(MODULES.map((m) => [m.id, `${m.emoji} ${m.title}`]));
  $main().innerHTML = `
    <div class="crumb">📖 Glossary</div>
    <h1 class="lesson-title">Glossary — ${GLOSSARY.length} terms</h1>
    <p style="color:var(--muted)">Every term from the course. This is also your flashcard deck.</p>
    <input class="gl-search" placeholder="Search terms and definitions…">
    <div id="gl-list"></div>`;
  const list = document.getElementById("gl-list");
  function draw(filter) {
    const f = (filter || "").toLowerCase();
    const items = GLOSSARY.filter((g) => !f || g.term.toLowerCase().includes(f) || g.def.toLowerCase().includes(f));
    list.innerHTML = items.map((g) => `<div class="gl-item"><b>${g.term}</b><span class="gl-mod">${modNames[g.m]}</span><br>${g.def}</div>`).join("") || `<p style="color:var(--muted)">No matches.</p>`;
    list.querySelectorAll(".gl-item").forEach((el, i) => linkifyGlossary(el, new Set([items[i].term])));
  }
  document.querySelector(".gl-search").addEventListener("input", (e) => draw(e.target.value));
  draw();
}

// ─── inline glossary references: auto-link terms in prose to a definition popover ───
function escapeRegex(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

function buildAliasIndex() {
  const idx = [];
  GLOSSARY.forEach((g) => {
    const aliases = new Set([g.term]);
    const paren = g.term.match(/^(.*?)\s*\(([^)]+)\)$/);
    if (paren) { aliases.add(paren[1].trim()); aliases.add(paren[2].trim()); }
    g.term.split(" / ").forEach((p) => aliases.add(p.trim()));
    aliases.forEach((a) => { if (a && a.length >= 2) idx.push({ alias: a, g }); });
  });
  idx.sort((a, b) => b.alias.length - a.alias.length);
  return idx;
}
const ALIAS_INDEX = buildAliasIndex();

// Wraps the first mention of each glossary term inside `root` in a clickable
// .gl-ref span. `preUsed` seeds already-linked terms (e.g. a glossary item's
// own heading) so a definition never links to itself.
function linkifyGlossary(root, preUsed) {
  if (!root) return;
  const used = new Set(preUsed || []);
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
      if (node.parentElement && node.parentElement.closest("code, pre, a, .gl-ref, .term-pill, b"))
        return NodeFilter.FILTER_REJECT;
      return NodeFilter.FILTER_ACCEPT;
    },
  });
  const nodes = [];
  let n;
  while ((n = walker.nextNode())) nodes.push(n);
  nodes.forEach((node) => {
    const text = node.nodeValue;
    const matches = [];
    for (const { alias, g } of ALIAS_INDEX) {
      if (used.has(g.term)) continue;
      const re = new RegExp(`\\b${escapeRegex(alias)}\\b`, "i");
      const m = re.exec(text);
      if (m) { matches.push({ start: m.index, end: m.index + m[0].length, g, text: m[0] }); used.add(g.term); }
    }
    if (!matches.length) return;
    matches.sort((a, b) => a.start - b.start);
    const final = [];
    let lastEnd = -1;
    for (const m of matches) if (m.start >= lastEnd) { final.push(m); lastEnd = m.end; }
    const frag = document.createDocumentFragment();
    let cursor = 0;
    final.forEach((m) => {
      if (m.start > cursor) frag.appendChild(document.createTextNode(text.slice(cursor, m.start)));
      const span = document.createElement("span");
      span.className = "gl-ref";
      span.dataset.term = m.g.term;
      span.textContent = m.text;
      frag.appendChild(span);
      cursor = m.end;
    });
    if (cursor < text.length) frag.appendChild(document.createTextNode(text.slice(cursor)));
    node.parentNode.replaceChild(frag, node);
  });
}

let popoverEl = null;
function showGlossaryPopover(span) {
  closeGlossaryPopover();
  const term = GLOSSARY.find((g) => g.term === span.dataset.term);
  if (!term) return;
  const pop = document.createElement("div");
  pop.className = "gl-popover";
  pop.innerHTML = `<b>${term.term}</b><p>${term.def}</p><a href="#/glossary" class="gl-pop-link" onclick="closeGlossaryPopover()">Open full glossary →</a>`;
  document.body.appendChild(pop);
  const r = span.getBoundingClientRect();
  pop.style.top = r.bottom + window.scrollY + 8 + "px";
  let left = r.left + window.scrollX;
  const maxLeft = window.scrollX + document.documentElement.clientWidth - pop.offsetWidth - 16;
  left = Math.min(left, maxLeft);
  left = Math.max(left, window.scrollX + 8);
  pop.style.left = left + "px";
  popoverEl = pop;
  span.classList.add("gl-ref-active");
  setTimeout(() => document.addEventListener("click", onGlossaryDocClick), 0);
}
function closeGlossaryPopover() {
  if (popoverEl) { popoverEl.remove(); popoverEl = null; }
  document.querySelectorAll(".gl-ref-active").forEach((s) => s.classList.remove("gl-ref-active"));
  document.removeEventListener("click", onGlossaryDocClick);
}
function onGlossaryDocClick(e) {
  if (popoverEl && !popoverEl.contains(e.target) && !e.target.classList.contains("gl-ref")) closeGlossaryPopover();
}
document.addEventListener("click", (e) => {
  const span = e.target.closest(".gl-ref");
  if (span) { e.stopPropagation(); showGlossaryPopover(span); }
});
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeGlossaryPopover(); });
window.addEventListener("scroll", closeGlossaryPopover, { passive: true });

// ─── mobile off-canvas sidebar ───
function closeSidebar() {
  document.querySelector(".sidebar").classList.remove("open");
  document.getElementById("sidebar-backdrop").classList.remove("open");
}
function toggleSidebar() {
  document.querySelector(".sidebar").classList.toggle("open");
  document.getElementById("sidebar-backdrop").classList.toggle("open");
}
document.getElementById("hamburger-btn").addEventListener("click", toggleSidebar);
document.getElementById("sidebar-backdrop").addEventListener("click", closeSidebar);

// ─── router ───
// scrollMemory remembers scroll position per hash so the browser Back button
// returns you to exactly where you were reading, not just the right page.
const scrollMemory = {};
let currentRoute = location.hash || "#/";

function route() {
  scrollMemory[currentRoute] = window.scrollY;
  closeGlossaryPopover();
  closeSidebar();
  const h = location.hash || "#/";
  currentRoute = h;
  renderSidebar();
  const parts = h.slice(2).split("/");
  if (parts[0] === "lesson" && parts[1] && parts[2]) renderLesson(parts[1], parts[2]);
  else if (parts[0] === "quiz" && parts[1]) renderQuiz(parts[1]);
  else if (parts[0] === "cards") renderCards();
  else if (parts[0] === "glossary") renderGlossary();
  else renderDashboard();
  requestAnimationFrame(() => window.scrollTo(0, scrollMemory[h] || 0));
}
window.addEventListener("hashchange", route);
route();
