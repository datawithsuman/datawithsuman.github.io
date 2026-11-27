"""Collect the last 7 days of AI news for the /news/ page.

Reads the company blogs, release pages, expert writers and tech press listed in SOURCES,
keeps posts published in the last 7 days, drops what isn't AI building news (funding,
politics, consumer features, quotes, pre-releases...), merges the same story from several
sources, tags a topic, and writes news.json next to this file. build.py copies it into the
site, and the GitHub Action also writes it straight into docs/news/.

Summaries are each post's own short description. overrides.json (keyed by post URL) can
replace a title, summary or topic, or hide a post: {"https://...": {"hide": true}}.

Run: python3 new-site/news/fetch_news.py [out.json]
"""
import datetime as dt, gzip, html, json, re, sys, urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from email.utils import parsedate_to_datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DAYS = 7
NOW = dt.datetime.now(dt.timezone.utc)
CUT = (NOW - dt.timedelta(days=DAYS)).replace(hour=0, minute=0, second=0, microsecond=0)
UA = {"User-Agent": "aimlrounds-news/1.0 (+https://aimlrounds.com/news/)"}
A = "{http://www.w3.org/2005/Atom}"

# (name, short badge, kind, url). kind: blog = company or engineering blog, release = GitHub
# releases, writer = expert writer, press = tech press, or a scraper name for sites with no feed.
SOURCES = [
    ("OpenAI", "OAI", "blog", "https://openai.com/news/rss.xml"),
    ("Google", "G", "blog", "https://blog.google/rss/"),
    ("Google Research", "GR", "blog", "https://research.google/blog/rss/"),
    ("Google DeepMind", "GDM", "blog", "https://deepmind.google/blog/rss.xml"),
    ("Google Developers", "GD", "blog", "https://developers.googleblog.com/rss/"),
    ("Anthropic", "A", "anthropic", "https://www.anthropic.com/news"),
    ("Anthropic", "A", "anthropic", "https://www.anthropic.com/engineering"),
    ("Anthropic", "A", "claude", "https://claude.com/blog"),
    ("Thinking Machines", "TM", "thinking", "https://thinkingmachines.ai/news/"),
    ("Microsoft Research", "MSR", "blog", "https://www.microsoft.com/en-us/research/feed/"),
    ("NVIDIA", "NV", "blog", "https://developer.nvidia.com/blog/feed/"),
    ("AWS", "AWS", "blog", "https://aws.amazon.com/blogs/machine-learning/feed/"),
    ("Cloudflare", "CF", "blog", "https://blog.cloudflare.com/tag/ai/rss"),
    ("Cloudflare", "CF", "blog", "https://blog.cloudflare.com/tag/agents/rss"),
    ("Hugging Face", "HF", "blog", "https://huggingface.co/blog/feed.xml"),
    ("GitHub", "GH", "blog", "https://github.blog/ai-and-ml/feed/"),
    ("Vercel", "V", "blog", "https://vercel.com/atom"),
    ("LangChain", "LC", "blog", "https://www.langchain.com/blog/rss.xml"),
    ("Meta Engineering", "M", "blog", "https://engineering.fb.com/feed/"),
    ("Netflix", "N", "blog", "https://netflixtechblog.com/feed"),
    ("vLLM", "vL", "release", "https://github.com/vllm-project/vllm/releases.atom"),
    ("Ollama", "OL", "release", "https://github.com/ollama/ollama/releases.atom"),
    ("transformers", "TF", "release", "https://github.com/huggingface/transformers/releases.atom"),
    ("LangGraph", "LG", "release", "https://github.com/langchain-ai/langgraph/releases.atom"),
    ("MCP Python SDK", "MCP", "release", "https://github.com/modelcontextprotocol/python-sdk/releases.atom"),
    ("MCP TypeScript SDK", "MCP", "release", "https://github.com/modelcontextprotocol/typescript-sdk/releases.atom"),
    ("DSPy", "DS", "release", "https://github.com/stanfordnlp/dspy/releases.atom"),
    ("LlamaIndex", "LI", "release", "https://github.com/run-llama/llama_index/releases.atom"),
    ("Simon Willison", "SW", "writer", "https://simonwillison.net/atom/everything/"),
    ("Latent Space", "LS", "writer", "https://www.latent.space/feed"),
    ("Phil Schmid", "PS", "writer", "https://www.philschmid.de/rss"),
    ("Eugene Yan", "EY", "writer", "https://eugeneyan.com/rss/"),
    ("Hamel Husain", "HH", "writer", "https://hamel.dev/index.xml"),
    ("Jason Liu", "JL", "writer", "https://jxnl.co/feed_rss_created.xml"),
    ("Analytics India Mag", "AIM", "press", "https://analyticsindiamag.com/feed/"),
    ("TechCrunch", "TC", "press", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("The Verge", "VG", "press", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
]
OFFICIAL = {"blog", "anthropic", "claude", "thinking", "release"}

AI = re.compile(r"\b(AI|LLMs?|GenAI|models?|agents?|agentic|MCP|inference|transformers?|attention|tokens?|fine-tun\w*|RAG|"
                r"embeddings?|GPT|Gemini|Claude|Llama|neural|reasoning|evals?|benchmarks?|open[- ]weights?|multimodal|speech|vision)\b", re.I)
# Not AI building news: money, people, politics, events, consumer products.
NOISE = re.compile(r"\b(IPO|raises?|raised|funding|valuation|Series [A-F]|seed round|investors?|invests?|investment|shares|stock|earnings|revenue|"
                   r"credit rating|acquir\w+|acquisition|merger|lawsuits?|sues|court|bankrupt\w*|antitrust|regulat\w+|ban(s|ned)?|bill|senators?|"
                   r"governments?|govt|ministry|election|Trump|White House|export|CEO|founder|resign\w*|reinstat\w+|hires?|appoint\w*|"
                   r"joins .{0,30} as|layoffs?|job cuts|restructur\w+|webinar|summit|conference|event|podcast|episode|watch|"
                   r"partners? with|partnership|tie-up|teams up|deal|contract|sponsor\w*|data cent(er|re)s?|satellites?|"
                   r"certification|ISO \d+|country manager|Black Friday|Christmas|music|film|movie|games?|gaming|DLSS|earbuds|"
                   r"Instagram|WhatsApp|Photoshop|toys?|kids?|fans?|initiative|programme|partner\w*|holiday|memories|year-end|filmmakers?|anniversary|years of|"
                   r"interview|Q&A|in review|roundup|recap|newsletter)\b|^[\w&.' ]+'s [A-Z]\w+ [A-Z]\w+ on ", re.I)
LAUNCH = re.compile(r"\b(launch\w*|releas\w*|introduc\w*|unveil\w*|open[- ]sourc\w*|debuts?|rolls? out|ships?|announc\w*|now available|builds?)\b", re.I)
TOPICS = [  # first match wins
    ("prod", re.compile(r"customer-stories|\bhow [A-Z][\w.&-]+ (uses|scales|builds|automates|runs|turns)\b|\bhelps (companies|teams|sales)\b", re.I)),
    ("agents", re.compile(r"\b(agents?|agentic|MCP|tool[- ]?(use|calls?|gateway)|skills?|multi-agent|swarms?|workflows?|computer use|browser)\b", re.I)),
    ("infer", re.compile(r"\b(inference|serving|KV[- ]cach\w*|latency|throughput|GPUs?|quantiz\w*|FP4|NVFP4|FP8|kernels?|speculative|vLLM|Rust|CPU|memory)\b", re.I)),
    ("research", re.compile(r"\b(research|benchmarks?|evals?|evaluation|papers?|algorithms?|study|reasoning|perplexity|formal verification|residual)\b", re.I)),
    ("models", re.compile(r"\b(models?|open[- ]weights?|LLMs?|\d+B\b|Gemini \d|GPT-\d|Claude \w+ \d|Inkling|Llama|Mistral|Qwen|GLM)\b", re.I)),
]


def get(url, timeout=30):
    body = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()
    return gzip.decompress(body) if body[:2] == b"\x1f\x8b" else body  # some servers gzip even when not asked


def clean(x):
    x = re.sub(r"<[^>]+>", " ", html.unescape(x or ""))
    x = re.sub(r"The post .{0,200}? appeared first on .{0,80}?\.?\s*$", "", x)
    return re.sub(r"\s+", " ", x).strip()


def when(s):
    s = (s or "").strip()
    for f in (parsedate_to_datetime, lambda v: dt.datetime.fromisoformat(v.replace("Z", "+00:00"))):
        try:
            d = f(s)
            return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)
        except Exception:
            pass
    return None


def day(s, fmt):
    return dt.datetime.strptime(s, fmt).replace(hour=12, tzinfo=dt.timezone.utc)


def post(src, url, title, at, desc=""):
    return {"src": src[0], "ab": src[1], "kind": src[2], "url": url, "title": clean(title), "at": at, "desc": clean(desc)}


def feed(src):
    root, out = ET.fromstring(get(src[3])), []
    for it in root.findall(".//item") or root.findall(f".//{A}entry"):
        g = lambda t: it.findtext(t) or it.findtext(A + t) or ""
        link = g("link").strip() or (it.find(A + "link").get("href") if it.find(A + "link") is not None else "")
        d = None
        for t in ("pubDate", "published", A + "published", "updated", A + "updated", "{http://purl.org/dc/elements/1.1/}date"):
            if it.findtext(t):
                d = when(it.findtext(t))
                break
        desc = g("description") or g("summary") or it.findtext("{http://purl.org/rss/1.0/modules/content/}encoded") or g("content")
        if d:
            out.append(post(src, link, g("title"), d, desc[:3000]))
    return out


def anthropic(src):
    """anthropic.com lists posts in an embedded JSON blob: href, title, date."""
    h, out = get(src[3]).decode("utf8", "ignore").replace('\\"', '"'), {}
    for m in re.finditer(r'"href":"(/(?:news|research|engineering)/[^"]+)","title":"([^"]+)"[^{}]*?"date":"([A-Z][a-z]{2} \d{1,2}, \d{4})"', h):
        out.setdefault(m[1], post(src, "https://www.anthropic.com" + m[1], m[2], day(m[3], "%b %d, %Y")))
    for m in re.finditer(r'href="(/(?:news|research|engineering)/[a-z0-9-]+)"(.{0,3000}?)([A-Z][a-z]{2} \d{1,2}, 20\d\d)', h, re.S):
        if m[1] in out or m[1].split("/")[2] in ("announcements", "product", "policy", "societal-impacts", "economic-research", "alignment", "interpretability"):
            continue
        parts = [p.strip() for p in re.sub(r"<[^>]+>", "|", html.unescape(m[2])).split("|") if len(p.strip()) > 12 and "{" not in p]
        if parts:
            out[m[1]] = post(src, "https://www.anthropic.com" + m[1], parts[0], day(m[3], "%b %d, %Y"), " ".join(parts[1:2]))
    return list(out.values())


def claude(src):
    """claude.com/blog cards: link, then date, then title and a one-line description."""
    h, out = get(src[3]).decode("utf8", "ignore"), []
    links = [(m.start(), m[1]) for m in re.finditer(r'href="(/(?:resources/articles|blog)/[a-z0-9-]+)"', h)]
    for m in re.finditer(r"\b([A-Z][a-z]{2} \d{1,2}, 20\d\d)\b", h):
        before = [u for p, u in links if p < m.start() and m.start() - p < 4000]
        if not before:
            continue
        parts = [p.strip() for p in re.sub(r"<[^>]+>", "|", html.unescape(h[m.end():m.end() + 1500])).split("|") if p.strip() and not re.search(r"[<>]|\bd=|^\W+$", p)]
        if parts and before[-1] not in {o["url"] for o in out}:
            out.append(post(src, "https://claude.com" + before[-1], parts[0], day(m[1], "%b %d, %Y"), parts[1] if len(parts) > 1 and len(parts[1]) > 40 else ""))
    return out


def thinking(src):
    h, out = get(src[3]).decode("utf8", "ignore"), {}
    for m in re.finditer(r'<a[^>]+href="(/news/[a-z0-9-]+/)"[^>]*>(.*?)</a>', h, re.S):
        t = clean(m[2])
        d = re.search(r"([A-Z][a-z]{2} \d{1,2}, 20\d\d)$", t)
        if d and m[1] not in out:
            out[m[1]] = post(src, "https://thinkingmachines.ai" + m[1], t[:d.start()].strip(), day(d[1], "%b %d, %Y"))
    return list(out.values())


def fetch(src):
    try:
        return {"anthropic": anthropic, "claude": claude, "thinking": thinking}.get(src[2], feed)(src)
    except Exception as e:
        print(f"  ! {src[0]} ({src[3]}): {type(e).__name__} {str(e)[:80]}", file=sys.stderr)
        return []


def keep(p):
    """Rules that drop what isn't AI building news. Returns the reason to drop, or None."""
    t, d, k, s = p["title"], p["desc"], p["kind"], p["src"]
    if p["at"] < CUT:
        return "older than 7 days"
    if k == "release":
        v = re.search(r"(\d+)\.(\d+)\.(\d+)", t)
        if re.search(r"rc\d|alpha|beta|dev\d|\.post|cli==|patch", t, re.I) or not v or v[3] != "0":
            return "pre-release or patch"
        p["title"] = f"{s} {t.split(':')[0].replace('Release ', '').strip()} released"
        return None
    if NOISE.search(t):
        return "not building news"
    if s == "Google" and not re.search(r"/(models-and-research|developers-tools|google-deepmind|technology/ai)/", p["url"]):
        return "Google consumer or company post"
    if re.match(r"(Watch|Join|Register)\b", d):
        return "webinar or event"
    if k == "writer":
        if s == "Simon Willison" and (t.startswith("Quoting") or re.match(r"(Release|Tool):", d) or "(YouTube)" in t or not AI.search(t)):
            return "quote, short link or not AI"
        if s == "Latent Space" and (t.startswith("[AINews]") or " — " in t):
            return "roundup or podcast"
    if k == "press" and not (LAUNCH.search(t) and AI.search(t)):
        return "press story that isn't a launch"
    if s in ("Vercel", "NVIDIA", "Meta Engineering", "Netflix", "Microsoft Research") and not AI.search(t + " " + d[:300]):
        return "not AI"
    if re.search(r"[぀-ヿ一-鿿]", t):
        return "not English"
    if re.search(r"llama\.cpp", t, re.I):
        return "llama.cpp (not covered)"
    return None


def words(t):
    return {w for w in re.findall(r"[a-z0-9]+", t.lower()) if len(w) > 2} - {"the", "and", "for", "with", "new", "now", "how", "its", "our", "your", "from", "into"}


LAUNCH_NAME = re.compile(r"\b(?:Introduc\w*|Welcome|Announc\w*|Meet|Launch\w*|Unveil\w*)\s+(.+?)(?: to | for | with |[,:]|$)|^(.+?) (?:is )?now (?:available|open)", re.I)


def launch_name(t):
    """The product a launch-style title is about, so "Introducing X" and "Welcome X" merge."""
    m = LAUNCH_NAME.search(t)
    return (m[1] or m[2]).strip().lower() if m else None


def summary(d):
    d = re.sub(r"^(Overview|What's Changed|TL;DR)\s*", "", d).strip()
    out = ""
    for sent in re.split(r"(?<=[.!?])\s+", d):
        if len(out) + len(sent) > 300 and out:
            break
        out = (out + " " + sent).strip()
    return out[:320].rstrip() + ("…" if len(out) > 320 else "")


def describe(p):
    """Posts whose feed gives no description: read the page's own og:description."""
    if len(p["desc"]) >= 60:
        return p
    try:
        h = get(p["url"], 20).decode("utf8", "ignore")
        m = (re.search(r'<meta[^>]+(?:property|name)="(?:og:description|description)"[^>]+content="([^"]*)"', h)
             or re.search(r'<meta[^>]+content="([^"]*)"[^>]+(?:property|name)="(?:og:description|description)"', h))
        d = clean(m[1]) if m else ""
        if not d or len(d) < 60 or re.search(r"journey to advance and democratize|^A Blog post by", d):
            paras = [clean(x) for x in re.findall(r"<p[^>]*>(.*?)</p>", h, re.S)]
            d = next((x for x in paras if len(x) > 120 and not re.search(r"Search models|Explore (our|all)|cookies|Sign (in|up)", x)), d)
        if d:
            p["desc"] = d
    except Exception:
        pass
    return p


def main(out_path=None):
    with ThreadPoolExecutor(12) as ex:
        posts = [p for r in ex.map(fetch, SOURCES) for p in r]
    seen, uniq = set(), []
    for p in posts:
        u = p["url"].split("?")[0].rstrip("/")
        if u not in seen:
            seen.add(u)
            uniq.append(p)
    dropped = {}
    kept = []
    for p in uniq:
        why = keep(p)
        if why:
            dropped[why] = dropped.get(why, 0) + 1
        else:
            kept.append(p)
    over = json.loads((HERE / "overrides.json").read_text()) if (HERE / "overrides.json").exists() else {}
    kept = [p for p in kept if not over.get(p["url"], {}).get("hide")]
    with ThreadPoolExecutor(10) as ex:
        kept = list(ex.map(describe, kept))

    # The same story from several sources becomes one card; the company's own post wins.
    kept.sort(key=lambda p: (p["kind"] not in OFFICIAL, p["at"]))
    cards = []
    for p in kept:
        w = words(p["title"])
        nm = launch_name(p["title"])
        twin = next((c for c in cards if abs((c["at"] - p["at"]).days) <= 3 and (len(w & c["w"]) >= max(3, 0.5 * min(len(w), len(c["w"])))
                                                                              or (nm and nm == c.get("nm")))), None)
        if twin:
            twin["also"] = twin.get("also") or p["src"]
            continue
        p["w"], p["nm"] = w, nm
        cards.append(p)

    items = []
    for c in cards:
        o = over.get(c["url"], {})
        text = c["title"] + " " + c["desc"] + " " + c["url"]
        topic = next((k for k, rx in TOPICS if rx.search(text)), "tools")
        items.append({"src": c["src"], "ab": c["ab"], "at": c["at"].isoformat(timespec="minutes"), "topic": o.get("topic", topic),
                      "title": o.get("title", c["title"]), "url": c["url"], "sum": o.get("sum", summary(c["desc"])), **({"also": c["also"]} if c.get("also") else {})})
    items.sort(key=lambda i: i["at"], reverse=True)
    data = {"updated": NOW.isoformat(timespec="minutes"), "days": DAYS, "count": len(items), "sources": len({i["src"] for i in items}), "items": items}
    text = json.dumps(data, ensure_ascii=False, indent=1)
    (HERE / "news.json").write_text(text)
    if out_path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(out_path).write_text(text)
    print(f"{len(posts)} posts, {len(uniq)} unique, {len(items)} kept from {data['sources']} sources. Dropped: {dropped}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
