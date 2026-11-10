// Role roadmaps: one topic graph per role, a side panel per topic, progress from this browser.
(function () {
  var D = window.ROADMAP, graph = document.getElementById("rmGraph");
  if (!D || !graph) return;
  var root = document.body.dataset.root || "", summary = document.getElementById("rmSummary");
  var drawer = document.getElementById("rmDrawer"), back = document.getElementById("rmBack");
  var tabs = Array.prototype.slice.call(document.querySelectorAll(".rm-tabs [data-role]"));

  function read(key, fallback) {
    try { var v = localStorage.getItem(key); return v === null ? fallback : JSON.parse(v); } catch (e) { return fallback; }
  }
  function write(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) {} }
  function esc(t) { var d = document.createElement("div"); d.textContent = t; return d.innerHTML; }

  var progress = read("dws.progress", {}) || {};
  function done(key) { return progress[key] === "done"; }
  function count(tid) {
    var ls = D.topics[tid].lessons, n = 0;
    ls.forEach(function (k) { if (done(k)) n++; });
    return { done: n, total: ls.length };
  }
  function roleById(id) { return D.roles.filter(function (r) { return r.id === id; })[0]; }
  function topicIds(role) { return [].concat.apply([], role.rows); }
  function isUseful(role, tid) { return role.useful.indexOf(tid) > -1; }
  function parents(role, tid) { return role.edges.filter(function (e) { return e[1] === tid; }).map(function (e) { return e[0]; }); }

  // The next topic: the first core topic, top to bottom, that is not finished.
  function here(role) {
    var ids = topicIds(role).filter(function (t) { return !isUseful(role, t); });
    for (var i = 0; i < ids.length; i++) { var c = count(ids[i]); if (c.done < c.total) return ids[i]; }
    return null;
  }
  function nextLesson(tid) {
    var ls = D.topics[tid].lessons;
    for (var i = 0; i < ls.length; i++) if (!done(ls[i])) return ls[i];
    return ls[0];
  }

  var role, lastNode;

  function drawGraph() {
    var cur = here(role);
    var rows = role.rows.map(function (row, ri) {
      return '<div class="rm-row">' + row.map(function (tid) {
        var t = D.topics[tid], c = count(tid), pct = Math.round(100 * c.done / c.total), after = parents(role, tid);
        var cls = "rm-node t-" + t.track + (isUseful(role, tid) ? " is-useful" : "") + (tid === cur ? " is-here" : "") + (c.done === c.total ? " is-done" : "");
        return '<button type="button" class="' + cls + '" data-topic="' + tid + '">' +
          (tid === cur ? '<span class="rm-here">You are here</span>' : "") +
          '<span class="rm-name">' + esc(t.name) + '</span>' +
          '<span class="rm-bar" aria-hidden="true"><i style="width:' + pct + '%"></i></span>' +
          '<span class="rm-count">' + c.done + " / " + c.total + (isUseful(role, tid) ? " · Useful" : "") + '</span>' +
          (after.length ? '<span class="rm-after">After: ' + after.map(function (p) { return esc(D.topics[p].name); }).join(", ") + '</span>' : "") +
          '</button>';
      }).join("") + "</div>";
    }).join("");
    graph.innerHTML = '<div class="rm-canvas"><svg class="rm-edges" aria-hidden="true"></svg><div class="rm-rows">' + rows + "</div></div>" +
      '<p class="rm-legend"><span class="rm-key"></span> Core <span class="rm-key is-useful"></span> Useful, if you have time</p>';
    graph.querySelectorAll(".rm-node").forEach(function (b) {
      b.addEventListener("click", function () { lastNode = b; openTopic(b.dataset.topic); });
    });
    drawEdges();
  }

  function drawEdges() {
    var canvas = graph.querySelector(".rm-canvas"), svg = graph.querySelector(".rm-edges");
    if (!canvas || getComputedStyle(svg).display === "none") return;
    var box = canvas.getBoundingClientRect(), paths = "";
    svg.setAttribute("width", box.width); svg.setAttribute("height", box.height);
    role.edges.forEach(function (e) {
      var a = canvas.querySelector('[data-topic="' + e[0] + '"]'), b = canvas.querySelector('[data-topic="' + e[1] + '"]');
      if (!a || !b) return;
      var A = a.getBoundingClientRect(), B = b.getBoundingClientRect();
      var x1 = A.left + A.width / 2 - box.left, y1 = A.bottom - box.top, x2 = B.left + B.width / 2 - box.left, y2 = B.top - box.top;
      var dy = Math.max(24, (y2 - y1) / 2), faded = isUseful(role, e[0]) || isUseful(role, e[1]);
      paths += '<path class="' + (faded ? "is-useful" : "") + '" d="M' + x1 + " " + y1 + " C" + x1 + " " + (y1 + dy) + " " + x2 + " " + (y2 - dy) + " " + x2 + " " + y2 + '"/>';
    });
    svg.innerHTML = paths;
  }

  function drawSummary() {
    var ids = topicIds(role), core = ids.filter(function (t) { return !isUseful(role, t); });
    var total = 0, n = 0, byType = {};
    core.forEach(function (tid) {
      D.topics[tid].lessons.forEach(function (k) {
        var type = D.lessons[k][2], d = done(k);
        total++; if (d) n++;
        byType[type] = byType[type] || [0, 0]; byType[type][1]++; if (d) byType[type][0]++;
      });
    });
    var usefulCount = ids.filter(function (t) { return isUseful(role, t); }).reduce(function (s, t) { return s + D.topics[t].lessons.length; }, 0);
    var cur = here(role), r = 34, circ = 2 * Math.PI * r, frac = total ? n / total : 0;
    var next = cur ? nextLesson(cur) : null, L = next && D.lessons[next];
    var types = Object.keys(byType).map(function (t) { return "<li><span>" + esc(t) + "</span><b>" + byType[t][0] + " / " + byType[t][1] + "</b></li>"; }).join("");
    summary.innerHTML = '<p class="eyebrow">' + esc(role.name) + '</p><p class="rm-blurb">' + esc(role.blurb) + "</p>" +
      '<div class="rm-ring"><svg viewBox="0 0 80 80" width="96" height="96" aria-hidden="true"><circle cx="40" cy="40" r="' + r + '" class="rm-ring-bg"/>' +
      '<circle cx="40" cy="40" r="' + r + '" class="rm-ring-fg" stroke-dasharray="' + (circ * frac) + " " + circ + '" transform="rotate(-90 40 40)"/></svg>' +
      '<div><b>' + n + " / " + total + '</b><span>core lessons done</span></div></div>' +
      '<ul class="rm-types">' + types + "</ul>" +
      (L ? '<a class="btn btn-primary rm-continue" href="' + root + L[1] + '"><span class="pn-label">' + (n ? "Continue" : "Start here") + "</span>" + esc(L[0]) + "</a>"
         : '<p class="note">All core lessons done. Try the useful topics next.</p>') +
      '<p class="note">Plus ' + usefulCount + " lessons in useful topics. Progress is saved in this browser only.</p>";
  }

  function openTopic(tid) {
    var t = D.topics[tid], c = count(tid), pre = parents(role, tid);
    var rows = t.lessons.map(function (k) {
      var L = D.lessons[k], st = progress[k];
      return '<tr><td><span class="dot"' + (st ? ' data-state="' + st + '"' : "") + ' role="img" aria-label="' + (st === "done" ? "Done" : st ? "In progress" : "Not started") + '"><svg viewBox="0 0 12 12" aria-hidden="true"><path d="M3 6.2 5.1 8.3 9 4" fill="none" stroke="#fff" stroke-width="1.7"/></svg></span></td>' +
        '<td><a href="' + root + L[1] + '">' + esc(L[0]) + '</a></td><td><span class="chip">' + esc(L[2]) + "</span></td><td class=\"rm-min\">" + (L[3] ? L[3] + " min" : "") + "</td></tr>";
    }).join("");
    drawer.innerHTML = '<div class="rm-drawer-head"><div><p class="eyebrow">' + (isUseful(role, tid) ? "Useful topic" : "Core topic") + '</p><h2 id="rmDrawerTitle">' + esc(t.name) + '</h2>' +
      '<p class="note">' + c.done + " of " + c.total + ' lessons done</p></div><button type="button" class="btn-close" id="rmClose">Close</button></div>' +
      '<span class="rm-bar rm-bar-big" aria-hidden="true"><i style="width:' + Math.round(100 * c.done / c.total) + '%"></i></span>' +
      (pre.length ? '<h3 class="rm-sub">Learn first</h3><div class="rm-pre">' + pre.map(function (p) {
        var pc = count(p); return '<button type="button" class="panel rm-pre-card" data-topic="' + p + '"><b>' + esc(D.topics[p].name) + "</b><span>" + pc.done + " / " + pc.total + " done</span></button>";
      }).join("") + "</div>" : "") +
      '<h3 class="rm-sub">Lessons</h3><div class="rm-table-wrap"><table class="rm-table"><thead><tr><th><span class="sr">Status</span></th><th>Lesson</th><th>Type</th><th>Time</th></tr></thead><tbody>' + rows + "</tbody></table></div>";
    drawer.className = "rm-drawer t-" + t.track;
    drawer.hidden = false; back.hidden = false;
    document.body.classList.add("rm-open");
    document.getElementById("rmClose").addEventListener("click", closeTopic);
    drawer.querySelectorAll(".rm-pre-card").forEach(function (b) { b.addEventListener("click", function () { openTopic(b.dataset.topic); }); });
    drawer.scrollTop = 0;
    document.getElementById("rmClose").focus();
  }
  function closeTopic() {
    drawer.hidden = true; back.hidden = true;
    document.body.classList.remove("rm-open");
    if (lastNode && document.contains(lastNode)) lastNode.focus();
  }
  back.addEventListener("click", closeTopic);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !drawer.hidden) closeTopic(); });

  function setRole(id, push) {
    role = roleById(id) || D.roles[0];
    tabs.forEach(function (t) {
      var on = t.dataset.role === role.id;
      t.setAttribute("aria-selected", on); t.tabIndex = on ? 0 : -1;
    });
    graph.setAttribute("aria-labelledby", "tab-" + role.id);
    write("dws.role", role.id);
    if (push) history.replaceState(null, "", "#" + role.id);
    drawGraph(); drawSummary();
  }
  tabs.forEach(function (t, i) {
    t.addEventListener("click", function () { setRole(t.dataset.role, true); });
    t.addEventListener("keydown", function (e) {
      var k = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
      if (!k) return;
      var n = tabs[(i + k + tabs.length) % tabs.length]; n.focus(); setRole(n.dataset.role, true);
    });
  });
  var timer;
  window.addEventListener("resize", function () { clearTimeout(timer); timer = setTimeout(drawEdges, 120); });
  window.addEventListener("hashchange", function () { setRole(location.hash.slice(1), false); });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(drawEdges);
  setRole(location.hash.slice(1) || read("dws.role", D.roles[0].id), false);
})();
