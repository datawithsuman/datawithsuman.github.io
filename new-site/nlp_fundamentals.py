# The NLP part of the Fundamentals track. Lesson text comes from the live pages (see ml_import.py).
# Each lesson here adds what to read first. Interview questions live in the lesson's plan once it's converted.

GROUPS = [
    ("text-basics", "Text basics", "Preprocessing, bag-of-words, TF-IDF and text classification."),
    ("lm-tokens", "Language models and tokenisation", "N-gram models, perplexity and subword tokenisers."),
    ("tasks-eval", "Tagging, retrieval and evaluation", "Named entities, search and how to score generated text."),
]

LESSONS = {
    "text-preprocessing": {},
    "bag-of-words-and-tf-idf": {"prereqs": ["text-preprocessing", "vectors-and-cosine-similarity"]},
    "text-classification": {"prereqs": ["bag-of-words-and-tf-idf", "naive-bayes", "logistic-regression"]},
    "n-gram-language-models": {"prereqs": ["probability-and-bayes", "entropy-cross-entropy-kl"]},
    "subword-tokenisation": {"prereqs": ["bag-of-words-and-tf-idf"]},
    "sequence-labelling-and-ner": {"prereqs": ["text-classification"]},
    "search-and-retrieval": {"prereqs": ["bag-of-words-and-tf-idf", "embeddings"], "related": ["ai-engineering/rag-end-to-end"]},
    "nlp-evaluation-metrics": {"prereqs": ["text-classification"]},
    "nlp-practice": {"type": "interview", "prereqs": ["search-and-retrieval", "nlp-evaluation-metrics"]},
}
for _l in LESSONS.values():
    _l["prereqs"] = [f"fundamentals/{p}" for p in _l.get("prereqs", [])]
