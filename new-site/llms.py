# The LLMs part of the Fundamentals track. Lesson text comes from the live pages (see ml_import.py).
# Each lesson here adds what to read first. Interview questions live in the lesson's plan once it's converted.

GROUPS = [
    ("architecture", "Modern architecture", "What modern LLMs changed: RMSNorm, SwiGLU, GQA, MLA, FlashAttention, long context and MoE."),
    ("pretraining", "Pretraining", "Next-token prediction, data pipelines, scaling laws, distributed training and stability."),
    ("post-training", "Post-training", "SFT, RLHF and reward models, DPO, reasoning models, distillation and LoRA."),
    ("generation", "Generation", "Decoding and sampling, prompting and chain-of-thought, and hallucination."),
    ("llm-eval", "Evaluating LLMs and practice", "Benchmarks, contamination, LLM-as-a-judge and two practice sets."),
]

LESSONS = {
    "modern-llm-architecture": {"prereqs": ["transformer-end-to-end"]},
    "attention-variants-mqa-gqa-mla": {"prereqs": ["modern-llm-architecture", "multi-head-attention"]},
    "flashattention": {"prereqs": ["self-attention"]},
    "long-context": {"prereqs": ["positional-encodings", "attention-variants-mqa-gqa-mla"]},
    "mixture-of-experts": {"prereqs": ["modern-llm-architecture"]},
    "next-token-prediction": {"prereqs": ["n-gram-language-models", "transformer-end-to-end"]},
    "pretraining-data": {"prereqs": ["next-token-prediction"]},
    "scaling-laws": {"prereqs": ["next-token-prediction"]},
    "distributed-training": {"prereqs": ["modern-llm-architecture"]},
    "training-instabilities": {"prereqs": ["next-token-prediction", "normalisation-layers"]},
    "supervised-fine-tuning": {"prereqs": ["next-token-prediction"]},
    "rlhf-and-reward-models": {"prereqs": ["supervised-fine-tuning"]},
    "dpo": {"prereqs": ["rlhf-and-reward-models"]},
    "reasoning-models-grpo": {"prereqs": ["rlhf-and-reward-models"]},
    "distillation": {"prereqs": ["supervised-fine-tuning"]},
    "lora-and-qlora": {"prereqs": ["supervised-fine-tuning"]},
    "decoding-and-sampling": {"prereqs": ["next-token-prediction"]},
    "in-context-learning-and-cot": {"prereqs": ["decoding-and-sampling"]},
    "hallucination": {"prereqs": ["in-context-learning-and-cot"]},
    "benchmarks-and-contamination": {"prereqs": ["pretraining-data"]},
    "llm-as-a-judge": {"prereqs": ["benchmarks-and-contamination"]},
    "llm-practice-scaling": {"type": "interview", "prereqs": ["distributed-training", "mixture-of-experts"]},
    "llm-practice-post-training": {"type": "interview", "prereqs": ["lora-and-qlora", "llm-as-a-judge"]},
}
for _l in LESSONS.values():
    _l["prereqs"] = [f"fundamentals/{p}" for p in _l.get("prereqs", [])]
