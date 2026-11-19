"""Machine-readable copy of the site, for AI tools: /llms.txt, /llms-full.txt and /api/v1/.

build.py calls export() after every page is written. It reads each lesson's built HTML and turns
the lesson article into plain Markdown (interactive widgets and drawings are skipped; equations
keep their TeX). The MCP server in ../mcp reads these files, so it never needs its own copy.

  api/v1/index.json            every lesson: id, title, track, part, section, type, minutes, lead, headings, url
  api/v1/lessons/<id>.md       one lesson as Markdown
  api/v1/quizzes.json          topic quizzes with answers and explanations
  api/v1/mocks.json            mock interview rounds with model answers
  api/v1/roadmap.json          role roadmaps: topics in order, with their lessons
  api/v1/new.json              recently added pages
"""
import json
import re
from datetime import date
from html import unescape
from html.parser import HTMLParser

SKIP = {"script", "style", "svg", "button", "input", "select", "textarea", "label", "output", "canvas", "noscript", "template", "nav", "form"}
VOID = {"br", "hr", "img", "input", "meta", "link", "source", "col", "wbr", "area", "base", "embed", "param", "track"}
BLOCK = {"p", "div", "section", "article", "figure", "figcaption", "blockquote", "ul", "ol", "li", "table", "tr", "details", "summary",
         "h1", "h2", "h3", "h4", "h5", "h6", "pre", "aside", "header", "footer", "main", "dl", "dt", "dd"}


class Node:
    __slots__ = ("tag", "attrs", "kids")

    def __init__(self, tag, attrs):
        self.tag, self.attrs, self.kids = tag, dict(attrs), []

    def cls(self):
        return self.attrs.get("class") or ""


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root", {})
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs)
        self.stack[-1].kids.append(n)
        if tag not in VOID:
            self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].kids.append(Node(tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].kids.append(data)


def parse(html):
    t = Tree()
    t.feed(html)
    return t.root


def find(node, pred):
    if isinstance(node, str):
        return None
    if pred(node):
        return node
    for k in node.kids:
        r = find(k, pred)
        if r is not None:
            return r
    return None


def clean_tex(tex):
    # \class{term t-x}{BODY} -> BODY (the site uses these only for hover colours)
    out, i = "", 0
    while True:
        j = tex.find(r"\class{", i)
        if j < 0:
            return out + tex[i:]
        out += tex[i:j]
        k = tex.find("}", j) + 1  # end of the class name
        if k <= 0 or k >= len(tex) or tex[k] != "{":
            out += tex[j:k]
            i = k
            continue
        depth, m = 0, k
        while m < len(tex):
            depth += {"{": 1, "}": -1}.get(tex[m], 0)
            if depth == 0:
                break
            m += 1
        out += clean_tex(tex[k + 1:m])
        i = m + 1


def inline(node):
    """Text of a node with **bold**, _italic_, `code` and inline maths."""
    if isinstance(node, str):
        return re.sub(r"\s+", " ", node)
    if skipped(node):
        return ""
    if node.attrs.get("data-tex"):
        tex = clean_tex(unescape(node.attrs["data-tex"]))
        return f" $$ {tex} $$ " if node.tag == "div" else f"${tex}$"
    if node.tag == "br":
        return "\n"
    s = "".join(inline(k) for k in node.kids)
    if node.tag in ("b", "strong") and s.strip():
        return f"**{s.strip()}** " if s.endswith(" ") else f"**{s.strip()}**"
    if node.tag in ("i", "em") and s.strip():
        return f"_{s.strip()}_"
    if node.tag == "code" and s.strip():
        return f"`{s.strip()}`"
    return s


def has_block(node):
    return any(not isinstance(k, str) and not skipped(k) and (k.tag in BLOCK or k.attrs.get("data-tex") and k.tag == "div" or has_block(k)) for k in node.kids)


def table_md(node):
    rows = []

    def walk(n):
        for k in n.kids:
            if isinstance(k, str):
                continue
            if k.tag == "tr":
                rows.append([inline(c).strip().replace("|", "\\|") for c in k.kids if not isinstance(c, str) and c.tag in ("td", "th")])
            else:
                walk(k)
    walk(node)
    rows = [r for r in rows if any(r)]
    if not rows:
        return ""
    w = max(len(r) for r in rows)
    rows = [r + [""] * (w - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


SKIP_CLASS = {"stats", "stat", "legend", "hint", "mine", "pill", "meter", "checks", "check-meter", "say-actions", "say-hint",
              "say-score", "stage", "seg", "lesson-tabs", "depth", "panel-next", "sr", "say-dot"}


def skipped(k):
    if k.tag in SKIP or k.attrs.get("aria-hidden") == "true" or k.attrs.get("hidden") is not None or k.attrs.get("role") == "tablist":
        return True
    return bool(SKIP_CLASS & set(k.cls().split()))


def is_inline(k):
    return isinstance(k, str) or (k.tag not in BLOCK and not (k.attrs.get("data-tex") and k.tag == "div") and not has_block(k))


def blocks(node, out, depth=0):
    """Appends Markdown blocks for node's children to out. Runs of text and inline tags become one paragraph."""
    buf = []

    def flush():
        t = re.sub(r"\s+", " ", "".join(buf)).strip()
        buf.clear()
        if t:
            out.append(t)

    def eqs(n):
        for x in n.kids:
            if isinstance(x, str):
                continue
            if x.attrs.get("data-tex"):
                out.append(f"$$ {clean_tex(unescape(x.attrs['data-tex']))} $$")
            else:
                eqs(x)

    for k in node.kids:
        if not isinstance(k, str) and skipped(k):
            if k.tag == "svg" and k.attrs.get("aria-label") and not k.attrs.get("data-o"):
                flush()
                out.append(f"[Figure: {k.attrs['aria-label']}]")
            elif k.tag not in SKIP:
                flush()
                eqs(k)  # an equation sitting inside a drawing area
            continue
        if is_inline(k):
            buf.append(inline(k))
            continue
        flush()
        c = set(k.cls().split())
        if "reader" in c and k.attrs.get("data-reader"):
            # equation reader: the equation, then what each part means
            blocks(k, out, depth)
            try:
                for item in json.loads(k.attrs["data-reader"]):
                    out.append(f"- **{item.get('label', '')}**: {item.get('say', '')}")
            except ValueError:
                pass
            continue
        if "lab" in c:
            # interactive lab: keep only its written explanation
            def paras(n):
                for x in n.kids:
                    if isinstance(x, str) or skipped(x):
                        continue
                    if x.tag == "p":
                        t = inline(x).strip()
                        if t:
                            out.append(t)
                    else:
                        paras(x)
            paras(k)
            continue
        if k.attrs.get("data-tex") and k.tag == "div":
            out.append(f"$$ {clean_tex(unescape(k.attrs['data-tex']))} $$")
            continue
        if re.fullmatch(r"h[1-6]", k.tag):
            lvl = min(6, int(k.tag[1]) + 1)  # h1 is the page title; lessons start at ##
            t = inline(k).strip()
            if t:
                out.append("#" * lvl + " " + t)
            continue
        if k.tag == "p":
            t = inline(k).strip()
            if t:
                out.append(t)
            continue
        if k.tag in ("ul", "ol"):
            n = 0
            for li in k.kids:
                if isinstance(li, str) or li.tag != "li" or skipped(li):
                    continue
                n += 1
                sub = []
                blocks(li, sub, depth + 1)
                t = " ".join(sub).strip()
                if t:
                    out.append(("  " * depth) + (f"{n}. " if k.tag == "ol" else "- ") + t)
            continue
        if k.tag == "table":
            t = table_md(k)
            if t:
                out.append(t)
            continue
        if k.tag == "blockquote":
            sub = []
            blocks(k, sub, depth)
            if sub:
                out.append("\n".join("> " + s for s in "\n\n".join(sub).split("\n")))
            continue
        if k.tag == "summary":
            t = inline(k).strip()
            if t:
                out.append(f"**{t}**")
            continue
        if k.tag == "pre":
            out.append("```\n" + "".join(inline(x) if not isinstance(x, str) else x for x in k.kids).strip("\n") + "\n```")
            continue
        if k.tag == "figcaption":
            t = inline(k).strip()
            if t:
                out.append(f"_{t}_")
            continue
        if "tab-panel" in c:
            label = TAB_NAMES.get(k.attrs.get("aria-labelledby", ""), "")
            if label:
                out.append(f"## {label}")
            blocks(k, out, depth)
            continue
        blocks(k, out, depth)
    flush()


TAB_NAMES = {}


def lesson_markdown(html):
    """Returns (markdown body, list of section headings) for a built lesson page."""
    tree = parse(html)
    art = find(tree, lambda n: n.tag == "article" and "lesson" in n.cls().split())
    if art is None:
        return "", []
    TAB_NAMES.clear()
    tabs = find(art, lambda n: n.attrs.get("role") == "tablist")
    if tabs:
        for b in tabs.kids:
            if not isinstance(b, str) and b.attrs.get("id"):
                TAB_NAMES[b.attrs["id"]] = "".join(x for x in b.kids if isinstance(x, str)).strip()
    # Drop the parts already in the header or that only make sense on the page.
    drop = ("crumbs", "lesson-meta", "h1-lesson", "lead", "prev-next", "mark-done", "quiz-cta", "picture")
    art.kids = [k for k in art.kids if isinstance(k, str) or not any(d in k.cls().split() for d in drop)]
    out = []
    blocks(art, out)
    md, prev = [], None
    for b in out:
        b = re.sub(r"[ \t]+", " ", b).strip()
        if b and b != prev and not (prev and prev.startswith("#") and prev.lstrip("# ") == b):
            md.append(b)
        prev = b
    # drop headings with nothing under them (prompts for on-page widgets)
    level = lambda x: len(x) - len(x.lstrip("#")) if x.startswith("#") else 99
    md = [x for i, x in enumerate(md) if not (x.startswith("#") and (i + 1 == len(md) or level(md[i + 1]) <= level(x)))]
    text = "\n\n".join(md)
    text = re.sub(r"\n{3,}", "\n\n", text)
    heads = [m[2:].strip("# ").strip() for m in md if m.startswith("###") and not m.startswith("#####")]
    return text, heads


def export(b):
    """b is the build module (TRACKS, ORDERED, LESSONS, RM, quizzes, mocks, DIST, BASE, ...)."""
    base, dist = b.BASE, b.DIST
    api = dist / "api/v1"
    (api / "lessons").mkdir(parents=True, exist_ok=True)
    rows, full = [], []
    quiz_by_lesson = {}
    for tid in b.quizzes.READY:
        for k in b.RM["topics"][tid]["lessons"]:
            quiz_by_lesson[k] = tid
    for l in b.ORDERED:
        html = (dist / l["url"] / "index.html").read_text(encoding="utf-8")
        body, heads = lesson_markdown(html)
        t, m = l["track"], l["module"]
        part = m.get("part") or ""
        crumbs = " › ".join([t["name"]] + ([part] if part else []) + ([m["name"]] if m["name"] != part else []))
        head = [f"# {l['title']}", "", f"> {l['lead']}", "",
                f"- Track: {crumbs}",
                f"- Type: {b.TYPE_LABEL[l['type']]} · {l['minutes']} min",
                f"- Page: {base}{l['url']}"]
        if l.get("prereqs"):
            head.append("- Before this: " + ", ".join(f"{b.LESSONS[k]['title']} (`{k}`)" for k in l["prereqs"]))
        if l.get("related"):
            head.append("- Related: " + ", ".join(f"{b.LESSONS[k]['title']} (`{k}`)" for k in l["related"]))
        if l["key"] in quiz_by_lesson:
            head.append(f"- Quiz topic: `{quiz_by_lesson[l['key']]}`")
        md = "\n".join(head) + "\n\n" + body + "\n"
        path = api / "lessons" / f"{l['key']}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")
        full.append(md)
        rows.append({"id": l["key"], "title": l["title"], "track": t["id"], "trackName": t["name"], "part": part,
                     "section": m["name"], "type": b.TYPE_LABEL[l["type"]].lower(), "minutes": l["minutes"],
                     "lead": l["lead"], "q": l.get("q", "") if l.get("q") != l["lead"] else "",
                     "headings": heads[:30], "words": len(body.split()), "url": base + l["url"],
                     "quiz": quiz_by_lesson.get(l["key"], "")})

    topics = b.RM["topics"]
    quizzes = {tid: {"id": tid, "name": topics[tid]["name"], "url": base + f"quiz/{b.QUIZ_SLUG[tid]}/",
                     "questions": [{"q": q[0], "options": q[1], "answer": q[2], "why": q[3],
                                    "lesson": next(k for k in topics[tid]["lessons"] if k.endswith("/" + q[4]))}
                                   for q in b.quizzes.QUIZZES[tid]]}
               for tid in b.quizzes.READY}
    mocks = [{"id": m["id"], "name": m["name"], "blurb": m["blurb"], "url": base + f'mock/{m["id"]}/',
              "rounds": [{"id": r["id"], "name": r["name"], "minutes": r["minutes"], "intro": r["intro"],
                          "url": base + f'mock/{m["id"]}/{r["id"]}/',
                          "questions": [{"q": q["q"], "answer": q["a"], "listen_for": q["listen"], "lessons": q["lessons"]}
                                        for q in r["questions"]]} for r in m["rounds"]]} for m in b.mocks.MOCKS]
    roles = []
    for r in b.RM["roles"]:
        useful = set(r.get("useful", []))
        order = [tid for row in r["rows"] for tid in row]
        roles.append({"id": r["id"], "name": r["name"], "blurb": r.get("blurb", ""), "url": base + f'roadmap/#{r["id"]}',
                      "mock": r["id"] if r.get("mock") else "",
                      "steps": [{"topic": tid, "name": topics[tid]["name"], "level": "useful" if tid in useful else "core",
                                 "quiz": tid if tid in quizzes else "", "lessons": topics[tid]["lessons"]} for tid in order]})
    tracks = [{"id": t["id"], "name": t["name"], "url": base + f'tracks/{t["id"]}/',
               "sections": [{"part": m.get("part") or "", "name": m["name"], "lessons": [l["key"] for l in m["lessons"]]}
                            for m in t["modules"]]} for t in b.TRACKS]

    def dump(name, obj):
        (api / name).write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    today = date.today().isoformat()
    dump("index.json", {"site": base, "updated": today, "tracks": tracks, "lessons": rows,
                        "quizzes": [{"id": q["id"], "name": q["name"], "n": len(q["questions"])} for q in quizzes.values()],
                        "mocks": [{"id": m["id"], "name": m["name"], "rounds": [r["id"] for r in m["rounds"]]} for m in mocks]})
    dump("quizzes.json", quizzes)
    dump("mocks.json", mocks)
    dump("roadmap.json", roles)
    dump("new.json", [{**x, "url": base + x["url"] if x["url"] else ""} for x in b.updates()[:60]])

    # llms.txt: the standard short map for AI tools, and the full text in one file.
    lines = ["# AIML Rounds", "",
             "> Free AI/ML interview prep: lessons on maths, classical ML, deep learning, NLP, LLMs, RAG, agents, inference, MLOps, "
             "evals and AI/ML system design, plus role roadmaps, topic quizzes, mock interviews and a daily AI/ML jobs list for India.", "",
             f"Every lesson is also available as Markdown under {base}api/v1/lessons/. "
             f"A JSON index is at {base}api/v1/index.json."
             + (" The official AIML Rounds MCP server for Claude and other AI tools is https://mcp.aimlrounds.com/mcp "
                "(MCP Registry name: com.aimlrounds/aimlrounds). Servers at other addresses are not run by this site." if b.MCP_PUBLIC else ""), ""]
    for t in b.TRACKS:
        lines.append(f"## {t['name']}")
        lines.append("")
        for l in [x for x in b.ORDERED if x["track"] is t]:
            lines.append(f"- [{l['title']}]({base}api/v1/lessons/{l['key']}.md): {l['lead']}")
        lines.append("")
    lines += ["## Practice", "", f"- [Role roadmaps]({base}roadmap/)", f"- [Mock interviews]({base}mock/)",
              f"- [AI/ML jobs in India]({base}jobs/): updated daily, JSON at {base}jobs/jobs.json", ""]
    (dist / "llms.txt").write_text("\n".join(lines), encoding="utf-8")
    (dist / "llms-full.txt").write_text("\n\n---\n\n".join(full), encoding="utf-8")
    return len(rows)
