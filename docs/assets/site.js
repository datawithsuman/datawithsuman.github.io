(function () {
  var PROGRESS = "dws.progress", LABELS = { "in-progress": "In progress", done: "Done" };

  // Storage can be blocked or empty, so the site must work without it.
  function read(key, fallback) {
    try { var v = localStorage.getItem(key); return v === null ? fallback : JSON.parse(v); }
    catch (e) { return fallback; }
  }
  function write(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) {}
  }

  var progress = read(PROGRESS, {}) || {};
  function paintDots() {
    document.querySelectorAll(".dot[data-key]").forEach(function (d) {
      var s = progress[d.dataset.key];
      if (s) d.dataset.state = s; else delete d.dataset.state;
      d.setAttribute("aria-label", LABELS[s] || "Not started");
    });
  }
  function setState(key, state) {
    if (progress[key] === "done" && state !== "done") return;
    progress[key] = state;
    write(PROGRESS, progress);
    paintDots();
  }

  var main = document.querySelector("[data-lesson]");
  if (main) {
    var key = main.dataset.lesson;
    setState(key, "in-progress");
    write("dws.last." + key.split("/")[0], key);

    var mark = document.getElementById("markDone");
    function showDone() { if (mark) { mark.textContent = "Marked done"; mark.disabled = true; } }
    function setDone() { setState(key, "done"); showDone(); }
    if (progress[key] === "done") showDone();
    if (mark) mark.addEventListener("click", setDone);

    // Only after a real scroll, so a short page is not marked done on opening.
    var cards = document.querySelectorAll(".interview"), block = cards[cards.length - 1];
    // Say it counts as done at its answer step instead (see below).
    if (block && "IntersectionObserver" in window) {
      var inView = false, scrolled = false;
      function check() { if (inView && scrolled) setDone(); }
      new IntersectionObserver(function (e) { inView = e[0].isIntersecting; check(); }, { threshold: 0.15 }).observe(block);
      window.addEventListener("scroll", function () { if (window.scrollY > 40) { scrolled = true; check(); } }, { passive: true });
    }
  }
  paintDots();

  // Wide tables and code in moved lessons scroll sideways, so they need keyboard focus.
  document.querySelectorAll(".lx pre, .lx .tw, .lx .scroll, .lx .tablewrap").forEach(function (el) { el.tabIndex = 0; });

  // Equation marks. Each lesson's reader draws a brace under the terms it is reading.
  // Here a wide equation is shrunk to fit (or scrolls when it would get too small),
  // and the brace and its label are kept under the terms and inside the box.
  var MIN_SCALE = 0.6;
  function fitEq(eq) {
    var mj = eq.querySelector("mjx-container"), svg = mj && mj.querySelector("svg");
    if (!svg) return;
    var cs = getComputedStyle(eq), avail = eq.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    if (avail <= 0) return false;
    svg.style.maxWidth = "none"; // a capped width clips the equation instead of scaling it
    mj.style.fontSize = "";
    var natural = svg.getBoundingClientRect().width;
    if (natural > avail) mj.style.fontSize = Math.max(avail / natural, MIN_SCALE) * 100 + "%";
    return true;
  }
  function placeBrace(eq) {
    var brace = eq.querySelector(".brace"), mj = eq.querySelector("mjx-container");
    if (!eq.dataset.fitted && fitEq(eq)) eq.dataset.fitted = "1";
    if (!brace || !mj || +brace.style.opacity === 0) return;
    var terms = Array.prototype.filter.call(eq.querySelectorAll(".term.on"), function (t) { return t.getBoundingClientRect().width; });
    if (!terms.length) return;
    var rects = function () { return terms.map(function (t) { return t.getBoundingClientRect(); }); };
    var r = rects(), M = mj.getBoundingClientRect();
    var tl = Math.min.apply(null, r.map(function (x) { return x.left; })), tr = Math.max.apply(null, r.map(function (x) { return x.right; }));
    if (mj.scrollWidth > mj.clientWidth + 1 && (tl < M.left || tr > M.right)) { // bring the terms into view
      // All of them if they fit, else the first one, marking only what is on screen.
      mj.scrollLeft += tr - tl <= M.width ? (tl + tr) / 2 - (M.left + M.right) / 2 : tl - M.left - 8;
      r = rects();
      var seen = r.filter(function (x) { return x.left >= M.left - 1 && x.right <= M.right + 1; });
      if (seen.length) r = seen;
      tl = Math.min.apply(null, r.map(function (x) { return x.left; })); tr = Math.max.apply(null, r.map(function (x) { return x.right; }));
    }
    var box = eq.getBoundingClientRect(), lo = Math.max(M.left, box.left + 2) - box.left, hi = Math.min(M.right, box.right - 2) - box.left;
    var left = Math.max(tl - box.left, lo), right = Math.min(tr - box.left, hi);
    if (right - left < 6) { brace.style.opacity = 0; return; }
    var bottom = Math.max.apply(null, r.map(function (x) { return x.bottom; })) - box.top;
    brace.style.left = left + "px"; brace.style.width = (right - left) + "px"; brace.style.top = (bottom + 6) + "px";
    var label = brace.querySelector("span"), width = eq.clientWidth;
    if (label) {
      label.style.marginLeft = "0px"; label.style.whiteSpace = ""; label.style.width = "";
      var center = (left + right) / 2, half = label.offsetWidth / 2, nudge = 0;
      if (half * 2 > width - 8) { label.style.whiteSpace = "normal"; label.style.width = (width - 8) + "px"; label.style.textAlign = "center"; half = label.offsetWidth / 2; }
      if (center - half < 4) nudge = 4 - (center - half);
      else if (center + half > width - 4) nudge = width - 4 - (center + half);
      label.style.marginLeft = nudge + "px";
    }
    brace.dataset.placed = brace.style.cssText;
  }
  document.querySelectorAll(".reader").forEach(function (reader) {
    new MutationObserver(function (changes) {
      changes.forEach(function (change) {
        var brace = change.target;
        if (!brace.classList.contains("brace") || brace.style.cssText === brace.dataset.placed) return;
        placeBrace(brace.parentNode);
      });
    }).observe(reader, { subtree: true, attributes: true, attributeFilter: ["style"] });
    reader.addEventListener("scroll", function (e) {
      if (e.target.matches && e.target.matches("mjx-container")) placeBrace(e.target.closest(".eq"));
    }, true);
  });
  var resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      document.querySelectorAll(".reader .eq").forEach(function (eq) { delete eq.dataset.fitted; placeBrace(eq); });
    }, 150);
  });

  // Equation readers measure their labels only when a step changes, so a hidden one needs a fresh look once shown.
  function refreshReaders(root) {
    root.querySelectorAll(".reader .dots button.on").forEach(function (dot) { dot.click(); });
  }

  // Depth is one number per track. A lesson with fewer layers shows its deepest.
  var depth = document.querySelector(".depth");
  function spy() {
    var links = Array.prototype.filter.call(document.querySelectorAll(".page-toc li"), function (li) { return !li.hidden; });
    var current = null;
    links.forEach(function (li) {
      var a = li.querySelector("a"), el = document.querySelector(a.getAttribute("href"));
      if (el && el.getBoundingClientRect().top < 140) current = a;
      a.removeAttribute("aria-current");
    });
    if (!current && links.length) current = links[0].querySelector("a");
    if (current) current.setAttribute("aria-current", "true");
  }
  if (depth) {
    var buttons = depth.querySelectorAll("button"), storeKey = "dws.depth." + depth.dataset.track;
    function applyDepth(n) {
      buttons.forEach(function (b, i) { b.setAttribute("aria-pressed", i === n ? "true" : "false"); });
      document.querySelectorAll("[data-layer]").forEach(function (el) { el.hidden = +el.dataset.layer > n; });
      refreshReaders(document);
      spy();
    }
    buttons.forEach(function (b, i) {
      b.addEventListener("click", function () { applyDepth(i); write(storeKey, i); });
    });
    var saved = read(storeKey, 0);
    applyDepth(typeof saved === "number" ? Math.min(Math.max(saved, 0), buttons.length - 1) : 0);
  }
  if (document.querySelector(".page-toc")) {
    spy();
    window.addEventListener("scroll", spy, { passive: true });
  }

  document.querySelectorAll("[data-reveal]").forEach(function (b) {
    b.addEventListener("click", function () {
      var open = b.getAttribute("aria-expanded") !== "true", ans = document.getElementById(b.getAttribute("aria-controls"));
      b.setAttribute("aria-expanded", open);
      b.textContent = open ? "Hide answer" : "Reveal answer";
      ans.classList.toggle("open", open);
    });
  });

  // Lesson tabs: one part at a time. Without JavaScript every part shows, one after another.
  var tabBar = document.querySelector(".lesson-tabs");
  if (tabBar) {
    var tabs = Array.prototype.slice.call(tabBar.querySelectorAll("[data-tab]"));
    var openTab = function (key, move) {
      tabs.forEach(function (b) {
        var on = b.dataset.tab === key;
        b.setAttribute("aria-selected", on ? "true" : "false");
        b.tabIndex = on ? 0 : -1;
        document.getElementById("panel-" + b.dataset.tab).hidden = !on;
      });
      document.querySelectorAll(".page-toc li[data-panel]").forEach(function (li) { li.hidden = li.dataset.panel !== key; });
      refreshReaders(document.getElementById("panel-" + key));
      if (key === "why" && document.getElementById("markDone")) document.getElementById("markDone").click();
      spy();
      if (move && tabBar.getBoundingClientRect().top <= 0) tabBar.nextElementSibling.scrollIntoView();
    };
    tabs.forEach(function (b, i) {
      b.addEventListener("click", function () { openTab(b.dataset.tab, true); });
      b.addEventListener("keydown", function (e) {
        var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        var next = tabs[(i + d + tabs.length) % tabs.length];
        openTab(next.dataset.tab, false);
        next.focus();
      });
    });
    document.querySelectorAll("[data-tab-go]").forEach(function (b) {
      b.addEventListener("click", function () {
        openTab(b.dataset.tabGo, false);
        tabBar.scrollIntoView();
        document.getElementById("tab-" + b.dataset.tabGo).focus({ preventScroll: true });
      });
    });
    var byHash = function () {
      var el = location.hash.length > 1 && document.getElementById(location.hash.slice(1));
      var holder = el && el.closest(".tab-panel");
      if (holder) { openTab(holder.id.replace("panel-", ""), false); el.scrollIntoView(); return true; }
      return false;
    };
    if (!byHash()) openTab(tabs[0].dataset.tab, false);
    window.addEventListener("hashchange", byHash);
  }

  // Practice pages: one question at a time.
  document.querySelectorAll(".practice-card").forEach(function (box) {
    var qs = box.querySelectorAll("[data-pq]"), dots = box.querySelectorAll(".say-stepper button"), seen = {};
    function show(i, move) {
      qs.forEach(function (q, k) { q.hidden = k !== i; });
      dots.forEach(function (d, k) {
        d.parentNode.dataset.state = k === i ? "current" : seen[k] ? "done" : "";
        if (k === i) d.setAttribute("aria-current", "step"); else d.removeAttribute("aria-current");
      });
      if (!move) return;
      qs[i].focus({ preventScroll: true });
      var top = box.getBoundingClientRect().top;
      if (top < 0) window.scrollBy(0, top - 12);
    }
    box.querySelectorAll("[data-pq-go]").forEach(function (b) {
      b.addEventListener("click", function () { show(+b.dataset.pqGo, true); });
    });
    qs.forEach(function (q, i) {
      q.querySelector("[data-reveal]").addEventListener("click", function () { seen[i] = true; });
    });
    var finish = box.querySelector("[data-pq-finish]");
    if (finish) finish.addEventListener("click", function () {
      var mark = document.getElementById("markDone");
      if (mark) mark.click();
      finish.textContent = "Finished";
      finish.disabled = true;
    });
    show(0, false);
  });

  // Say it: one step at a time. Every step shows without JavaScript.
  document.querySelectorAll(".say-card").forEach(function (box) {
    var steps = box.querySelectorAll("[data-say-step]"), fus = box.querySelectorAll("[data-fu]"), checks = box.querySelectorAll("[data-check]");
    var stepper = box.querySelectorAll(".say-stepper button"), count = box.querySelector("[data-check-count]"), bar = box.querySelector("[data-check-bar]");
    var score = box.querySelector("[data-say-score]"), furthest = 0, ticked = false, shownFu = 0;
    function tally() {
      var n = Array.prototype.filter.call(checks, function (c) { return c.checked; }).length;
      count.textContent = n + " of " + checks.length + " covered";
      bar.style.width = (n / checks.length * 100) + "%";
      ticked = ticked || n > 0;
      if (ticked) { score.hidden = false; score.textContent = "You covered " + n + " of " + checks.length + " key points."; }
    }
    function go(i, move) {
      furthest = Math.max(furthest, i);
      steps.forEach(function (s, k) { s.hidden = k !== i; });
      stepper.forEach(function (b, k) {
        b.disabled = k > furthest;
        b.parentNode.dataset.state = k === i ? "current" : k <= furthest ? "done" : "";
        if (k === i) b.setAttribute("aria-current", "step"); else b.removeAttribute("aria-current");
      });
      if (!move) return;
      if (i === 3 && document.getElementById("markDone")) document.getElementById("markDone").click();
      steps[i].focus({ preventScroll: true });
      var top = box.getBoundingClientRect().top;
      if (top < 0) window.scrollBy(0, top - 12);
    }
    fus.forEach(function (f, i) { f.hidden = i > 0; });
    checks.forEach(function (c) { c.addEventListener("change", tally); });
    box.querySelectorAll("[data-say-go]").forEach(function (b) {
      b.addEventListener("click", function () { go(+b.dataset.sayGo, true); });
    });
    box.querySelectorAll("[data-next-fu]").forEach(function (b) {
      b.addEventListener("click", function () { fus[shownFu].hidden = true; shownFu += 1; fus[shownFu].hidden = false; steps[2].focus({ preventScroll: true }); });
    });
    tally();
    go(0, false);
  });

  // Token picker
  document.querySelectorAll('[data-widget="attention"]').forEach(function (w) {
    var m = JSON.parse(w.dataset.matrix), toks = w.querySelectorAll(".token"), rows = w.querySelectorAll(".bar-row"), cap = w.querySelector(".widget-caption");
    toks.forEach(function (t, i) {
      t.addEventListener("click", function () {
        var row = m.weights[i], top = Math.max.apply(null, row), topWord = m.tokens[row.indexOf(top)];
        toks.forEach(function (x, j) {
          var isTop = row[j] === top;
          x.style.setProperty("--w", isTop ? 1 : (row[j] / top * 0.6).toFixed(3));
          x.classList.toggle("is-top", isTop);
          x.classList.toggle("selected", j === i);
          x.setAttribute("aria-pressed", j === i ? "true" : "false");
          rows[j].querySelector("i").style.width = row[j] + "%";
          rows[j].querySelector(".bar-pct").textContent = row[j] + "%";
        });
        cap.innerHTML = "<b>" + m.tokens[i] + "</b> looks at " + (topWord === m.tokens[i] ? "itself" : "<b>" + topWord + "</b>") + " the most.";
      });
    });
  });

  // Continue card on track pages
  var cont = document.getElementById("continue");
  if (cont) {
    var list = JSON.parse(cont.dataset.lessons), started = list.filter(function (l) { return progress[l.key]; });
    if (started.length) {
      var lastKey = read("dws.last." + cont.dataset.track, null);
      var last = list.filter(function (l) { return l.key === lastKey; })[0] || started[started.length - 1];
      var done = list.filter(function (l) { return progress[l.key] === "done"; }).length;
      document.getElementById("continueTitle").textContent = last.title;
      document.getElementById("continueLink").href = last.url;
      document.getElementById("continueNote").textContent = done + " of " + list.length + " lessons done";
      var bar = document.getElementById("continueBar");
      bar.setAttribute("aria-label", done + " of " + list.length + " lessons done");
      bar.querySelector("i").style.width = (done / list.length * 100) + "%";
      cont.hidden = false;
    }
  }

  // Phones start with the lesson, not the whole track list.
  var box = document.querySelector(".contents-box");
  if (box && window.matchMedia("(max-width: 820px)").matches) box.open = false;

  // Search
  var dialog = document.getElementById("searchDialog"), input = document.getElementById("searchInput"), results = document.getElementById("searchResults");
  var opener = document.getElementById("searchOpen"), root = document.body.dataset.root, index = window.SEARCH_INDEX || [];
  var isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
  if (isMac) opener.querySelector("kbd").textContent = "⌘ K";

  function esc(s) { var d = document.createElement("div"); d.textContent = s; return d.innerHTML; }
  function render() {
    var words = input.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    if (!words.length) {
      results.innerHTML = '<p class="search-empty">Type to search ' + index.length + " lessons.</p>";
      return;
    }
    var hits = index.filter(function (r) {
      var hay = (r.title + " " + r.module + " " + r.trackName + " " + r.text + " " + r.type).toLowerCase();
      return words.every(function (w) { return hay.indexOf(w) > -1; });
    });
    if (!hits.length) { results.innerHTML = '<p class="search-empty">No lessons match that.</p>'; return; }
    var groups = {}, order = [];
    hits.forEach(function (r) { if (!groups[r.track]) { groups[r.track] = []; order.push(r.track); } groups[r.track].push(r); });
    results.innerHTML = order.map(function (t) {
      var g = groups[t];
      return '<div class="search-group t-' + t + '"><span class="chip type-track">' + esc(g[0].trackName) + "</span>" + g.map(function (r) {
        return '<a class="search-hit" href="' + root + r.url + '"><b>' + esc(r.title) + "</b><span>" + esc(r.module) + " · " + esc(r.type) + "</span></a>";
      }).join("") + "</div>";
    }).join("");
  }
  function openSearch() { if (!dialog.open) { dialog.showModal(); input.select(); render(); } }
  opener.addEventListener("click", openSearch);
  document.getElementById("searchClose").addEventListener("click", function () { dialog.close(); });
  dialog.addEventListener("click", function (e) { if (e.target === dialog) dialog.close(); });
  input.addEventListener("input", render);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { e.preventDefault(); dialog.close(); }
    if (e.key === "Enter") { var first = results.querySelector("a"); if (first) first.click(); }
    if (e.key === "ArrowDown") { var a = results.querySelector("a"); if (a) { e.preventDefault(); a.focus(); } }
  });
  results.addEventListener("keydown", function (e) {
    if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
    e.preventDefault();
    var links = Array.prototype.slice.call(results.querySelectorAll("a")), i = links.indexOf(document.activeElement) + (e.key === "ArrowDown" ? 1 : -1);
    if (i < 0) input.focus(); else if (links[i]) links[i].focus();
  });
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); openSearch(); }
  });
  // Track pages: modules collapse. Keep what the reader opened, and open whatever a link points to.
  (function () {
    var modules = document.querySelectorAll("details.module");
    if (!modules.length) return;
    var key = "aimlrounds:open-modules:" + location.pathname;
    function save() {
      var open = [];
      modules.forEach(function (m) { if (m.open) open.push(m.id); });
      try { localStorage.setItem(key, JSON.stringify(open)); } catch (e) {}
    }
    var saved = null;
    try { saved = JSON.parse(localStorage.getItem(key)); } catch (e) {}
    if (Array.isArray(saved)) modules.forEach(function (m) { m.open = saved.indexOf(m.id) !== -1; });
    function openFromHash() {
      var el = location.hash.length > 1 && document.getElementById(location.hash.slice(1));
      if (el && el.matches("details.module")) { el.open = true; el.scrollIntoView(); }
    }
    openFromHash();
    window.addEventListener("hashchange", openFromHash);
    modules.forEach(function (m) { m.addEventListener("toggle", save); });
  })();
})();
