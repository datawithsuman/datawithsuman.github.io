# Logistic Regression

> Why is a classifier called regression, and what does log-loss punish?

- Track: Fundamentals › Classical ML › Linear models
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/logistic-regression/
- Before this: Linear Regression (`fundamentals/linear-regression`), Maximum Likelihood & MAP (`fundamentals/mle-and-map`)
- Quiz topic: `lin`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-20 · Version: ac3ae3a28b

## Intuition

### The situation

You have 20 students, their hours studied, and whether each one passed. You need a yes or no, and how sure you are. The interviewer asks:

> What is logistic regression, and why is it called regression?

**Running example:** 20 students, hours studied, and whether each passed the exam (illustrative data). Goal: given hours, predict the _probability_ of passing.

#### Predict yes or no, and how sure you are

Spam or not, churn or not, default or not, click or not: a huge share of real ML problems have a yes/no answer. You want two things: a decision, and a **probability** you can rank, threshold and trust ("82% likely to default" is far more useful than "yes"). The target is 0 or 1, which breaks the tool from the last two lessons.

### The idea

Think of a judge weighing evidence. Each fact adds or takes away points, and the total can be any number. A curve then squashes that total into a chance between 0 and 100%.

[Figure: Evidence adds up to a score, a curve squashes the score, and out comes a chance between 0 and 100 percent]

_Illustrative. In the model, the points are the weights and the curve is the sigmoid._

### Play

**Try to break it.** Here w is how much each hour counts, and b is where the judge starts. Lower log-loss means a better fit. Drag w as high as it goes.

#### w sets the steepness, b sets where it crosses 50%

Each student's contribution to the loss is drawn as a red bar: the bar is long when the curve gives low probability to what actually happened. Notice that a very steep curve (large w) gets punished hard for the few students on the "wrong" side.

**Now say why:** why does the steepest curve get punished, even though it looks so confident?

## Maths

### Maths

#### In one breath

Logistic regression is a **classifier**. It models the **log-odds** of the positive class as a weighted sum of features and squashes that through a sigmoid to get a probability between 0 and 1. It is trained by maximum likelihood, which is the same as minimising **log-loss** (cross-entropy): a convex problem with one best answer and no closed form. Its decision boundary is a straight line (a hyperplane), its weights read as odds multipliers, and with regularization its probabilities are often well calibrated. What you'll be able to do after this: explain why it's called "regression", why we don't use squared error, derive the gradient, interpret a coefficient as an odds ratio, and handle separable data, thresholds and calibration.

#### Probability, odds and log-odds

Three ways to say the same thing. A probability p lives in [0, 1]. The **odds** p / (1 − p) live in [0, ∞): p = 0.8 is odds of 4 ("4 to 1"). The **log-odds** (the **logit**) log(p / (1 − p)) live on the whole real line, from −∞ to +∞, with 0 meaning a coin flip.

That last scale is the key: a weighted sum of features can be any real number, and so can log-odds. So we let the linear part predict the log-odds.

#### A linear model for the log-odds, squashed into a probability

$$ {h_\theta(x)} = {g}\big({\theta^{\top}x}\big) = 1\,/\,\big(1 + e^{-\theta^{\top}x}\big) \qquad {\log\!\big(h/(1-h)\big) = \theta^{\top}x} $$

CS229 §2.1 [CS229 notes](https://cs229.stanford.edu/main_notes.pdf). The derivative is neat: g′(z) = g(z)(1 − g(z)), which keeps the gradient simple.

- **the probability**: h(x) = P(y = 1 | x): the model's probability of a pass.

- **the sigmoid**: g(z) = 1 / (1 + e^(−z)). Maps any real number to (0, 1): very negative → near 0, 0 → 0.5, very positive → near 1.

- **the logit**: θᵀx: an ordinary weighted sum of features, exactly like linear regression. It can be any real number.

- **the same thing, inverted**: Solve for the linear part: log-odds = θᵀx. Logistic regression is linear regression on the log-odds scale. That's where “regression” in the name comes from.

#### Maximum likelihood gives log-loss, not squared error

Treat each label as a coin flip with probability h(x). The probability of all the observed labels is a product; take its log and you get the log-likelihood [CS229 Eq. 2.1](https://cs229.stanford.edu/main_notes.pdf). Its negative is **log-loss**, also called binary cross-entropy:

$$ {\ell(\theta)} = {\sum_{i=1}^{n}}\Big[{y^{(i)}\log h(x^{(i)})} + {(1-y^{(i)})\log\big(1-h(x^{(i)})\big)}\Big] $$

- **log-likelihood**: How probable the observed passes and fails are under θ. Maximise it (or minimise its negative, the log-loss).

- **when y = 1**: Only this term is active for a pass: log of the predicted pass probability. Predict 0.99 → about 0; predict 0.01 → −4.6.

- **when y = 0**: Only this term is active for a fail: log of the predicted fail probability.

- **over all students**: Add over the n examples. One term per example, one active part per term.

##### Feel the penalty

Squared error never exceeds 1, so a confident wrong answer costs at most 1. Log-loss goes to infinity as p → 0: a model that says "1% chance" about something that happened is punished severely. That's a difference in how hard each punishes a confident mistake. Both are proper scoring rules: each is best when you report the true probability.

##### Why not squared error? The shape of the loss

Both losses on our 20 students as the weight w changes (bias kept so the curve crosses 50% at the fitted threshold). Log-loss (orange) is a single convex valley. Squared error on sigmoid outputs (purple) flattens into a plateau for wrong-sign weights and is non-convex there: gradients vanish, and an optimiser can stall. With log-loss, the gradient is simply (prediction − label) × feature, and it never vanishes while the model is wrong.

#### The gradient is (label − prediction) × feature, again

Differentiate the log-likelihood using g′ = g(1 − g), and nearly everything cancels [CS229 Eq. 2.2](https://cs229.stanford.edu/main_notes.pdf):

$$ {\tfrac{\partial}{\partial\theta_j}\ell(\theta)} = {\big(y - h_\theta(x)\big)}\,{x_j} $$

- **slope for weight j**: How the log-likelihood changes when weight j moves, for one example.

- **the error**: Label minus predicted probability. If the model said 0.9 and the student passed, the error is only 0.1.

- **the feature**: Scaled by the feature value, just like linear regression's LMS rule.

That's the same form as the least-squares update, but it isn't the same algorithm: h is now the sigmoid of θᵀx. CS229 asks whether the match is a coincidence and answers with generalized linear models (see the family tree below): both are GLMs with their natural "canonical" link. Unlike linear regression, setting the gradient to zero has **no closed-form solution**, so we iterate: gradient descent, Newton's method or L-BFGS. The log-loss is convex, so they all reach the same optimum, when one exists (perfectly separable data has none).

#### Each weight is an odds multiplier

Because the model is linear in the log-odds, one extra unit of a feature adds w to the log-odds, which **multiplies the odds by ew**, no matter where you start.

Fitted on our 20 students. The odds ratio is constant, but the change in _probability_ isn't: one extra hour moves P(pass) a lot near 50% and very little near 0% or 100%. Interview trap: "a coefficient of 0.86 means 86% more likely" is wrong; it means the odds multiply by e0.86 ≈ 2.36.

#### With two features, the boundary is a straight line

1. Now two features: hours studied and hours slept. Each dot is a student (illustrative).

2. P = 0.5 exactly where the logit is zero: 0.9·study + 0.8·sleep − 9.5 = 0. That's a straight line, the **decision boundary**.

3. Every probability level is a line parallel to it. Probability changes only as you move across the lines, never along them.

4. The weight vector is perpendicular to the boundary and points toward higher pass odds. In more dimensions the boundary is a flat hyperplane.

A straight boundary is both the strength and the limit. If the classes are separated by a curve (a ring, an XOR pattern), plain logistic regression can't follow it. Add features (squares, products, splines), or use a non-linear model. That's exactly what a neural network's hidden layers do before its final logistic or softmax layer.

#### Perceptron, GLMs, and softmax

**The perceptron: logistic regression with a hard step**

Replace the sigmoid with a hard threshold (output 1 if θᵀx ≥ 0, else 0) and use the same update θj := θj + α(y − h(x))xj, and you get the perceptron (1950s–60s). It finds a separating line if one exists, but CS229 notes "it is difficult to endow the perceptron's predictions with meaningful probabilistic interpretations" [CS229 §2.2](https://cs229.stanford.edu/main_notes.pdf). Logistic regression is the smooth, probabilistic version.

**Generalized linear models: why sigmoid, and why the same gradient**

Linear and logistic regression are both GLMs: pick an exponential-family distribution for y given x, model its natural parameter as θᵀx, and predict its mean. Gaussian y gives linear regression (identity link); Bernoulli y gives logistic regression, and writing the Bernoulli in exponential-family form produces the sigmoid on its own. Poisson y (counts) gives Poisson regression. Every GLM with the canonical link has the gradient (y − prediction)·x, which answers the "coincidence" above [CS229 §3](https://cs229.stanford.edu/main_notes.pdf).

More than two classes? Give each class its own weight vector and replace the sigmoid with a softmax. That's the next lesson.

GLMs have their own lesson: see Generalised Linear Models.

## In practice

### In practice

#### Still a workhorse

Logistic regression is the default baseline for binary classification and still production-grade in credit scoring, medical risk scores, fraud and click-through-rate models, wherever probabilities and explainability matter. In scikit-learn it's `LogisticRegression` (L-BFGS by default, and **L2-regularised by default**, with `C = 1`); statsmodels' `Logit` gives the unregularised fit with standard errors; `SGDClassifier(loss="log_loss")` trains it on streams. scikit-learn notes the default penalty explicitly: "Regularization is applied by default, which is common in machine learning but not in statistics" [scikit-learn docs](https://scikit-learn.org/stable/modules/linear_model.html).

#### 0.5 is a default, not a law

On our 20 students with the fitted model. Lower the threshold and you catch more passers (recall up) but also more failers (precision down). Pick the threshold from the costs: missing a fraud costs far more than reviewing a false alarm, so fraud models use low thresholds.

**Calibration** means "of all cases predicted at 70%, about 70% are positive." Logistic regression is good at this by construction. scikit-learn: it "is more likely to return well calibrated predictions by itself as it has a canonical link function for its loss," which in the unpenalised case gives the "balance property" [scikit-learn calibration docs](https://scikit-learn.org/stable/modules/calibration.html). The guarantee weakens with strong penalties, a mis-specified model, or resampled training data (e.g. after oversampling the rare class). Check a reliability curve, and recalibrate if needed.

#### Shipping a logistic regression

1. Split train/test (stratified, so both keep the class ratio).

2. Encode categories (one-hot), standardise numeric features (needed for the penalty and for fast convergence).

3. Fit with L2 (default) and cross-validate C; try L1 or Elastic Net if you want feature selection.

4. Evaluate with metrics that fit the problem: log-loss and ROC-AUC for ranking quality, PR-AUC when positives are rare. Accuracy misleads on imbalanced data.

5. Check calibration (a reliability curve); recalibrate if you resampled or regularised heavily.

6. Choose the threshold from business costs, on validation data.

7. Explain with odds ratios (ew per unit, or per standard deviation for standardised features).

#### Use it, or reach for something else?

##### Use logistic regression when

- You need probabilities and a strong, fast baseline

- You need to explain decisions (regulated domains like credit and health)

- Data is high-dimensional and sparse (text with TF-IDF, one-hot features)

- Latency or memory is tight

##### Reach for something else when

- Strong non-linear interactions in tabular data → gradient boosting

- Images, audio, raw text → neural networks (with a logistic/softmax output layer)

- More than two classes → softmax regression (or one-vs-rest)

### The answer that sounds right

#### "Just run linear regression on the 0s and 1s"

Fit a straight line to the 0/1 labels and call anything above 0.5 a pass. It sort of works on tidy data. Then one diligent student who studied a lot (and passed, obviously) joins the dataset:

Purple: least-squares line on 0/1 labels. Orange: logistic curve. The extra student is an easy, correct "pass", yet the straight line tilts to reach them, its 0.5 crossing slides right, and it starts misclassifying students it got right before. The logistic fit barely moves. (Axis shows 0–20 hours; points further right are off-screen.)

##### What breaks

A line predicts values below 0 and above 1, which aren't probabilities. Its squared error punishes being "too right" (predicting 1.4 for a sure pass), so easy points far from the boundary drag the fit. CS229 makes the same point: "it is easy to construct examples where this method performs very poorly" and "it also doesn't make sense for hθ(x) to take values larger than 1 or smaller than 0" [CS229 §2](https://cs229.stanford.edu/main_notes.pdf).

#### Perfectly separable data: the weights run to infinity

If a line separates passes from fails perfectly, the likelihood keeps improving as the sigmoid gets steeper, with no finite best weight. The optimiser just keeps going:

Same 20 students, but relabelled so everyone with ≥ 3.75 hours passed (perfectly separable). Gradient descent, learning rate 0.5. Without a penalty, w keeps growing and the curve becomes a step with fake 100%/0% certainty. With an L2 penalty (λ = 0.05) it converges to a finite, sensible slope.

This is one big reason scikit-learn regularises by default. The strength is set by `C`, the _inverse_ of the penalty: small C means strong regularization [scikit-learn docs](https://scikit-learn.org/stable/modules/linear_model.html). With many features, separable data is common, and the same L1/L2/Elastic Net trade-offs from the last lesson apply.

#### What to keep

**The lesson:** logistic regression is linear regression on the log-odds, trained with log-loss. Convex, fast, calibrated-ish, explainable, and the building block (as the output layer) of most neural classifiers.

- **Linear boundary only.** Interactions and curves must be engineered in.

- **Separable data and many features** need regularization, or weights explode.

- **Class imbalance** doesn't break the model but does break accuracy and the 0.5 threshold. Use class weights or threshold tuning, and remember that reweighting shifts the probabilities.

- **Collinear features** make individual odds ratios unstable, exactly as in linear regression.

## Say it

### What is logistic regression, and why is it called regression?

#### The interviewer pushes further

Follow-up 1 of 6

Why is it called regression if it's a classifier?

It's a regression model for the log-odds (a GLM with a logit link): it predicts a continuous quantity, the probability, and classification only happens when you apply a threshold.

Follow-up 2 of 6

Why log-loss and not MSE?

Log-loss is the negative Bernoulli log-likelihood, so it's the principled choice. With a sigmoid output it's convex in the weights and gives the clean gradient (h − y)x. MSE on sigmoid outputs is non-convex with flat regions where gradients vanish, and it penalises a confident wrong prediction by at most 1, so those mistakes push back only weakly during training.

Follow-up 3 of 6

How do you interpret a coefficient?

A one-unit increase in the feature, holding others fixed, adds w to the log-odds, so it multiplies the odds by ew. The effect on probability depends on where you are on the curve: largest near 0.5.

Follow-up 4 of 6

What happens with perfectly separable data?

The maximum-likelihood estimate doesn't exist: weights grow without bound while the loss keeps falling toward zero. Regularization (scikit-learn's default L2) or early stopping gives finite, sensible weights.

Follow-up 5 of 6

Is the decision boundary linear?

Yes, in the features you give it: θᵀx = log(t/(1 − t)) for threshold t. Add polynomial or interaction features to get curved boundaries in the original space.

Follow-up 6 of 6

How would you handle class imbalance?

Keep log-loss, but use class weights or resampling, evaluate with PR-AUC or recall at a fixed precision rather than accuracy, and tune the threshold. If you reweight or resample, the predicted probabilities shift, so recalibrate if you need true probabilities.

#### The 30-second answer

Logistic regression is a linear classifier. It models the log-odds of the positive class as a linear function of the features, and the sigmoid turns that into a probability. It's trained by maximum likelihood, which means minimising log-loss: convex, solved iteratively with gradient descent or L-BFGS, with gradient (prediction − label) × feature. Coefficients are log odds ratios, the decision boundary is a hyperplane, and in practice it's L2-regularised, which also handles separable data. It's called regression because it regresses the log-odds.

**Go further**

#### The 2-minute walkthrough

Problem: binary target, want calibrated probabilities. Why not linear regression (outputs outside [0, 1], easy points drag the fit). Odds and log-odds; model logit = θᵀx; sigmoid. Bernoulli likelihood → log-loss; why not MSE (non-convex, vanishing gradients, weak penalty for confident errors). Gradient (y − h)x, no closed form, convex optimisation. Interpretation via odds ratios. Boundary is linear; feature engineering for curves. Separable data → infinite weights → regularization (C). Threshold from costs; calibration and the balance property.

#### What not to say

- "It outputs a class." It outputs a probability; the class comes from your threshold.

- "Coefficient 0.5 means 50% more likely." It's +0.5 log-odds, an odds ratio of about 1.65.

- "It can't do non-linear problems." Not with raw features, but with engineered features it can.

- "There's a closed-form solution like linear regression." There isn't; it's solved iteratively.

**Key terms and sources**

Built from Stanford CS229 notes (§2–3), scikit-learn's linear-model and calibration docs · checked 28 Oct 2026

#### Glossary

| Term | Meaning |
|---|---|
| **Sigmoid / logistic function** | g(z) = 1/(1 + e−z), squashes to (0, 1). |
| **Logit / log-odds** | log(p/(1 − p)); the linear part of the model. |
| **Odds ratio** | ew: how the odds multiply per unit of a feature. |
| **Log-loss / binary cross-entropy** | −[y log p + (1 − y) log(1 − p)], averaged. |
| **Decision boundary** | Where p = threshold; a hyperplane θᵀx = const. |
| **Calibration** | Predicted probabilities match observed frequencies. |
| **C (scikit-learn)** | Inverse regularization strength. |
| **GLM** | Generalized linear model: exponential-family response with a linear predictor. |

#### What this page is built from

1. A. Ng, T. Ma et al., [Stanford CS229 lecture notes](https://cs229.stanford.edu/main_notes.pdf), §2 (logistic regression, perceptron, multi-class) and §3 (GLMs).

2. scikit-learn, [Linear models user guide](https://scikit-learn.org/stable/modules/linear_model.html): LogisticRegression objective, C, default regularization, solvers.

3. scikit-learn, [Probability calibration](https://scikit-learn.org/stable/modules/calibration.html): why logistic regression tends to be calibrated.

4. Hastie, Tibshirani & Friedman, _The Elements of Statistical Learning_, §4.4 (logistic regression), background.

5. Interview angle: [Analytics Vidhya, 30 logistic regression interview questions](https://www.analyticsvidhya.com/?p=37752); [DataLemur ML interview questions](https://datalemur.com/blog/machine-learning-interview-questions).

Student data is illustrative; every fit and curve on this page is computed live.
