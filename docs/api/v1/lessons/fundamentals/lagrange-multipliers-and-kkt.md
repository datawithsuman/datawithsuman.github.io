# Lagrange Multipliers and KKT

> What are Lagrange multipliers, and how do they explain PCA, SVMs and regularisation?

- Track: Fundamentals › Maths for ML › Calculus and optimisation
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/lagrange-multipliers-and-kkt/
- Before this: Convexity & Local Minima (`fundamentals/convexity-and-local-minima`)
- Related: Principal Component Analysis (`fundamentals/pca`), Support Vector Machines (`fundamentals/support-vector-machines`)
- Quiz topic: `calc`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: c5903ed087

## Intuition

### The situation

A colleague can state that PCA finds eigenvectors, and that SVMs depend on support vectors, but can't explain why. You're also asked to maximise a function under a limit on the total weights. The interviewer asks:

> What are Lagrange multipliers, and how do they explain PCA, SVMs and regularisation?

#### Why it matters

Much of ML is optimisation with limits. This one tool derives PCA, the SVM dual and why regularisation acts like a budget. See convexity first.

### The idea

Think of hiking along a fixed path, trying to get as low in a valley as you can. You keep going until the downhill direction points straight across the path, as there's nothing more to gain along it. If you're told how much lower you could get by moving the path slightly, that's the multiplier.

[Figure: The condition at the best point. Without a constraint, the gradient is zero. With an equality, the gradients are parallel. With an inequality, either it's tight, or its multiplier is zero.]

_Each adds one idea to the same question._

### Play

**Try to break it.** Slide c below 0, and watch λ. Then move your point along the line.

#### Find the constrained minimum

Minimising x² + y². The shaded side is allowed. Green is the best point, and the orange dot is your point on the line x + y = c. Circles are contours of the objective.

Slide c from **2** down below **0**. The unconstrained minimum at the origin becomes allowed, so the constraint stops mattering, and **λ falls to zero**. That's complementary slackness, and it's exactly why points far from an SVM's margin don't count.

**Now say why:** why does the multiplier become zero when the constraint isn't tight?

## Maths

### Maths

#### In one breath

To optimise under a constraint, look for the point where the objective's gradient and the constraint's gradient line up: **∇f = λ∇g**. Otherwise you could slide along the constraint and improve. The multiplier **λ** is the price of the constraint: how much the best value changes if you loosen it. For inequalities, the **KKT conditions** add that a constraint that isn't tight has λ = 0. This explains why PCA gives eigenvectors, and why only support vectors matter in an SVM.

#### Optimising with limits

##### Why the gradients line up

Imagine walking along a road, trying to reach the lowest point of a valley, while staying on the road. If the valley's downhill direction has any part along the road, you can keep going. You stop only when downhill points straight across the road. That means the two gradients are parallel.

##### The recipe

1. Write the Lagrangian: 𝓛(x, λ) = f(x) − λ(g(x) − c).

2. Set its derivative with respect to x to zero: ∇f = λ∇g.

3. The derivative with respect to λ gives back the constraint: g(x) = c.

4. Solve them together.

##### Inequalities: the KKT conditions

For minimising f, subject to h(x) ≤ 0:

| Condition | Meaning |
|---|---|
| **Stationarity** | The gradients balance: ∇f + μ∇h = 0. |
| **Primal feasibility** | The constraint holds: h(x) ≤ 0. |
| **Dual feasibility** | The multiplier isn't negative: μ ≥ 0. |
| **Complementary slackness** | μ × h(x) = 0: either the constraint is tight, or its multiplier is zero. |

##### Three ML results from one tool

- **PCA:** maximise wᵀΣw, with wᵀw = 1. Stationarity gives Σw = λw, so w is an eigenvector, and the variance equals λ.

- **SVM:** complementary slackness means points away from the margin have zero multiplier. So only support vectors decide the boundary.

- **Regularisation:** minimising loss with ‖w‖² ≤ t is equivalent to minimising loss + λ‖w‖² for a matching λ. The penalty weight is the price of the budget.

#### The maths

$$ {\mathcal{L}(x,\lambda)} = {f(x)} - {\lambda}\,{(g(x) - c)}, \qquad {\nabla f = \lambda \nabla g}, \qquad {\lambda = \frac{d f^*}{d c}} $$

Worked example: minimise x² + y², with x + y = c. Then 2x = λ and 2y = λ, so x = y = c/2, λ = c and f* = c²/2. Check: df*/dc = c = λ.

- **the Lagrangian**: Combines objective and constraint into one function.

- **the objective**: What you want to optimise.

- **the multiplier**: One number per constraint. It’s found as part of the solution.

- **the constraint**: Zero when the constraint is met.

- **the condition at the best point**: The gradients are parallel, so you can’t improve by moving along the constraint.

- **what λ means**: How fast the best value changes as you loosen the constraint. It’s often called the shadow price.

## In practice

### In practice

#### In practice

- **Read the multipliers:** a large λ means that constraint is costing you a lot, and is worth loosening.

- **The dual problem:** optimising over multipliers can be easier. For SVMs, the data appears only as dot products, which is what makes kernels possible.

- **Guarantees:** KKT conditions are necessary under mild assumptions, and sufficient for convex problems. For non-convex ones, they only identify candidates.

- **In deep learning:** hard constraints are rare, so people use penalties or projection. Constrained RL and fairness methods use multipliers directly.

### The answer that sounds right

#### "Add the constraint as a penalty, and it's the same thing"

It sounds right, and it often works. But a fixed penalty only encourages the constraint, and doesn't guarantee it unless you pick the right weight. Lagrange multipliers find exactly that weight. For convex problems, penalty and budget forms match for some λ, but you don't know which one in advance.

## Say it

### What are Lagrange multipliers, and how do they explain PCA, SVMs and regularisation?

#### The interviewer pushes further

Follow-up 1 of 3

Derive PCA using Lagrange multipliers.

Maximise wᵀΣw with wᵀw = 1. The Lagrangian is wᵀΣw − λ(wᵀw − 1). Setting its gradient to zero gives 2Σw − 2λw = 0, so Σw = λw. So w is an eigenvector, and the variance wᵀΣw = λ. The largest variance comes from the largest eigenvalue.

Follow-up 2 of 3

Why do only support vectors matter in an SVM?

Each point has a multiplier. Complementary slackness says the multiplier times the slack of its margin constraint equals zero. Points strictly outside the margin aren't tight, so their multiplier is zero, and they drop out of the solution. Only points on the margin or violating it have non-zero multipliers.

Follow-up 3 of 3

How is ridge regression a constrained problem?

Minimising the loss, with ‖w‖² ≤ t, has the Lagrangian loss + λ(‖w‖² − t). For a given t, there's a matching λ, and the −λt term doesn't affect the weights. So the penalty form and the budget form are the same problem, for convex losses, and a smaller budget means a larger λ.

#### The 30-second answer

At the best point under a constraint, the objective's gradient must be parallel to the constraint's. Otherwise you could slide along the constraint and improve. So I set grad f equal to lambda grad g, and solve with the constraint. Lambda is the shadow price: how much the best value changes if I loosen the constraint. For inequalities, the KKT conditions add complementary slackness: either the constraint's tight, or its multiplier is zero. That gives PCA as an eigenvector problem, and it's why only support vectors matter in an SVM.

**Key terms and sources**

Optimising under constraints: the Lagrangian, what multipliers mean, the KKT conditions and complementary slackness, with PCA, SVM and regularisation as examples. · checked 6 Nov 2026

#### Sources

- [Deisenroth, Faisal and Ong, Mathematics for Machine Learning](https://mml-book.github.io/)

- [Goodfellow et al., Deep Learning, slides for chapter 4](https://mnassar.github.io/deeplearninghandbook/slides/04_numerical.pdf)

- [Boyd and Vandenberghe, Introduction to Applied Linear Algebra](https://web.stanford.edu/~boyd/vmls/)

- PCA on this site

- SVMs on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
