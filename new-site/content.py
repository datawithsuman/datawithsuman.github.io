# Seed content for the design preview. Lessons without a "body" render as placeholder pages.
# Minutes are placeholders until the real lessons move in.

TRACKS = [
    {
        "id": "fundamentals", "n": "01", "name": "Fundamentals", "status": "Start here",
        "desc": "The core ideas behind every model, from maths and regression to neural nets.",
        "topics": ["Vectors, gradients and probability", "A/B testing", "Linear and logistic regression", "Trees and boosting", "Neural nets and backprop"],
        "know": [],
        # build.py adds the Maths for ML, A/B Testing, Classical ML, Deep Learning, NLP and LLMs modules.
        "modules": [
        ],
    },
    {
        "id": "ai-engineering", "n": "02", "name": "AI Engineering", "status": "Needs Fundamentals",
        "desc": "How LLM applications are served, built and run, from inference to retrieval and agents.",
        "topics": ["LLM inference and serving", "Prompts and RAG", "Agents and tool use", "MLOps and LLMOps"],
        "know": ["fundamentals/logistic-regression", "fundamentals/backpropagation"],
        # build.py adds the modules.
        "modules": [
        ],
    },
    {
        "id": "system-design", "n": "03", "name": "System Design", "status": "Can run in parallel",
        "desc": "How AI and ML systems are designed, from requirements to rollout.",
        "topics": ["Design a support chatbot", "Design a research agent", "Design code autocomplete", "Design a shared LLM platform", "A/B testing design scenarios"],
        "know": ["fundamentals/gradient-boosting"],
        "modules": [
            {"part": "Recommendation Systems", "name": "Designs", "desc": "Find a few good items for each user from a very large catalogue.", "lessons": [
                {"slug": "recommendation-system", "title": "Design a recommendation system", "type": "design", "minutes": 10,
                 "lead": "How do you pick a few items for a user from millions?",
                 "prereqs": ["fundamentals/gradient-boosting", "fundamentals/embeddings"],
                 "body": "recsys"},
            ]},
        ],
    },
    {
        "id": "papers", "n": "04", "name": "Papers", "status": "Any time",
        "desc": "Important papers taught step by step: the gist, the method, the results and why they matter.",
        "topics": ["Attention Is All You Need", "Harness Engineering", "Context Language Models"],
        "know": ["fundamentals/self-attention"],
        "modules": [
            {"name": "Models", "desc": "The architecture behind modern LLMs.", "lessons": [
                {"slug": "attention-is-all-you-need", "title": "Attention Is All You Need", "type": "paper", "minutes": 8,
                 "lead": "What happens if you remove recurrence and keep only attention?",
                 "prereqs": ["fundamentals/self-attention"],
                 "related": ["fundamentals/multi-head-attention"], "body": "aiayn"},
            ]},
            {"name": "Agents and memory", "desc": "How AI agents are built, and how they manage context.", "lessons": [
                {"slug": "harness-engineering", "title": "Harness Engineering", "type": "paper", "minutes": 25, "imported": True,
                 "lead": "What is actually inside a coding agent?",
                 "prereqs": ["ai-engineering/what-is-an-agent"], "related": ["papers/context-language-models"]},
                {"slug": "context-language-models", "title": "Context Language Models", "type": "paper", "minutes": 8, "imported": True,
                 "lead": "What if an AI agent could edit its own memory?",
                 "prereqs": ["papers/harness-engineering"], "related": ["papers/harness-engineering"]},
            ]},
        ],
    },
]

TOKENS = ["The", "cat", "chased", "its", "tail"]
# Hand-written and illustrative: each row adds up to 100.
WEIGHTS = [
    [30, 50, 8, 4, 8],
    [14, 52, 20, 6, 8],
    [4, 38, 34, 6, 18],
    [4, 58, 8, 18, 12],
    [3, 22, 10, 35, 30],
]

ATTENTION_CODE = """import numpy as np

def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)

def attention(Q, K, V):
    d = K.shape[-1]
    scores = Q @ K.T / np.sqrt(d)   # how well each query matches each key
    weights = softmax(scores)       # each row adds up to 1
    return weights @ V              # mix the values"""

TOOL_CODE = """def run_agent(task, tools, max_steps=5):
    messages = [user_message(task)]

    for _ in range(max_steps):
        reply = model(messages, tools)
        messages.append(reply)

        if not reply.tool_calls:
            return reply.text           # the model has finished

        for call in reply.tool_calls:
            result = tools[call.name](**call.args)   # your code runs it
            messages.append(tool_result(call.id, result))

    raise RuntimeError("Stopped after too many steps")"""

BODIES = {
    "attention": {
        "idea": "Think of reading as asking questions. When the model reaches the word 'its', it asks: which earlier word am I talking about? Attention is the scoring of every other word against that question, then mixing the best matches together.",
        "layers": [
            {"name": "Intuition", "sections": [{"id": "try-it", "title": "Try it: click a word", "widget": "attention"}]},
            {"name": "Maths", "sections": [{"id": "maths", "title": "The formula", "html": """
<div class="mono-box">Attention(Q, K, V) = softmax( Q·Kᵀ / √d ) · V</div>
<ul class="explain">
  <li><code>Q·Kᵀ</code> scores every query against every key. A higher score means a better match.</li>
  <li><code>/√d</code> stops the scores growing with the vector size d.</li>
  <li><code>softmax</code> turns each row of scores into weights that add up to 1.</li>
  <li><code>·V</code> mixes the values using those weights.</li>
</ul>"""}]},
        ],
        "interview": [("Why do we divide by √d in attention?",
                       "Dot products grow with the vector size. Large scores push softmax towards one-hot, where gradients almost vanish. Dividing by √d keeps the variance near 1.")],
    },
    "recsys": {
        "idea": "You cannot score every item for every user. So you narrow in stages: a cheap step finds a few hundred candidates, then a slower, smarter step ranks only those. Each stage trades accuracy for speed.",
        "layers": [
            {"name": "Intuition", "sections": []},
            {"name": "Architecture", "sections": [
                {"id": "architecture", "title": "Four stages", "html": """
<ol class="stages">
  <li><span class="mono-num">1</span><b>Request</b><span>User, context</span></li>
  <li><span class="mono-num">2</span><b>Candidate generation</b><span>Fast, high recall</span></li>
  <li><span class="mono-num">3</span><b>Ranking model</b><span>Slow, high precision</span></li>
  <li><span class="mono-num">4</span><b>Re-rank and filter</b><span>Business rules, diversity</span></li>
</ol>
<div class="dashed">Underneath all stages: a feature store for fresh user and item features, and an event log that feeds training.</div>"""},
                {"id": "trade-offs", "title": "Trade-offs to name in the interview", "html": """
<ul class="explain">
  <li>Candidate count vs latency.</li>
  <li>Feature freshness vs serving cost.</li>
  <li>Two-tower for retrieval vs cross-feature model for ranking.</li>
</ul>"""},
            ]},
            {"name": "Numbers", "sections": [{"id": "numbers", "title": "Capacity maths", "html": """
<div class="mono-box">requests per second ≈ [daily users] × [requests per user] ÷ 86,400
peak requests per second ≈ [requests per second] × [peak factor]
ranking scores per second ≈ [peak requests per second] × [candidates per request]
ranking servers ≈ [ranking scores per second] ÷ [scores per server per second]</div>
<p class="note">Fill in the brackets with numbers from your interviewer or your own stated assumptions.</p>"""}]},
        ],
        "interview": [("Why not rank every item with the best model?",
                       "Cost grows with the catalogue size times the model cost per item. A cheap first stage cuts the catalogue to a few hundred, so the expensive model only runs where it can change the answer.")],
    },
    "tool_use": {
        "idea": "A model can only write text. To use a tool, it writes a request naming the tool and its inputs. Your code runs the tool and hands back the result. The model reads it and decides what to do next. That loop is the whole idea.",
        "layers": [
            {"name": "Intuition", "sections": [{"id": "the-loop", "title": "The loop", "html": """
<ol class="stages">
  <li><span class="mono-num">1</span><b>Model asks</b><span>Tool name and inputs</span></li>
  <li><span class="mono-num">2</span><b>Your code runs it</b><span>Checks, then calls the tool</span></li>
  <li><span class="mono-num">3</span><b>Result goes back</b><span>Added to the conversation</span></li>
  <li><span class="mono-num">4</span><b>Model decides</b><span>Ask again, or answer</span></li>
</ol>"""}]},
        ],
        "interview": [("Who actually runs the tool?",
                       "Your code does. The model only writes a request with a tool name and inputs. That is why you validate the inputs, check permissions, and cap the number of steps.")],
    },
    "aiayn": {
        "idea": "Recurrent models read a sentence one word at a time, which makes them slow to train and weak over long distances. This 2017 paper removed recurrence and built a translation model from attention alone.",
        "layers": [
            {"name": "Gist", "sections": [{"id": "gist", "title": "The claim", "html": """
<p>Attention is enough on its own. Every position can look at every other position in a single step, and all positions can be computed at once.</p>"""}]},
            {"name": "Method", "sections": [{"id": "method", "title": "What they built", "html": """
<ul class="explain">
  <li>An encoder and a decoder, each a stack of 6 identical layers.</li>
  <li>Multi-head attention with 8 heads and a model size of 512.</li>
  <li>A feed-forward layer applied to each position on its own.</li>
  <li>Sine and cosine position signals, since attention alone ignores word order.</li>
</ul>"""}]},
            {"name": "Why it matters", "sections": [{"id": "why-it-matters", "title": "Why it matters", "html": """
<p>Training could now run in parallel across a sequence, and distant words were one step apart. This architecture became the base of modern LLMs.</p>
<p class="note">Source: <a href="https://arxiv.org/abs/1706.03762">Vaswani et al., 2017</a>.</p>"""}]},
        ],
        "interview": [("What did the Transformer replace, and what did it gain?",
                       "It replaced recurrence with attention. It gained parallel training across a sequence and a direct path between any two positions. The cost is that word order has to be added separately, and attention grows with the square of the sequence length.")],
    },
    "interview_round": {
        "idea": None,
        "layers": [],
        "interview": [
            ("Why does a transformer need positional information?",
             "Self-attention treats its input as a set. Shuffling the tokens only shuffles the outputs, so order has to be added, using sine and cosine signals or learned embeddings."),
            ("Why use several attention heads instead of one big one?",
             "Each head has its own projections, so it can learn a different kind of relationship. The model size is split across the heads, so the total cost stays about the same as one head."),
            ("What does the feed-forward layer add?",
             "Attention output is a weighted sum of value vectors. The feed-forward layer adds a non-linear step, applied to each position on its own."),
            ("Why is the decoder masked?",
             "During training the decoder has the whole target sequence available. The mask stops each position looking at later tokens, so it learns from the same information it will have at generation time."),
        ],
    },
}
