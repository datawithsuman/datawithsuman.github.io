# Convexity & Local Minima

> When does the starting point decide where you end up?

- Track: Fundamentals › Maths for ML › Calculus and optimisation
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/convexity-and-local-minima/
- Before this: Gradient Descent, Momentum & Adam (`fundamentals/gradient-descent`)
- Quiz topic: `calc`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-20 · Version: e6e707c45d

## Intuition

### The situation

Logistic regression gives you the same answer on every run, but your neural network ends somewhere different with each seed. The interviewer asks:

> What does convexity guarantee, and which models have a convex loss?

**Running example:** two one-parameter losses for a delivery-time model: a convex bowl, L(θ) = θ² − θ + 1, and a non-convex loss with two valleys, L(θ) = θ⁴ − 3θ² + θ. Gradient descent (η = 0.01, 500 steps) starts from wherever you choose.

#### Did training find the best model, or just a nearby dip?

Gradient descent only knows the local slope. If the loss has several valleys, it settles in whichever one it starts near. Knowing whether a loss is convex tells you whether that's a risk at all, which is why "is this problem convex?" is a classic interview question.

### The idea

Think of dropping a marble. In a smooth bowl, it always ends at the same lowest point. On a bumpy surface, it settles in whichever dip is nearest, and that may not be the deepest one.

[Figure: Left: a smooth bowl with one marble at the single lowest point. Right: a bumpy curve with two dips, one deeper, and marbles settled in each.]

_Illustrative. The red marble is stuck in a local minimum, and its slope there is zero, so it has no reason to move._

### Play

**Try to break it.** Choose the non-convex loss, start at θ = 0, then start at θ = 0.5. Then switch to the convex loss and try any start you like.

#### Where does gradient descent end up?

Gradient descent with η = 0.01 for 500 steps. Dots show every 20th step.

**Now say why:** why does the same algorithm land in different places on one loss, but not on the other?

## Maths

### Maths

#### In one breath

A function is **convex** if it's bowl-shaped everywhere: the straight line between any two points on its graph lies above the graph. For convex losses, any point where the gradient is zero is the **global** minimum, so gradient descent (with a sensible step) can't get stuck, and where you start doesn't matter. Linear regression (squared error), logistic regression (log loss), ridge, lasso and SVMs are convex. Neural networks are **not**: their losses have many minima and saddle points, so initialisation, learning rate and randomness affect the answer. In very high dimensions, saddle points are a bigger nuisance than bad local minima. What you'll be able to do after this: define convexity, test it with the second derivative or Hessian, say which classic models are convex, and explain what non-convexity means for training networks.

#### The definition and two tests

$$ {f(\lambda\theta + (1-\lambda)\theta^{\prime})} \le {\lambda f(\theta) + (1-\lambda) f(\theta^{\prime})} $$

Boyd & Vandenberghe, _Convex Optimization_, §3.1, [free online](https://web.stanford.edu/~boyd/cvxbook/).

- **the function between two points**: Evaluate f somewhere on the segment between θ and θ′ (λ between 0 and 1).

- **the straight line between them**: The chord: the weighted average of the two endpoint values. Convex means the function never rises above its chords.

- **Second-derivative test (1-D):** f″(θ) ≥ 0 everywhere ⇔ convex. θ² has f″ = 2: convex. θ⁴ − 3θ² + θ has f″ = 12θ² − 6, negative near 0: not convex.

- **Hessian test (many parameters):** the matrix of second derivatives is positive semi-definite everywhere (all eigenvalues ≥ 0; see Eigenvalues).

- **Building blocks:** sums of convex functions are convex; a convex function of a linear function (like log loss of w·x) is convex; max of convex functions is convex.

#### For convex functions, local = global

If a convex function had a local minimum that wasn't global, the chord from it to the better point would dip below the function near the local minimum, which convexity forbids. So any point with zero gradient is a global minimum, and strictly convex functions have exactly one. That's why convex models give the same answer from any starting point, and why their training is "solved" rather than an art.

#### How curvature sets a safe step size

If a loss never curves more sharply than L, called **L-smooth**, then gradient descent is guaranteed to reduce it with any step size below 2/L, and 1/L is the classic safe choice. On a convex loss, that means reaching the minimum, and **strong convexity**, a minimum curvature, makes it converge at a steady rate.

The ratio of largest to smallest curvature is the condition number, and it sets how slowly gradient descent progresses.

Next: Taylor series and curvature derives this limit, Newton's method removes the dependence on condition number, and Lagrange multipliers add constraints.

## In practice

### In practice

#### Which ML problems are convex?

| Model / loss | Convex in its parameters? |
|---|---|
| Linear regression (MSE), ridge, lasso | Yes |
| Logistic / softmax regression (log loss), with L1/L2 | Yes |
| Linear and kernel SVMs (hinge loss + L2) | Yes |
| k-means (inertia over centroids and assignments) | No: local minima, hence k-means++ and restarts |
| Gaussian mixtures (likelihood) | No: EM finds local optima |
| Neural networks (any loss) | No: hidden layers make the loss non-convex |
| Decision trees | Not even continuous: greedy search instead |

See the lessons on Logistic Regression, SVMs, k-Means and GMMs.

#### Why deep learning works anyway

- **Saddle points, not bad minima:** in high dimensions a zero-gradient point is far more likely to be a saddle (down in some directions, up in others) than a local minimum. Dauphin et al. (2014) argue that saddle points, not local minima, are the main source of slow training in high-dimensional non-convex problems [arXiv:1406.2572](https://arxiv.org/abs/1406.2572). Noise from mini-batches and momentum help escape them.

- **Many good minima:** in large over-parameterised networks, different runs reach different weights with similar test performance (see double descent).

- **Practical consequences:** results depend on initialisation and seeds, so report variance across seeds; learning-rate schedules and warm-up matter; ensembles of differently-seeded models help.

### The answer that sounds right

#### "Gradient descent always finds the minimum"

On the non-convex loss, gradient descent started anywhere left of θ ≈ 0.17 (the hump between the valleys) reaches the deep valley at θ ≈ −1.30 with loss −3.51. Started anywhere right of it, it stops at θ ≈ 1.13 with loss −1.07, a local minimum three times worse, and its gradient there is exactly zero, so it has no reason to move. Same algorithm, same learning rate: the answer depends on the starting point.

## Say it

### What does convexity guarantee, and which models have a convex loss?

#### The interviewer pushes further

Follow-up 1 of 3

Why is logistic regression convex?

Log loss −y log σ(w·x) − (1 − y) log(1 − σ(w·x)) is a convex function of the linear score w·x, and a convex function of a linear map is convex; the sum over examples is convex. Its Hessian XᵀSX (S diagonal with σ(1 − σ)) is positive semi-definite.

Follow-up 2 of 3

Is MSE with a neural network convex?

No: the network output is a non-linear function of the weights, so even a convex loss of the output gives a non-convex loss in the weights.

Follow-up 3 of 3

How do you know you're at a minimum vs a saddle?

Gradient zero and Hessian positive definite → local minimum; Hessian with both positive and negative eigenvalues → saddle.

#### The 30-second answer

A function is convex if the line segment between any two points on its graph lies above the graph; equivalently its Hessian is positive semi-definite everywhere. For convex losses every local minimum is global, so gradient-based training converges to the best solution regardless of initialisation. Linear and logistic regression, ridge, lasso and SVMs are convex. Neural networks, k-means and Gaussian mixtures are not, so results depend on initialisation and can stop at local optima or slow down near saddle points; in high dimensions saddle points are the bigger problem, and SGD noise and momentum help.

**Go further**

#### What not to say

- "Neural networks get stuck in bad local minima all the time." In large networks, saddle points and plateaus are the more common issue.

- "Convex means the function has a minimum." eˣ is convex with no minimum.

**Key terms and sources**

Convex functions, the second-derivative and Hessian tests, why a local minimum of a convex loss is global, which ML losses are convex, and local minima and saddle points in neural networks · built from Boyd & Vandenberghe, _Convex Optimization_, Deisenroth et al., _MML_ (ch. 7.3) and Dauphin et al. (2014) · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Convex function** | Lies below its chords; bowl-shaped. |
| **Strictly convex** | Strictly below its chords; unique minimum. |
| **Local minimum** | Lowest point in a neighbourhood. |
| **Global minimum** | Lowest point overall. |
| **Saddle point** | Zero gradient, but curving up in some directions and down in others. |
| **Positive semi-definite Hessian** | All second-derivative eigenvalues ≥ 0: the multivariate convexity test. |

#### Sources

1. S. Boyd & L. Vandenberghe, _Convex Optimization_, Cambridge University Press 2004, [web.stanford.edu/~boyd/cvxbook](https://web.stanford.edu/~boyd/cvxbook/) (ch. 3).

2. M. P. Deisenroth, A. A. Faisal & C. S. Ong, _Mathematics for Machine Learning_, CUP 2020, §7.3.

3. Y. Dauphin et al., "Identifying and attacking the saddle point problem in high-dimensional non-convex optimization", NeurIPS 2014, [arXiv:1406.2572](https://arxiv.org/abs/1406.2572).
