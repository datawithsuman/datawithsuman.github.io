# Softmax Regression

> How does logistic regression handle many classes, and why does every LLM end with it?

- Track: Fundamentals › Classical ML › Linear models
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/softmax-regression/
- Before this: Logistic Regression (`fundamentals/logistic-regression`), Entropy, Cross-Entropy & KL Divergence (`fundamentals/entropy-cross-entropy-kl`)
- Related: Self-Attention (Q, K, V) (`fundamentals/self-attention`)
- Quiz topic: `lin`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-20 · Version: d5d694eb34

## Intuition

### The situation

You're sorting fruit into apple, orange or banana. A teammate turns scores into probabilities by dividing each by the total, and then one score goes negative. The interviewer asks:

> What is softmax regression, and how is it trained?

**Running example:** sort 27 fruits into apple, orange or banana from two measurements: length (cm) and "yellowness" (0–1, from a colour sensor). Illustrative data, generated with a fixed seed.

#### More than two answers, and one probability for each

Digit recognition (10 classes), intent detection (dozens), product categories (thousands), next-token prediction (over 100,000): most real classification has more than two classes. You want a probability for every class, all of them between 0 and 1, summing to exactly 1. Logistic regression gives one probability for one yes/no question. How do you get a proper distribution over K options?

### The idea

Think of a vote share. Each class gets a score, and raising e to that score makes it positive and widens the lead. Dividing by the total then gives shares that add up to 100%.

[Figure: Three scores, 2, 1 and minus 1, become probabilities of 71, 26 and 4 percent after softmax. They add up to 100 percent.]

_Worked from the scores 2, 1 and −1. Percentages are rounded._

### Play

**Try to break it.** Add 3 to every logit. Then raise the temperature, and then lower it.

#### Move the scores, watch the distribution

Things to try. Add the same amount to every logit: nothing changes (the Maths tab shows why). Raise T: the distribution flattens toward uniform. Lower T: it sharpens toward the single biggest logit. That's exactly the "temperature" knob in LLM sampling.

**Now say why:** why does adding the same amount change nothing, and what does temperature really do?

## Maths

### Maths

#### In one breath

Softmax regression extends logistic regression to K classes. Each class gets its own weight vector and its own score (a **logit**); the **softmax** exponentiates the scores and normalises them, so they're positive and sum to 1. It's trained with **cross-entropy**, and the gradient is beautifully simple: (predicted probability − one-hot label) × features. With two classes it reduces exactly to the sigmoid. And it's not just classical ML: the last layer of every LLM is softmax regression over its vocabulary. What you'll be able to do after this: derive softmax and its gradient, explain why logits are shift-invariant, implement it without overflow, compare it with one-vs-rest, and connect temperature to LLM sampling.

#### One score per class, then turn scores into probabilities

Give each class k its own weight vector θk. For a fruit with features x, each class gets a score tk = θkᵀx: how much the features look like that class. These raw scores are called **logits**. They can be any real number, so we need a function that turns K arbitrary numbers into a probability distribution. CS229 points out the two problems with using them directly: θkᵀx "is not necessarily within [0, 1]" and "the summation of θkᵀx's is not necessarily 1" [CS229 §2.3](https://cs229.stanford.edu/main_notes.pdf).

Notation: the label is often written **one-hot**, a vector with a 1 in the true class's slot and 0 elsewhere. A banana is (0, 0, 1).

#### Exponentiate the scores, then normalise

$$ {P(y=i\mid x)} = {\exp({\theta_i^{\top}x})} \,\Big/\, {\textstyle\sum_{j=1}^{K}\exp(\theta_j^{\top}x)} $$

CS229 Eqs. 2.9–2.10 [CS229 §2.3](https://cs229.stanford.edu/main_notes.pdf). "Softmax" because it's a smooth version of "argmax": the biggest score gets most of the probability, but the others keep some.

- **probability of class i**: The model's probability that this fruit is class i.

- **exponentiate**: e^(score): always positive, and it stretches differences: a score 1 higher means a 2.7× bigger number.

- **normalise**: Divide by the sum over all K classes, so the probabilities add up to exactly 1.

- **the logit**: Class i's score: θᵢᵀx, a weighted sum of the features, one weight vector per class.

#### Adding a constant to every logit changes nothing

$$ {\mathrm{softmax}(t + c)_i} = {e^{c}\,e^{t_i} \,/\, \textstyle\sum_j e^{c}\,e^{t_j}} = {\mathrm{softmax}(t)_i} $$

- **shifted scores**: Add the same number c to every class's logit.

- **factor out**: e^(t+c) = e^c · e^t: the same factor e^c appears on top and in every term of the sum.

- **identical output**: It cancels. Softmax depends only on the differences between logits.

Two consequences. First, the parameters are **redundant**: add the same vector to every θk and predictions don't change, so one class's weights can be fixed at zero without losing anything. Regularization also pins this down. Second, it gives the standard trick for computing softmax without overflow:

Computed live in your browser with 64-bit floats. e1000 overflows to Infinity, and Infinity / Infinity is NaN. e−1000 underflows to 0, and 0 / 0 is also NaN. Subtracting the largest logit first makes the biggest exponent e0 = 1: same answer, no overflow. Every library does this, and computes log-softmax as t − max − log Σ et − max (the log-sum-exp trick).

#### Cross-entropy, and the cleanest gradient in ML

Maximum likelihood again: maximise the probability the model gives to the true class. For one example the loss is just −log of that probability [CS229 §2.3](https://cs229.stanford.edu/main_notes.pdf):

$$ {\ell_{\text{ce}}} = -\log{\phi_{y}} \qquad {\nabla_{\theta_i}\ell_{\text{ce}}} = {\big(\phi_i - \mathbb{1}\{y=i\}\big)}\,{x} $$

With φ = softmax of the logits; in vector form, ∂ℓ/∂t = φ − ey (CS229 Eq. 2.17).

- **cross-entropy loss**: For one example with true class y.

- **the true class's probability**: Only the probability of the correct class appears. Predict 0.9 for it → loss 0.105; predict 0.01 → 4.6.

- **gradient for class i's weights**: How to change θᵢ, from CS229 Eq. 2.18.

- **prediction − truth**: φᵢ minus 1 if i is the true class, else 0. Push up the true class by (1 − its probability); push every other class down by its probability.

- **the features**: Scaled by the input, exactly like linear and logistic regression.

–

Using the trained model from the next section. Bars: predicted probability φ (filled) and the one-hot label (outline). The gradient on each class's logit is φ − label: negative means "raise this score", positive means "lower it". Confident and correct → tiny gradient; confused → big push.

#### Straight-edged regions, one per class

1. 27 fruits by length and yellowness. Bananas are long and yellow; apples and oranges differ mainly in colour.

2. After training (gradient descent on cross-entropy, a light L2 penalty), each point of the plane is assigned to the class with the biggest logit. These are the decision regions.

3. Region edges are where two logits tie: θaᵀx = θbᵀx, which is a straight line. So softmax regression is still a linear classifier: K classes, regions bounded by straight lines.

4. Curved class shapes need engineered features, or hidden layers in front: a neural network is learned features plus this same softmax layer.

**Go deeper: two classes = the sigmoid**

With K = 2 and logits (t₁, t₂): P(class 1) = et₁ / (et₁ + et₂) = 1 / (1 + e−(t₁ − t₂)) = σ(t₁ − t₂). Binary softmax is exactly logistic regression, with weight vector θ₁ − θ₂ (the redundancy from the section above, in action). In GLM terms, softmax is the canonical response function of the multinomial distribution, just as the sigmoid is for the Bernoulli [CS229 §3](https://cs229.stanford.edu/main_notes.pdf).

For the wider family, see Generalised Linear Models.

## In practice

### In practice

#### Two ways to go multi-class

| Approach | How | Trade-off |
|---|---|---|
| **One-vs-rest (OvR)** | Train K separate binary logistic regressions ("apple vs not", …), predict the highest | Simple and parallel, but the K probabilities don't sum to 1 and weren't trained together (see Softmax vs one-vs-rest below) |
| **Multinomial / softmax** | One model, K weight vectors, a single softmax, a single cross-entropy loss | Coherent probabilities; the standard choice; it's the output layer of neural classifiers and LLMs |

scikit-learn's `LogisticRegression` fits the multinomial (softmax) model for multi-class problems with its default solver, and uses a coefficient matrix W with one row per class; the old liblinear solver "cannot learn a true multinomial (multiclass) model" [scikit-learn docs](https://scikit-learn.org/stable/modules/linear_model.html). In PyTorch, it's a `nn.Linear` layer followed by `CrossEntropyLoss`, which applies the softmax internally.

#### OvR's probabilities don't add up

Both models trained on the same 27 fruits. OvR runs three independent "this class vs the rest" logistic regressions; their outputs answer three different questions, so they can sum to more or less than 1. Softmax's outputs are one coherent distribution. Both usually pick the same winner; the difference shows up when you use the probabilities (ranking, thresholds, expected cost).

#### Every LLM ends with softmax regression

A language model's last step is exactly this lesson. The network turns the context into a hidden vector (4,096 numbers in Llama 3.1 8B), and a final linear layer produces one logit per token in the vocabulary: 128,256 of them. Softmax turns those into next-token probabilities, and training minimises cross-entropy against the actual next token [Llama 3.1 8B config (a copy that needs no login)](https://huggingface.co/unsloth/Llama-3.1-8B/raw/main/config.json). That one output matrix alone holds 4,096 × 128,256 ≈ 525 million weights: softmax regression with 128,256 classes.

$$ {q_i} = \exp({z_i / {T}}) \,\Big/\, \textstyle\sum_j \exp(z_j / T) $$

Temperature softmax as used in knowledge distillation, Hinton, Vinyals & Dean, [Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531) (2015), where a high T exposes the teacher's "dark knowledge" in the small probabilities of wrong classes. The same knob controls randomness in LLM sampling.

- **softened probability**: The probability of class (or token) i at temperature T.

- **logits ÷ T**: Divide every logit by T before the softmax.

- **temperature**: T = 1: the normal softmax. T > 1: flatter, more random, lets low-probability options through. T < 1: sharper. T → 0: always the top choice (greedy).

#### Training a softmax classifier

1. Encode labels as integers (or one-hot); stratified train/test split.

2. Standardise features; add engineered features if classes have curved shapes.

3. Compute logits t = Wx + b, then the loss with a fused, stable log-softmax + cross-entropy (never take the log of a softmax you computed separately).

4. Optimise with L-BFGS (small data) or SGD/Adam (large); add L2 regularization (it also removes the redundancy in the logits).

5. Evaluate with per-class precision and recall, a confusion matrix, macro-F1 for imbalanced classes, and log-loss for probability quality.

6. For decisions, use argmax, or thresholds and costs per class; check calibration if probabilities feed decisions.

#### Use it, or reach for something else?

##### Use softmax regression when

- Classes are mutually exclusive and you need coherent probabilities

- You want a fast, interpretable multi-class baseline (e.g. text with TF-IDF)

- You're building the output layer of any neural classifier

##### Use something else when

- Items can carry several labels → one sigmoid per label

- Classes are ordered (ratings 1–5) → ordinal regression

- Boundaries are strongly non-linear in tabular data → gradient boosting

### The answer that sounds right

#### "Divide each score by the total"

The first idea: just normalise, pk = tk / Σ tj. Scores of (2, 1, 1) give (0.5, 0.25, 0.25). Looks fine, until a score is negative or the scores sum to zero:

Apple and orange scores fixed at 2.0 and 1.0. Plain division produces negative "probabilities", values above 1, or a division by zero as banana's score moves. Softmax always gives a valid distribution, and keeps the order of the scores.

##### What breaks

Plain normalisation needs every score to be positive. Exponentiating first fixes that (et > 0 always), and it has a deeper reason: it's what you get by extending the logistic model's log-odds idea to K classes.

#### What to keep

**The lesson:** softmax regression is logistic regression for K classes: one logit per class, exponentiate and normalise, cross-entropy loss, gradient φ − y. It's linear, convex, and the output layer of almost every modern classifier and language model.

- **Mutually exclusive classes only.** If an item can have several labels at once (multi-label tagging), use independent sigmoids per label, not one softmax.

- **Softmax probabilities are not automatically calibrated**, especially in big neural nets, which tend to be overconfident. Temperature scaling on a validation set is the usual fix.

- **Huge K is expensive.** The normaliser sums over every class; with very large vocabularies, training uses tricks like sampled softmax, and inference often only needs the top few logits.

- **Linear boundaries**, just like logistic regression.

## Say it

### What is softmax regression, and how is it trained?

#### The interviewer pushes further

Follow-up 1 of 5

Derive the gradient of softmax + cross-entropy with respect to the logits.

ℓ = −ty + log Σj etj. ∂ℓ/∂ti = −1{i = y} + eti/Σ etj = φi − 1{i = y}. So the gradient vector is φ − one-hot(y), and with respect to θi it's (φi − 1{i = y})·x.

Follow-up 2 of 5

Why subtract the max logit?

exp overflows for logits above about 709 in float64 (far less in float16), and very negative logits underflow to 0, both producing NaN. Softmax is invariant to adding a constant, so subtracting the max gives identical results with the largest exponent equal to 1.

Follow-up 3 of 5

Softmax vs sigmoid outputs?

Softmax: one distribution over mutually exclusive classes (sums to 1). Independent sigmoids: one yes/no probability per label, for multi-label problems. For exactly two exclusive classes, softmax over two logits equals a sigmoid of their difference.

Follow-up 4 of 5

What does temperature do?

Dividing logits by T > 1 flattens the distribution (more diverse samples, exposes small probabilities, used in distillation); T < 1 sharpens it; T → 0 is argmax. The ranking of classes never changes.

Follow-up 5 of 5

One-vs-rest or multinomial?

Multinomial gives coherent, jointly trained probabilities and is the default in modern libraries. OvR is simpler to parallelise and can be fine for ranking, but its scores don't sum to 1 and aren't comparable across classes without recalibration.

#### The 30-second answer

Softmax regression is multinomial logistic regression. Each class has a weight vector that gives a logit; softmax exponentiates and normalises the logits into a probability distribution. It's trained by minimising cross-entropy, the negative log probability of the true class, and the gradient with respect to the logits is just predicted probabilities minus the one-hot label. It's convex and linear in its decision boundaries, reduces to the sigmoid for two classes, and in practice you subtract the max logit for numerical stability. It's also exactly the output layer of neural classifiers and LLMs.

**Go further**

#### The 2-minute walkthrough

Need: a distribution over K exclusive classes. Logits tk = θkᵀx; why not divide by the sum (negatives); exponentiate and normalise. Shift invariance → redundancy and the max-subtraction trick. Cross-entropy from maximum likelihood; gradient φ − y times x. Binary case = sigmoid of the logit difference. Decision regions with straight edges. Versus one-vs-rest: incoherent probabilities. Temperature, and the LLM output layer (Llama 3.1 8B: 128,256 classes).

#### What not to say

- "Softmax probabilities are the model's true confidence." Often overconfident; calibrate.

- "Softmax is non-linear, so the model is non-linear." The decision boundaries are linear in the features.

- "Use softmax for multi-label." Use independent sigmoids.

- "Higher temperature changes which class is most likely." It never changes the ordering, only the spread.

**Key terms and sources**

Multinomial logistic regression · built from Stanford CS229 notes (§2.3, §3), scikit-learn's docs and Hinton et al. (2015) · checked 28 Oct 2026

#### Glossary

| Term | Meaning |
|---|---|
| **Logit** | A class's raw score θkᵀx, before softmax. |
| **Softmax** | exp(ti) / Σ exp(tj): logits → probability distribution. |
| **Cross-entropy** | −log(probability of the true class); averaged over examples. |
| **One-hot** | Label vector with 1 in the true class, 0 elsewhere. |
| **Log-sum-exp trick** | Subtract the max logit before exponentiating to avoid overflow. |
| **Temperature** | Divide logits by T to flatten (T > 1) or sharpen (T < 1) the distribution. |
| **One-vs-rest** | K independent binary classifiers instead of one joint softmax. |
| **Multinomial logistic regression** | Another name for softmax regression. |

#### What this page is built from

1. A. Ng, T. Ma et al., [Stanford CS229 lecture notes](https://cs229.stanford.edu/main_notes.pdf), §2.3 (multi-class classification: softmax, cross-entropy, gradient Eqs. 2.9–2.19) and §3 (GLMs).

2. scikit-learn, [Linear models user guide](https://scikit-learn.org/stable/modules/linear_model.html): multinomial logistic regression, solvers.

3. G. Hinton, O. Vinyals & J. Dean, [Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531), 2015: temperature softmax.

4. Meta, [Llama 3.1 8B config (a copy that needs no login)](https://huggingface.co/unsloth/Llama-3.1-8B/raw/main/config.json): hidden size 4,096, vocabulary 128,256.

5. Interview angle: [DataLemur ML interview questions](https://datalemur.com/blog/machine-learning-interview-questions); [AIM, 60 ML interview questions](https://analyticsindiamag.com/60-interview-questions-on-machine-learning).

Fruit data is illustrative; models are trained with a fixed seed and computed live in this page.
