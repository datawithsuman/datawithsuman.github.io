# The NLP part of the Fundamentals track. Lesson text comes from the live pages (see ml_import.py).
# Each lesson here adds what to read first. Interview questions live in the lesson's plan once it's converted.

GROUPS = [
    ("text-basics", "Text basics", "Preprocessing, bag-of-words, TF-IDF, text classification and topic modelling."),
    ("lm-tokens", "Language models and tokenisation", "N-gram models, perplexity, edit distance and subword tokenisers."),
    ("tasks-eval", "Tagging, retrieval and evaluation", "Named entities, sequence models, BERT, information extraction, search and scoring generated text."),
]

LESSONS = {
    "text-preprocessing": {},
    "bag-of-words-and-tf-idf": {"prereqs": ["text-preprocessing", "vectors-and-cosine-similarity"]},
    "text-classification": {"prereqs": ["bag-of-words-and-tf-idf", "naive-bayes", "logistic-regression"]},
    "topic-modelling": {"prereqs": ["bag-of-words-and-tf-idf"]},
    "n-gram-language-models": {"prereqs": ["probability-and-bayes", "entropy-cross-entropy-kl"]},
    "edit-distance-and-spelling-correction": {"prereqs": ["n-gram-language-models"]},
    "subword-tokenisation": {"prereqs": ["bag-of-words-and-tf-idf"]},
    "sequence-labelling-and-ner": {"prereqs": ["text-classification"]},
    "hmms-crfs-and-viterbi": {"prereqs": ["sequence-labelling-and-ner"]},
    "bert-and-masked-language-models": {"prereqs": ["sequence-labelling-and-ner", "encoder-decoder-architectures"]},
    "information-extraction": {"prereqs": ["sequence-labelling-and-ner", "bert-and-masked-language-models"]},
    "search-and-retrieval": {"prereqs": ["bag-of-words-and-tf-idf", "embeddings"], "related": ["ai-engineering/rag-end-to-end"]},
    "nlp-evaluation-metrics": {"prereqs": ["text-classification"]},
    "nlp-practice": {"type": "interview", "prereqs": ["search-and-retrieval", "nlp-evaluation-metrics"]},
}
for _l in LESSONS.values():
    _l["prereqs"] = [f"fundamentals/{p}" for p in _l.get("prereqs", [])]
