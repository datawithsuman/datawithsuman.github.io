// The single list of tracks and lessons, in order. The home page, track pages, breadcrumbs and
// Previous / Next buttons are all built from this. To add a lesson: add its folder, then one line here.
// Addresses use the slug (never the number), so shared links keep working when lessons are reordered.
window.LESSONS = {
  tracks: [
    { id: 'llm-inference', title: 'LLM Inference', desc: 'How LLMs actually run: speed, memory, and the tricks that make serving fast and cheap.', lessons: [
      { slug: 'prefill-vs-decode', title: 'Prefill vs Decode', sub: 'Why does an LLM read your prompt fast but write its answer slowly?', level: 'Intermediate', mins: 30 },
      { slug: 'llm-quantization', title: 'LLM Quantization', sub: 'How does an LLM survive losing 75% of its bits?', level: 'Intermediate', mins: 35 },
    ] },
    { id: 'ml-scenarios', title: 'ML Scenarios', prefix: 'Q', desc: 'Real interview scenarios: your model does X, what do you do? Diagnose first, then fix.', lessons: [] },
    { id: 'ml-system-design', title: 'ML System Design', desc: 'ML systems from an ML engineer\'s view: data, features, serving, monitoring and trade-offs.', lessons: [] },
    { id: 'ml-papers', title: 'ML Papers Explained', desc: 'The idea and the key result of important papers, explained simply.', lessons: [
      { slug: 'context-language-models', title: 'Context Language Models', sub: 'What if an AI agent could edit its own memory?', level: 'Intermediate', mins: 8 },
      { slug: 'harness-engineering', title: 'Harness Engineering', sub: 'What is actually inside a coding agent?', level: 'Intermediate', mins: 25 },
    ] },
    { id: 'genai-engineering', title: 'GenAI & LLM Engineering', desc: 'Building with LLMs in practice: RAG, agents, fine-tuning and evaluation.', lessons: [
      { slug: 'rag-wrong-answer', title: 'RAG: Wrong Answer, Where to Look First', sub: 'Your chatbot gave a confident, wrong answer. Where do you look first?', level: 'Intermediate', mins: 8 },
      { slug: 'rag-at-scale', title: 'RAG at Scale: Slow and Wrong', sub: 'Your RAG worked on 100 docs, but broke at 10 million. Why?', level: 'Intermediate', mins: 8 },
    ] },
    { id: 'ml-fundamentals', title: 'ML Fundamentals', desc: 'The core ideas every AI/ML interview still asks about.',
      groups: [
        { id: 'linear-models', title: 'Linear Models', desc: 'Weighted sums of features: regression, regularization and classification.' },
        { id: 'tree-models', title: 'Tree-Based Models', desc: 'Splits, ensembles and boosting: the workhorses of tabular data.' },
        { id: 'classic-classifiers', title: 'Other Classic Classifiers', desc: 'Margins, neighbours and probabilities.' },
        { id: 'unsupervised', title: 'Unsupervised Learning', desc: 'Finding structure without labels.' },
        { id: 'metrics', title: 'Evaluation Metrics', desc: 'Which number to trust, and when: scenario by scenario.' },
        { id: 'core-concepts', title: 'Core Concepts', desc: 'The ideas behind every model: generalization, evaluation and validation.' },
      ],
      lessons: [
      { slug: 'linear-regression', group: 'linear-models', title: 'Linear Regression', sub: 'What does least squares actually minimise, and when does it break?', level: 'Beginner', mins: 30 },
      { slug: 'regularized-linear-models', group: 'linear-models', title: 'Regularized Linear Models', sub: 'Ridge vs Lasso vs Elastic Net: why does L1 zero out weights while L2 only shrinks them?', level: 'Intermediate', mins: 30 },
      { slug: 'logistic-regression', group: 'linear-models', title: 'Logistic Regression', sub: 'Why is a classifier called regression, and what does log-loss punish?', level: 'Beginner', mins: 30 },
      { slug: 'softmax-regression', group: 'linear-models', title: 'Softmax Regression', sub: 'How does logistic regression handle many classes, and why does every LLM end with it?', level: 'Intermediate', mins: 25 },
      { slug: 'decision-trees', group: 'tree-models', title: 'Decision Trees', sub: 'How does a tree choose its questions, and why does a deep tree memorise noise?', level: 'Beginner', mins: 30 },
      { slug: 'random-forest', group: 'tree-models', title: 'Random Forest', sub: 'How do many wobbly trees make one steady prediction?', level: 'Beginner', mins: 25 },
      { slug: 'gradient-boosting', group: 'tree-models', title: 'Gradient Boosting', sub: 'How do hundreds of tiny trees, each fixing the last one\'s mistakes, win on tabular data?', level: 'Intermediate', mins: 35 },
      { slug: 'classification-metrics', group: 'metrics', title: 'Classification Metrics', sub: 'Your fraud model is 99.8% accurate. Why is your manager unhappy?', level: 'Beginner', mins: 30 },
      { slug: 'roc-auc-vs-pr-auc', group: 'metrics', title: 'ROC-AUC vs PR-AUC', sub: 'Why can a 0.98 ROC-AUC fraud model still be nearly useless?', level: 'Intermediate', mins: 25 },
      { slug: 'thresholds-and-costs', group: 'metrics', title: 'Thresholds & Misclassification Costs', sub: 'Why flag at 0.5, when a missed fraud costs 100 reviews?', level: 'Intermediate', mins: 30 },
      { slug: 'regression-metrics', group: 'metrics', title: 'Regression Metrics', sub: 'RMSE went up 9× but MAE barely moved. Is the model worse?', level: 'Beginner', mins: 30 },
      { slug: 'ranking-metrics', group: 'metrics', title: 'Ranking Metrics', sub: 'How do you score a search page, a recommendation list, or a RAG retriever?', level: 'Intermediate', mins: 25 },
      { slug: 'probability-metrics', group: 'metrics', title: 'Probability Metrics', sub: 'The model ranks perfectly, so why are the bids wrong?', level: 'Intermediate', mins: 25 },
      { slug: 'choosing-the-right-metric', group: 'metrics', title: 'Choosing the Right Metric', sub: 'Which metric would you use for X? Twelve scenarios to practise.', level: 'Intermediate', mins: 25 },
    ] },
  ],
};
