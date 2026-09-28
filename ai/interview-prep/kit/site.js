// Shared lesson-site behaviour: quiz, section reveals. Page-specific labs live in the page's own main.js.
(function () {
  // Quiz: <div class="quiz"><button class="opt" data-ok="1" data-why="...">…</button>…</div><p class="quiz-why"></p>
  document.querySelectorAll('.quiz').forEach((quiz) => {
    const why = quiz.parentElement.querySelector('.quiz-why');
    quiz.querySelectorAll('.opt').forEach((b) => b.addEventListener('click', () => {
      quiz.querySelectorAll('.opt').forEach((o) => o.classList.remove('right', 'wrong'));
      b.classList.add(b.dataset.ok === '1' ? 'right' : 'wrong');
      if (b.dataset.ok !== '1') quiz.querySelector('.opt[data-ok="1"]')?.classList.add('right');
      if (why) why.textContent = b.dataset.why || '';
    }));
  });
  // Reveal sections on scroll
  const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.08 });
  document.querySelectorAll('main section:not(.hero)').forEach((s) => { s.classList.add('reveal'); io.observe(s); });
})();

// Small helper for SVG overlays on data figures: map data coords → % of the figure box.
window.Lesson = {
  svg(tag, attrs = {}, parent) {
    const e = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    parent?.appendChild(e);
    return e;
  },
  scaler([x0, x1, y0, y1]) {
    return (x, y) => [((x - x0) / (x1 - x0)) * 100, (1 - (y - y0) / (y1 - y0)) * 100];
  },
};

// ---------- lessons site: home cards, track lists, breadcrumb + previous/next, all from lessons.js ----------
// <body data-page="home|track|lesson" data-root="../../" data-track="llm-inference" data-lesson="prefill-vs-decode">
(function () {
  const L = window.LESSONS, b = document.body;
  if (!L || !b.dataset.page) return;
  const root = b.dataset.root || '';
  const el = (h) => { const t = document.createElement('template'); t.innerHTML = h.trim(); return t.content.firstChild; };
  const num = (tr, i) => `${tr.prefix || ''}${i + 1}`;
  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const track = L.tracks.find((t) => t.id === b.dataset.track);

  // header handle links home on every page
  document.querySelectorAll('header .handle').forEach((h) => { const a = el(`<a class="handle handle-link" href="${root}index.html">${h.textContent}</a>`); h.replaceWith(a); });

  if (b.dataset.page === 'home') {
    const box = document.getElementById('tracks');
    box.innerHTML = L.tracks.map((t) => {
      const n = t.lessons.length;
      return `<a class="card tcard" href="${t.id}/index.html"><h3>${esc(t.title)}</h3><p>${esc(t.desc)}</p>
        <span class="count${n ? '' : ' soon'}">${n ? `${n} lesson${n > 1 ? 's' : ''}` : 'coming soon'}</span></a>`;
    }).join('');
  }

  if (b.dataset.page === 'track' && track) {
    document.getElementById('trackTitle').textContent = track.title;
    document.getElementById('trackDesc').textContent = track.desc;
    document.title = `${track.title} · AI & ML, explained simply`;
    const box = document.getElementById('list');
    box.innerHTML = track.lessons.length
      ? `<ol class="llist">${track.lessons.map((l, i) => `<li><a class="card" href="${l.slug}/index.html">
          <span class="num">${num(track, i)}</span>
          <div><h3>${esc(l.title)}</h3><p>${esc(l.sub)}</p><div class="meta"><span class="pill lvl-${l.level}">${l.level}</span><span class="pill">${l.mins} min</span></div></div></a></li>`).join('')}</ol>`
      : `<div class="card soonbox">Lessons coming soon.</div>`;
  }

  if (b.dataset.page === 'lesson' && track) {
    const i = track.lessons.findIndex((l) => l.slug === b.dataset.lesson);
    if (i < 0) return;
    const cur = track.lessons[i], prev = track.lessons[i - 1], next = track.lessons[i + 1];
    const header = document.querySelector('header');
    header.after(el(`<nav class="crumbs wrap" aria-label="Breadcrumb"><a href="${root}index.html">Lessons</a> › <a href="${root}${track.id}/index.html">${esc(track.title)}</a> › <span class="here">${num(track, i)}. ${esc(cur.title)}</span></nav>`));
    const link = (l, j, cls, label) => l
      ? `<a class="card ${cls}" href="../${l.slug}/index.html"><small>${label}</small><b>${num(track, j)}. ${esc(l.title)}</b></a>`
      : `<span class="${cls} empty"></span>`;
    const footer = document.querySelector('footer');
    footer.before(el(`<nav class="pn wrap" aria-label="More lessons">${link(prev, i - 1, 'prev', '← Previous')}${link(next, i + 1, 'next', 'Next →')}</nav>`));
  }
})();
