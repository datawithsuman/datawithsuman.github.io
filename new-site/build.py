#!/usr/bin/env python3
"""Builds the static site into dist/. Run: python3 build.py"""
import json
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
                        + moved_modules("Classical ML", "machine-learning", classical_ml)
                        + moved_modules("Deep Learning", "deep-learning", deep_learning)
                        + moved_modules("NLP Fundamentals", "nlp-fundamentals", nlp_fundamentals)
                        + moved_modules("LLMs", "llms", llms)
                        + TRACKS[0]["modules"])

TRACKS[1]["modules"] = [m for part, track_dir, source in ai_engineering.PARTS for m in moved_modules(part, track_dir, source) if m["lessons"]]

TRACKS[2]["modules"] = moved_modules("", "system-design/ml-system-design", ai_engineering.DESIGNS) + TRACKS[2]["modules"]

LESSONS, ORDERED = {}, []
for t in TRACKS:
    for mi, m in enumerate(t["modules"], 1):
        for l in m["lessons"]:
            l.update(track=t, module=m, module_n=mi, key=f"{t['id']}/{l['slug']}", url=f"tracks/{t['id']}/{l['slug']}/")
            LESSONS[l["key"]] = l
            ORDERED.append(l)


def track_lessons(t):
    return [l for l in ORDERED if l["track"] is t]


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


def head_html(title, desc, root, active=None, page="home", extra_head=""):
    if page == "home":
        nav = ('<nav class="links" aria-label="Main"><a href="#tracks">Tracks</a><a href="#how">How lessons work</a>'
               '<a href="#roadmap">Roadmap</a></nav>')
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
<script>document.documentElement.classList.add('has-js')</script>
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{root}assets/site.css">
{extra_head}
</head>
<body{f' class="t-{active["id"]}"' if active else ''} data-root="{root}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="{width} head-inner">
<a class="brand" href="{root}">{LOGO}<span>datawithsuman</span></a>
{nav}
<button type="button" class="search-btn" id="searchOpen" aria-haspopup="dialog">{SEARCH_ICON}<span class="search-label">Search lessons</span><kbd>Ctrl K</kbd></button>
</div></header>
"""


def foot_html(root, width="page", scripts=""):
    return f"""{scripts}<footer class="site-foot"><div class="{width} foot-inner"><span>@datawithsuman</span><span>AI &amp; ML, explained simply.</span><a href="{root}roadmaps/">Free roadmaps</a></div></footer>
<dialog class="search" id="searchDialog" aria-label="Search lessons">
<div class="search-top"><label class="sr" for="searchInput">Search lessons</label><input id="searchInput" type="search" placeholder="Search lessons" autocomplete="off"><button type="button" class="btn-close" id="searchClose">Close</button></div>
<div id="searchResults" class="search-results" aria-live="polite"></div>
</dialog>
<script src="{root}assets/search-index.js"></script>
<script src="{root}assets/site.js"></script>
</body>
</html>
"""


def home():
    root = ""
    first = LESSONS["fundamentals/vectors-and-cosine-similarity"]
    pills = "".join(f'<span class="tag">{p}</span>' for p in ["Intuition", "Play", "Maths", "Say it"])
    starts = [
        ("Interview in 2 weeks", "Interview sprint", "Go straight to the interview rounds, then fill the gaps they show.", "tracks/ai-engineering/llm-inference-practice/", " dark"),
        ("Starting from zero", "Fundamentals path", "Begin with the maths, then regression, and build up to neural nets one idea at a time.", "tracks/fundamentals/", ""),
        ("I build production systems", "System design path", "Start with how real AI systems are designed, from requirements to rollout.", "tracks/system-design/", ""),
    ]
    start_html = "".join(f'<a class="panel start{d}" href="{u}"><span class="eyebrow">{e}</span><h3>{t}</h3><p>{p}</p></a>' for e, t, p, u, d in starts)
    tracks = ""
    for t in TRACKS:
        topics = "".join(f"<li>{esc(x)}</li>" for x in t["topics"])
        tracks += (f'<a class="panel track-card t-{t["id"]}" href="tracks/{t["id"]}/"><span class="track-top"><span class="chip track-num">{t["n"]}</span>'
                   f'<span class="status-note">{t["status"]}</span></span><h3>{t["name"]}</h3><p>{t["desc"]}</p><ul>{topics}</ul></a>')
    tiles = [
        ("1", "The situation", "The question an interviewer would actually ask.", ""),
        ("2", "The idea", "One analogy, one picture.", ""),
        ("3", "Play", "Change an input, try to break it, then say why.", ""),
        ("4", "How it works", "ML: the formula. System design: the diagram. Papers: the method.", ""),
        ("5", "In practice", "The steps and when to use it. System design gets capacity maths.", ""),
        ("6", "The answer that sounds right", "The tempting wrong answer, and why it fails.", ""),
        ("7", "Say it", "Say it out loud, tick what you covered, take the follow-ups.", " dark"),
    ]
    tile_html = "".join(f'<li class="panel tile{d}"><span class="eyebrow">{n}</span><h3>{h}</h3><p>{p}</p></li>' for n, h, p, d in tiles)
    path = [("Maths for ML", "fundamentals/vectors-and-cosine-similarity"), ("Regression", "fundamentals/linear-regression"), ("Neural nets", "fundamentals/perceptron-to-mlp"),
            ("Attention", "fundamentals/self-attention"), ("Embeddings and RAG", "fundamentals/embeddings"),
            ("Serving LLMs", "ai-engineering/prefill-vs-decode"), ("Agent design", "system-design/design-refund-agent")]
    road = "".join(f'<li><a class="chip chip-road t-{LESSONS[k]["track"]["id"]}" href="{LESSONS[k]["url"]}">{n}</a></li>' for n, k in path)
    html = head_html("datawithsuman: learn AI until you can explain it",
                     "Short, visual lessons on machine learning, LLMs and system design. Concept lessons end with you saying the answer out loud. Paper lessons end with what changed.", root)
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
<section class="page section"><h2>Where are you starting from?</h2><div class="card-grid">{start_html}</div></section>
<section class="page section" id="tracks"><h2>Four tracks, one colour each</h2>
<p class="section-lead">The colour follows you into every lesson, so you always know which track you are in.</p>
<div class="card-grid">{tracks}</div></section>
<section class="page section" id="how"><h2>Every lesson starts and ends the same way.</h2>
<p class="section-lead">The labels change with the track, and a lesson only shows what it really has. Each tab shows one part, so open only what you need. Paper lessons have their own path: gist, method, results and why it matters.</p>
<ol class="grid-tiles">{tile_html}</ol></section>
<section class="page section" id="roadmap"><div class="panel road-card"><h2>Not sure what's next? Follow the path.</h2>
<ol class="road">{road}</ol>
<p class="section-lead">Each step lists what you need before it. Nothing is locked, but the order is the one that makes the next idea easy.</p></div></section>
</main>
"""
    write("index.html", html + foot_html(root))


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
            for l in m["lessons"])
        heading = "h3" if m.get("part") else "h2"
        mods += (f'<section class="panel module" id="module-{mi}"><header><p class="eyebrow">Module {mi}</p><{heading}>{m["name"]}</{heading}><p>{m["desc"]}</p></header>'
                 f'<ol class="rows">{rows}</ol></section>')
    nxt = TRACKS[idx + 1] if idx + 1 < len(TRACKS) else None
    if nxt:
        foot = f'<section class="panel next-track t-{nxt["id"]}"><div><p class="eyebrow">Next track</p><h2>Next track: {nxt["name"]}</h2><p>{nxt["desc"]}</p></div><a class="btn btn-secondary" href="../{nxt["id"]}/">Open {nxt["name"]}</a></section>'
    else:
        foot = f'<section class="panel next-track"><div><p class="eyebrow">Last track</p><h2>That is all four tracks.</h2><p>Go back to the roadmap to see what to revisit.</p></div><a class="btn btn-secondary" href="{root}#roadmap">See the roadmap</a></section>'
    html = head_html(f'{t["name"]} · datawithsuman', t["desc"], root, t, "track")
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
    html = head_html(f'{l["title"]} · {t["name"]} · datawithsuman', l["lead"], root, t, "lesson", extra_head)
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
    site_files()
    write("assets/search-index.js", "window.SEARCH_INDEX=" + json.dumps(rows, ensure_ascii=False) + ";\n")


def roadmaps_page():
    """Free study roadmaps. One PDF per topic, kept where the current site keeps them."""
    root = "../"
    (DIST / "roadmaps").mkdir(parents=True, exist_ok=True)
    shutil.copy(ml_import.SRC.parent / "roadmaps/rag-roadmap.pdf", DIST / "roadmaps/rag-roadmap.pdf")
    desc = "One PDF per topic: the core concepts, the interview questions and a study plan. Free to download."
    html = head_html("Free study roadmaps · datawithsuman", desc, root)
    html += f"""<main id="main"><section class="page hero-roadmaps"><p class="eyebrow">ROADMAPS</p><h1 class="h1-home">Free study roadmaps.</h1><p class="lead">{desc}</p>
<div class="card-grid"><a class="panel start" href="rag-roadmap.pdf"><span class="eyebrow">PDF</span><h3>The Complete RAG Roadmap</h3><p>30 core concepts, 24 interview questions, common mistakes, a debug-a-wrong-answer cheat sheet and a 6-week study plan.</p></a></div>
</section></main>
"""
    write("roadmaps/index.html", html + foot_html(root))


def site_files():
    """What GitHub Pages needs at the site root: no Jekyll, a 404 page, a sitemap and robots."""
    write(".nojekyll", "")
    desc = "This page isn't here. Lessons sit under the four tracks."
    html = head_html("Page not found · datawithsuman", desc, "/")
    html += f"""<main id="main"><section class="page hero-roadmaps"><p class="eyebrow">404</p><h1 class="h1-home">This page isn't here.</h1><p class="lead">{desc}</p>
<div class="btn-row"><a class="btn btn-primary" href="/">Go to the home page</a><a class="btn btn-secondary" href="/#tracks">See the tracks</a></div></section></main>
"""
    write("404.html", html + foot_html("/"))
    base = "https://datawithsuman.github.io/"
    urls = ["", "roadmaps/"] + [f'tracks/{t["id"]}/' for t in TRACKS] + [l["url"] for l in ORDERED]
    rows = "".join(f"<url><loc>{base}{u}</loc></url>" for u in urls)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {base}sitemap.xml\n")


def write(rel, text):
    p = DIST / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    shutil.rmtree(DIST, ignore_errors=True)
    shutil.copytree(HERE / "assets", DIST / "assets")
    home()
    for idx, t in enumerate(TRACKS):
        track_page(t, idx)
    for l in ORDERED:
        lesson_page(l)
    search_index()
    print(f"Built {1 + len(TRACKS) + len(ORDERED)} pages into {DIST}")
