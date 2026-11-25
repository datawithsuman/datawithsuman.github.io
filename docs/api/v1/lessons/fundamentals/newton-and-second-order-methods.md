# Newton's Method and Second-Order Optimisation

> What is Newton's method, and why isn't it used to train deep networks?

- Track: Fundamentals › Maths for ML › Calculus and optimisation
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/newton-and-second-order-methods/
- Before this: Taylor Series and Curvature (`fundamentals/taylor-series-and-curvature`), Gradient Descent, Momentum & Adam (`fundamentals/gradient-descent`)
- Related: Gradient Boosting (`fundamentals/gradient-boosting`)
- Quiz topic: `calc`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: 5b3fd96b53

## Intuition

### The situation

A colleague says Newton's method converges in very few steps and doesn't need a learning rate, so why not train your deep model with it? Meanwhile, your logistic regression solver uses something called L-BFGS. The interviewer asks:

> What is Newton's method, and why isn't it used to train deep networks?

#### Why it matters

This is a common interview question, and the answer explains why deep learning uses Adam, not a seemingly better method. These ideas are still used directly in logistic regression and gradient boosting. See Taylor series first.

### The idea

Think of hiking down a valley. Gradient descent only feels the slope underfoot, so it takes cautious steps. Newton also has a map of how the land curves, and jumps straight to the bottom of the local bowl. It's a great jump, but drawing that map for a million-dimensional land is impossibly costly.

[Figure: Comparing methods. Gradient descent uses the slope, and it's cheap per step. Newton uses exact curvature, and is costly. L-BFGS approximates curvature from history, and sits between them.]

_Newton wins per step, and loses on what each step costs._

### Play

**Try to break it.** Raise the condition number, then raise the weights.

#### Compare the two methods

On a pure quadratic, using gradient descent's best fixed learning rate, to reduce the error a million times. Real losses aren't quadratic, so Newton needs several steps. Assumes 4 bytes per number.

Raise the condition number: gradient descent's steps grow in proportion, and Newton's stay at one. Now raise the weights: the memory needed for the Hessian grows a hundred times for every tenfold increase. Newton wins per step, and loses on what each step costs.

**Now say why:** why does the Hessian's memory grow so much faster than the gradient's?

## Maths

### Maths

#### In one breath

Gradient descent only uses slope, so it needs a learning rate and struggles when curvature differs by direction. **Newton's method** jumps to the minimum of the local quadratic: w − H⁻¹g. It's scale-free and converges very fast near a solution. But with n weights, the Hessian has **n² entries and n³ solving cost**, and it can head towards saddle points. So deep learning sticks to first-order methods, while **L-BFGS** and Newton-style boosting work well on smaller or convex problems.

#### Using curvature

##### Where the step comes from

Take the second-order Taylor approximation, and jump straight to its minimum by setting its gradient to zero: g + HΔ = 0, so Δ = −H⁻¹g. It scales each direction by its curvature, taking long steps where the loss is flat and short ones where it's sharp.

##### How it compares

| | Gradient descent | Newton | L-BFGS |
|---|---|---|---|
| **Uses** | Slope | Slope and exact Hessian | Slope and recent history |
| **Learning rate** | Needs tuning | Natural step of 1 | Usually a line search |
| **Memory** | n | n² | About 2mn, for m past steps |
| **Cost per step** | n, per example | n³ to solve | About mn |
| **Near the solution** | Steady | Very fast, doubling correct digits | Fast |

##### Why deep learning doesn't use it

- **Size:** a million weights gives a trillion Hessian entries.

- **Saddle points:** Newton looks for any flat point, so with mixed-sign curvature, it can move towards a saddle.

- **Noise:** mini-batches give noisy curvature estimates, and approximate curvature methods are sensitive to this.

##### Where these ideas are used

- **Logistic regression:** Newton's method, as IRLS, and L-BFGS are common solvers, as the problem is convex and small enough.

- **Gradient boosting:** XGBoost-style trees use first and second derivatives of the loss per example. See gradient boosting.

- **Adam:** it divides by a running estimate of squared gradients, which acts as a rough per-weight scale. It isn't true curvature, but it has a similar spirit.

#### The maths

$$ {w_{t+1}} = w_t - {H^{-1}}\,{g}, \qquad {w_{t+1}} = w_t - (H + \lambda I)^{-1} g $$

Example: f(x) = x² − 4x. At x = 10, g = 16 and H = 2, so the step is 8, and you land on the minimum at x = 2 in one go.

- **Newton’s update**: Jumps to the minimum of the local bowl. On a true quadratic, it lands there in one step.

- **the inverse Hessian**: Shrinks steps in sharp directions, and stretches them in flat directions. In practice, you solve a system rather than computing an inverse.

- **the gradient**: Which way the loss changes, as in gradient descent.

- **damped Newton**: Adding λI keeps the system well behaved when curvature is small or negative. Larger λ makes it act more like gradient descent.

## In practice

### In practice

#### In practice

- **Small, convex problems:** L-BFGS is often a great default, because it needs no learning rate.

- **Don't store the Hessian:** Hessian-free methods use conjugate gradient with Hessian-vector products, so they only need matrix-vector operations.

- **Natural gradient:** similar in spirit, using the Fisher matrix. K-FAC approximates it for neural networks.

- **Damping and line search:** plain Newton can overshoot far from the solution. Both make it more robust.

- **Full batch:** L-BFGS expects fairly accurate gradients, so it suits full or large batches rather than noisy ones.

### The answer that sounds right

#### "Newton's is better because it converges in fewer steps"

It sounds right, as fewer steps looks like less work. But steps aren't the cost: each one needs the full Hessian. With a million weights, that's four terabytes, plus an n³ solve, while a gradient step costs almost nothing. What matters is total time to a good result, and on large models, first-order methods win.

## Say it

### What is Newton's method, and why isn't it used to train deep networks?

#### The interviewer pushes further

Follow-up 1 of 3

Why does Newton's method have no learning rate?

The Hessian scales each direction by its curvature, so it already knows how far to go in the quadratic model. A natural step size is 1. In practice, damping or a line search reduce it when the approximation isn't trustworthy, particularly far from the solution.

Follow-up 2 of 3

Why might Newton's method be attracted to saddle points?

It solves for where the gradient is zero, and a saddle has zero gradient too. With a negative curvature direction, the step can go towards the saddle instead of away. Gradient descent doesn't have this attraction. Damping or using absolute curvature can help.

Follow-up 3 of 3

How does XGBoost use second derivatives?

It approximates the loss with a second-order Taylor expansion around current predictions. Each example gives a gradient and a Hessian, and these determine leaf values and how good a split is. It makes the same procedure work for many losses, and it's cheap because the Hessian is per example, not per weight.

#### The 30-second answer

Newton's method jumps to the minimum of the local quadratic, using w minus H inverse g. It accounts for curvature, so it needs no learning rate, and converges very quickly near a solution. It's not used for deep networks for three reasons. With n weights, the Hessian takes n squared memory and n cubed to solve. It can move towards saddle points, since it finds any flat point. And mini-batch curvature is noisy. So we use first-order methods. L-BFGS approximates it using recent gradients, and it works well on convex problems. XGBoost also uses second derivatives per example.

**Key terms and sources**

Newton's step, why it handles ill-conditioning, its cost, quasi-Newton methods like L-BFGS, and where second-order ideas are used in ML, such as XGBoost. · checked 6 Nov 2026

#### Sources

- [Goodfellow et al., Deep Learning, slides for chapter 8](https://mnassar.github.io/deeplearninghandbook/slides/08_optimization.pdf)

- [CS231n, Neural Networks Part 3](https://cs231n.github.io/neural-networks-3/)

- [Boyd and Vandenberghe, Introduction to Applied Linear Algebra](https://web.stanford.edu/~boyd/vmls/)

- [XGBoost paper, Chen and Guestrin (2016)](https://arxiv.org/abs/1603.02754)

- Taylor series on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
