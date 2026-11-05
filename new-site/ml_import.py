"""Reads the live Fundamentals lessons and splits them into the new lesson format.

Lesson text, labs and scripts are kept as they are. Only the order of the outer
blocks changes: each chapter is given a depth, and the interview chapter moves
into the interview block. The source pages stay the single source of truth.
"""
import hashlib
import re
from pathlib import Path

SRC = Path(__file__).parent.parent / "ai/interview-prep"
FUNDAMENTALS = SRC / "fundamentals"
MOVED = "machine-learning|maths-for-ml|deep-learning|nlp-fundamentals|llms"
AI_ENGINEERING = "llm-inference|prompt-engineering|rag|agentic-ai|mlops|llmops"
LIVE = "https://datawithsuman.github.io/ai/interview-prep/"
REFERENCE = ("evidence", "caveats", "key terms")

# Colours and type for the new site. Lesson accents keep their light-theme values.
OVERRIDES = """
.lx{--bg:#F5F6F8;--bg2:#EDEFF3;--card:#FFFFFF;--line:#DDE1E8;--ink:#11141B;--dim:#4B5363;--faint:#6A7281;--r:10px;color-scheme:light;
  --mono:"JetBrains Mono",ui-monospace,monospace;background:transparent;color:var(--ink);font:400 16px/1.6 "Instrument Sans",system-ui,sans-serif;min-width:0}
.lx ul,.lx ol{list-style:revert;margin:revert;padding:revert}
.lx p{text-wrap:pretty}
.lx h2,.lx h3,.lx h4{font-family:"Bricolage Grotesque",system-ui,sans-serif;letter-spacing:-.015em;text-wrap:balance;color:var(--ink)}
.lx h2{font-size:clamp(22px,3vw,26px);font-weight:700;line-height:1.15}
.lx h3{font-size:19px;font-weight:600}
.lx button{font:inherit;color:inherit}
.lx input[type=range]{min-height:32px}
.lx section.ch{margin-top:16px;padding:clamp(18px,2.6vw,26px);background:var(--card);border:1px solid var(--line);border-radius:14px}
.lx .chap{font:500 12px/1.4 var(--mono);text-transform:uppercase;letter-spacing:.04em;color:var(--dim)}
.lx .chap::before{content:none}
.lx .card{background:var(--bg);box-shadow:none}
.lx .stage,.lx .stage.plot{background:var(--card)}
.lx .preamble{margin-top:16px}
.lx .preamble p{margin:0}
.lx .tip{background:#fff;color:var(--ink)}
.lx .tool{margin-top:10px;font-size:15px;color:var(--dim)}
.lx .more{margin-top:16px;background:var(--card);border:1px solid var(--line);border-radius:14px}
.lx .more>summary{display:flex;align-items:center;min-height:56px;padding:6px 22px;font:600 18px/1.2 "Bricolage Grotesque",system-ui,sans-serif;letter-spacing:-.01em;cursor:pointer}
.lx .more section.ch{margin:0;border:0;border-top:1px solid var(--line);border-radius:0;background:transparent}
.lx .built-from{padding:0 22px 16px;margin:0}
.lx{--warn:#A5491A;--a:#0A7267;--b:#8F5500;--ok:#17703F;--st:#5E41C2;--bad:#B02C2C;--info:#2558B4;--faint:#5F6776}
.lx .lab label{flex-wrap:wrap;min-width:0}
.lx table[data-o="list"] tr[style*="opacity"]{opacity:1!important;background:var(--bg2)}
.lx .lab label input[type=range]{flex:1 1 120px;min-width:120px;max-width:100%}
.lx .ctl button,.lx .seg button,.lx .lab>button,.lx .lab .btn{min-height:44px}
.lx .ctl .dots{gap:0}
.lx .ctl .dots button{box-sizing:border-box;width:24px;height:24px;min-height:24px;padding:7px;border:0;border-radius:50%;background-clip:content-box}
.lx .ctl{flex-wrap:wrap}
@media (max-width:560px){.lx .brace span{display:none}}
@media (max-width:560px){.lx section.ch{padding:16px 12px}.lx .card{padding:14px 12px}.lx .more>summary{padding-inline:12px}.lx .built-from{padding-inline:12px}}
"""


def _rules(css):
    """Yields (prelude, body) for each top-level rule, keeping nested blocks whole."""
    i, n = 0, len(css)
    while i < n:
        open_at = css.find("{", i)
        if open_at < 0:
            return
        depth, j = 1, open_at + 1
        while j < n and depth:
            depth += {"{": 1, "}": -1}.get(css[j], 0)
            j += 1
        yield css[i:open_at].strip(), css[open_at + 1:j - 1]
        i = j


def _split_selectors(prelude):
    parts, depth, cur = [], 0, ""
    for ch in prelude:
        depth += {"(": 1, "[": 1, ")": -1, "]": -1}.get(ch, 0)
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def _scope_selector(sel):
    if '[data-theme="dark"]' in sel and ":not(" not in sel:
        return None
    if "themeBtn" in sel or "sitebar" in sel:
        return None
    new = re.sub(r':root(\[data-theme="light"\]|:not\(\[data-theme="dark"\]\))?', ".lx", sel)
    new = re.sub(r"\b(html|body)\b(?![\w-])", ".lx", new)
    new = re.sub(r"(\.lx\s+)+\.lx\b", ".lx", new)
    return new if new.startswith(".lx") else f".lx {new}"


def scope_css(css):
    """Prefixes lesson CSS with .lx and fixes it to the light theme."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = []
    for prelude, body in _rules(css):
        if prelude.startswith("@"):
            if "prefers-color-scheme" in prelude:
                continue
            if prelude.startswith(("@media", "@supports")):
                out.append(f"{prelude}{{{scope_css(body)}}}")
            else:
                out.append(f"{prelude}{{{body}}}")
            continue
        selectors = [s for s in map(_scope_selector, _split_selectors(prelude)) if s]
        if selectors:
            out.append(f"{','.join(selectors)}{{{body}}}")
    return "\n".join(out).replace("Inter,", '"Instrument Sans",').replace(" Inter", ' "Instrument Sans"')


def _new_home(path):
    """Where a live page now lives, as (track, slug, rest), or None if it hasn't moved."""
    m = re.match(rf"fundamentals/(?:{MOVED})/([\w-]+)/?(.*)", path)
    if m:
        return "fundamentals", m.group(1), m.group(2)
    m = re.match(rf"system-design/(?:{AI_ENGINEERING})/([\w-]+)/?(.*)", path)
    if m:
        return "ai-engineering", m.group(1), m.group(2)
    m = re.match(r"system-design/ml-system-design/([\w-]+)/?(.*)", path)
    if m:
        return "system-design", m.group(1), m.group(2)
    return None


def _fix_links(html, track="fundamentals", live_dir="fundamentals/machine-learning"):
    """Moved lessons sit under tracks/<track>/<slug>/. Everything else still lives on the current site."""
    html = html.replace("<th></th>", "<td></td>")
    parent = live_dir.rsplit("/", 1)[0]

    def fix(m):
        href = m.group(1)
        if href.startswith(LIVE):
            path = href[len(LIVE):]
        elif href.startswith("../../../"):
            path = href[9:]
        elif href.startswith("../../"):
            path = f"{parent}/{href[6:]}"
        elif href.startswith("../"):
            path = f"{live_dir}/{href[3:]}"
        else:
            return m.group(0)
        home = _new_home(path)
        if not home:
            return f'href="{LIVE}{path}"'
        return f'href="../{home[1]}/{home[2]}"' if home[0] == track else f'href="../../{home[0]}/{home[1]}/{home[2]}"'
    return re.sub(r'href="([^"]*)"', fix, html)


def _layer_for(section_id, toc, body):
    label = toc.lower()
    if section_id == "src" or any(word in label for word in REFERENCE):
        return "reference"
    if "<pre" in body:
        return "code"
    has_formula = 'class="eq' in body or 'class="reader' in body or "$$" in body
    is_core = section_id == "c1" or "core idea" in label
    return "maths" if has_formula and not is_core else "intuition"


def _read_questions(html, fix=_fix_links):
    """Splits a practice page's question list into label, question and worked answer."""
    out = []
    for m in re.finditer(r'<div class="qcard" id="(q\d+)"><div class="qhead">(.*?)</div>\s*<p class="qtext">(.*?)</p>\s*<details class="qa"><summary>[^<]*</summary>(.*?)</details></div>', html, re.S):
        label = " · ".join(re.findall(r">([^<]+)</span>", m.group(2)))
        out.append({"id": m.group(1), "label": label, "q": fix(m.group(3)), "answer": fix(m.group(4))})
    return out


def read_lesson(track_dir, slug):
    live_dir = track_dir if "/" in track_dir else f"fundamentals/{track_dir}"
    track = "system-design" if live_dir.endswith("ml-system-design") else "ai-engineering" if live_dir.startswith("system-design/") else "fundamentals"
    fix = lambda html: _fix_links(html, track, live_dir)  # noqa: E731
    text = (SRC / live_dir / slug / "index.html").read_text(encoding="utf-8")
    if '<section class="ch"' not in text:
        return _read_scenario(live_dir, slug, text, fix)
    head, body = text.split("</head>", 1)
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", head, re.S))

    head_scripts = re.findall(r"<script[^>]*>.*?</script>", head, re.S)
    scripts = [s.replace("<th></th>", "<td></td>") for s in re.findall(r"<script[^>]*>.*?</script>", body, re.S) if "themeBtn" not in s]

    header = re.search(r'<header class="top">(.*?)</header>', body, re.S).group(1)
    tldr = re.search(r'<div class="tldr">(.*?)</div>\s*(?:<div class="legend"|$)', header, re.S)
    idea = re.sub(r"^\s*<b>(?:In one breath|How to use):</b>\s*", "", tldr.group(1)).replace("<br>", "")
    # The label is gone, so the sentence needs its capital. Names like k-means and t-SNE keep theirs.
    idea = re.sub(r"^((?:<[^>]+>)*)([a-z])(?!-)", lambda m: m.group(1) + m.group(2).upper(), idea)
    legend = re.search(r'<div class="legend">.*?</div>', header, re.S)
    built_from = re.search(r'<div class="meta">(.*?)</div>', header, re.S).group(1)

    rest = body[body.index("</header>") + len("</header>"):]
    pattern = re.compile(r'<section class="ch"[^>]*?id="([^"]+)"[^>]*?data-toc="([^"]*)"[^>]*>.*?</section>', re.S)
    chapters, cursor, preamble = [], 0, ""
    for m in pattern.finditer(rest):
        gap = re.sub(r"<!--.*?-->", "", rest[cursor:m.start()], flags=re.S).strip()
        if gap and not chapters:
            preamble = gap
        chapters.append({"id": m.group(1), "toc": m.group(2), "html": m.group(0), "layer": _layer_for(m.group(1), m.group(2), m.group(0))})
        cursor = m.end()

    questions = []
    answer = ""
    practice = next((c for c in chapters if c["id"] == "qs"), None)
    if practice:
        chapters.remove(practice)
        questions = _read_questions(practice["html"], fix)
        for c in chapters:
            c["layer"] = "reference"
    else:
        interview = next(c for c in chapters if c["id"] == "iv")
        chapters.remove(interview)
        answer = re.sub(r'^\s*<div class="chap">.*?</div>\s*<h2>.*?</h2>', "", re.sub(r"</?section[^>]*>", "", interview["html"]), flags=re.S)

    return {
        "css": css,
        "head_scripts": head_scripts,
        "scripts": scripts,
        "idea": fix(idea),
        "legend": legend.group(0) if legend else "",
        "built_from": fix(built_from),
        "preamble": fix(preamble),
        "chapters": [{**c, "html": fix(c["html"])} for c in chapters],
        "answer": fix(answer),
        "questions": questions,
    }


# The two older scenario pages have no spoken answer, so these are written from each page's own content.
SPOKEN = {
    "rag-wrong-answer": "I wouldn't touch the prompt or the model first. I'd look at the chunks retrieved for that exact question, because one check splits the problem in two. If the right chunk never came back, it's the retrieval side: chunking, metadata, top-k and reranking. If it came back and the answer is still wrong, it's the generation side: the step that packs chunks into the prompt, or the model not extracting the answer. I'd fix the stage that lost the answer, re-test the same question, and keep a small set of real questions with known answers, so it stays fixed.",
    "rag-at-scale": "These are two different problems, so I'd split them first: time each stage, and check whether the right chunk is still retrieved. Slow usually means exact search, where the work grows with the pile, so I'd move to an approximate index like HNSW or IVF and tune its search knob until recall@10 is good enough on my test set. Wrong usually means look-alikes burying the right chunk: old versions, drafts and other regions. So I'd filter by metadata like team, date and version, retrieve wide, rerank with a cross-encoder and send only the best few chunks. And I'd remove duplicates and old versions at ingest.",
}

# The older pages use the dark Reels kit. Same rules, with its colours mapped to the light theme.
SCENARIO_COLOURS = """
.lx{--surface:#FFFFFF;--surface-2:#EDEFF3;--ink-2:#4B5363;--muted:#4B5363;--blue:#0057B8;--yellow:#8A5A00;--red:#B3261E;--green:#1B6B3A;
  --blue-soft:rgba(0,87,184,.1);--yellow-soft:rgba(138,90,0,.1);--red-soft:rgba(179,38,30,.1);--green-soft:rgba(27,107,58,.1);--shadow:none;--serif:"Instrument Sans",system-ui,sans-serif}
.lx .chunk.out{opacity:1;border-style:dashed;background:transparent;color:var(--muted)}
.lx .quiz-why{font-size:17px}
.lx #tip:empty{display:none}
"""

# The quiz behaviour from the kit's site.js.
SCENARIO_QUIZ = """<script>document.querySelectorAll('.lx .quiz').forEach((quiz) => { const why = quiz.parentElement.querySelector('.quiz-why');
  quiz.querySelectorAll('.opt').forEach((b) => b.addEventListener('click', () => { quiz.querySelectorAll('.opt').forEach((o) => o.classList.remove('right', 'wrong'));
    b.classList.add(b.dataset.ok === '1' ? 'right' : 'wrong'); if (b.dataset.ok !== '1') quiz.querySelector('.opt[data-ok="1"]')?.classList.add('right');
    if (why) why.textContent = b.dataset.why || ''; })); });</script>"""


def _read_scenario(live_dir, slug, text, fix):
    """Reads an older scenario page. Its sections become chapters, and its text and labs stay as they are."""
    folder = SRC / live_dir / slug
    head, body = text.split("</head>", 1)
    kit = re.sub(r"@font-face\s*\{.*?\}", "", (SRC / "kit/site.css").read_text(encoding="utf-8"), flags=re.S)
    kit = re.sub(r"(?<![\w.#-])section\s*\{[^}]*\}", "", kit)  # The kit's page spacing would hit the lesson's own panels.
    css = kit + "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", head, re.S)) + SCENARIO_COLOURS
    scripts = [f"<script>{(folder / name).read_text(encoding='utf-8')}</script>" for name in ("lesson.js", "main.js")] + [SCENARIO_QUIZ]

    hero = re.search(r'<section class="hero wrap">(.*?)</section>', body, re.S).group(1)
    lead = re.search(r'<p class="lead">(.*?)</p>', hero, re.S).group(1)
    chapters = []
    recap = re.search(r'<div class="card recap">.*?</div>', body, re.S).group(0)
    followups = ""
    for m in re.finditer(r'<section class="wrap" id="([\w-]+)">(.*?)</section>', body, re.S):
        section_id, html = m.groups()
        html = re.sub(r'<span class="step">\d+</span>\s*', "", html)
        title = re.sub(r"<[^>]+>", "", re.search(r"<h2>(.*?)</h2>", html, re.S).group(1)).strip()
        html = re.sub(r"<h2>.*?</h2>", f"<h2>{title}</h2>", html, count=1, flags=re.S)
        if section_id == "followups":
            followups = re.sub(r'<details class="card"><summary><span>(.*?)</span></summary>', r'<details class="qa"><summary>\1</summary>', html[html.index('<div class="qa">') + 16:html.rindex("</div>")])
            continue
        if section_id == "mistakes":
            html += recap
        chapters.append({"id": section_id, "toc": title, "layer": "intuition", "html": f'<section class="ch" id="{section_id}" data-toc="{title}">{html}</section>'})
    chapters.append({"id": "sources", "toc": "Sources", "layer": "reference",
                     "html": '<section class="ch" id="sources" data-toc="Sources"><p class="note" id="qual">–</p><p class="src" id="src">–</p></section>'})
    answer = f'<h3>The 30-second answer</h3><p class="say30">{SPOKEN[slug]}</p><h3>Likely follow-ups</h3>{followups}'
    return {"css": css, "head_scripts": [], "scripts": scripts, "idea": lead, "legend": "", "built_from": "", "preamble": "",
            "chapters": [{**c, "html": fix(c["html"])} for c in chapters], "answer": fix(answer), "questions": []}


def lesson_meta():
    """Title, scenario question, group and minutes from the live site's lesson map."""
    src = (SRC / "lessons.js").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r'\{slug: "([\w-]+)",[^\n]*?\}', src):
        row = m.group(0)
        field = lambda name: re.search(rf'{name}: "((?:[^"\\\\]|\\\\.)*)"', row)  # noqa: E731
        group, title, sub, mins = field("group"), field("title"), field("sub"), re.search(r"mins: (\d+)", row)
        if title and sub and mins:
            out[m.group(1)] = {"group": group.group(1) if group else "lessons", "title": title.group(1), "lead": sub.group(1).replace('\\"', '"'), "minutes": int(mins.group(1))}
    return out


def css_asset(css):
    """Lessons share a few stylesheets, so each distinct one is written once."""
    scoped = scope_css(css) + OVERRIDES
    return "lx-" + hashlib.md5(scoped.encode()).hexdigest()[:8] + ".css", scoped


def _fix_paper_links(html):
    """Papers sit at tracks/papers/<slug>/. Moved lessons are local, everything else stays on the current site."""
    def fix(m):
        home = _new_home(m.group(2))
        return f'href="../../{home[0]}/{home[1]}/{home[2]}"' if home else f'href="{LIVE}{m.group(2)}"'
    return re.sub(rf'href="({re.escape(LIVE)}|(?:\.\./){{2,3}})([^"]*)"', fix, html)


def extract_div(html, div_id):
    """Pulls one element out by id, counting nested divs. Returns (element, html without it)."""
    start = html.index(f'id="{div_id}"')
    start = html.rindex("<div", 0, start)
    depth, i = 0, start
    for m in re.finditer(r"<(/?)div\b", html[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            end = html.index(">", start + m.start()) + 1
            return html[start:end], html[:start] + html[end:]
    raise ValueError(div_id)


def read_paper(slug):
    """Reads a live paper page. The two papers use different templates, so chapters are normalised here."""
    folder = SRC / "papers" / slug
    text = (folder / "index.html").read_text(encoding="utf-8")
    head, body = text.split("</head>", 1)
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", head, re.S))
    header = re.search(r"<header[^>]*>(.*?)</header>", body, re.S).group(1)
    tldr = re.search(r'<div class="tldr">(.*?)</div>', header, re.S).group(1)
    tldr = re.sub(r"^\s*<b>(?:In one breath:|TL;DR)</b>\s*", "", tldr).replace("<br>", " ")
    tldr = re.sub(r"^((?:<[^>]+>)*)([a-z])(?!-)", lambda m: m.group(1) + m.group(2).upper(), tldr)
    legend = re.search(r'<div class="legend">.*?</div>', header, re.S)
    figure = re.search(r'<figure class="fig">.*?</figure>', header, re.S)
    chapters = {}
    for m in re.finditer(r"<section\b([^>]*)>(.*?)</section>", body[body.index("</header>"):], re.S):
        section_id = re.search(r'id="([^"]+)"', m.group(1)).group(1)
        toc = re.search(r'data-toc="([^"]*)"', m.group(1))
        inner = re.sub(r'<span class="n">\d+</span>', "", m.group(2))
        heading = re.search(r"<h2[^>]*>(.*?)</h2>", inner, re.S)
        label = toc.group(1) if toc else re.sub("<[^>]+>", "", heading.group(1)).strip()
        chapters[section_id] = _fix_paper_links(f'<section class="ch" id="{section_id}" data-toc="{label}">{inner}</section>')
    return {
        "css": css,
        "head_scripts": re.findall(r"<script[^>]*>.*?</script>", head, re.S),
        "scripts": [s for s in re.findall(r"<script[^>]*>.*?</script>", body, re.S) if "themeBtn" not in s],
        "meta": re.search(r'<div class="meta">(.*?)</div>', header, re.S).group(1),
        "tldr": _fix_paper_links(tldr),
        "legend": legend.group(0) if legend else "",
        "figure": figure.group(0) if figure else "",
        "chapters": chapters,
        "figures_dir": folder / "figures",
        "has_tip": 'id="tip"' in body,
    }
