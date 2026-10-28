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

// ---------- lessons site: home, section pages, track lists, breadcrumbs + previous/next, all from lessons.js ----------
// <body data-page="home|section|track|lesson" data-root="../../" data-section="fundamentals" data-track="machine-learning" data-lesson="linear-regression">
(function () {
  const L = window.LESSONS, b = document.body;
  if (!L || !b.dataset.page) return;
  const root = b.dataset.root || '';
  const el = (h) => { const t = document.createElement('template'); t.innerHTML = h.trim(); return t.content.firstChild; };
  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const track = L.tracks.find((t) => t.id === b.dataset.track);
  const live = (s) => s.tracks.filter((t) => t.lessons.length);
  const count = (n) => `${n} lesson${n === 1 ? '' : 's'}`;
  // a section with one track (Papers) links straight to that track
  const secHref = (s) => s.tracks.length === 1 ? `${root}${s.tracks[0].dir}/index.html` : `${root}${s.id}/index.html`;
  const card = (t) => `<a class="card tcard" href="${root}${t.dir}/index.html"><h3>${esc(t.title)}</h3><p>${esc(t.desc)}</p><span class="count">${count(t.lessons.length)}</span></a>`;
  // numbering restarts inside each group; tracks without groups number straight through
  const numOf = (t, l) => { const peers = t.groups ? t.lessons.filter((x) => x.group === l.group) : t.lessons; return `${t.prefix || ''}${peers.indexOf(l) + 1}`; };

  // header handle links home on every page
  document.querySelectorAll('header .handle').forEach((h) => { const a = el(`<a class="handle handle-link" href="${root}index.html">${h.textContent}</a>`); h.replaceWith(a); });

  if (b.dataset.page === 'home') {
    const box = document.getElementById('tracks');
    box.classList.remove('tracks');
    box.innerHTML = L.sections.filter((s) => live(s).length).map((s) => {
      const n = s.tracks.reduce((a, t) => a + t.lessons.length, 0);
      return `<section class="lgroup"><h2 class="ghead"><a href="${secHref(s)}" style="color:inherit;text-decoration:none">${esc(s.title)}</a> <span class="gcount">${count(n)}</span></h2><p class="gdesc">${esc(s.desc)}</p><div class="tracks">${live(s).map(card).join('')}</div></section>`;
    }).join('');
  }

  if (b.dataset.page === 'section') {
    const s = L.sections.find((x) => x.id === b.dataset.section);
    if (s) {
      document.getElementById('trackTitle').textContent = s.title;
      document.getElementById('trackDesc').textContent = s.desc;
      document.title = `${s.title} · AI & ML, explained simply`;
      const c = document.getElementById('crumbHere'); if (c) c.textContent = s.title;
      document.getElementById('list').innerHTML = live(s).length ? `<div class="tracks">${live(s).map(card).join('')}</div>` : `<div class="card soonbox">Lessons coming soon.</div>`;
    }
  }

  if (b.dataset.page === 'track' && track) {
    const s = track.section;
    document.getElementById('trackTitle').textContent = track.title;
    document.getElementById('trackDesc').textContent = track.desc;
    document.title = `${track.title} · AI & ML, explained simply`;
    const crumbs = document.getElementById('crumbs');
    if (crumbs) crumbs.innerHTML = `<a href="${root}index.html">Lessons</a> › ` + (s.tracks.length > 1 ? `<a href="${secHref(s)}">${esc(s.title)}</a> › ` : '') + `<span class="here">${esc(track.title)}</span>`;
    const box = document.getElementById('list');
    const item = (l) => `<li><a class="card" href="${l.slug}/index.html">
          <span class="num">${numOf(track, l)}</span>
          <div><h3>${esc(l.title)}</h3><p>${esc(l.sub)}</p><div class="meta"><span class="pill lvl-${l.level}">${l.level}</span><span class="pill">${l.mins} min</span></div></div></a></li>`;
    const groups = (track.groups || []).map((g) => ({ ...g, ls: track.lessons.filter((l) => l.group === g.id) })).filter((g) => g.ls.length);
    box.innerHTML = !track.lessons.length ? `<div class="card soonbox">Lessons coming soon.</div>`
      : groups.length ? groups.map((g) => `<section class="lgroup" id="${g.id}"><h2 class="ghead">${esc(g.title)} <span class="gcount">${count(g.ls.length)}</span></h2>${g.desc ? `<p class="gdesc">${esc(g.desc)}</p>` : ''}<ol class="llist">${g.ls.map(item).join('')}</ol></section>`).join('')
      : `<ol class="llist">${track.lessons.map(item).join('')}</ol>`;
  }

  if (b.dataset.page === 'lesson' && track) {
    const i = track.lessons.findIndex((l) => l.slug === b.dataset.lesson);
    if (i < 0) return;
    const cur = track.lessons[i], prev = track.lessons[i - 1], next = track.lessons[i + 1], s = track.section;
    const header = document.querySelector('header');
    header.after(el(`<nav class="crumbs wrap" aria-label="Breadcrumb"><a href="${root}index.html">Lessons</a> › ` + (s.tracks.length > 1 ? `<a href="${secHref(s)}">${esc(s.title)}</a> › ` : '') + `<a href="${root}${track.dir}/index.html">${esc(track.title)}</a> › <span class="here">${numOf(track, cur)}. ${esc(cur.title)}</span></nav>`));
    const link = (l, cls, label) => l
      ? `<a class="card ${cls}" href="../${l.slug}/index.html"><small>${label}</small><b>${numOf(track, l)}. ${esc(l.title)}</b></a>`
      : `<span class="${cls} empty"></span>`;
    const footer = document.querySelector('footer');
    footer.before(el(`<nav class="pn wrap" aria-label="More lessons">${link(prev, 'prev', '← Previous')}${link(next, 'next', 'Next →')}</nav>`));
  }
})();
