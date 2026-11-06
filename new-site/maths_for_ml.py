# The Maths for ML part of the Fundamentals track. Lesson text comes from the live pages (see ml_import.py).
# Each lesson here adds its interview question and what to read first. Practice pages have their own questions.

GROUPS = [
    ("linear-algebra", "Linear algebra", "Vectors, norms, matrices, rank, projections, eigenvectors, SVD, solving systems and matrix calculus."),
    ("calculus", "Calculus and optimisation", "Gradients, the chain rule and gradient descent."),
    ("probability", "Probability", "Bayes' rule, distributions, expectation and maximum likelihood."),
    ("prob-practice", "Probability practice", "Interview questions on Bayes, coins, dice, cards and urns, with worked answers."),
    ("statistics", "Statistics", "Confidence intervals, hypothesis tests and causation."),
    ("info-theory", "Information theory", "Entropy, cross-entropy and KL divergence."),
]

LESSONS = {
    "vectors-and-cosine-similarity": {"q": "What is the difference between a dot product and cosine similarity?",
                                      "related": ["ai-engineering/rag-end-to-end"]},
    "matrices-as-transformations": {"q": "What does a matrix do to a vector, and what does its determinant measure?", "prereqs": ["vectors-and-cosine-similarity"]},
    "eigenvalues-and-eigenvectors": {"q": "What is an eigenvector, and how does PCA use eigenvectors?", "prereqs": ["matrices-as-transformations"],
                                     "related": ["fundamentals/pca"]},
    "svd-and-low-rank": {"q": "What is SVD, and what do you get by keeping only the top k singular values?", "prereqs": ["eigenvalues-and-eigenvectors"]},
    "vector-and-matrix-norms": {"q": "What's the difference between L1 and L2 norms, and why does L1 give sparse weights?", "prereqs": ["vectors-and-cosine-similarity"], "related": ["fundamentals/regularized-linear-models"]},
    "matrix-multiplication-and-tensor-shapes": {"q": "How do you reason about tensor shapes and the cost of matrix multiplication in a model?", "prereqs": ["matrices-as-transformations"], "related": ["fundamentals/self-attention"]},
    "linear-independence-basis-and-rank": {"q": "What is the rank of a matrix, and why do correlated features break linear regression?", "prereqs": ["matrices-as-transformations"], "related": ["fundamentals/linear-regression"]},
    "orthogonality-and-projections": {"q": "Why is least squares a projection, and why are orthogonal matrices so useful?", "prereqs": ["vectors-and-cosine-similarity", "linear-independence-basis-and-rank"], "related": ["fundamentals/linear-regression"]},
    "positive-definite-matrices": {"q": "What is a positive definite matrix, and where does it show up in ML?", "prereqs": ["eigenvalues-and-eigenvectors"], "related": ["fundamentals/convexity-and-local-minima"]},
    "solving-linear-systems": {"q": "Why shouldn't you invert a matrix to solve Ax = b, and what is the pseudoinverse?", "prereqs": ["svd-and-low-rank", "orthogonality-and-projections"]},
    "matrix-calculus": {"q": "How do you differentiate a matrix expression, like the least-squares loss?", "prereqs": ["matrix-multiplication-and-tensor-shapes", "derivatives-and-chain-rule"], "related": ["fundamentals/backpropagation"]},
    "linear-algebra-practice": {"type": "interview", "prereqs": ["svd-and-low-rank"]},
    "derivatives-and-chain-rule": {"q": "How does backpropagation use the chain rule?", "related": ["fundamentals/backpropagation"]},
    "gradient-descent": {"q": "Why can a larger learning rate make training diverge, and how do momentum and Adam help?", "prereqs": ["derivatives-and-chain-rule"]},
    "convexity-and-local-minima": {"q": "What does convexity guarantee, and which models have a convex loss?", "prereqs": ["gradient-descent"]},
    "probability-and-bayes": {"q": "Why can an accurate test for a rare event still produce mostly false positives?"},
    "probability-distributions": {"q": "How does the distribution you assume for the target decide the loss?", "prereqs": ["probability-and-bayes"]},
    "expectation-and-variance": {"q": "Why does averaging correlated models help less than averaging independent ones?", "prereqs": ["probability-distributions"],
                                 "related": ["fundamentals/random-forest"]},
    "mle-and-map": {"q": "What is the difference between MLE and MAP?", "prereqs": ["probability-distributions"],
                    "related": ["fundamentals/regularized-linear-models"]},
    "practice-bayes": {"type": "interview", "prereqs": ["probability-and-bayes"]},
    "practice-coins": {"type": "interview", "prereqs": ["expectation-and-variance"]},
    "practice-dice": {"type": "interview", "prereqs": ["expectation-and-variance"]},
    "practice-cards": {"type": "interview", "prereqs": ["probability-and-bayes"]},
    "practice-balls-and-urns": {"type": "interview", "prereqs": ["probability-and-bayes"]},
    "practice-classic-puzzles": {"type": "interview", "prereqs": ["expectation-and-variance"]},
    "confidence-intervals-and-bootstrap": {"q": "What does a 95% confidence interval actually mean, and when would you use the bootstrap?", "prereqs": ["expectation-and-variance"]},
    "hypothesis-testing-and-ab-tests": {"q": "How would you run an A/B test, and what does the p-value mean?", "prereqs": ["confidence-intervals-and-bootstrap"], "related": ["fundamentals/randomisation-and-assignment"]},
    "correlation-vs-causation": {"q": "How can correlation mislead you, and how do you estimate a causal effect?", "prereqs": ["hypothesis-testing-and-ab-tests"]},
    "entropy-cross-entropy-kl": {"q": "How are entropy, cross-entropy and KL divergence related?", "prereqs": ["probability-distributions", "mle-and-map"],
                                 "related": ["fundamentals/softmax-regression"]},
}
for _l in LESSONS.values():
    _l["prereqs"] = [f"fundamentals/{p}" for p in _l.get("prereqs", [])]
