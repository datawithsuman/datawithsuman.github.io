// Interview experiences: the /experiences/ list and the /experiences/share/ form.
// Both talk to the experiences Worker; its address comes from data-api on <main>.
(function () {
  var main = document.getElementById("main");
  var API = (main && main.dataset.api) || "";
  if (!API) return;
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function fmt(d) { var p = String(d).split("-"); return +p[2] + " " + MONTHS[+p[1] - 1] + " " + p[0]; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (m) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[m]; }); }
  function mark(html, words) {
    if (!words.length) return html;
    var re = new RegExp("\\b(" + words.map(function (w) { return w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }).join("|") + ")", "gi");
    return html.replace(/(^|>)([^<]+)/g, function (m, a, t) { return a + t.replace(re, "<mark>$1</mark>"); });
  }
  // The cleaned post format: "## Heading" lines, "- " or "• " bullets, blank lines between paragraphs.
  function render(body) {
    var out = [], list = [];
    function flush() { if (list.length) { out.push("<ul>" + list.join("") + "</ul>"); list = []; } }
    String(body).split("\n").forEach(function (line) {
      var l = line.trim();
      if (!l) { flush(); return; }
      if (/^#{2,3}\s+/.test(l)) { flush(); out.push("<h3>" + esc(l.replace(/^#+\s+/, "")) + "</h3>"); return; }
      if (/^[-•*]\s+/.test(l)) { list.push("<li>" + esc(l.replace(/^[-•*]\s+/, "")) + "</li>"); return; }
      flush(); out.push("<p>" + esc(l) + "</p>");
    });
    flush();
    return out.join("");
  }

  // ---------- list ----------
  var list = document.getElementById("expList");
  if (list) {
    var meta = document.getElementById("expMeta"), search = document.getElementById("expSearch");
    var family = "", query = "", next = null, loading = false, done = false, shown = 0, seq = 0;
    var reported = {};
    try { reported = JSON.parse(localStorage.getItem("exp-reported")) || {}; } catch (e) {}

    function words() { return query.toLowerCase().split(/[^a-z0-9+#]+/).filter(function (w) { return w.length > 1; }); }
    function card(p) {
      return '<li class="exp" data-id="' + p.id + '"><div class="exp-head"><span class="exp-who"><span class="exp-role">' + esc(p.role) + "</span>" + (p.company ? '<span class="exp-company">' + mark(esc(p.company), words()) + "</span>" : "") + '</span><time class="exp-date" datetime="' + p.date + '">' + fmt(p.date) + "</time></div>" +
        '<div class="exp-body">' + mark(render(p.body), words()) + "</div>" +
        '<div class="exp-foot"><button type="button" class="exp-more" hidden>Read more</button><span class="exp-gap"></span>' +
        '<button type="button" class="exp-report"' + (reported[p.id] ? " disabled>Reported" : ">Report") + "</button></div></li>";
    }
    function clampCheck() {
      Array.prototype.forEach.call(list.querySelectorAll(".exp:not([data-ck])"), function (li) {
        li.dataset.ck = "1";
        var body = li.querySelector(".exp-body");
        if (query || body.scrollHeight <= body.clientHeight + 4) body.classList.add("is-full");
        else li.querySelector(".exp-more").hidden = false;
      });
    }
    function load(reset) {
      if (!reset && (loading || done)) return;
      var my = ++seq;
      loading = true;
      if (reset) { next = null; done = false; shown = 0; list.innerHTML = ""; list.scrollTop = 0; meta.textContent = query ? "Searching…" : "Loading experiences…"; }
      var q = "v1/experiences?limit=20" + (family ? "&family=" + encodeURIComponent(family) : "") + (query ? "&q=" + encodeURIComponent(query) : "") + (next ? "&before=" + next : "");
      fetch(API + q).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(function (data) {
        if (my !== seq) return;
        list.insertAdjacentHTML("beforeend", data.posts.map(card).join(""));
        shown += data.posts.length; next = data.next; done = !next;
        if (!shown) list.innerHTML = '<li class="exp-empty">' + (query ? "No experiences match “" + esc(query) + "”. Try fewer or different words." : family ? "No experiences for this role yet." : "No experiences yet.") + ' <a href="share/">Share yours →</a></li>';
        meta.textContent = shown ? (query ? shown + (done ? "" : "+") + " matching “" + query + "”" : "Newest first · " + shown + (done ? "" : "+") + " shown") : "";
        clampCheck();
      }).catch(function () {
        if (my === seq) meta.textContent = "Couldn't load experiences. Please try again later.";
      }).then(function () { if (my === seq) loading = false; });
    }
    list.addEventListener("scroll", function () { if (list.scrollTop + list.clientHeight > list.scrollHeight - 300) load(); });
    list.addEventListener("click", function (e) {
      var more = e.target.closest(".exp-more");
      if (more) {
        var body = more.closest(".exp").querySelector(".exp-body"), open = body.classList.toggle("is-full");
        more.textContent = open ? "Show less" : "Read more";
        return;
      }
      var rep = e.target.closest(".exp-report");
      if (rep && !rep.disabled) {
        var id = rep.closest(".exp").dataset.id;
        rep.disabled = true; rep.textContent = "Reported";
        reported[id] = 1;
        try { localStorage.setItem("exp-reported", JSON.stringify(reported)); } catch (err) {}
        fetch(API + "v1/report", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ id: +id }) }).catch(function () {});
      }
    });
    var timer = null;
    search.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () { var v = search.value.trim(); if (v !== query) { query = v; load(true); } }, 300);
    });
    var btns = Array.prototype.slice.call(document.querySelectorAll("[data-exp-family]"));
    btns.forEach(function (b) {
      b.addEventListener("click", function () {
        btns.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        family = b.dataset.expFamily; load(true);
      });
    });
    load(true);
  }

  // ---------- share form ----------
  var form = document.getElementById("expForm");
  if (form) {
    var role = form.querySelector("#expRole"), company = form.querySelector("#expCompany"), text = form.querySelector("#expBody"), count = document.getElementById("expCount"), out = document.getElementById("expResult");
    var max = +text.getAttribute("maxlength");
    function upd() {
      var n = (text.value.match(/\S+/g) || []).length;
      count.textContent = n + (n === 1 ? " word" : " words") + (text.value.length > max * 0.9 ? " · " + text.value.length.toLocaleString("en") + " / " + max.toLocaleString("en") + " characters" : "");
    }
    try {
      var draft = JSON.parse(localStorage.getItem("exp-draft") || "null");
      if (draft) { if (!role.value) role.value = draft.role || ""; if (!company.value) company.value = draft.company || ""; if (!text.value) text.value = draft.body || ""; }
    } catch (e) {}
    function save() { try { localStorage.setItem("exp-draft", JSON.stringify({ role: role.value, company: company.value, body: text.value })); } catch (e) {} }
    text.addEventListener("input", function () { upd(); save(); });
    role.addEventListener("input", save); company.addEventListener("input", save);
    upd();
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = form.querySelector("button[type=submit]"), tokenEl = form.querySelector("[name=cf-turnstile-response]");
      var token = tokenEl ? tokenEl.value : "";
      function bad(msg) { out.className = "exp-result bad"; out.textContent = msg; out.hidden = false; }
      if (!role.value.trim()) return bad("Please add the role you interviewed for.");
      if (!text.value.trim()) return bad("Please write your experience.");
      if (!token) return bad("Please wait for the bot check to finish, then try again.");
      btn.disabled = true; btn.textContent = "Sharing…"; out.hidden = true;
      fetch(API + "v1/experiences", { method: "POST", headers: { "content-type": "application/json" },
        body: JSON.stringify({ role: role.value, company: company.value, body: text.value, token: token }) })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (res.status === "pending" || res.status === "approved") {
            out.className = "exp-result ok"; out.hidden = false;
            out.innerHTML = esc(res.message) + ' <a href="../">See all experiences →</a>';
            form.reset(); form.hidden = true;
            try { localStorage.removeItem("exp-draft"); } catch (err) {}
          } else bad(res.message || "Something went wrong. Please try again.");
        })
        .catch(function () { bad("Couldn't reach the server. Please try again."); })
        .then(function () { btn.disabled = false; btn.textContent = "Share experience"; if (window.turnstile) try { window.turnstile.reset(); } catch (err) {} });
    });
  }
})();
