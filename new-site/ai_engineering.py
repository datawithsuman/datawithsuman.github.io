# The AI Engineering track. Lesson text comes from the live pages (see ml_import.py).
# Each lesson here adds what to read first. Interview questions live in the lesson's plan once it's converted.
from types import SimpleNamespace


def _f(name):
    return f"fundamentals/{name}"


def _a(name):
    return f"ai-engineering/{name}"


def _part(lessons_desc, lessons):
    groups = [("lessons", "Lessons", lessons_desc), ("scenarios", "Scenarios", "Practice questions and real-world incidents to diagnose. New ones are added over time.")]
    return SimpleNamespace(GROUPS=groups, LESSONS=lessons)


PARTS = [
    ("LLM inference and serving", "system-design/llm-inference", _part("How LLMs run fast and cheap: memory, batching, caching, decoding and scale.", {
        "prefill-vs-decode": {"prereqs": [_f("attention-variants-mqa-gqa-mla")]},
        "llm-quantization": {"prereqs": [_a("prefill-vs-decode")]},
        "kv-cache-and-pagedattention": {"prereqs": [_a("prefill-vs-decode")]},
        "kv-cache-compression": {"prereqs": [_a("kv-cache-and-pagedattention")]},
        "continuous-batching": {"prereqs": [_a("kv-cache-and-pagedattention")]},
        "prefix-caching": {"prereqs": [_a("kv-cache-and-pagedattention")]},
        "speculative-decoding": {"prereqs": [_a("prefill-vs-decode")]},
        "serving-metrics-and-slos": {"prereqs": [_a("continuous-batching")]},
        "scaling-inference": {"prereqs": [_a("serving-metrics-and-slos"), _f("distributed-training")]},
        "serving-moe-models": {"prereqs": [_a("scaling-inference"), _f("mixture-of-experts")]},
        "serving-agents-and-reasoning-models": {"prereqs": [_a("prefix-caching"), _a("kv-cache-compression")]},
        "sizing-and-cost": {"prereqs": [_a("scaling-inference")]},
        "llm-inference-practice": {"type": "interview", "prereqs": [_a("sizing-and-cost")]},
    })),
    ("Prompt engineering", "system-design/prompt-engineering", _part("Structuring prompts, getting reliable output and choosing the right tool.", {
        "prompt-engineering-patterns": {"prereqs": [_f("in-context-learning-and-cot")]},
        "prompting-reasoning-models": {"prereqs": [_a("prompt-engineering-patterns"), _f("reasoning-models-grpo")]},
        "structured-output": {"prereqs": [_a("prompt-engineering-patterns"), _f("decoding-and-sampling")]},
        "system-prompts-with-many-rules": {"prereqs": [_a("prompt-engineering-patterns"), _a("guardrails-and-prompt-injection")]},
        "automatic-prompt-optimization": {"prereqs": [_a("prompt-engineering-patterns"), _a("evaluating-llm-apps")]},
        "prompt-vs-rag-vs-fine-tuning": {"prereqs": [_a("prompt-engineering-patterns"), _f("lora-and-qlora")]},
        "prompt-change-broke-production": {"prereqs": [_a("prompt-engineering-patterns"), _f("llm-as-a-judge")]},
        "prompt-engineering-practice": {"type": "interview", "prereqs": [_a("prompt-change-broke-production")]},
    })),
    ("RAG", "system-design/rag", _part("Building retrieval-augmented generation: parsing, indexes, ranking, grounded answers, agents, security, upkeep and evaluation.", {
        "rag-end-to-end": {"prereqs": [_f("search-and-retrieval"), _f("embeddings")]},
        "parsing-and-chunking": {"prereqs": [_a("rag-end-to-end")]},
        "embeddings-and-vector-indexes": {"prereqs": [_a("rag-end-to-end"), _f("embeddings")]},
        "advanced-rag": {"prereqs": [_a("rag-end-to-end")]},
        "reranking-and-late-interaction": {"prereqs": [_a("advanced-rag")]},
        "grounded-answers": {"prereqs": [_a("rag-end-to-end")]},
        "agentic-rag": {"prereqs": [_a("advanced-rag"), _a("what-is-an-agent")]},
        "permissions-and-poisoning": {"prereqs": [_a("rag-end-to-end"), _a("guardrails-and-prompt-injection")]},
        "keeping-an-index-current": {"prereqs": [_a("embeddings-and-vector-indexes")]},
        "evaluating-llm-apps": {"prereqs": [_a("rag-end-to-end"), _f("llm-as-a-judge")]},
        "rag-wrong-answer": {"type": "interview", "prereqs": [_a("rag-end-to-end")]},
        "rag-at-scale": {"type": "interview", "prereqs": [_a("rag-end-to-end"), _a("advanced-rag")]},
        "rag-practice": {"type": "interview", "prereqs": [_a("reranking-and-late-interaction"), _a("evaluating-llm-apps")]},
    })),
    ("Agentic AI", "system-design/agentic-ai", _part("The agent loop, tools, planning, memory and skills, MCP and other protocols, multi-agent systems, frameworks, long-running agents, evaluation and safety.", {
        "what-is-an-agent": {"prereqs": [_a("prompt-engineering-patterns")]},
        "tool-calling": {"prereqs": [_a("what-is-an-agent"), _a("structured-output")]},
        "planning-and-reflection": {"prereqs": [_a("what-is-an-agent")]},
        "memory-and-context-engineering": {"prereqs": [_a("what-is-an-agent")]},
        "agent-skills-and-self-improving-context": {"prereqs": [_a("memory-and-context-engineering")]},
        "model-context-protocol": {"prereqs": [_a("tool-calling")]},
        "mcp-under-the-hood": {"prereqs": [_a("model-context-protocol")]},
        "agent-protocols": {"prereqs": [_a("model-context-protocol")]},
        "multi-agent-systems": {"prereqs": [_a("what-is-an-agent")]},
        "agent-infrastructure": {"prereqs": [_a("what-is-an-agent")]},
        "agent-frameworks-and-harnesses": {"prereqs": [_a("agent-infrastructure")]},
        "long-running-and-scheduled-agents": {"prereqs": [_a("agent-frameworks-and-harnesses"), _a("multi-agent-systems")]},
        "evaluating-agents": {"prereqs": [_a("what-is-an-agent")]},
        "agent-and-tool-evaluation-metrics": {"prereqs": [_a("evaluating-agents"), _a("tool-calling")]},
        "agent-safety": {"prereqs": [_a("tool-calling")]},
        "human-in-the-loop-design": {"prereqs": [_a("agent-safety"), _a("agent-frameworks-and-harnesses")]},
        "agentic-ai-practice": {"type": "interview", "prereqs": [_a("agent-safety")]},
        "agent-scenarios-context-and-memory": {"type": "interview", "prereqs": [_a("memory-and-context-engineering")]},
        "agent-scenarios-tools-and-mcp": {"type": "interview", "prereqs": [_a("tool-calling"), _a("mcp-under-the-hood")]},
        "agent-scenarios-planning-and-reliability": {"type": "interview", "prereqs": [_a("planning-and-reflection"), _a("agent-infrastructure")]},
        "agent-scenarios-multi-agent-and-protocols": {"type": "interview", "prereqs": [_a("multi-agent-systems"), _a("agent-protocols")]},
        "agent-scenarios-observability": {"type": "interview", "prereqs": [_a("agent-infrastructure")]},
        "agent-scenarios-evaluation": {"type": "interview", "prereqs": [_a("evaluating-agents"), _a("agent-and-tool-evaluation-metrics")]},
        "agent-scenarios-safety-and-security": {"type": "interview", "prereqs": [_a("agent-safety")]},
        "agent-scenarios-cost-and-latency": {"type": "interview", "prereqs": [_a("agent-infrastructure")]},
        "agent-scenarios-human-in-the-loop": {"type": "interview", "prereqs": [_a("human-in-the-loop-design")]},
        "agent-scenarios-long-running": {"type": "interview", "prereqs": [_a("long-running-and-scheduled-agents")]},
    })),
    ("MLOps", "system-design/mlops", _part("Skew, serving modes, deployment, reproducibility, drift and retraining.", {
        "training-serving-skew-and-feature-stores": {"prereqs": [_f("cross-validation-and-leakage")]},
        "batch-vs-online-inference": {},
        "deployment-patterns": {"prereqs": [_a("batch-vs-online-inference")]},
        "experiment-tracking-and-model-registry": {},
        "drift-detection-and-monitoring": {"prereqs": [_a("training-serving-skew-and-feature-stores")]},
        "monitoring-without-labels": {"prereqs": [_a("drift-detection-and-monitoring")]},
        "retraining-pipelines": {"prereqs": [_a("drift-detection-and-monitoring"), _a("deployment-patterns")]},
        "feedback-loops-and-unbiased-data": {"prereqs": [_a("retraining-pipelines"), _f("bandits-vs-ab-tests")]},
        "mlops-practice": {"type": "interview", "prereqs": [_a("retraining-pipelines")]},
    })),
    ("LLMOps", "system-design/llmops", _part("Versioned configurations and release gates, guardrails, cost and latency.", {
        "llmops": {"prereqs": [_a("deployment-patterns"), _a("evaluating-llm-apps")]},
        "tracing-and-observability": {"prereqs": [_a("llmops")]},
        "model-upgrades-and-retirements": {"prereqs": [_a("llmops")]},
        "guardrails-and-prompt-injection": {"prereqs": [_a("llmops")]},
        "cost-and-latency": {"prereqs": [_a("llmops"), _a("prefix-caching")]},
        "llm-api-reliability": {"prereqs": [_a("cost-and-latency")]},
        "genai-scenarios-set-1": {"type": "interview", "prereqs": [_a("cost-and-latency")]},
    })),
]
for _p in PARTS:
    for _l in _p[2].LESSONS.values():
        _l.setdefault("prereqs", [])

# System Design sub-sections (8 Nov 2026). Each holds its designs, and later its scenarios.
# New designs go in the matching sub-section.
def _sd(lessons, group="designs", desc="End-to-end system designs in interview format. New designs are added over time."):
    return SimpleNamespace(GROUPS=[(group, "Designs", desc)], LESSONS=lessons)


SD_PARTS = [
    ("LLM Apps and Chatbots", _sd({"design-support-chatbot": {"type": "design", "prereqs": [_a("rag-end-to-end"), _a("guardrails-and-prompt-injection")]}, "design-store-assistant": {"type": "design", "prereqs": [_a("what-is-an-agent"), _a("tool-calling")]}, "design-voice-agent": {"type": "design", "prereqs": [_a("tool-calling"), _a("serving-metrics-and-slos")]}, "design-ai-tutor": {"type": "design", "prereqs": [_a("prompt-engineering-patterns"), _a("evaluating-llm-apps")]}}, desc="Assistants that answer from your content, act through tools and know when to hand over to a person.")),
    ("RAG and Search", _sd({"design-enterprise-rag": {"type": "design", "prereqs": [_a("permissions-and-poisoning"), _a("advanced-rag")]}, "design-text-to-sql": {"type": "design", "prereqs": [_a("rag-end-to-end"), _a("advanced-rag")]}, "design-semantic-search": {"type": "design", "prereqs": [_a("embeddings-and-vector-indexes"), _a("advanced-rag")]}}, desc="Systems that find the right documents or data and answer questions from them, at company scale.")),
    ("Document AI", _sd({"design-document-extraction": {"type": "design", "prereqs": [_a("parsing-and-chunking"), _a("structured-output")]}, "design-vision-llm": {"type": "design", "prereqs": [_f("vision-language-models"), _f("lora-and-qlora")]}}, desc="Turning invoices, forms and other documents into reliable structured data, with people checking what the model isn't sure about.")),
    ("Trust and Safety", _sd({"design-content-moderation": {"type": "design", "prereqs": [_a("guardrails-and-prompt-injection"), _f("classification-metrics")]}}, desc="Keeping platforms safe at huge scale: fast classifiers, clear policies, and people for the hard calls.")),
    ("Agents", _sd({"design-refund-agent": {"type": "design", "prereqs": [_a("what-is-an-agent"), _a("agent-safety")]}, "design-research-agent": {"type": "design", "prereqs": [_a("multi-agent-systems"), _a("agent-infrastructure")]}}, desc="Agents that plan, use tools and take actions, with safety limits and hand-offs built in.")),
    ("Recommendation Systems", None),  # its existing design lives in content.py
    ("Fraud and Risk", _sd({"design-fraud-detection": {"type": "design", "prereqs": [_f("class-imbalance"), _f("thresholds-and-costs")]}}, desc="Catching fraud in milliseconds while keeping good customers moving, with labels that arrive weeks late.")),
    ("Feeds and Ranking", _sd({"design-feed-ranking": {"type": "design", "prereqs": [_f("ranking-metrics"), _a("embeddings-and-vector-indexes")]}}, desc="Choosing what each person sees from billions of posts, fast, without rewarding clickbait.")),
    ("Developer Tools", _sd({"design-code-autocomplete": {"type": "design", "prereqs": [_a("continuous-batching"), _a("scaling-inference")]}, "design-coding-agent": {"type": "design", "prereqs": [_a("what-is-an-agent"), _a("agent-safety")]}}, desc="AI for writing and reviewing code, where speed and accuracy both matter.")),
    ("ML and LLM Platforms", _sd({"design-llm-platform": {"type": "design", "prereqs": [_a("llmops"), _a("guardrails-and-prompt-injection")]}, "design-llm-eval-platform": {"type": "design", "prereqs": [_a("evaluating-llm-apps"), _a("llmops")]}}, desc="Shared infrastructure that lets many teams use models safely, cheaply and consistently.")),
    ("Experimentation", _sd({"design-llm-prompt-test": {"type": "design", "prereqs": [_f("sample-size-and-power"), _f("llm-as-a-judge")]}, "design-ai-subject-lines": {"type": "design", "prereqs": [_f("reading-ab-results"), _a("prompt-engineering-patterns")]}, "design-interleaving": {"type": "design", "prereqs": [_f("sample-size-and-power"), _f("ranking-metrics")]}, "design-network-experiment": {"type": "design", "prereqs": [_f("interference-in-experiments")]}, "design-image-personalisation": {"type": "design", "prereqs": [_f("bandits-vs-ab-tests")]}, "design-launch-decision-rule": {"type": "design", "prereqs": [_f("choosing-ab-metrics"), _f("multiple-testing")]}, "design-experimentation-platform": {"type": "design", "prereqs": [_f("running-many-tests-at-once"), _f("sample-ratio-mismatch")]}}, "ab-designs", "Testing AI and ranking changes with experiments, based on documented real-world cases.")),
]
