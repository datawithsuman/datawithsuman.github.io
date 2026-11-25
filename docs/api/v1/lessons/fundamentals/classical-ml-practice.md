# Classical ML Practice

> Ensembles, metrics, odds, Gini and leakage: can you answer these quickly?

- Track: Fundamentals › Classical ML › Core concepts
- Type: Interview · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/classical-ml-practice/
- Before this: The Bias–Variance Trade-off (`fundamentals/bias-variance`), Classification Metrics (`fundamentals/classification-metrics`)
- Quiz topic: `mlcore`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-19 · Version: df249e9ebc

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your approach out loud, then open the answer and compare the method, not just the number.

**Tools for this page:** ask what the model is reducing, bias or variance, then which errors cost most, and whether any step used data it shouldn't have.

Question 1 · Easy · trees

### Does a random forest mainly reduce bias or variance? What about gradient boosting?

Answer: **Random forest: variance. Boosting: mainly bias**

1. A forest averages many deep, nearly independent trees, which smooths out their noise.

2. Boosting adds shallow trees one by one, each fixing earlier errors, which lowers bias.

3. Boosting also overfits more easily if you add too many trees.

That's why forests need little tuning, while boosting needs a learning rate and early stopping.

Question 2 · Easy · regularisation

### What's the practical difference between L1 and L2 regularisation?

Answer: **L1 can make weights exactly zero. L2 shrinks them all**

1. L1 has a constant pull towards zero, so small weights get removed.

2. L2's pull weakens near zero, so weights rarely reach zero.

So L1 also selects features, while L2 handles correlated features more steadily.

Question 3 · Easy · starting point

### You have 5,000 rows of tabular data. What do you try first, and why?

Answer: **A simple baseline, then gradient boosting**

1. Logistic regression, or a similar simple model, sets a baseline and catches data problems.

2. Gradient boosting usually does very well on tabular data, with little preparation.

Getting a sound validation split matters more than the model choice.

Question 4 · Medium · metrics

### TP = 80, FP = 20 and FN = 40. What are precision, recall and F1?

Answer: **Precision 0.80, recall 0.67, F1 0.73**

1. Precision: 80 ÷ 100 = 0.80.

2. Recall: 80 ÷ 120 ≈ 0.67.

3. F1: 2 × 0.80 × 0.67 ÷ (0.80 + 0.67) ≈ 0.73.

Which matters more depends on the cost of each error.

Question 5 · Medium · imbalance

### A fraud model scores 99% accuracy, and 1% of transactions are fraud. Is that good?

Answer: **Not necessarily. Predicting "not fraud" always gets 99%**

1. Accuracy here says almost nothing.

2. Check precision and recall, or PR-AUC, on the fraud class.

3. Choose a threshold from the costs of each kind of error.

Resampling isn't always needed. Class weights and a good threshold often do enough.

Question 6 · Medium · logistic regression

### In logistic regression, a feature has a coefficient of 0.7. What does this mean?

Answer: **Each unit multiplies the odds by about 2**

1. Coefficients act on the log odds.

2. e^0.7 ≈ 2.01.

3. So each extra unit about doubles the odds, holding other features fixed.

It doesn't double the probability. That depends on where you start.

Question 7 · Hard · decision trees

### A node is 50 yes and 50 no. A split gives one side 40 yes, 10 no, and the other 10 yes, 40 no. What's the fall in Gini impurity?

Answer: **0.18**

1. Parent: 1 − 0.5² − 0.5² = 0.50.

2. Each child: 1 − 0.8² − 0.2² = 0.32.

3. Weighted child average: 0.32, so the fall is 0.50 − 0.32 = 0.18.

Trees choose the split with the largest such fall.

Question 8 · Hard · leakage

### You scale all the data, choose features, then cross-validate, and get 95%. In production, it's 70%. What likely happened?

Answer: **Leakage through preprocessing and selection**

1. Scaling and especially selection used rows from the test folds.

2. Move every step that learns from data into a pipeline, fit on training folds only.

3. Also check for time leakage, and whether production data has shifted.

Selecting with test labels is the most damaging of these.

**More practice and sources**

8 interview questions, easy to hard · answers hidden until you click · checked 6 Nov 2026

Keep practising

Review gradient boosting, regularisation, classification metrics, logistic regression, decision trees and leakage.
