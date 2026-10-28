// The single map of the site: sections → tracks → (optional groups) → lessons, in order.
// Home, section pages, track pages, breadcrumbs and Previous / Next are all built from this.
// A track lives at <dir>/, its lessons at <dir>/<slug>/. Empty tracks and empty groups stay hidden.
// Addresses use slugs (never numbers), so shared links keep working when lessons are reordered.
window.LESSONS = {
  sections: [
    { id: "fundamentals", title: "Fundamentals", desc: "The core ideas behind every model: classic ML, deep learning and LLMs.", tracks: [
      { id: "machine-learning", dir: "fundamentals/machine-learning", title: "Machine Learning", desc: "Classic ML that every AI/ML interview still asks about: models, metrics and core concepts.",
        groups: [
          {id: "linear-models",title: "Linear Models",desc: "Weighted sums of features: regression, regularization and classification."},
          {id: "tree-models",title: "Tree-Based Models",desc: "Splits, ensembles and boosting: the workhorses of tabular data."},
          {id: "classic-classifiers",title: "Other Classic Classifiers",desc: "Margins, neighbours and probabilities."},
          {id: "unsupervised",title: "Unsupervised Learning",desc: "Finding structure without labels."},
          {id: "metrics",title: "Evaluation Metrics",desc: "Which number to trust, and when: scenario by scenario."},
          {id: "core-concepts",title: "Core Concepts",desc: "The ideas behind every model: generalization, evaluation and validation."},
        ],
        lessons: [
          {slug: "linear-regression",group: "linear-models",title: "Linear Regression",sub: "What does least squares actually minimise, and when does it break?",level: "Beginner",mins: 30},
          {slug: "regularized-linear-models",group: "linear-models",title: "Regularized Linear Models",sub: "Ridge vs Lasso vs Elastic Net: why does L1 zero out weights while L2 only shrinks them?",level: "Intermediate",mins: 30},
          {slug: "logistic-regression",group: "linear-models",title: "Logistic Regression",sub: "Why is a classifier called regression, and what does log-loss punish?",level: "Beginner",mins: 30},
          {slug: "softmax-regression",group: "linear-models",title: "Softmax Regression",sub: "How does logistic regression handle many classes, and why does every LLM end with it?",level: "Intermediate",mins: 25},
          {slug: "decision-trees",group: "tree-models",title: "Decision Trees",sub: "How does a tree choose its questions, and why does a deep tree memorise noise?",level: "Beginner",mins: 30},
          {slug: "random-forest",group: "tree-models",title: "Random Forest",sub: "How do many wobbly trees make one steady prediction?",level: "Beginner",mins: 25},
          {slug: "gradient-boosting",group: "tree-models",title: "Gradient Boosting",sub: "How do hundreds of tiny trees, each fixing the last one's mistakes, win on tabular data?",level: "Intermediate",mins: 35},
          {slug: "support-vector-machines",group: "classic-classifiers",title: "Support Vector Machines",sub: "Of all the lines that separate the data, why pick the one with the widest street?",level: "Intermediate",mins: 35},
          {slug: "k-nearest-neighbours",group: "classic-classifiers",title: "k-Nearest Neighbours",sub: "No training at all: how can copying your neighbours work, and when does it fail?",level: "Beginner",mins: 30},
          {slug: "naive-bayes",group: "classic-classifiers",title: "Naive Bayes",sub: "Its core assumption is almost always wrong. Why does it still classify so well?",level: "Beginner",mins: 30},
          {slug: "classification-metrics",group: "metrics",title: "Classification Metrics",sub: "Your fraud model is 99.8% accurate. Why is your manager unhappy?",level: "Beginner",mins: 30},
          {slug: "roc-auc-vs-pr-auc",group: "metrics",title: "ROC-AUC vs PR-AUC",sub: "Why can a 0.98 ROC-AUC fraud model still be nearly useless?",level: "Intermediate",mins: 25},
          {slug: "thresholds-and-costs",group: "metrics",title: "Thresholds & Misclassification Costs",sub: "Why flag at 0.5, when a missed fraud costs 100 reviews?",level: "Intermediate",mins: 30},
          {slug: "regression-metrics",group: "metrics",title: "Regression Metrics",sub: "RMSE went up 9× but MAE barely moved. Is the model worse?",level: "Beginner",mins: 30},
          {slug: "ranking-metrics",group: "metrics",title: "Ranking Metrics",sub: "How do you score a search page, a recommendation list, or a RAG retriever?",level: "Intermediate",mins: 25},
          {slug: "probability-metrics",group: "metrics",title: "Probability Metrics",sub: "The model ranks perfectly, so why are the bids wrong?",level: "Intermediate",mins: 25},
          {slug: "choosing-the-right-metric",group: "metrics",title: "Choosing the Right Metric",sub: "Which metric would you use for X? Twelve scenarios to practise.",level: "Intermediate",mins: 25},
        ] },
      { id: "deep-learning", dir: "fundamentals/deep-learning", title: "Deep Learning", desc: "Neural networks from the ground up: training, architectures and representations.",
        groups: [
          {id: "nn-basics",title: "Neural Network Basics",desc: "Neurons, layers, activations and backpropagation."},
          {id: "training",title: "Training & Optimization",desc: "Optimisers, schedules, initialisation, normalisation and regularisation."},
          {id: "architectures",title: "Architectures",desc: "CNNs, RNNs, attention and the Transformer."},
          {id: "representation",title: "Representation Learning",desc: "Embeddings, contrastive and self-supervised learning."},
        ],
        lessons: [
        ] },
      { id: "llms", dir: "fundamentals/llms", title: "LLMs", desc: "How large language models are built, trained, aligned and evaluated.",
        groups: [
          {id: "building-blocks",title: "Building Blocks",desc: "Tokenization, embeddings, positional encodings, attention variants, MoE."},
          {id: "pretraining",title: "Pretraining",desc: "Next-token prediction, data and scaling laws."},
          {id: "post-training",title: "Post-training",desc: "SFT, RLHF, DPO, GRPO and reasoning models."},
          {id: "generation",title: "Generation",desc: "Decoding, sampling and hallucination."},
          {id: "llm-eval",title: "Evaluating LLMs",desc: "Benchmarks, LLM-as-judge and contamination."},
        ],
        lessons: [
        ] },
    ] },
    { id: "system-design", title: "System Design", desc: "Designing, serving and debugging ML and LLM systems in production.", tracks: [
      { id: "llm-inference", dir: "system-design/llm-inference", title: "LLM Inference & Serving", desc: "How LLMs actually run: speed, memory, and the tricks that make serving fast and cheap.",
        lessons: [
          {slug: "prefill-vs-decode",title: "Prefill vs Decode",sub: "Why does an LLM read your prompt fast but write its answer slowly?",level: "Intermediate",mins: 30},
          {slug: "llm-quantization",title: "LLM Quantization",sub: "How does an LLM survive losing 75% of its bits?",level: "Intermediate",mins: 35},
        ] },
      { id: "genai-apps", dir: "system-design/genai-apps", title: "GenAI Application Design", desc: "Building with LLMs in practice: RAG, agents, fine-tuning, guardrails and evaluation.",
        groups: [
          {id: "rag",title: "Retrieval-Augmented Generation",desc: "Grounding LLM answers in your own data."},
          {id: "agents",title: "Agents & Tool Use",desc: "LLMs that plan, call tools and act."},
          {id: "fine-tuning",title: "Fine-tuning",desc: "Adapting models: LoRA, QLoRA and when to fine-tune."},
          {id: "app-eval",title: "Evaluation & Guardrails",desc: "Measuring and protecting LLM applications."},
        ],
        lessons: [
          {slug: "rag-wrong-answer",title: "RAG: Wrong Answer, Where to Look First",sub: "Your chatbot gave a confident, wrong answer. Where do you look first?",level: "Intermediate",mins: 8,group: "rag"},
          {slug: "rag-at-scale",title: "RAG at Scale: Slow and Wrong",sub: "Your RAG worked on 100 docs, but broke at 10 million. Why?",level: "Intermediate",mins: 8,group: "rag"},
        ] },
      { id: "ml-system-design", dir: "system-design/ml-system-design", title: "ML System Design", desc: "End-to-end ML systems: recommendations, search, ads, fraud, feeds and pricing.",
        lessons: [
        ] },
      { id: "ml-scenarios", dir: "system-design/ml-scenarios", title: "ML Scenarios", prefix: "Q", desc: "Real interview scenarios: your model does X, what do you do? Diagnose first, then fix.",
        lessons: [
        ] },
      { id: "mlops", dir: "system-design/mlops", title: "MLOps & Production", desc: "Pipelines, feature stores, deployment, monitoring, drift and A/B testing.",
        lessons: [
        ] },
    ] },
    { id: "papers", title: "Papers", desc: "The idea and the key result of important papers, explained step by step.", tracks: [
      { id: "papers", dir: "papers", title: "Papers Explained", desc: "The idea and the key result of important papers, explained step by step.",
        groups: [
          {id: "agents",title: "Agents & Memory",desc: "How AI agents are built, and how they manage context."},
          {id: "paper-inference",title: "LLM Inference",desc: ""},
          {id: "paper-training",title: "Training & Alignment",desc: ""},
          {id: "paper-retrieval",title: "Retrieval",desc: ""},
          {id: "paper-arch",title: "Architectures",desc: ""},
        ],
        lessons: [
          {slug: "context-language-models",title: "Context Language Models",sub: "What if an AI agent could edit its own memory?",level: "Intermediate",mins: 8,group: "agents"},
          {slug: "harness-engineering",title: "Harness Engineering",sub: "What is actually inside a coding agent?",level: "Intermediate",mins: 25,group: "agents"},
        ] },
    ] },
  ],
};
// Flat list of tracks (each knows its section), used everywhere below.
window.LESSONS.tracks = window.LESSONS.sections.flatMap((s) => s.tracks.map((t) => Object.assign(t, { section: s })));
