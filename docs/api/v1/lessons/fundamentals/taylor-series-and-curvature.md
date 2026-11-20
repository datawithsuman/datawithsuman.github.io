# Taylor Series and Curvature

> What does a Taylor expansion tell you about optimisation, and why does curvature limit the learning rate?

- Track: Fundamentals › Maths for ML › Calculus and optimisation
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/taylor-series-and-curvature/
- Before this: Derivatives, Gradients & the Chain Rule (`fundamentals/derivatives-and-chain-rule`), Matrix Calculus (`fundamentals/matrix-calculus`)
- Quiz topic: `calc`

## Intuition

### The situation

Your training was stable at a learning rate of 0.001, but it blows up at 0.01. A teammate asks why a small change can cause that, and whether there's a principled limit. The interviewer asks:

> What does a Taylor expansion tell you about optimisation, and why does curvature limit the learning rate?

#### Why it matters

Taylor is the idea behind most of optimisation. It tells you why gradients work only locally, why learning rates have a limit, and how saddle points and Newton's method fit together. See derivatives and matrix calculus first.

### The idea

Think of driving at night with short-range headlights. The road ahead looks straight, so you can trust that for a short distance. If the road bends sharply, you can only safely go a little before the picture is wrong. The straight-road picture is the gradient, and the bend is the curvature.

[Figure: Local approximations. First order gives a line, which leads to gradient descent. Second order gives a bowl or saddle, which leads to Newton's method.]

_Each order adds detail, but only near the point you started from._

### Play

**Try to break it.** Make the step large. Then move the point near x = 0, where the curve bends the other way.

#### Approximate a curve

The curve is f(x) = x⁴ − 3x² + x, a made-up function. Blue is the tangent, and green is the second-order approximation. The red dot is where you start, and the purple dot is where the step lands. Safe learning rate is 2 ÷ f″(x), valid only near this point.

Move to a point near **x = 0**. Curvature is negative, so the approximation opens downwards, and there's no safe-rate formula here. Then make the step large, and see both approximations leave the curve. That's why learning rates must stay small on a curving loss.

**Now say why:** why must the learning rate shrink as curvature grows?

## Maths

### Maths

#### In one breath

Near a point, any smooth function looks like a simple polynomial. The **first-order Taylor approximation** is a straight line, and it's why gradient descent works: for a small step, the loss falls along the negative gradient. The **second-order** version adds curvature through the Hessian. Curvature is what limits your learning rate: on a curve with second derivative L, steps above **2/L** diverge.

#### Local pictures of a function

| Order | Shape | It tells you | Leads to |
|---|---|---|---|
| **First** | Tangent line or plane | Which way is downhill. | Gradient descent |
| **Second** | A bowl or saddle | How fast the slope changes. | Newton's method |

##### Why gradient descent lowers the loss

By first-order Taylor, L(w + Δ) ≈ L(w) + ∇Lᵀ Δ. Choose Δ = −η∇L, and the change is −η‖∇L‖², which is negative. So a small enough step always reduces the loss, unless the gradient is zero. "Small enough" is the catch: the line is only accurate nearby.

##### Why curvature limits the learning rate

Take a simple quadratic with second derivative L, so L(w) = ½Lw². A gradient step gives w ← (1 − ηL)w.

- **η below 1/L:** moves steadily towards the minimum.

- **η between 1/L and 2/L:** overshoots, but still shrinks.

- **η above 2/L:** each overshoot is bigger than the last, and the loss explodes.

With many dimensions, the sharpest direction sets the limit, so the largest Hessian eigenvalue decides the largest safe learning rate. Flat directions then move slowly, which is the problem of ill-conditioning.

##### Reading the Hessian at a flat point

When the gradient is zero, the second-order term decides what you have. All-positive eigenvalues mean a minimum, all-negative a maximum and mixed signs a saddle. See positive definite matrices.

#### The maths

$$ {f(x+\Delta)} \approx {f(x)} + {\nabla f(x)^\top \Delta} + {\tfrac{1}{2}\Delta^\top H(x)\,\Delta} $$

Worked example: f(x) = x² near x = 3, with Δ = 0.1. Value 9, slope term 0.6, curvature term 0.01. The total of 9.61 is exactly 3.1², since a quadratic’s approximation is exact.

- **the value nearby**: What you’d like to estimate, a small step Δ away.

- **where you are**: The starting value.

- **the slope term**: The first-order change. This gives gradient descent.

- **the curvature term**: The second-order change, using the Hessian H. This gives Newton’s method, and it decides what kind of flat point you’re at.

## In practice

### In practice

#### In practice

- **When training diverges:** the learning rate is probably above 2 divided by the sharpest curvature. Lower it, or use warm-up, which lets the model reach flatter regions first.

- **Sharp vs flat minima:** the sharper the region, the smaller the safe step. Large learning rates can't settle in very sharp regions.

- **You rarely compute the Hessian:** Hessian-vector products or tracking the loss are far cheaper ways of learning about curvature.

- **Non-smooth losses:** Taylor assumes smoothness. Clipping and normalising tame sudden changes.

### The answer that sounds right

#### "The gradient points downhill, so a bigger step gets there faster"

It sounds right, as the direction is right. But the gradient is only accurate nearby. On a curved loss, a big step passes the minimum and lands higher up the other side. Above 2/L, each step is worse than the last. Direction and step size are separate questions.

## Say it

### What does a Taylor expansion tell you about optimisation, and why does curvature limit the learning rate?

#### The interviewer pushes further

Follow-up 1 of 3

Why is the safe limit 2/L and not 1/L?

Each step multiplies the distance by 1 − ηL. At 1/L, you land exactly on the minimum in one step on a quadratic. Between 1/L and 2/L you overshoot, but the size of 1 − ηL stays below 1, so you still converge. Above 2/L it exceeds 1, and you diverge.

Follow-up 2 of 3

How does ill-conditioning follow from this?

The sharpest direction limits your learning rate, while the flattest direction wants a large one. With a large ratio between them, the condition number, progress along flat directions is painfully slow, and you get zig-zagging. Momentum and second-order methods address this.

Follow-up 3 of 3

Does the first-order approximation guarantee a lower loss?

Only for small enough steps. It's a local statement, and curvature can make a larger step go uphill. That's why training can diverge, and why methods like line search exist.

#### The 30-second answer

A Taylor expansion approximates a function near a point with a polynomial. First order is the gradient term, and it's why gradient descent works: a small step along the negative gradient changes the loss by minus eta times the squared gradient norm. Second order adds curvature, through the Hessian. On a quadratic with second derivative L, a gradient step multiplies the distance by one minus eta L, so above 2 over L it diverges. In many dimensions, the largest Hessian eigenvalue sets the limit. At a flat point, the Hessian's signs distinguish minima and saddles.

**Key terms and sources**

First and second-order Taylor approximations, what the Hessian says about curvature, and how they explain gradient descent, learning rate limits and saddle points. · checked 6 Nov 2026

#### Sources

- [Deisenroth, Faisal and Ong, Mathematics for Machine Learning](https://mml-book.github.io/)

- [Boyd and Vandenberghe, Introduction to Applied Linear Algebra](https://web.stanford.edu/~boyd/vmls/)

- [Goodfellow et al., Deep Learning, slides for chapter 4](https://mnassar.github.io/deeplearninghandbook/slides/04_numerical.pdf)

- Learning rate schedules on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
