# The Bias–Variance Trade-off

> Two models are equally wrong for opposite reasons. How do you tell which, and fix it?

- Track: Fundamentals › Classical ML › Core concepts
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/bias-variance/
- Before this: Linear Regression (`fundamentals/linear-regression`)
- Quiz topic: `mlcore`

## Intuition

### The situation

A straight-line model misses your delivery curve the same way every time. A degree-15 model fits its training data, but gives a completely different wiggle on each new sample. The interviewer asks:

> What is the bias–variance trade-off?

**Running example:** the food-delivery app predicts delivery time (minutes) from distance (km). The true relationship is a known smooth curve, and each delivery adds random noise with a standard deviation of 4 minutes (traffic, a slow lift, a chatty customer). A training set is 25 deliveries spread over 0–10 km. Because we know the truth, we can redraw the training set again and again and measure bias and variance exactly, something you can never do with real data.

#### Two different ways to be wrong

A straight-line model misses the curve: it's wrong in the same direction every time, no matter which 25 deliveries it sees. A wiggly degree-15 polynomial passes near every training delivery, but each new training set gives a completely different wiggle. Both have bad test error, for opposite reasons, and they need opposite fixes. Telling them apart is one of the most practical skills in ML, and the most-asked "fundamentals" interview topic.

### The idea

Think of archery. Bias is every arrow landing together in the wrong spot. Variance is arrows scattered all over the target. Making a model more flexible usually trades the first problem for the second.

[Figure: Two archery targets. On the left, arrows cluster tightly but away from the centre, which is high bias. On the right, arrows scatter widely around the centre, which is high variance.]

_Illustrative. Test error adds these two to noise you can't remove._

### Play

**Try to break it.** Start at degree 1 and move up to the highest degree. Watch the thin lines, and read bias² and variance at each step.

#### See bias and variance by refitting on many samples

Thin lines: the same model trained on 20 different samples of 25 deliveries. Thick green: the truth. Dashed: the average of 60 fits. Numbers average over 60 training sets and 41 test distances in 0.5–9.5 km.

Degree 1: all twenty lines agree with each other (variance 1.06) and all miss the curve the same way (bias² 8.1). Degree 15: the average of the fits sits almost exactly on the truth (bias² 0.07), but individual fits swing wildly, especially near the ends (variance 9.0). The best expected error is at **degree 4**: 18.9, against the floor of 16 set by noise.

**Now say why:** why does total test error fall and then rise, even though training error keeps falling?

## Maths

### Maths

#### In one breath

A model's expected error on new data splits into three parts: **bias²** (how far its _average_ prediction is from the truth: too simple a model is wrong the same way every time), **variance** (how much its predictions jump around when you train it on a different sample: too flexible a model chases noise), and **irreducible noise** (no model can remove it). Making a model more flexible lowers bias and raises variance, so test error is U-shaped in complexity. You move along the U with model size, regularisation and features, and you **shrink variance** with more data, averaging (bagging) or stronger regularisation. Modern over-parameterised models add a twist: past the point where they fit the training data exactly, test error can fall again (**double descent**). What you'll be able to do after this: state and read the decomposition, diagnose underfitting vs overfitting from train/validation curves, pick the right fix for each, and explain double descent without overclaiming.

#### The decomposition

Imagine training the same kind of model on many different training sets drawn from the same world. At a test input x, look at the prediction f̂(x) across all those models. For squared error:

$$ {\mathbb{E}\bigl[(y - \hat f(x))^2\bigr]} = {\bigl(\mathbb{E}[\hat f(x)] - f(x)\bigr)^2} + {\mathbb{E}\bigl[(\hat f(x) - \mathbb{E}[\hat f(x)])^2\bigr]} + {\sigma^2} $$

The standard decomposition for squared loss, e.g. Hastie, Tibshirani & Friedman, _The Elements of Statistical Learning_ §7.3; named and analysed for neural networks by Geman, Bienenstock & Doursat (1992). It's an identity: the cross terms vanish because the new label's noise is independent of the training set.

- **expected test error**: Averaged over training sets and over the noise in the new point’s label. What you actually care about.

- **bias²**: Squared gap between the average prediction (over training sets) and the true value f(x). Systematic error from the model being too simple or wrongly shaped.

- **variance**: How much predictions at x scatter around their own average when the training set changes. Error from the model being sensitive to the particular sample.

- **irreducible noise**: σ², the variance of the label around the truth. Here σ = 4 minutes, so 16. No model can beat it.

**Go deeper: why the cross terms vanish**

Write y − f̂ = (y − f) + (f − E f̂) + (E f̂ − f̂). Square and take expectations. y − f is the new point's noise: mean zero and independent of the training set, so it's uncorrelated with the other two terms. (f − E f̂) is a constant at fixed x, and E[E f̂ − f̂] = 0, so their product averages to zero. What's left is noise + bias² + variance. For other losses (0–1 loss in classification) the decomposition isn't this clean, but the intuition carries over.

#### The U-shaped test-error curve

Stacked: noise (grey, 16), bias² (orange) and variance (violet) for each polynomial degree, computed from 60 simulated training sets each.

| Degree | 1 | 3 | 4 | 6 | 10 | 15 |
|---|---|---|---|---|---|---|
| bias² | 8.14 | 7.15 | 0.46 | 0.04 | 0.05 | 0.07 |
| variance | 1.06 | 1.82 | 2.41 | 3.44 | 5.96 | 9.04 |
| total | 25.2 | 25.0 | 18.9 | 19.5 | 22.0 | 25.1 |

Bias falls off a cliff at degree 4, when the polynomial can finally bend the way the truth does; after that it's essentially zero, and each extra degree only adds variance. A useful rule from this: once bias is gone, extra flexibility is pure cost. A fresh-sample check agrees: simulated test error was 18.2 at degree 4 and 22.2 at degree 12.

#### Keep the flexible model, tame it with λ

Instead of choosing a smaller model, keep degree 15 and add a ridge penalty λ‖w‖² (see Regularized Linear Models). λ is a continuous dial between the two failure modes:

For the degree-15 model: λ = 10−6 gives total 22.4 (variance-dominated), λ = 0.01 gives **19.5**, and λ = 100 gives 56.9 (bias² 40: the curve is flattened). The regularised flexible model nearly matches the best hand-picked degree (18.9) without having to guess the right degree. That's why "big model + regularisation, tuned by validation" is the default modern recipe.

#### Variance shrinks with n; bias doesn't

Lines show 20 degree-12 fits at this n. With few points the flexible model is chaotic; with many, it settles onto the truth.

With 10 deliveries the degree-12 model's expected error is 512 (variance 493); with 200 it's 16.8, and both models approach the noise floor of 16. Variance falls roughly like 1/n; bias stays wherever the model's shape puts it (the straight line would stay biased forever). Practical reading of a **learning curve** (train and validation error against n): a big gap between them that shrinks with n means variance, so more data helps; both high and close together means bias, so more data won't help; change the model.

#### Double descent: past the interpolation threshold

Deep networks have far more parameters than training points and fit the training data exactly, yet generalise well. That seems to contradict the U-curve. Belkin, Hsu, Ma & Mandal (2019) showed the U is only the left half of the picture: as capacity grows, test error first follows the U, peaks around the **interpolation threshold** (just enough parameters to fit the training data exactly), and then **decreases again**, often below the classical sweet spot.

1. Below the threshold: the classical U. Test error falls (less bias), then rises (more variance) as training error drops.

2. Near the threshold the model has just enough parameters to pass through every training point, and the only way to do it is a wild, high-norm fit. Test error peaks.

3. Add even more parameters: many functions now fit the data exactly, and the training method picks a smooth, low-norm one among them. Test error falls again, while training error stays at zero.

4. The classical picture isn't wrong; it describes the left part of a longer curve.

Their evidence: random-feature models on 10,000 MNIST images peak at exactly N = n = 10,000 features, then improve "dramatically" past it, beating the classical sweet spot; two-layer networks, random forests and boosting show similar shapes [Belkin et al. 2019, pp. 4–8](https://arxiv.org/pdf/1812.11118#page=4). Their explanation: past the threshold, the minimum-norm interpolating solution acts as a strong implicit regulariser (smoothness). Caveats from the same paper: regularisation and early stopping hide the peak, which is why practitioners rarely see it. And it doesn't license dropping validation: you still pick models by held-out error.

## In practice

### In practice

#### The knobs that move you along the trade-off

| Knob | More flexible (less bias, more variance) | Less flexible |
|---|---|---|
| Model size | Higher polynomial degree, deeper trees, more layers | Fewer parameters |
| Regularisation | Smaller λ / larger C, less dropout | Larger λ, early stopping |
| Neighbours | Small k in k-NN | Large k |
| Features | More and richer features | Fewer features |

Two things reduce variance _without_ adding much bias: **more training data**, and **averaging many models** (bagging, random forests). Boosting does the opposite: it starts from high-bias weak learners and reduces bias step by step. See Random Forest and Gradient Boosting.

#### Diagnose, then fix

| Symptom | Diagnosis | Fixes |
|---|---|---|
| Train error high, validation ≈ train | High bias (underfitting) | Bigger model, better features, less regularisation, boosting, train longer |
| Train error low, validation much higher | High variance (overfitting) | More data, stronger regularisation, smaller model, bagging/ensembles, early stopping, data augmentation, feature selection |
| Both near a floor you can't beat | Irreducible noise | Better labels or new information (features), not a new model |

#### When it matters

##### Scenario: model is great offline, poor in production

Check leakage and distribution shift first (next lesson); if validation was honest and the gap is train vs validation, it's variance: regularise, simplify, get more data.

##### Scenario: more data didn't help

Both errors high and close: a bias problem. Add features or capacity; more rows of the same features won't move it.

To diagnose this on a real model, see learning curves and debugging.

### The answer that sounds right

#### "Pick the model with the lowest training error"

Training error falls every time you add flexibility, all the way to zero when the model can pass through every point. But low training error only shows low bias; it hides variance completely. A model that has memorised 25 deliveries, noise included, will be confidently wrong on the 26th. That's why model choice uses held-out data (the next lesson), never training error.

#### Caveats

- The clean three-way split holds for squared error. For classification losses there are several competing definitions; the intuition (systematic vs sample-driven error) still holds.

- You can't compute bias and variance on real data (you don't know the truth or have many training sets); you infer them from train/validation gaps and learning curves.

- "Complexity" isn't just parameter count: regularisation, early stopping and the training algorithm all change effective capacity. Double descent is the clearest example.

- Variance also comes from the training procedure (random seeds, data order), not only from the sample.

## Say it

### What is the bias–variance trade-off?

#### The interviewer pushes further

Follow-up 1 of 5

How do you tell bias from variance in practice?

Compare training and validation error, and plot learning curves. Large gap that narrows with more data: variance. Both high and close: bias.

Follow-up 2 of 5

How do bagging and boosting relate to bias and variance?

Bagging averages many high-variance, low-bias models (deep trees) to cut variance. Boosting adds weak, high-bias learners sequentially to cut bias, and needs regularisation (shrinkage, early stopping) to control variance.

Follow-up 3 of 5

How does regularisation affect the trade-off?

It constrains the model (shrinks weights), increasing bias slightly and reducing variance; tuned well, total error falls.

Follow-up 4 of 5

What is double descent?

Beyond the interpolation threshold, increasing capacity can lower test error again, because among the many interpolating solutions the training algorithm finds low-norm, smooth ones (Belkin et al. 2019). Explicit regularisation and early stopping usually hide the peak.

Follow-up 5 of 5

Does more data always help?

It reduces variance; it doesn't reduce bias. If you're bias-limited, more of the same data won't help.

#### The 30-second answer

For squared error, expected test error decomposes into bias squared, variance and irreducible noise. Bias is the error of the average model: too simple a model misses the pattern consistently. Variance is how much the model changes with the training sample: too flexible a model fits noise. Increasing complexity lowers bias and raises variance, so test error is U-shaped and we pick complexity with validation data. High bias shows as high training and validation error; high variance as a large gap between them. Fix bias with more capacity or features; fix variance with more data, regularisation, smaller models or bagging. Modern over-parameterised models can show double descent, where error falls again past the interpolation threshold.

**Go further**

#### What not to say

- "Overfitting means high bias." It's high variance.

- "Zero training error means the model is overfit." Usually, but interpolating models can generalise well (double descent).

- "You can measure bias and variance on your dataset directly." You can only estimate them indirectly.

**Key terms and sources**

Underfitting vs overfitting, the decomposition of test error, model complexity, regularisation, more data, and double descent · built from Hastie, Tibshirani & Friedman (ESL §2.9, §7.3), Geman, Bienenstock & Doursat (1992) and Belkin et al. (2019) · checked 28 Oct 2026

#### Evidence

##### Expected test error by degree (this page's simulation)

degree 1 (high bias)

25.2

degree 4 (sweet spot)

18.9

degree 15 (high variance)

25.1

degree 15 + ridge λ = 0.01

19.5

noise floor σ²

16.0

Mean squared error in minutes², 25 training deliveries, 60 simulated training sets. Lower is better. Illustrative.

#### Key terms

| Term | Meaning |
|---|---|
| **Bias** | Average prediction minus truth, over training sets. |
| **Variance** | Spread of predictions across training sets. |
| **Irreducible error** | Noise variance σ² in the labels. |
| **Underfitting / overfitting** | Bias-dominated / variance-dominated error. |
| **Learning curve** | Train and validation error against training-set size. |
| **Interpolation threshold** | Smallest capacity that fits the training data exactly. |
| **Double descent** | Test error falling again beyond the interpolation threshold. |

#### What this page is built from

1. T. Hastie, R. Tibshirani & J. Friedman, _The Elements of Statistical Learning_, 2nd ed., Springer 2009, §2.9 and §7.3 (the decomposition, model complexity).

2. S. Geman, E. Bienenstock & R. Doursat, "Neural networks and the bias/variance dilemma", _Neural Computation_ 4, 1992.

3. M. Belkin, D. Hsu, S. Ma & S. Mandal, "Reconciling modern machine-learning practice and the classical bias–variance trade-off", _PNAS_ 2019, [arXiv:1812.11118](https://arxiv.org/abs/1812.11118).

4. scikit-learn, [Validation curves and learning curves](https://scikit-learn.org/stable/modules/learning_curve.html) (tools for diagnosis).

Delivery data is simulated with a known true curve; every fit and decomposition is computed live in your browser.
