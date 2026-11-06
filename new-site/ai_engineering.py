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
        "continuous-batching": {"prereqs": [_a("kv-cache-and-pagedattention")]},
        "prefix-caching": {"prereqs": [_a("kv-cache-and-pagedattention")]},
        "speculative-decoding": {"prereqs": [_a("prefill-vs-decode")]},
        "serving-metrics-and-slos": {"prereqs": [_a("continuous-batching")]},
        "scaling-inference": {"prereqs": [_a("serving-metrics-and-slos"), _f("distributed-training")]},
        "sizing-and-cost": {"prereqs": [_a("scaling-inference")]},
        "llm-inference-practice": {"type": "interview", "prereqs": [_a("sizing-and-cost")]},
    })),
    ("Prompt engineering", "system-design/prompt-engineering", _part("Structuring prompts, getting reliable output and choosing the right tool.", {
        "prompt-engineering-patterns": {"prereqs": [_f("in-context-learning-and-cot")]},
        "structured-output": {"prereqs": [_a("prompt-engineering-patterns"), _f("decoding-and-sampling")]},
        "prompt-vs-rag-vs-fine-tuning": {"prereqs": [_a("prompt-engineering-patterns"), _f("lora-and-qlora")]},
    })),
    ("RAG", "system-design/rag", _part("Building retrieval-augmented generation, from basic pipelines to advanced retrieval, and how to evaluate it.", {
        "rag-end-to-end": {"prereqs": [_f("search-and-retrieval"), _f("embeddings")]},
        "advanced-rag": {"prereqs": [_a("rag-end-to-end")]},
        "evaluating-llm-apps": {"prereqs": [_a("rag-end-to-end"), _f("llm-as-a-judge")]},
        "rag-wrong-answer": {"type": "interview", "prereqs": [_a("rag-end-to-end")]},
        "rag-at-scale": {"type": "interview", "prereqs": [_a("rag-end-to-end"), _a("advanced-rag")]},
    })),
    ("Agentic AI", "system-design/agentic-ai", _part("The agent loop, tools, planning, memory, MCP, multi-agent systems, infrastructure, evaluation and safety.", {
        "what-is-an-agent": {"prereqs": [_a("prompt-engineering-patterns")]},
        "tool-calling": {"prereqs": [_a("what-is-an-agent"), _a("structured-output")]},
        "planning-and-reflection": {"prereqs": [_a("what-is-an-agent")]},
        "memory-and-context-engineering": {"prereqs": [_a("what-is-an-agent")]},
        "model-context-protocol": {"prereqs": [_a("tool-calling")]},
        "multi-agent-systems": {"prereqs": [_a("what-is-an-agent")]},
        "agent-infrastructure": {"prereqs": [_a("what-is-an-agent")]},
        "evaluating-agents": {"prereqs": [_a("what-is-an-agent")]},
        "agent-safety": {"prereqs": [_a("tool-calling")]},
        "agentic-ai-practice": {"type": "interview", "prereqs": [_a("agent-safety")]},
        "agent-scenarios-set-1": {"type": "interview", "prereqs": [_a("agentic-ai-practice")]},
    })),
    ("MLOps", "system-design/mlops", _part("Skew, serving modes, deployment, reproducibility, drift and retraining.", {
        "training-serving-skew-and-feature-stores": {"prereqs": [_f("cross-validation-and-leakage")]},
        "batch-vs-online-inference": {},
        "deployment-patterns": {"prereqs": [_a("batch-vs-online-inference")]},
        "experiment-tracking-and-model-registry": {},
        "drift-detection-and-monitoring": {"prereqs": [_a("training-serving-skew-and-feature-stores")]},
        "retraining-pipelines": {"prereqs": [_a("drift-detection-and-monitoring"), _a("deployment-patterns")]},
        "mlops-practice": {"type": "interview", "prereqs": [_a("retraining-pipelines")]},
    })),
    ("LLMOps", "system-design/llmops", _part("Versioned configurations and release gates, guardrails, cost and latency.", {
        "llmops": {"prereqs": [_a("deployment-patterns"), _a("evaluating-llm-apps")]},
        "guardrails-and-prompt-injection": {"prereqs": [_a("llmops")]},
        "cost-and-latency": {"prereqs": [_a("llmops"), _a("prefix-caching")]},
        "genai-scenarios-set-1": {"type": "interview", "prereqs": [_a("cost-and-latency")]},
    })),
]
for _p in PARTS:
    for _l in _p[2].LESSONS.values():
        _l.setdefault("prereqs", [])

# New designs go in this group.
DESIGNS = SimpleNamespace(
    GROUPS=[("designs", "Designs", "End-to-end AI/ML system designs in interview format. New designs are added over time."),
            ("ab-designs", "A/B Testing", "Experiment design scenarios based on documented real-world cases.")],
    LESSONS={
        "design-refund-agent": {"type": "design", "prereqs": [_a("what-is-an-agent"), _a("agent-safety")]},
        "design-support-chatbot": {"type": "design", "prereqs": [_a("rag-end-to-end"), _a("guardrails-and-prompt-injection")]},
        "design-store-assistant": {"type": "design", "prereqs": [_a("what-is-an-agent"), _a("tool-calling")]},
        "design-research-agent": {"type": "design", "prereqs": [_a("multi-agent-systems"), _a("agent-infrastructure")]},
        "design-text-to-sql": {"type": "design", "prereqs": [_a("rag-end-to-end"), _a("advanced-rag")]},
        "design-code-autocomplete": {"type": "design", "prereqs": [_a("continuous-batching"), _a("scaling-inference")]},
        "design-llm-platform": {"type": "design", "prereqs": [_a("llmops"), _a("guardrails-and-prompt-injection")]},
        "design-llm-prompt-test": {"type": "design", "prereqs": [_f("sample-size-and-power"), _f("llm-as-a-judge")]},
        "design-ai-subject-lines": {"type": "design", "prereqs": [_f("reading-ab-results"), _a("prompt-engineering-patterns")]},
        "design-interleaving": {"type": "design", "prereqs": [_f("sample-size-and-power"), _f("ranking-metrics")]},
        "design-network-experiment": {"type": "design", "prereqs": [_f("interference-in-experiments")]},
        "design-image-personalisation": {"type": "design", "prereqs": [_f("bandits-vs-ab-tests")]},
        "design-launch-decision-rule": {"type": "design", "prereqs": [_f("choosing-ab-metrics"), _f("multiple-testing")]},
    },
)
