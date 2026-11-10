"""Role roadmaps for /roadmap/: topics made of existing lessons, and one topic graph per role.

A topic is a group of lessons. Fundamentals topics are whole modules. AI Engineering and
System Design topics are runs of lessons, from a starting lesson to the next one.
Each role lists its graph row by row (top to bottom), the edges between topics, and which
topics are only "useful" (shown faded). Everything else in a role is core.
"""

# id: (name, track, how to find its lessons)
#   ("modules", [module names])     every lesson in those Fundamentals modules
#   ("run", first lesson slug)      AI Engineering lessons from this slug up to the next run
#   ("slugs", [slugs])              exactly these lessons
#   ("group", track, group)         every lesson in that track group
TOPICS = {
    "la": ("Linear algebra", ("modules", ["Linear algebra"])),
    "calc": ("Calculus and optimisation", ("modules", ["Calculus and optimisation"])),
    "prob": ("Probability", ("modules", ["Probability", "Probability practice"])),
    "stats": ("Statistics", ("modules", ["Statistics"])),
    "info": ("Information theory", ("modules", ["Information theory"])),
    "ab": ("A/B testing", ("modules", ["Designing a test", "Reading the result", "Can you trust it?", "Beyond the fixed test"])),
    "feat": ("Data and features", ("modules", ["Data and features"])),
    "mlcore": ("ML core concepts", ("modules", ["Core concepts"])),
    "lin": ("Linear models", ("modules", ["Linear models"])),
    "trees": ("Tree-based models", ("modules", ["Tree-based models"])),
    "clf": ("Other classifiers", ("modules", ["Other classic classifiers"])),
    "unsup": ("Unsupervised learning", ("modules", ["Unsupervised learning"])),
    "ts": ("Time series", ("modules", ["Time series"])),
    "metrics": ("Evaluation metrics", ("modules", ["Evaluation metrics"])),
    "nn": ("Neural network basics", ("modules", ["Neural network basics"])),
    "train": ("Training deep nets", ("modules", ["Training deep nets", "Regularisation and debugging"])),
    "cnn": ("CNNs and vision", ("modules", ["CNNs", "Computer vision"])),
    "seq": ("Sequence models", ("modules", ["Sequence models"])),
    "attn": ("Attention and Transformers", ("modules", ["Attention and Transformers"])),
    "genm": ("Generative models", ("modules", ["Representation and generative models"])),
    "nlp": ("NLP basics", ("modules", ["Text basics", "Language models and tokenisation", "Tagging, retrieval and evaluation"])),
    "arch": ("LLM architecture", ("modules", ["Modern architecture"])),
    "pre": ("Pretraining", ("modules", ["Pretraining"])),
    "post": ("Post-training", ("modules", ["Post-training"])),
    "llmgen": ("Generation and LLM evals", ("modules", ["Generation", "Evaluating LLMs and practice"])),
    "infer": ("Inference and serving", ("run", "prefill-vs-decode")),
    "prompt": ("Prompting", ("run", "prompt-engineering-patterns")),
    "rag": ("RAG", ("run", "rag-end-to-end")),
    "agents": ("Agents and MCP", ("run", "what-is-an-agent")),
    "mlops": ("MLOps", ("run", "training-serving-skew-and-feature-stores")),
    "llmops": ("LLMOps", ("run", "llmops")),
    "sdllm": ("LLM and agent system design", ("group", "system-design", "designs")),
    "sdrec": ("Recommenders and ranking", ("slugs", ["recommendation-system", "design-semantic-search", "design-interleaving", "design-image-personalisation"])),
    "sdexp": ("Experiment design", ("slugs", ["design-llm-prompt-test", "design-ai-subject-lines", "design-network-experiment", "design-launch-decision-rule", "design-experimentation-platform"])),
    "papers": ("Key papers", ("group", "papers", None)),
}

ROLES = [
    {
        "id": "ai-engineering", "name": "AI Engineering",
        "blurb": "Build products on LLMs: prompting, RAG, agents, serving and the systems around them.",
        "rows": [["la", "prob", "mlcore"], ["nn", "nlp"], ["attn"], ["arch", "papers"], ["pre", "infer"],
                 ["post", "llmops"], ["prompt", "llmgen"], ["rag"], ["agents"], ["sdllm"]],
        "edges": [("la", "nn"), ("prob", "nn"), ("mlcore", "nn"), ("nn", "attn"), ("nlp", "attn"), ("attn", "arch"), ("attn", "papers"),
                  ("arch", "pre"), ("arch", "infer"), ("pre", "post"), ("infer", "llmops"), ("post", "prompt"), ("post", "llmgen"),
                  ("prompt", "rag"), ("rag", "agents"), ("llmops", "agents"), ("llmgen", "agents"), ("agents", "sdllm")],
        "useful": ["la", "prob", "mlcore"],
    },
    {
        "id": "ml-engineering", "name": "ML Engineering",
        "blurb": "Train, ship and run models: classic ML, deep learning, MLOps, serving and ML system design.",
        "rows": [["la", "calc", "prob"], ["mlcore", "feat", "stats"], ["lin", "trees", "metrics"], ["nn", "clf", "unsup", "mlops"],
                 ["train", "ab"], ["cnn", "seq", "genm"], ["attn"], ["arch", "infer"], ["prompt", "sdrec"], ["rag", "sdllm"]],
        "edges": [("la", "mlcore"), ("calc", "mlcore"), ("prob", "stats"), ("mlcore", "lin"), ("stats", "lin"), ("mlcore", "trees"), ("feat", "trees"),
                  ("stats", "metrics"), ("lin", "nn"), ("lin", "clf"), ("trees", "unsup"), ("metrics", "mlops"), ("nn", "train"), ("metrics", "ab"),
                  ("train", "cnn"), ("train", "seq"), ("train", "genm"), ("seq", "attn"), ("attn", "arch"), ("attn", "infer"), ("mlops", "infer"),
                  ("arch", "prompt"), ("infer", "sdrec"), ("prompt", "rag"), ("infer", "sdllm"), ("rag", "sdllm")],
        "useful": ["clf", "unsup", "ab", "genm", "arch", "prompt", "rag"],
    },
    {
        "id": "data-science", "name": "Data Science",
        "blurb": "Answer questions with data: statistics, classic ML, experiments and A/B tests.",
        "rows": [["la", "prob", "calc"], ["mlcore", "stats", "feat"], ["lin", "trees", "metrics", "info"], ["clf", "unsup", "ts", "ab"],
                 ["nn", "sdexp"], ["nlp", "sdrec"]],
        "edges": [("la", "mlcore"), ("calc", "mlcore"), ("prob", "stats"), ("stats", "info"), ("mlcore", "lin"), ("stats", "lin"), ("mlcore", "trees"),
                  ("feat", "trees"), ("stats", "metrics"), ("lin", "clf"), ("trees", "unsup"), ("metrics", "ts"), ("metrics", "ab"),
                  ("clf", "nn"), ("ab", "sdexp"), ("nn", "nlp"), ("ab", "sdrec")],
        "useful": ["calc", "info", "nn", "nlp", "sdrec"],
    },
]


def build_data(ordered, type_label):
    """Turn lessons into {topics, lessons, roles} for assets/roadmap-data.js. Fails loudly if the map and lessons disagree."""
    ai = [l for l in ordered if l["track"]["id"] == "ai-engineering"]
    starts = {spec[1]: tid for tid, (_, spec) in TOPICS.items() if spec[0] == "run"}
    run_of, current = {}, None
    for l in ai:
        current = starts.get(l["slug"], current)
        run_of[l["key"]] = current
    topics, used = {}, {}
    for tid, (name, spec) in TOPICS.items():
        kind = spec[0]
        if kind == "modules":
            ls = [l for l in ordered if l["track"]["id"] == "fundamentals" and l["module"]["name"] in spec[1]]
        elif kind == "run":
            ls = [l for l in ai if run_of[l["key"]] == tid]
        elif kind == "slugs":
            ls = [l for l in ordered if l["slug"] in spec[1]]
        else:
            # A whole track group, minus lessons another topic lists by name.
            named = {x for _, (_, sp) in TOPICS.items() if sp[0] == "slugs" for x in sp[1]}
            ls = [l for l in ordered if l["track"]["id"] == spec[1] and (spec[2] is None or l.get("group") == spec[2]) and l["slug"] not in named]
        if not ls:
            raise SystemExit(f"roadmap topic {tid} has no lessons")
        for l in ls:
            if l["key"] in used:
                raise SystemExit(f'{l["key"]} is in both {used[l["key"]]} and {tid}')
            used[l["key"]] = tid
        tracks = sorted({l["track"]["id"] for l in ls})
        topics[tid] = {"name": name, "track": tracks[0], "lessons": [l["key"] for l in ls]}
    for role in ROLES:
        ids = [t for row in role["rows"] for t in row]
        for a, b in role["edges"]:
            if a not in ids or b not in ids:
                raise SystemExit(f'{role["id"]}: edge {a}->{b} uses a topic not on the graph')
        for t in ids + role["useful"]:
            if t not in topics:
                raise SystemExit(f'{role["id"]}: unknown topic {t}')
    lessons = {l["key"]: [l["title"], l["url"], type_label[l["type"]], l.get("minutes") or 0] for l in ordered if l["key"] in used}
    roles = [{**r, "edges": [list(e) for e in r["edges"]]} for r in ROLES]
    return {"topics": topics, "lessons": lessons, "roles": roles}
