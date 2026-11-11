#!/usr/bin/env python3
"""Builds the static site into dist/. Run: python3 build.py"""
import json
import random
import re
import shutil
from html import escape as esc
from pathlib import Path

import classical_ml
import deep_learning
import nlp_fundamentals
import llms
import ai_engineering
import maths_for_ml
import ab_testing
import ml_import
from lesson_plans import PAPER_PLANS, PLANS
from content import BODIES, TOKENS, TRACKS, WEIGHTS

HERE = Path(__file__).parent
DIST = HERE.parent / "docs"
FONTS = "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap"
TYPE_LABEL = {"concept": "Concept", "lab": "Lab", "interview": "Interview", "paper": "Paper", "design": "Design"}


def moved_modules(part, track_dir, source):
    meta = ml_import.lesson_meta()
    modules = []
    for group, name, desc in source.GROUPS:
        lessons = [{"slug": slug, "type": "concept", "imported": True, "src_dir": track_dir, "q": meta[slug]["lead"], **meta[slug], **extra}
                   for slug, extra in source.LESSONS.items() if meta[slug]["group"] == group]
        lessons.sort(key=lambda l: list(meta).index(l["slug"]))
        modules.append({"part": part, "name": name, "desc": desc, "lessons": lessons})
    return modules


TRACKS[0]["modules"] = (moved_modules("Maths for ML", "maths-for-ml", maths_for_ml)
                        + moved_modules("A/B Testing", "ab-testing", ab_testing)
                        + moved_modules("Classical ML", "machine-learning", classical_ml)
                        + moved_modules("Deep Learning", "deep-learning", deep_learning)
                        + moved_modules("NLP Fundamentals", "nlp-fundamentals", nlp_fundamentals)
                        + moved_modules("LLMs", "llms", llms)
                        + TRACKS[0]["modules"])

TRACKS[1]["modules"] = [m for part, track_dir, source in ai_engineering.PARTS for m in moved_modules(part, track_dir, source) if m["lessons"]]

_sd_old = TRACKS[2]["modules"]
for _m in _sd_old:
    _m.setdefault("part", "Recommendation Systems")
TRACKS[2]["modules"] = [m for part, src in ai_engineering.SD_PARTS
                        for m in (_sd_old if src is None else moved_modules(part, "system-design/ml-system-design", src)) if m["lessons"]]
for _m in TRACKS[2]["modules"]:
    _m["hide_name"] = True  # the sub-section title above already names it

LESSONS, ORDERED = {}, []
for t in TRACKS:
    for mi, m in enumerate(t["modules"], 1):
        for l in m["lessons"]:
            l.update(track=t, module=m, module_n=mi, key=f"{t['id']}/{l['slug']}", url=f"tracks/{t['id']}/{l['slug']}/")
            LESSONS[l["key"]] = l
            ORDERED.append(l)


def track_lessons(t):
    return [l for l in ORDERED if l["track"] is t]


import roadmap  # noqa: E402  (needs the lessons above)
RM = roadmap.build_data(ORDERED, TYPE_LABEL)

import quizzes  # noqa: E402
QUIZ_SLUG, QUIZ_AFTER = {}, {}
for _tid in quizzes.READY:
    _keys = RM["topics"][_tid]["lessons"]
    for _q in quizzes.QUIZZES[_tid]:
        _k = next((k for k in _keys if k.endswith("/" + _q[4])), None)
        if _k is None:
            raise SystemExit(f"quiz {_tid}: lesson {_q[4]} is not in that topic")
        if not 0 <= _q[2] < len(_q[1]) == 4:
            raise SystemExit(f"quiz {_tid}: bad options or answer in {_q[0][:50]}")
    QUIZ_SLUG[_tid] = re.sub(r"[^a-z0-9]+", "-", RM["topics"][_tid]["name"].lower()).strip("-")
    QUIZ_AFTER[_keys[-1]] = _tid
    RM["topics"][_tid]["quiz"] = f"quiz/{QUIZ_SLUG[_tid]}/"
    RM["topics"][_tid]["quizN"] = len(quizzes.QUIZZES[_tid])

import mocks  # noqa: E402
for _m in mocks.MOCKS:
    for _r in _m["rounds"]:
        for _q in _r["questions"]:
            for _k in _q["lessons"]:
                if _k not in LESSONS:
                    raise SystemExit(f"mock {_m['id']}/{_r['id']}: unknown lesson {_k}")
    for _role in RM["roles"]:
        if _role["id"] == _m["id"]:
            _role["mock"] = f"mock/{_m['id']}/"

import hashlib  # noqa: E402
# Changes with every edit to the shared files or lessons, so browsers fetch the new copy at once.
ASSET_V = hashlib.md5(b"".join((HERE / "assets" / n).read_bytes() for n in ("site.css", "site.js", "roadmap.js"))
                      + json.dumps(RM).encode() + json.dumps([l["key"] for l in ORDERED]).encode()).hexdigest()[:8]


BASE = "https://aimlrounds.com/"
LOGO = '<svg class="logo" width="28" height="28" viewBox="0 0 28 28" aria-hidden="true"><rect width="28" height="28" rx="7" fill="#11141B"/><circle cx="8" cy="14" r="2.4" fill="#fff"/><circle cx="14" cy="14" r="2.4" fill="#fff"/><circle cx="20" cy="14" r="2.4" fill="#fff"/></svg>'
SEARCH_ICON = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="7" cy="7" r="5"/><path d="m11 11 3.5 3.5"/></svg>'


def dot(l):
    return (f'<span class="dot" data-key="{l["key"]}" role="img" aria-label="Not started">'
            '<svg viewBox="0 0 12 12" aria-hidden="true"><path d="M3 6.2 5.1 8.3 9 4" fill="none" stroke="#fff" stroke-width="1.7"/></svg></span>')


def type_chip(kind):
    return f'<span class="chip type-{kind}">{TYPE_LABEL[kind]}</span>'


def lesson_chip(l, root):
    return f'<a class="chip chip-link t-{l["track"]["id"]}" href="{root}{l["url"]}">{esc(l["title"])}</a>'


def tokens_html(selected, interactive=False):
    row = WEIGHTS[selected]
    top = max(row)
    out = []
    for i, tok in enumerate(TOKENS):
        w = 1 if row[i] == top else round(row[i] / top * 0.6, 3)
        cls = "token" + (" is-top" if row[i] == top else "") + (" selected" if i == selected else "")
        if interactive:
            out.append(f'<button type="button" class="{cls}" style="--w:{w}" data-i="{i}" aria-pressed="{"true" if i == selected else "false"}">{tok}</button>')
        else:
            out.append(f'<span class="{cls}" style="--w:{w}">{tok}</span>')
    return "".join(out)


def bars_html(selected):
    return "".join(
        f'<div class="bar-row"><span class="bar-label">{tok}</span><span class="meter"><i style="width:{WEIGHTS[selected][i]}%"></i></span>'
        f'<span class="bar-pct">{WEIGHTS[selected][i]}%</span></div>'
        for i, tok in enumerate(TOKENS))


def preview_tags(title, desc, path):
    """What LinkedIn, WhatsApp and search engines read. Pages with no address of their own, like the 404, skip the URL."""
    url = "" if path is None else f'<link rel="canonical" href="{BASE}{path}">\n<meta property="og:url" content="{BASE}{path}">\n'
    return (f'{url}<meta property="og:site_name" content="AIML Rounds">\n<meta property="og:type" content="website">\n'
            f'<meta property="og:title" content="{esc(title)}">\n<meta property="og:description" content="{esc(desc)}">\n'
            f'<meta property="og:image" content="{BASE}assets/og-image.png">\n<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="627">\n'
            '<meta name="twitter:card" content="summary_large_image">')


def head_html(title, desc, root, active=None, page="home", extra_head="", path=None):
    if page in ("home", "jobs", "roadmap", "quiz", "mock"):
        nav = (f'<nav class="links" aria-label="Main"><a href="{root}#tracks">Tracks</a>'
               f'<a href="{root}roadmap/"{' aria-current="page"' if page == "roadmap" else ""}>Roadmap</a><a href="{root}mock/"{' aria-current="page"' if page == "mock" else ""}>Mock interviews</a><a href="{root}jobs/"{' aria-current="page"' if page == "jobs" else ""}>Jobs</a></nav>')
    else:
        tabs = "".join(
            f'<a class="t-{t["id"]}{" active" if t is active else ""}" href="{root}tracks/{t["id"]}/"'
            + (' aria-current="page"' if t is active and page == "track" else ' aria-current="true"' if t is active else "")
            + f'>{t["name"]}</a>' for t in TRACKS)
        nav = f'<nav class="tabs" aria-label="Tracks">{tabs}</nav>'
    width = "page-wide" if page == "lesson" else "page"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{preview_tags(title, desc, path)}
<script>document.documentElement.classList.add('has-js')</script>
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{root}assets/site.css?v={ASSET_V}">
{extra_head}
</head>
<body{f' class="t-{active["id"]}"' if active else ''} data-root="{root}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="{width} head-inner">
<a class="brand" href="{root}">{LOGO}<span>AIML Rounds</span></a>
{nav}
{"" if page in ("home", "jobs", "roadmap", "quiz", "mock") else f'<a class="head-link" href="{root}roadmap/">Roadmap</a><a class="head-link" href="{root}mock/">Mocks</a><a class="head-link" href="{root}jobs/">Jobs</a>'}
<button type="button" class="search-btn" id="searchOpen" aria-haspopup="dialog">{SEARCH_ICON}<span class="search-label">Search lessons</span><kbd>Ctrl K</kbd></button>
</div></header>
"""


EMAIL = "datawithsuman@gmail.com"
SOCIAL = [
    ("LinkedIn", "https://www.linkedin.com/in/sumandey02/", '<path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.75h4V21H3zM9.5 9.75h3.8v1.54h.05c.53-1 1.82-2.05 3.75-2.05 4 0 4.75 2.63 4.75 6.06V21h-4v-5c0-1.2-.02-2.73-1.66-2.73-1.67 0-1.92 1.3-1.92 2.65V21h-4z"/>'),
    ("GitHub", "https://github.com/datawithsuman/datawithsuman.github.io", '<path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.61.07-.61 1 .07 1.53 1.03 1.53 1.03.9 1.52 2.34 1.08 2.91.83.09-.65.35-1.08.63-1.33-2.22-.25-4.55-1.11-4.55-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02a9.58 9.58 0 0 1 5 0c1.91-1.29 2.75-1.02 2.75-1.02.55 1.38.2 2.4.1 2.65.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.68-4.57 4.93.36.31.68.92.68 1.85v2.75c0 .27.18.58.69.48A10 10 0 0 0 12 2z"/>'),
    ("X", "https://x.com/datawithsuman", '<path d="M17.53 3h3.06l-6.69 7.65L21.77 21h-6.16l-4.83-6.31L5.26 21H2.2l7.16-8.18L1.8 3h6.32l4.36 5.77zm-1.07 16.17h1.7L7.2 4.73H5.38z"/>'),
    ("Email", f"mailto:{EMAIL}", '<path d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm9 8.2L4.4 7.5v9.5h15.2V7.5zM5.8 7l6.2 4.6L18.2 7z"/>'),
]


def social_html(cls="foot-social"):
    links = "".join(f'<a href="{url}" aria-label="{name}" title="{name}"{"" if url.startswith("mailto") else " rel=me"}><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true">{icon}</svg></a>' for name, url, icon in SOCIAL)
    return f'<nav class="{cls}" aria-label="Find us elsewhere">{links}</nav>'


def foot_html(root, width="page", scripts=""):
    return f"""{scripts}<footer class="site-foot"><div class="{width} foot-inner"><span class="foot-name">@datawithsuman</span><span class="foot-tag">AI &amp; ML, explained simply.</span><nav class="foot-links" aria-label="Site"><a href="{root}about/">About</a><a href="{root}privacy/">Privacy</a></nav>{social_html()}</div></footer>
<dialog class="search" id="searchDialog" aria-label="Search lessons">
<div class="search-top"><label class="sr" for="searchInput">Search lessons</label><input id="searchInput" type="search" placeholder="Search lessons" autocomplete="off"><button type="button" class="btn-close" id="searchClose">Close</button></div>
<div id="searchResults" class="search-results" aria-live="polite"></div>
</dialog>
<script src="{root}assets/search-index.js?v={ASSET_V}"></script>
<script src="{root}assets/site.js?v={ASSET_V}"></script>
</body>
</html>
"""


def home():
    root = ""
    first = LESSONS["fundamentals/vectors-and-cosine-similarity"]
    pills = "".join(f'<span class="tag">{p}</span>' for p in ["Intuition", "Play", "Maths", "Say it"])
    starts = [
        ("Interview in 2 weeks", "Interview sprint", "Go straight to timed mock interviews for your role, then fill the gaps they show.", "mock/", " dark"),
        ("Starting from zero", "Fundamentals path", "Begin with the maths, then regression, and build up to neural nets one idea at a time.", "tracks/fundamentals/", ""),
        ("I build production systems", "System design path", f"{sum(1 for l in ORDERED if l['track']['id'] == 'system-design' and l['type'] == 'design')} real-world AI and ML system designs, from requirements to rollout.", "tracks/system-design/", ""),
    ]
    start_html = "".join(f'<a class="panel start{d}" href="{u}"><span class="eyebrow">{e}</span><h3>{t}</h3><p>{p}</p></a>' for e, t, p, u, d in starts)
    tracks = ""
    for t in TRACKS:
        topics = "".join(f"<li>{esc(x)}</li>" for x in t["topics"])
        tracks += (f'<a class="panel track-card t-{t["id"]}" href="tracks/{t["id"]}/"><span class="track-top"><span class="chip track-num">{t["n"]}</span>'
                   f'<span class="status-note">{t["status"]}</span></span><h3>{t["name"]}</h3><p>{t["desc"]}</p><ul>{topics}</ul></a>')
    path = [("Maths for ML", "fundamentals/vectors-and-cosine-similarity"), ("Regression", "fundamentals/linear-regression"), ("Neural nets", "fundamentals/perceptron-to-mlp"),
            ("Attention", "fundamentals/self-attention"), ("Embeddings and RAG", "fundamentals/embeddings"),
            ("Serving LLMs", "ai-engineering/prefill-vs-decode"), ("Agent design", "system-design/design-refund-agent")]
    role_cards = "".join(
        f'<a class="panel role-card" href="roadmap/#{r["id"]}" data-role-card="{r["id"]}"><span class="eyebrow">Roadmap</span><h3>{r["name"]}</h3><p>{r["blurb"]}</p>'
        f'<span class="role-meter"><i></i></span><span class="note role-note">{sum(len(RM["topics"][t]["lessons"]) for row in r["rows"] for t in row)} lessons</span></a>'
        for r in RM["roles"])
    road = "".join(f'<li><a class="chip chip-road t-{LESSONS[k]["track"]["id"]}" href="{LESSONS[k]["url"]}">{n}</a></li>' for n, k in path)
    html = head_html("AIML Rounds: learn AI until you can explain it",
                     "Short, visual lessons on machine learning, LLMs and system design. Concept lessons end with you saying the answer out loud. Paper lessons end with what changed.", root, path="")
    html += f"""<main id="main">
<section class="page hero">
  <div class="hero-copy">
    <p class="eyebrow">AI · ML · SYSTEM DESIGN</p>
    <h1 class="h1-home">Learn AI until you can explain it.</h1>
    <p class="lead">Short, visual lessons on machine learning, LLMs and system design. Concept lessons end with you saying the answer out loud. Paper lessons end with what changed.</p>
    <div class="btn-row"><a class="btn btn-primary" href="{first['url']}">Start with Maths for ML</a><a class="btn btn-secondary" href="#roadmap">See the roadmap</a></div>
  </div>
  <div class="panel preview t-fundamentals">
    <span class="chip type-track">Fundamentals</span>
    <h2>Self-attention</h2>
    <p>Click a word. See what it looks at.</p>
    <div class="tokens" aria-label="Example sentence: The cat chased its tail, with its selected">{tokens_html(3)}</div>
    <div class="pills">{pills}</div>
  </div>
</section>
<section class="page jobs-strip-wrap" data-jobs-strip hidden><a class="panel jobs-strip" href="jobs/"><span class="chip">Jobs</span><span><b data-jobs-count></b> new AI/ML job postings this week</span><span class="jobs-strip-go">See jobs →</span></a></section>
<section class="page section"><h2>Where are you starting from?</h2><div class="card-grid">{start_html}</div></section>
<section class="page section" id="tracks"><h2>Four tracks, one colour each</h2>
<p class="section-lead">The colour follows you into every lesson, so you always know which track you are in.</p>
<div class="card-grid">{tracks}</div></section>
<section class="page section" id="roadmap"><h2>Pick a role. Follow its roadmap.</h2>
<p class="section-lead">Each role has its own map of topics, in the order that makes the next one easy. Your progress is saved in this browser.</p>
<div class="card-grid role-cards">{role_cards}</div></section>
</main>
"""
    write("index.html", html + foot_html(root, scripts=f'<script src="{root}assets/roadmap-data.js?v={ASSET_V}"></script>'))


def quiz_row(key, root):
    """The quiz link that closes a topic, shown after the topic's last lesson."""
    tid = QUIZ_AFTER.get(key)
    if not tid:
        return ""
    n = len(quizzes.QUIZZES[tid])
    return (f'<li class="quiz-li"><a class="row quiz-row" href="{root}quiz/{QUIZ_SLUG[tid]}/"><span class="quiz-mark" aria-hidden="true">?</span>'
            f'<span class="row-title">Quiz: {esc(RM["topics"][tid]["name"])}</span><span class="chip">Quiz</span><span class="mins">{n} Qs</span></a></li>')


def quiz_cta(l, root):
    tid = QUIZ_AFTER.get(l["key"])
    if not tid:
        return ""
    name = RM["topics"][tid]["name"]
    return (f'<section class="panel quiz-cta"><div><p class="eyebrow">End of {esc(name)}</p><h2>Ready? Try the {esc(name)} quiz.</h2>'
            f'<p>{len(quizzes.QUIZZES[tid])} questions across this topic, each with the answer and the lesson to revisit.</p></div>'
            f'<a class="btn btn-primary" href="{root}quiz/{QUIZ_SLUG[tid]}/">Take the quiz</a></section>')


def quiz_page(tid):
    root = "../../"
    t, qs = RM["topics"][tid], quizzes.QUIZZES[tid]
    name = t["name"]
    desc = f"{len(qs)} questions on {name}, from {len(t['lessons'])} lessons. Pick an answer in your head, then open it."
    items = ""
    for i, (q, opts, ans, why, slug) in enumerate(qs, 1):
        key = next(k for k in t["lessons"] if k.endswith("/" + slug))
        les = LESSONS[key]
        letters = "ABCD"
        # Shuffle options with a seed from the question, so the right answer isn't always in the same slot
        # and the order stays the same between builds.
        order = list(range(len(opts)))
        random.Random(hashlib.md5(q.encode()).hexdigest()).shuffle(order)
        ans = order.index(ans)
        opts = [opts[k] for k in order]
        options = "".join(f'<li><b>{letters[j]}.</b> {esc(o)}</li>' for j, o in enumerate(opts))
        items += (f'<li class="panel quiz-q" id="q{i}"><p class="quiz-num">Question {i} of {len(qs)}</p><h2>{esc(q)}</h2><ol class="quiz-opts">{options}</ol>'
                  f'<details class="quiz-ans"><summary>View answer</summary><p class="quiz-right">✓ {letters[ans]}. {esc(opts[ans])}</p><p>{esc(why)}</p>'
                  f'<p class="quiz-lesson">Lesson: <a href="{root}{les["url"]}">{esc(les["title"])}</a></p></details></li>')
    roles = [r["name"] for r in RM["roles"] if tid in [x for row in r["rows"] for x in row]]
    html = head_html(f"{name} quiz · AIML Rounds", desc, root, page="quiz", path=f"quiz/{QUIZ_SLUG[tid]}/")
    html += f"""<main id="main"><section class="page quiz-page t-{t['track']}"><nav class="crumbs" aria-label="Breadcrumb"><a href="{root}">Home</a><span aria-hidden="true">/</span><a href="{root}roadmap/">Roadmap</a><span aria-hidden="true">/</span><b aria-current="page">{esc(name)} quiz</b></nav>
<p class="eyebrow">QUIZ</p><h1 class="h1-track">{esc(name)}</h1><p class="lead">{esc(desc)}</p>
<p class="note">On the roadmap for: {", ".join(roles)}.</p>
<ol class="quiz-list">{items}</ol>
<div class="btn-row"><a class="btn btn-secondary" href="{root}roadmap/">Back to the roadmap</a></div>
</section></main>
"""
    write(f"quiz/{QUIZ_SLUG[tid]}/index.html", html + foot_html(root))


def track_page(t, idx):
    root = "../../"
    lessons = track_lessons(t)
    know = ""
    if t["know"]:
        know = '<div class="know"><span>You should know:</span>' + "".join(lesson_chip(LESSONS[k], root) for k in t["know"]) + "</div>"
    data = esc(json.dumps([{"key": l["key"], "title": l["title"], "url": f'{root}{l["url"]}'} for l in lessons]))
    mods, part = "", None
    for mi, m in enumerate(t["modules"], 1):
        if m.get("part") and m["part"] != part:
            part = m["part"]
            mods += f'<h2 class="part-title">{part}</h2>'
        rows = "".join(
            f'<li><a class="row" href="{l["slug"]}/">{dot(l)}<span class="row-title">{esc(l["title"])}</span>{type_chip(l["type"])}<span class="mins">{l["minutes"]} min</span></a></li>'
            + quiz_row(l["key"], root)
            for l in m["lessons"])
        heading = "h3" if m.get("part") else "h2"
        count = len(m["lessons"])
        mods += (f'<details class="panel module" id="module-{mi}"{" open" if mi == 1 else ""}><summary><span class="module-text"><span class="eyebrow">Module {mi} · {count} lesson{"" if count == 1 else "s"}</span>'
                 + ("" if m.get("hide_name") else f'<{heading}>{m["name"]}</{heading}>') + f'<span class="module-desc">{m["desc"]}</span></span></summary>'
                 f'<ol class="rows">{rows}</ol></details>')
    nxt = TRACKS[idx + 1] if idx + 1 < len(TRACKS) else None
    if nxt:
        foot = f'<section class="panel next-track t-{nxt["id"]}"><div><p class="eyebrow">Next track</p><h2>Next track: {nxt["name"]}</h2><p>{nxt["desc"]}</p></div><a class="btn btn-secondary" href="../{nxt["id"]}/">Open {nxt["name"]}</a></section>'
    else:
        foot = f'<section class="panel next-track"><div><p class="eyebrow">Last track</p><h2>That is all four tracks.</h2><p>Go back to the roadmap to see what to revisit.</p></div><a class="btn btn-secondary" href="{root}#roadmap">See the roadmap</a></section>'
    html = head_html(f'{t["name"]} · AIML Rounds', t["desc"], root, t, "track", path=f'tracks/{t["id"]}/')
    html += f"""<main id="main">
<section class="band"><div class="page band-inner">
  <div>
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}">Home</a><span aria-hidden="true">/</span><b aria-current="page">{t['name']}</b></nav>
    <span class="chip type-track mono-num">Track {t['n']}</span>
    <h1 class="h1-track">{t['name']}</h1>
    <p class="lead">{t['desc']}</p>
    {know}
  </div>
  <section class="panel continue" id="continue" aria-label="Continue where you left off" data-track="{t['id']}" data-lessons="{data}" hidden>
    <p class="eyebrow">Continue where you left off</p>
    <h2 id="continueTitle"></h2>
    <div class="progress" role="img" id="continueBar"><i></i></div>
    <p class="progress-note" id="continueNote"></p>
    <a class="btn btn-primary" id="continueLink" href="#">Resume lesson</a>
  </section>
</div></section>
<div class="page modules">{mods}{foot}</div>
</main>
"""
    write(f'tracks/{t["id"]}/index.html', html + foot_html(root))


def layer_section(s, i):
    inner = ""
    if s.get("widget") == "attention":
        matrix = esc(json.dumps({"tokens": TOKENS, "weights": WEIGHTS}))
        inner = (f'<div class="widget" data-widget="attention" data-matrix="{matrix}">'
                 f'<div class="tokens" role="group" aria-label="Pick a word">{tokens_html(3, True)}</div>'
                 f'<p class="widget-caption" id="attnCaption"><b>its</b> looks at <b>cat</b> the most.</p>'
                 f'<div class="meters" aria-live="polite">{bars_html(3)}</div>'
                 '<p class="note">These weights are illustrative, written by hand.</p></div>')
    elif "code" in s:
        inner = f'<pre class="code-block" tabindex="0"><code>{esc(s["code"])}</code></pre>'
        if "note" in s:
            inner += f'<p class="note">{s["note"]}</p>'
    else:
        inner = s["html"]
    return f'<section class="panel block" id="{s["id"]}" data-layer="{i}"><h2>{esc(s["title"])}</h2>{inner}</section>'


def interview_html(questions):
    out = ""
    for i, (q, a) in enumerate(questions):
        sid = "interview" if i == 0 else f"interview-{i + 1}"
        out += f"""<section class="interview" id="{sid}">
<p class="eyebrow">Interview question{f' {i + 1}' if len(questions) > 1 else ''}</p>
<h2>{esc(q)}</h2>
<p class="say-first">Say your answer out loud first.</p>
<button type="button" class="btn btn-reveal" aria-expanded="false" aria-controls="{sid}-answer" data-reveal>Reveal answer</button>
<div class="answer" id="{sid}-answer"><p>{esc(a)}</p></div>
</section>"""
    return out


def contents_html(l, root):
    t = l["track"]
    out, part = "", None
    for m in t["modules"]:
        if m.get("part") and m["part"] != part:
            part = m["part"]
            out += f'<p class="contents-part">{part}</p>'
        links = ""
        for x in m["lessons"]:
            cur = x is l
            links += (f'<li><a{" class=\"current\" aria-current=\"page\"" if cur else ""} href="{root}{x["url"]}">{dot(x)}<span>{esc(x["title"])}</span></a></li>')
        out += f'<details class="mod"{" open" if m is l["module"] else ""}><summary>{m["name"]}</summary><ol>{links}</ol></details>'
    return out


def interview_card(sid, label, question, answer, extra=""):
    return f"""<section class="interview{extra}" id="{sid}">
<p class="eyebrow">{label}</p>
<h2>{question}</h2>
<p class="say-first">Say your answer out loud first.</p>
<button type="button" class="btn btn-reveal" aria-expanded="false" aria-controls="{sid}-answer" data-reveal>Reveal answer</button>
<div class="answer" id="{sid}-answer">{answer}</div>
</section>"""


def practice_card(questions):
    """Practice pages: one card, one question at a time. Without JavaScript every question shows."""
    n = len(questions)
    stepper = "".join(f'<li><button type="button" data-pq-go="{i}" aria-label="Question {i + 1}"><span class="say-dot">{i + 1}</span></button></li>' for i in range(n))
    body = ""
    for i, q in enumerate(questions):
        nxt = (f'<button type="button" class="btn btn-track" data-pq-go="{i + 1}">Next question</button>' if i + 1 < n else
               '<button type="button" class="btn btn-track" data-pq-finish>Finish</button>')
        label = q["label"].replace("Q", "Question ", 1)
        body += f"""<div class="pq" data-pq id="{q['id']}" tabindex="-1">
<header class="say-head"><p class="eyebrow">{label}</p><h2>{q['q']}</h2></header>
<div class="say-body"><div class="say-step">
<p class="say-hint">Say your approach out loud first.</p>
<div class="say-actions"><button type="button" class="btn btn-secondary" aria-expanded="false" aria-controls="{q['id']}-answer" data-reveal>Reveal answer</button>{nxt}</div>
<div class="answer" id="{q['id']}-answer">{q['answer']}</div>
</div></div>
</div>"""
    return f'<section class="say-card practice-card" id="questions"><ol class="say-stepper many" aria-label="Questions">{stepper}</ol>{body}</section>'


def imported_lesson(l, root):
    """Returns the centre column, page contents, head tags and scripts for a moved lesson."""
    src = ml_import.read_lesson(l["src_dir"], l["slug"])
    css_name, css = ml_import.css_asset(src["css"])
    write(f"assets/{css_name}", css)

    # Depth goes by what a chapter holds. Chapters stay in their original order.
    used = [x for x in ("intuition", "maths", "code") if any(c["layer"] == x for c in src["chapters"])]
    names = {"intuition": "Intuition", "maths": "Maths", "code": "Code"}
    center = ""
    if len(used) > 1:
        btns = "".join(f'<button type="button" data-depth="{n}" aria-pressed="{"true" if n == 0 else "false"}">{"+ " if n else ""}{names[x]}</button>' for n, x in enumerate(used))
        center += f'<div class="depth" role="group" aria-label="Choose depth" data-track="{l["track"]["id"]}">{btns}</div>'

    toc = [("idea", "How to use this page" if src["questions"] else "The idea", None)]
    chapters, reference = "", ""
    for c in src["chapters"]:
        if c["layer"] == "reference":
            reference += c["html"]
            continue
        n = used.index(c["layer"])
        chapters += c["html"].replace('<section class="ch"', f'<section data-layer="{n}" class="ch"', 1)
        toc.append((c["id"], c["toc"], n))
    more_title = "More practice and sources" if src["questions"] else "Evidence, caveats and sources"
    toc.append(("reference", more_title, None))
    if src["questions"]:
        toc = [("idea", "How to use this page", None), ("questions", "Questions", None), ("reference", more_title, None)]
    else:
        toc.append(("interview", "Interview question", None))

    preamble = f'<div class="preamble">{src["preamble"]}</div>' if src["preamble"] else ""
    more_block = f"""<details class="more" id="reference"><summary>{more_title}</summary><p class="small built-from">{src['built_from']}</p>{reference}</details>"""
    eyebrow = "How to use this page" if src["questions"] else "The idea"
    if src["questions"]:
        questions = practice_card(src["questions"])
    else:
        questions = interview_card("interview", "Interview question", esc(l["q"]), src["answer"])
    center += f"""<div class="lx">
<section class="panel block idea" id="idea"><p class="eyebrow">{eyebrow}</p><div class="idea-text">{src['idea']}</div>{src['legend']}</section>
{preamble}{chapters}
{"" if src["questions"] else more_block}
<div class="tip" id="tip"></div>
</div>
<div hidden><div id="prog"></div><nav class="toc" aria-hidden="true"></nav></div>
{questions}
{f'<div class="lx">{more_block}</div>' if src["questions"] else ""}
<p class="mark-done"><button type="button" class="link-btn" id="markDone">Mark done</button></p>"""
    extra_head = f'<link rel="stylesheet" href="{root}assets/{css_name}">\n' + "\n".join(src["head_scripts"])
    return center, toc, extra_head, "\n".join(src["scripts"]) + "\n"


def say_it_html(plan, followups, answer):
    """The interview block for seven-section lessons. Without JavaScript every step simply shows."""
    n = len(followups)
    steps = ["Say it", "Check", "Follow-ups", "Answer"]
    stepper = "".join(f'<li><button type="button" data-say-go="{i}"{"" if i == 0 else " disabled"}><span class="say-dot">{i + 1}</span><span>{s}</span></button></li>' for i, s in enumerate(steps))
    checks = "".join(f'<li><label><input type="checkbox" data-check><span>{esc(c)}</span></label></li>' for c in plan["checklist"])
    fus = ""
    for i, (q, a) in enumerate(followups, 1):
        nxt = ('<button type="button" class="btn btn-track" data-next-fu>Next follow-up</button>' if i < n else
               '<button type="button" class="btn btn-track" data-say-go="3">See our answer</button>')
        fus += f"""<div class="fu" data-fu>
<p class="eyebrow">Follow-up {i} of {n}</p>
<p class="fu-q">{q}</p>
<p class="say-hint">Answer it out loud, then check.</p>
<div class="say-actions"><button type="button" class="btn btn-secondary" aria-expanded="false" aria-controls="fu{i}-answer" data-reveal>Reveal answer</button>{nxt}</div>
<div class="answer" id="fu{i}-answer"><p>{a}</p></div>
</div>"""
    # The 30-second answer leads. Anything longer stays one click away.
    parts = re.split(r"(?=<h3>)", answer.strip())
    parts = [x for x in parts if x.strip()]
    lead, more = parts[0], "".join(parts[1:])
    more_html = f'<details class="say-more"><summary>Go further</summary>{more}</details>' if more else ""
    return f"""<section class="say-card" id="interview">
<header class="say-head"><p class="eyebrow">Say it</p><h2>{esc(plan['q'])}</h2></header>
<ol class="say-stepper" aria-label="Steps">{stepper}</ol>
<div class="say-body">
<div class="say-step" data-say-step tabindex="-1">
<h3>Say your answer out loud</h3>
<p class="say-hint">{plan.get("say_hint", "Aim for 30 seconds. It feels different from reading it, and that's the point.")}</p>
<div class="say-actions"><button type="button" class="btn btn-track" data-say-go="1">I've said it</button><button type="button" class="link-btn" data-say-go="3">Skip to our answer</button></div>
</div>
<div class="say-step" data-say-step tabindex="-1">
<h3>Tick what you covered</h3>
<ul class="checks">{checks}</ul>
<div class="check-meter"><span class="meter"><i data-check-bar></i></span><span class="check-count" aria-live="polite" data-check-count></span></div>
<div class="say-actions"><button type="button" class="btn btn-track" data-say-go="2">Take the follow-ups</button><button type="button" class="link-btn" data-say-go="3">Skip to our answer</button></div>
</div>
<div class="say-step" data-say-step tabindex="-1">
<h3>The interviewer pushes further</h3>
{fus}
</div>
<div class="say-step say-final" data-say-step tabindex="-1">
<p class="say-score" data-say-score hidden></p>
{lead}
{more_html}
</div>
</div>
</section>
<p class="mark-done"><button type="button" class="link-btn" id="markDone">Mark done</button></p>"""


def _plain_chapter(html, edits):
    """A chapter as it sits inside a section: no number label, headings one level down."""
    html = re.sub(r'<div class="chap">.*?</div>\s*', "", html, count=1, flags=re.S)
    html = re.sub(r"<(/?)h([23])\b", lambda m: f"<{m.group(1)}h{int(m.group(2)) + 1}", html)
    # A diagram with clickable boxes isn't one image, so screen readers should reach its links.
    html = re.sub(r"<svg\b[^>]*>.*?</svg>", lambda m: m.group(0).replace('role="img"', 'role="group"', 1) if "<a " in m.group(0) else m.group(0), html, flags=re.S)
    if "<h3" not in html:
        label = re.sub(r"^\d+ · ", "", re.search(r'data-toc="([^"]*)"', html).group(1))
        html = re.sub(r"(<section[^>]*>)", rf"\1<h3>{label}</h3>", html, count=1)
    return html


def plan_lesson(l, root):
    """Returns the centre column, page contents, head tags and scripts for a seven-section lesson."""
    plan = PLANS[l["key"]]
    extra_head, scripts = "", ""
    chapters, built_from, summary, preamble = {}, "", "", ""
    if l.get("imported"):
        src = ml_import.read_lesson(l["src_dir"], l["slug"])
        css_name, css = ml_import.css_asset(src["css"])
        write(f"assets/{css_name}", css)
        extra_head = f'<link rel="stylesheet" href="{root}assets/{css_name}">\n' + "\n".join(src["head_scripts"])
        scripts = "\n".join(src["scripts"]) + "\n"
        for old, new in plan.get("script_edits", []):
            if old not in scripts:
                raise ValueError(f'{l["key"]}: script edit does not match: {old}')
            scripts = scripts.replace(old, new)
        chapters = {c["id"]: c["html"] for c in src["chapters"]}
        built_from, preamble = src["built_from"], src["preamble"]
        summary = f'<section class="ch" id="summary"><h3>In one breath</h3>{src["idea"]}{src["legend"]}</section>'
        followups = re.findall(r'<details class="qa"><summary>(.*?)</summary>(?:<p>)?(.*?)(?:</p>)?</details>', src["answer"], re.S)
        answer = re.sub(r'<h3>Likely follow-ups</h3>|<details class="qa">.*?</details>', "", src["answer"], flags=re.S)
        placed = {plan["play"]["chapter"], *plan["situation_chapters"], *plan["how"], *plan["practice"], *plan["trap"], *plan["reference"]}
        missing = set(chapters) - placed
        if missing or placed - set(chapters):
            raise ValueError(f'{l["key"]}: chapters not placed {missing}, unknown {placed - set(chapters)}')
        joined = "\n".join(chapters.values()) + src["answer"]
        for old, new in plan.get("edits", []):
            if old not in joined:
                raise ValueError(f'{l["key"]}: edit does not match: {old}')
            chapters = {k: v.replace(old, new) for k, v in chapters.items()}
            followups = [(q.replace(old, new), a.replace(old, new)) for q, a in followups]
            answer = answer.replace(old, new)
        for pattern in plan.get("strip", []):
            if not re.search(pattern, "\n".join(chapters.values()), re.S):
                raise ValueError(f'{l["key"]}: strip does not match: {pattern}')
            chapters = {k: re.sub(pattern, "", v, flags=re.S) for k, v in chapters.items()}
        chapters = {k: _plain_chapter(v, None) for k, v in chapters.items()}
    else:
        followups, answer = plan["followups"], plan["answer"]

    def block(ids):
        return "".join(chapters[i] for i in ids)

    def section(sid, title, inner):
        return f'<div class="sec" id="{sid}"><h2 class="sec-title">{title}</h2>{inner}</div>'

    def chapter_toc(ids, panel):
        return [(i, re.sub(r"^\d+ · ", "", re.search(r'data-toc="([^"]*)"', chapters[i]).group(1)), panel) for i in ids]

    names = plan["tabs"] + ["Say it"]
    keys = ["intuition", "how", "practice", "say"]

    def panel(key, inner):
        n = keys.index(key)
        nxt = f'<button type="button" class="btn btn-track panel-next" data-tab-go="{keys[n + 1]}">Next: {names[n + 1]}</button>' if n < 3 else ""
        return f'<div class="tab-panel" id="panel-{key}" role="tabpanel" aria-labelledby="tab-{key}" tabindex="-1">{inner}{nxt}</div>'

    toc = [("situation", "The situation", "intuition"), ("idea", "The idea", "intuition")]
    situation_extra = f'<div class="sit-more">{preamble}{block(plan["situation_chapters"])}</div>' if l.get("imported") else ""
    intuition = f"""<section class="panel block sit" id="situation"><h2 class="eyebrow">The situation</h2>
<p class="sit-lead">{esc(plan['situation'])}</p>
<blockquote class="sit-q">{esc(plan['q'])}</blockquote>{situation_extra}</section>
<section class="panel block idea" id="idea"><h2 class="eyebrow">The idea</h2><p class="idea-analogy">{esc(plan['analogy'])}</p>
<figure class="picture">{plan['picture']}<figcaption>{esc(plan['caption'])}</figcaption></figure></section>"""
    if "play" in plan:
        toc.append(("play", "Play", "intuition"))
        intuition += section("play", "Play", f'<p class="play-try">{plan["play"]["try"]}</p>{block([plan["play"]["chapter"]])}<p class="play-why">{plan["play"]["why"]}</p>')

    trap_title = "The answer that sounds right"
    if l.get("imported"):
        toc.append(("summary", "In one breath", "how"))
        toc += chapter_toc(plan["how"], "how") + chapter_toc(plan["practice"], "practice")
        toc.append(("trap", trap_title, "practice"))
        how = summary + block(plan["how"])
        practice = block(plan["practice"])
        trap = block(plan["trap"])
        if plan.get("trap_html"):
            trap += f'<section class="ch" id="trap-note"><h3>{esc(plan["trap_title"])}</h3>{plan["trap_html"]}</section>'
    else:
        layers = BODIES[plan["body"]]["layers"]
        toc += [(s["id"], s["title"], "how") for s in layers[1]["sections"]]
        toc += [(s["id"], s["title"], "practice") for s in layers[2]["sections"]]
        toc.append(("trap", trap_title, "practice"))
        how = "".join(layer_section(s, 1).replace(' data-layer="1"', "") for s in layers[1]["sections"])
        practice = "".join(layer_section(s, 2).replace(' data-layer="2"', "") for s in layers[2]["sections"])
        trap = f'<section class="panel block"><h3>{esc(plan["trap_title"])}</h3>{plan["trap_html"]}</section>'
    toc.append(("interview", "Say it", "say"))

    panels = (panel("intuition", intuition) + panel("how", section("how", names[1], how))
              + panel("practice", section("practice", names[2], practice) + section("trap", trap_title, trap)))
    tabs = "".join(f'<button type="button" role="tab" id="tab-{k}" aria-controls="panel-{k}" data-tab="{k}" aria-selected="{"true" if k == "intuition" else "false"}">{n}</button>' for k, n in zip(keys, names))
    tablist = f'<div class="lesson-tabs" role="tablist" aria-label="Lesson sections">{tabs}</div>'
    say = panel("say", say_it_html(plan, followups, answer))
    if l.get("imported"):
        reference = (f'<details class="more" id="reference"><summary>Key terms and sources</summary>'
                     f'<p class="small built-from">{built_from}</p>{block(plan["reference"])}</details>')
        center = (f'{tablist}<div class="lx">{panels}</div>{say}<div class="lx">{reference}<div class="tip" id="tip"></div></div>'
                  '<div hidden><div id="prog"></div><nav class="toc" aria-hidden="true"></nav></div>')
    else:
        center = f"{tablist}{panels}{say}"
    return center, toc, extra_head, scripts


def paper_lesson(l, root):
    """Returns the centre column, page contents, head tags and scripts for a paper lesson."""
    plan = PAPER_PLANS[l["key"]]
    extra_head, scripts, chapters = "", "", {}
    imported = l.get("imported")
    if imported:
        src = ml_import.read_paper(l["slug"])
        css_name, css = ml_import.css_asset(src["css"])
        write(f"assets/{css_name}", css)
        extra_head = f'<link rel="stylesheet" href="{root}assets/{css_name}">\n' + "\n".join(src["head_scripts"])
        scripts = "\n".join(src["scripts"]) + "\n"
        if src["figures_dir"].exists():
            shutil.copytree(src["figures_dir"], DIST / l["url"] / "figures", dirs_exist_ok=True)
        chapters = dict(src["chapters"])
        placed = {*plan["problem"], *plan["how"], *plan["found"], *plan["limits"], *plan["verdict"], *plan["reference"], *plan["hidden"],
                  *plan.get("changed_chapters", []), *([plan["picture_chapter"]] if "picture_chapter" in plan else [])}
        if set(chapters) != placed:
            raise ValueError(f'{l["key"]}: not placed {set(chapters) - placed}, unknown {placed - set(chapters)}')
        joined = "\n".join(chapters.values())
        for old, new in plan.get("edits", []):
            if old not in joined:
                raise ValueError(f'{l["key"]}: edit does not match: {old}')
            chapters = {k: v.replace(old, new) for k, v in chapters.items()}
        for pattern in plan.get("strip", []):
            joined = "\n".join(chapters.values())
            if not re.search(pattern, joined, re.S):
                raise ValueError(f'{l["key"]}: strip does not match: {pattern}')
            chapters = {k: re.sub(pattern, "", v, flags=re.S) for k, v in chapters.items()}
        lab = ""
        if "play" in plan:
            lab, chapters[plan["play"]["chapter"]] = ml_import.extract_div(chapters[plan["play"]["chapter"]], plan["play"]["lab"])
        chapters = {k: _plain_chapter(v, None) for k, v in chapters.items()}
        tldr = src["tldr"]
        for old, new in plan.get("tldr_replace", []):
            if old not in tldr:
                raise ValueError(f'{l["key"]}: summary edit does not match: {old}')
            tldr = tldr.replace(old, new)
        meta, legend = src["meta"], src["legend"]
    else:
        tldr, meta, legend, lab = plan["tldr"], plan["meta"], "", ""

    def block(ids):
        return "".join(chapters[i] for i in ids)

    def card(inner):
        return f'<section class="panel block">{inner}</section>'

    def section(sid, title, inner):
        return f'<div class="sec" id="{sid}"><h2 class="sec-title">{title}</h2>{inner}</div>'

    def chapter_toc(ids, key):
        return [(i, re.sub(r"^\d+ · ", "", re.search(r'data-toc="([^"]*)"', chapters[i]).group(1)), key) for i in ids]

    keys = ["gist", "method", "results", "why"]
    names = ["Gist", "Method", "Results", "Why it matters"]

    def panel(key, inner):
        n = keys.index(key)
        nxt = f'<button type="button" class="btn btn-track panel-next" data-tab-go="{keys[n + 1]}">Next: {names[n + 1]}</button>' if n < 3 else ""
        return f'<div class="tab-panel" id="panel-{key}" role="tabpanel" aria-labelledby="tab-{key}" tabindex="-1">{inner}{nxt}</div>'

    intro = f'<section class="panel block paper-card" id="paper"><h2 class="eyebrow">The paper</h2><p class="paper-meta">{meta}</p><div class="paper-tldr">{tldr}</div>{legend}</section>'
    problem = block(plan["problem"]) if imported else card(plan["problem_html"])
    if "picture_chapter" in plan:
        flow = re.sub(r"<h3[^>]*>.*?</h3>", "", chapters[plan["picture_chapter"]], count=1, flags=re.S)
        flow = re.sub(r"</?section[^>]*>", "", flow)
        picture = f'<div class="picture">{flow}</div>'
    else:
        picture = f'<figure class="picture">{plan["picture"]}<figcaption>{esc(plan["caption"])}</figcaption></figure>'
    gist = (intro + section("problem-sec", "The problem", problem)
            + f'<section class="panel block idea" id="idea"><h2 class="eyebrow">The idea</h2><p class="idea-analogy">{esc(plan["analogy"])}</p>{picture}</section>')
    toc = [("paper", "The paper", "gist"), ("problem-sec", "The problem", "gist"), ("idea", "The idea", "gist")]
    if "play" in plan:
        toc.append(("play", "Play", "gist"))
        lab_box = f'<section class="ch">{lab}</section>'
        gist += section("play", "Play", f'<p class="play-try">{plan["play"]["try"]}</p>{lab_box}<p class="play-why">{plan["play"]["why"]}</p>')

    if imported:
        how, found, limits = block(plan["how"]), block(plan["found"]), block(plan["limits"])
        if plan.get("found_first_figure"):
            found = f'<section class="ch">{src["figure"]}</section>' + found
        changed_extra, verdict = block(plan.get("changed_chapters", [])), block(plan["verdict"])
        toc += chapter_toc(plan["how"], "method")
        changed_box = f'<section class="ch">{plan["changed_html"]}</section>'
    else:
        how, found, limits = card(plan["method_html"]), card(plan["found_html"]), card(plan["limits_html"])
        changed_extra, verdict = "", card("<h3>Verdict</h3>" + plan["verdict_html"])
        toc.append(("how", "Method", "method"))
        changed_box = card(plan["changed_html"])
    toc += [("found", "What they found", "results"), ("limits", "Where it falls short", "results"), ("changed", "What it changed", "why")]

    done = '<p class="mark-done"><button type="button" class="link-btn" id="markDone">Mark done</button></p>'
    panels = (panel("gist", gist) + panel("method", section("how", "Method", how))
              + panel("results", section("found", "What they found", found) + section("limits", "Where it falls short", limits))
              + panel("why", section("changed", "What it changed", changed_box + changed_extra + verdict) + done))
    tabs = "".join(f'<button type="button" role="tab" id="tab-{k}" aria-controls="panel-{k}" data-tab="{k}" aria-selected="{"true" if k == "gist" else "false"}">{n}</button>' for k, n in zip(keys, names))
    tablist = f'<div class="lesson-tabs" role="tablist" aria-label="Lesson sections">{tabs}</div>'
    if imported:
        tip = '<div class="tip" id="tip"></div>' if src["has_tip"] else ""
        reference = f'<details class="more" id="reference"><summary>Key terms and sources</summary>{block(plan["reference"])}</details>'
        toc.append(("reference", "Key terms and sources", None))
        center = f'{tablist}<div class="lx">{panels}{reference}{tip}</div><div hidden><div id="prog"></div><nav class="toc" aria-hidden="true"></nav></div>'
    else:
        center = f"{tablist}{panels}"
    return center, toc, extra_head, scripts


def lesson_page(l):
    root = "../../../"
    t = l["track"]
    body = BODIES.get(l.get("body"))
    lessons = track_lessons(t)
    i = lessons.index(l)
    prev_l, next_l = (lessons[i - 1] if i else None), (lessons[i + 1] if i + 1 < len(lessons) else None)

    meta = type_chip(l["type"]) + f'<span class="mins">{l["minutes"]} min</span>'
    if l.get("prereqs"):
        meta += '<span class="before">Before this:</span>' + "".join(lesson_chip(LESSONS[k], root) for k in l["prereqs"])

    toc, center, extra_head, scripts = [], "", "", ""
    if l["key"] in PAPER_PLANS:
        center, toc, extra_head, scripts = paper_lesson(l, root)
    elif l["key"] in PLANS:
        center, toc, extra_head, scripts = plan_lesson(l, root)
    elif l.get("imported"):
        center, toc, extra_head, scripts = imported_lesson(l, root)
    elif body:
        layers = body["layers"]
        if layers:
            btns = "".join(f'<button type="button" data-depth="{n}" aria-pressed="{"true" if n == 0 else "false"}">{"+ " if n else ""}{esc(x["name"])}</button>' for n, x in enumerate(layers))
            center += f'<div class="depth" role="group" aria-label="Choose depth" data-track="{t["id"]}">{btns}</div>'
        if body["idea"]:
            center += f'<section class="panel block idea" id="idea"><p class="eyebrow">The idea</p><p>{esc(body["idea"])}</p></section>'
            toc.append(("idea", "The idea", None))
        for n, layer in enumerate(layers):
            for s in layer["sections"]:
                center += layer_section(s, n)
                toc.append((s["id"], s["title"], n))
        center += interview_html(body["interview"])
        for n, (q, _) in enumerate(body["interview"]):
            toc.append(("interview" if n == 0 else f"interview-{n + 1}", "Interview question" + (f" {n + 1}" if len(body["interview"]) > 1 else ""), None))
        center += '<p class="mark-done"><button type="button" class="link-btn" id="markDone">Mark done</button></p>'
    else:
        center += ('<section class="panel block stub"><p class="eyebrow">Placeholder</p>'
                   '<p>This lesson moves here in the next step. The page is here so you can see the navigation working.</p></section>')

    if prev_l:
        prev_html = f'<a class="btn btn-secondary" rel="prev" href="{root}{prev_l["url"]}"><span class="pn-label">Previous</span>{esc(prev_l["title"])}</a>'
    else:
        prev_html = '<p class="first-note">This is the first lesson</p>'
    if next_l:
        next_html = f'<a class="btn btn-track" rel="next" href="{root}{next_l["url"]}"><span class="pn-label">Next</span>{esc(next_l["title"])}</a>'
    else:
        ti = TRACKS.index(t)
        if ti + 1 < len(TRACKS):
            nt = TRACKS[ti + 1]
            next_html = f'<a class="btn btn-track" href="{root}tracks/{nt["id"]}/"><span class="pn-label">Next track</span>{nt["name"]}</a>'
        else:
            next_html = f'<a class="btn btn-track" href="{root}#roadmap"><span class="pn-label">All done</span>Back to the roadmap</a>'

    toc_html = ""
    if toc:
        def toc_attr(n):
            return "" if n is None else f' data-panel="{n}"' if isinstance(n, str) else f' data-layer="{n}"'
        items = "".join(f'<li{toc_attr(n)}><a href="#{a}">{x if l.get("imported") or l["key"] in PAPER_PLANS else esc(x)}</a></li>' for a, x, n in toc)
        toc_html = f'<nav class="page-toc" aria-label="On this page"><p class="eyebrow">On this page</p><ul>{items}</ul></nav>'
    related = ""
    if l.get("related"):
        kinds = {"paper": "Paper", "design": "System design"}
        items = "".join(
            f'<li><span class="mono-mini">{kinds.get(LESSONS[k]["type"], "Lesson")}</span><a href="{root}{LESSONS[k]["url"]}">{esc(LESSONS[k]["title"])}</a></li>'
            for k in l["related"])
        related = f'<aside class="related" aria-label="Related"><p class="eyebrow">Related</p><ul>{items}</ul></aside>'

    attrs = f'data-lesson="{l["key"]}"' if body or l.get("imported") or l["key"] in PLANS or l["key"] in PAPER_PLANS else ""
    html = head_html(f'{l["title"]} · {t["name"]} · AIML Rounds', l["lead"], root, t, "lesson", extra_head, path=l["url"])
    html += f"""<main id="main" class="page-wide lesson-grid" {attrs}>
<aside class="contents" aria-label="{t['name']} contents">
  <details class="contents-box" open><summary>{t['name']} contents</summary>{contents_html(l, root)}</details>
</aside>
<article class="lesson">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}">Home</a><span aria-hidden="true">/</span><a href="{root}tracks/{t['id']}/">{t['name']}</a><span aria-hidden="true">/</span><a href="{root}tracks/{t['id']}/#module-{l['module_n']}">{l['module']['name']}</a><span aria-hidden="true">/</span><b aria-current="page">{esc(l['title'])}</b></nav>
  <div class="lesson-meta">{meta}</div>
  <h1 class="h1-lesson">{esc(l['title'])}</h1>
  <p class="lead">{esc(l['lead'])}</p>
  {center}
  {quiz_cta(l, root)}
  <nav class="prev-next" aria-label="Previous and next lesson">{prev_html}{next_html}</nav>
</article>
<div class="rail">{toc_html}{related}</div>
</main>
"""
    write(f'{l["url"]}index.html', html + foot_html(root, "page-wide", scripts))


def search_index():
    rows = [{"track": l["track"]["id"], "trackName": l["track"]["name"], "n": l["track"]["n"], "title": l["title"],
             "module": l["module"]["name"], "type": TYPE_LABEL[l["type"]], "url": l["url"], "text": f'{l["lead"]} {l.get("q", "")}'} for l in ORDERED]
    roadmaps_page()
    about_page()
    roadmap_page()
    for tid in quizzes.READY:
        quiz_page(tid)
    mock_pages()
    jobs_page()
    privacy_page()
    site_files()
    write("assets/search-index.js", "window.SEARCH_INDEX=" + json.dumps(rows, ensure_ascii=False) + ";\n")


def roadmaps_page():
    """No roadmaps page any more (removed 10 Nov 2026). Only the RAG PDF stays, at the old address the
    Instagram comment-to-DM automation links to (/ai/roadmaps/rag-roadmap.pdf), so those DMs keep working."""
    (DIST / "ai/roadmaps").mkdir(parents=True, exist_ok=True)
    shutil.copy(ml_import.SRC.parent / "roadmaps/rag-roadmap.pdf", DIST / "ai/roadmaps/rag-roadmap.pdf")


def roadmap_page():
    """Role roadmaps: a topic graph per role, a side panel per topic. assets/roadmap.js draws it from roadmap-data.js."""
    root = "../"
    desc = "A map of topics for each AI role, in the order that makes the next one easy. Click a topic to see its lessons."
    html = head_html("Roadmaps by role · AIML Rounds", desc, root, page="roadmap", path="roadmap/")
    tabs = "".join(f'<button type="button" role="tab" id="tab-{r["id"]}" aria-controls="rmGraph" data-role="{r["id"]}">{r["name"]}</button>' for r in RM["roles"])
    fallback = "".join(f'<section><h2>{r["name"]}</h2><ol>' + "".join(f'<li>{esc(RM["topics"][t]["name"])}</li>' for row in r["rows"] for t in row) + "</ol></section>" for r in RM["roles"])
    html += f"""<main id="main"><section class="page-wide rm-page"><p class="eyebrow">ROADMAP</p><h1 class="h1-track">Roadmaps by role</h1><p class="lead">{desc}</p>
<div class="rm-tabs" role="tablist" aria-label="Role">{tabs}</div>
<div class="rm-layout">
<div class="panel rm-graph" id="rmGraph" role="tabpanel"><noscript>{fallback}</noscript></div>
<aside class="panel rm-summary" id="rmSummary" aria-live="polite"></aside>
</div>
</section></main>
<div class="rm-drawer-back" id="rmBack" hidden></div>
<aside class="rm-drawer" id="rmDrawer" role="dialog" aria-modal="true" aria-labelledby="rmDrawerTitle" hidden></aside>
"""
    write("roadmap/index.html", html + foot_html(root, scripts=f'<script src="{root}assets/roadmap-data.js?v={ASSET_V}"></script><script src="{root}assets/roadmap.js?v={ASSET_V}"></script>'))


def mock_pages():
    """Mock interviews: /mock/ hub, /mock/<role>/ rounds, /mock/<role>/<round>/ questions."""
    desc = "Practice interview rounds for AI and ML roles. Answer out loud, then compare with a model answer and what the interviewer listens for."
    cards = "".join(
        f'<a class="panel role-card" href="{m["id"]}/"><span class="eyebrow">{len(m["rounds"])} rounds</span><h3>{m["name"]}</h3><p>{esc(m["blurb"])}</p></a>'
        for m in mocks.MOCKS)
    soon = [r["name"] for r in RM["roles"] if r["id"] not in {m["id"] for m in mocks.MOCKS}]
    soon_html = f'<p class="note">Coming soon: {", ".join(soon)}.</p>' if soon else ""
    html = head_html("Mock interviews · AIML Rounds", desc, "../", page="mock", path="mock/")
    html += f"""<main id="main"><section class="page mock-page"><p class="eyebrow">MOCK INTERVIEWS</p><h1 class="h1-track">Mock interviews</h1><p class="lead">{desc}</p>
<div class="card-grid role-cards">{cards}</div>{soon_html}
<section class="panel block"><h2>How to use a mock</h2><ol class="mock-how"><li>Set the timer, or just note the time.</li><li>Read a question and answer it out loud, as you would to an interviewer.</li><li>Open the model answer and tick off what the interviewer listens for.</li><li>Revisit the linked lessons for anything you missed.</li></ol></section>
</section></main>
"""
    write("mock/index.html", html + foot_html("../"))
    for m in mocks.MOCKS:
        root = "../../"
        rounds = "".join(
            f'<a class="panel role-card" href="{r["id"]}/"><span class="eyebrow">Round {i} · {len(r["questions"])} questions · {r["minutes"]} min</span><h3>{r["name"]}</h3><p>{esc(r["intro"])}</p></a>'
            for i, r in enumerate(m["rounds"], 1))
        html = head_html(f'{m["name"]} mock interviews · AIML Rounds', m["blurb"], root, page="mock", path=f'mock/{m["id"]}/')
        html += f"""<main id="main"><section class="page mock-page"><nav class="crumbs" aria-label="Breadcrumb"><a href="{root}">Home</a><span aria-hidden="true">/</span><a href="{root}mock/">Mock interviews</a><span aria-hidden="true">/</span><b aria-current="page">{m['name']}</b></nav>
<p class="eyebrow">MOCK INTERVIEWS</p><h1 class="h1-track">{m['name']}</h1><p class="lead">{esc(m['blurb'])}</p>
<div class="card-grid role-cards">{rounds}</div>
<div class="btn-row"><a class="btn btn-secondary" href="{root}roadmap/#{m['id']}">See the {m['name']} roadmap</a></div>
</section></main>
"""
        write(f'mock/{m["id"]}/index.html', html + foot_html(root))
        for i, r in enumerate(m["rounds"], 1):
            root = "../../../"
            qs = ""
            for j, q in enumerate(r["questions"], 1):
                answer = "".join(f"<p>{esc(p)}</p>" for p in q["a"])
                listen = "".join(f"<li>{esc(x)}</li>" for x in q["listen"])
                links = ", ".join(f'<a href="{root}{LESSONS[k]["url"]}">{esc(LESSONS[k]["title"])}</a>' for k in q["lessons"])
                qs += (f'<li class="panel quiz-q mock-q" id="q{j}"><p class="quiz-num">Question {j} of {len(r["questions"])}</p><h2>{esc(q["q"])}</h2>'
                       f'<p class="note">Answer out loud first, then open the model answer.</p>'
                       f'<details class="quiz-ans"><summary>View model answer</summary><div class="mock-answer">{answer}</div>'
                       f'<h3 class="mock-sub">What the interviewer listens for</h3><ul class="mock-listen">{listen}</ul>'
                       f'<p class="quiz-lesson">Lessons: {links}</p></details></li>')
            nxt = m["rounds"][i] if i < len(m["rounds"]) else None
            nxt_html = f'<a class="btn btn-primary" href="../{nxt["id"]}/">Next round: {nxt["name"]}</a>' if nxt else ""
            html = head_html(f'{r["name"]} · {m["name"]} mock · AIML Rounds', r["intro"], root, page="mock", path=f'mock/{m["id"]}/{r["id"]}/')
            html += f"""<main id="main"><section class="page quiz-page mock-page"><nav class="crumbs" aria-label="Breadcrumb"><a href="{root}">Home</a><span aria-hidden="true">/</span><a href="{root}mock/">Mock interviews</a><span aria-hidden="true">/</span><a href="../">{m['name']}</a><span aria-hidden="true">/</span><b aria-current="page">{r['name']}</b></nav>
<p class="eyebrow">{m['name'].upper()} · ROUND {i} OF {len(m['rounds'])}</p><h1 class="h1-track">{r['name']}</h1><p class="lead">{esc(r['intro'])}</p>
<div class="panel mock-timer" data-minutes="{r['minutes']}"><span>{len(r['questions'])} questions · suggested time <b>{r['minutes']} min</b></span><span class="mock-clock" aria-live="off" hidden></span><button type="button" class="btn btn-secondary" data-timer>Start timer</button></div>
<ol class="quiz-list">{qs}</ol>
<div class="btn-row">{nxt_html}<a class="btn btn-secondary" href="../">All {m['name']} rounds</a></div>
</section></main>
"""
            write(f'mock/{m["id"]}/{r["id"]}/index.html', html + foot_html(root))


def jobs_page():
    """AI/ML job postings in India from the last 7 days. jobs/fetch_jobs.py writes jobs.json; site.js draws the list."""
    root = "../"
    (DIST / "jobs").mkdir(parents=True, exist_ok=True)
    if (HERE / "jobs/jobs.json").exists():
        shutil.copy(HERE / "jobs/jobs.json", DIST / "jobs/jobs.json")
    desc = "AI and ML roles in India, posted in the 7 days before each update, from companies' own careers pages. Updated weekly, every Monday."
    html = head_html("AI/ML Job postings this week · AIML Rounds", desc, root, page="jobs", path="jobs/")
    html += f"""<main id="main"><section class="page jobs-page"><p class="eyebrow">JOBS</p><h1 class="h1-track">AI/ML Job postings this week</h1><p class="lead">{desc}</p>
<div class="jobs-tools"><label class="sr" for="jobSearch">Search jobs</label><input id="jobSearch" class="jobs-search" type="search" placeholder="Search by title, company or city" autocomplete="off"><p class="note" id="jobsMeta" aria-live="polite">Loading jobs…</p></div>
<ul class="panel jobs-list" id="jobsList" tabindex="0" aria-label="Job postings, scroll for more"></ul>
<noscript><p class="note">Turn on JavaScript to see the job list.</p></noscript>
<p class="note jobs-note">Every link goes to the company's own careers page. We collect these automatically and don't vet them, so check the details there before you apply.</p>
</section></main>
"""
    write("jobs/index.html", html + foot_html(root))


def about_page():
    """What the site is for, in plain words, with common questions and how to get in touch."""
    root = "../"
    desc = "A free site for learning AI and machine learning until you can explain it, with interactive lessons and interview practice."
    faq = [
        ("Is it free?", "Yes. Every lesson is free to read, and you don't need an account."),
        ("Who is it for?", "Anyone preparing for AI or ML interviews, and engineers who want to understand these ideas properly. You can start from zero, or jump straight to the part you need."),
        ("Where should I start?", f'If you\'re new, begin with <a href="{root}tracks/fundamentals/">Fundamentals</a>. If you have an interview soon, go to the interview questions and fill the gaps they show. If you already build systems, try <a href="{root}tracks/system-design/">System Design</a>.'),
        ("How much maths do I need?", f'Less than you might expect. <a href="{root}tracks/fundamentals/">Fundamentals</a> teaches the maths as it\'s used in ML, and each lesson lists what to read first. Nothing is locked, so you can skip what you know.'),
        ("Will I learn to code models here?", "Lessons focus on how ideas work and how to explain them, so they have very little code. They pair well with a hands-on course or your own projects."),
        ("Are the numbers from real companies?", "Where a lesson uses a real system, it links to its sources. Numbers in labs and estimates are examples for practice, unless the lesson says otherwise."),
        ("Does it save my progress?", f'Yes, in your own browser. It isn\'t sent anywhere, so it won\'t follow you to another device. See the <a href="{root}privacy/">privacy note</a>.'),
        ("I found a mistake. What should I do?", f'Please <a href="mailto:{EMAIL}">email me</a> with the lesson\'s name. Fixes go in as soon as they can.'),
    ]
    items = "".join(f'<details class="faq-item"><summary>{q}</summary><p>{a}</p></details>' for q, a in faq)
    how = "".join(f"<li>{x}</li>" for x in [
        "<b>It starts with a question.</b> Each lesson opens with what an interviewer would actually ask.",
        "<b>You build the idea.</b> One analogy, one picture, then a lab you can try to break.",
        "<b>You say it out loud.</b> Lessons end with you explaining the answer and taking follow-up questions, because reading isn't the same as knowing."])
    html = head_html("About · AIML Rounds", desc, root, path="about/")
    html += f"""<main id="main"><div class="page about">
<section class="hero-roadmaps"><p class="eyebrow">ABOUT</p><h1 class="h1-home">Learn AI until you can explain it.</h1><p class="lead">{desc}</p></section>
<section class="panel block" id="why"><h2>Why this site exists</h2><p>You can read about an idea, recognise it and still get stuck when someone asks you to explain it. AIML Rounds is built to close that gap. Its {len(ORDERED)} lessons cover maths, machine learning, deep learning, LLMs, AI engineering and system design.</p></section>
<section class="panel block" id="how"><h2>How lessons work</h2><ul class="about-list">{how}</ul></section>
<section class="panel block" id="faq"><h2>Common questions</h2><div class="faq">{items}</div></section>
<section class="panel block" id="contact"><h2>Get in touch</h2><p>Questions, corrections and ideas are all welcome at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>{social_html("about-social")}</section>
</div></main>
"""
    write("about/index.html", html + foot_html(root))


def privacy_page():
    """Plain facts about what the site stores. Update this if analytics or a sign-up is added."""
    root = "../"
    desc = "What this site stores, and which outside services your browser connects to."
    html = head_html("Privacy · AIML Rounds", desc, root, path="privacy/")
    html += f"""<main id="main"><div class="page about">
<section class="hero-roadmaps"><p class="eyebrow">PRIVACY</p><h1 class="h1-home">Privacy, in plain words.</h1><p class="lead">{desc}</p></section>
<section class="panel block"><h2>What the site itself keeps</h2><ul class="about-list"><li>There are no accounts, sign-ups, ads or analytics.</li><li>Your lesson progress and which sections you've opened are saved in your own browser, using local storage. They aren't sent to the site. Clearing your browser data removes them.</li></ul></section>
<section class="panel block"><h2>Outside services</h2><p>Like most websites, pages load through other services, and these can see basic request details such as your IP address:</p><ul class="about-list"><li><b>GitHub Pages</b> hosts the site.</li><li><b>Google Fonts</b> provides the fonts.</li><li><b>cdnjs</b>, from Cloudflare, provides the maths display on lesson pages.</li><li><b>Links to other sites</b> follow those sites' own policies once you click them.</li></ul></section>
<section class="panel block"><h2>Questions</h2><p>Email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></section>
</div></main>
"""
    write("privacy/index.html", html + foot_html(root))


def site_files():
    """What GitHub Pages needs at the site root: no Jekyll, a 404 page, the custom domain, a sitemap and robots."""
    write(".nojekyll", "")
    desc = "This page isn't here. Lessons sit under the four tracks."
    html = head_html("Page not found · AIML Rounds", desc, "/")
    html += f"""<main id="main"><section class="page hero-roadmaps"><p class="eyebrow">404</p><h1 class="h1-home">This page isn't here.</h1><p class="lead">{desc}</p>
<div class="btn-row"><a class="btn btn-primary" href="/">Go to the home page</a><a class="btn btn-secondary" href="/#tracks">See the tracks</a></div></section></main>
"""
    write("404.html", html + foot_html("/"))
    write("CNAME", "aimlrounds.com\n")
    base = BASE
    urls = ["", "about/", "roadmap/", "jobs/", "mock/"] + [f'mock/{m["id"]}/' for m in mocks.MOCKS] + [f'mock/{m["id"]}/{r["id"]}/' for m in mocks.MOCKS for r in m["rounds"]] + [f"quiz/{s}/" for s in QUIZ_SLUG.values()] + ["privacy/"] + [f'tracks/{t["id"]}/' for t in TRACKS] + [l["url"] for l in ORDERED]
    rows = "".join(f"<url><loc>{base}{u}</loc></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {base}sitemap.xml\n")


# Old lesson addresses that moved, mapped to their new pages.
REDIRECTS = {"tracks/ai-engineering/agent-scenarios-set-1/": "/tracks/ai-engineering/agent-scenarios-context-and-memory/"}


def redirects():
    for old, new in REDIRECTS.items():
        write(old + "index.html", f'<!doctype html><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="{new}"><meta http-equiv="refresh" content="0; url={new}"><p>This page moved to <a href="{new}">{new}</a>.</p>\n')


def write(rel, text):
    p = DIST / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    shutil.rmtree(DIST, ignore_errors=True)
    shutil.copytree(HERE / "assets", DIST / "assets")
    write("assets/roadmap-data.js", "window.ROADMAP=" + json.dumps(RM, ensure_ascii=False, separators=(",", ":")) + ";\n")
    home()
    for idx, t in enumerate(TRACKS):
        track_page(t, idx)
    for l in ORDERED:
        lesson_page(l)
    search_index()
    redirects()
    print(f"Built {1 + len(TRACKS) + len(ORDERED)} pages into {DIST}")
