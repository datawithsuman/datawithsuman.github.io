# Derivatives, Gradients & the Chain Rule

> How backprop is just the chain rule, applied carefully.

- Track: Fundamentals › Maths for ML › Calculus and optimisation
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/derivatives-and-chain-rule/
- Related: Backpropagation Through a Network (`fundamentals/backpropagation`)
- Quiz topic: `calc`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-20 · Version: 103e335f16

## Intuition

### The situation

Your model has billions of weights, and nudging each one to measure its effect would take billions of passes for a single step. The interviewer asks:

> How does backpropagation use the chain rule?

**Running example:** a one-neuron model predicting whether a delivery will be late. Input x (distance, scaled), weight w, bias b; the neuron computes z = wx + b, then the probability a = σ(z) = 1/(1 + e−z), and the loss is the squared error L = (a − y)² against the true label y. Training needs ∂L/∂w and ∂L/∂b.

#### Which way should each weight move?

A model has thousands to billions of weights and one number, the loss, that says how wrong it is. To improve, each weight must move in the direction that reduces the loss, by an amount that matches how sensitive the loss is to it. Derivatives give exactly that sensitivity, and the chain rule makes it computable for deep, nested models.

### The idea

Think of a row of gears. Turn the first one, and the last one moves by the product of every gear ratio in between. The chain rule is that product. Backprop walks the gears backwards from the loss to find how much each weight matters.

[Figure: A chain from weight w to score z to probability a to loss L, with a slope on each link. Multiplying the slopes 1, 0.21 and 1.38 gives about 0.30.]

_From the lesson's one-neuron example, with w = 1, x = 1, b = −0.2 and y = 0._

### Play

**Try to break it.** Here z is the neuron's score before the sigmoid. Raise w and x until z is above about 5, for example w = 3 and x = 2.

#### Chain rule vs finite differences

Push |z| above about 5 (e.g. w = 3, x = 2): the sigmoid saturates, ∂a/∂z collapses towards 0 and the gradient vanishes even though the prediction may be badly wrong. That's the vanishing-gradient problem in miniature.

**Now say why:** why does the gradient vanish even when the prediction is badly wrong?

## Maths

### Maths

#### In one breath

A **derivative** answers "if I nudge this input a little, how much does the output change?". With many inputs (every weight in a model), each has a **partial derivative**, and together they form the **gradient**: an arrow pointing in the direction where the loss rises fastest. Training walks the other way. Models are long chains of simple steps (multiply, add, squash, compare to the target), and the **chain rule** says the sensitivity through a chain is the **product of the local sensitivities**. **Backpropagation** computes all of them in one backward pass by reusing shared products, so a gradient costs about as much as one forward pass. What you'll be able to do after this: differentiate a loss with respect to a weight by hand, explain what the gradient vector means, apply the chain rule on a computation graph, and check a gradient numerically.

#### Derivative, partial derivative, gradient

$$ {f^{\prime}(x)} = {\lim_{h\to 0} \tfrac{f(x+h) - f(x)}{h}}, \qquad {\nabla_\theta L = \bigl(\tfrac{\partial L}{\partial \theta_1}, \dots, \tfrac{\partial L}{\partial \theta_n}\bigr)} $$

MML §5.1–5.2. Useful rules: d(x²)/dx = 2x; dσ(z)/dz = σ(z)(1 − σ(z)); d(log x)/dx = 1/x.

- **derivative**: The slope of f at x: how much f changes per unit nudge of x, in the limit of tiny nudges.

- **tiny nudge h**: Compare f just to the right of x with f at x, divided by the size of the nudge.

- **gradient**: For a function of many variables, list one partial derivative per variable (hold the others fixed). The gradient points uphill, steepest first; its length is how steep.

#### The chain rule

$$ {\frac{\partial L}{\partial w}} = {\frac{\partial L}{\partial a}} \cdot {\frac{\partial a}{\partial z}} \cdot {\frac{\partial z}{\partial w}} $$

The multivariate chain rule, MML §5.2.2. Backpropagation applies it systematically from the loss backwards (Rumelhart, Hinton & Williams, _Nature_ 1986).

- **what we want**: How the loss changes when we nudge the weight.

- **loss vs prediction**: ∂L/∂a = 2(a − y): how wrong the prediction is, and in which direction.

- **sigmoid’s slope**: ∂a/∂z = σ(z)(1 − σ(z)): at most 0.25, tiny when the neuron is saturated.

- **pre-activation vs weight**: ∂z/∂w = x: a weight matters in proportion to its input.

#### Forward: compute values. Backward: multiply local slopes.

1. The neuron as a chain of simple steps: a computation graph.

2. Forward pass: plug in numbers. With w = 1, x = 1, b = −0.2 and a true label y = 0 (on time), the model predicts 0.69 probability of late and the loss is 0.48.

3. Backward pass: at each step compute the local slope. ∂L/∂a = 2(a − y) = 1.38; ∂a/∂z = a(1 − a) = 0.21; ∂z/∂w = x = 1 and ∂z/∂b = 1.

4. Multiply along the path: ∂L/∂w ≈ 0.30. Positive, so increasing w would increase the loss: training will decrease w. In a big network, the shared products (here ∂L/∂z) are computed once and reused for every weight feeding into z.

#### Why the gradient is steepest, and what happens at kinks

##### Why the gradient points the steepest way

The rate of change in a unit direction u is the **directional derivative**: ∇f · u. A dot product is largest when both vectors point the same way, so the steepest increase is along the gradient, and the steepest decrease is directly against it. At right angles to the gradient, the function doesn't change at all, at first order. That's why contour lines are perpendicular to gradients.

Example: if ∇f = (3, 4), its length of 5 is the steepest slope available. The direction (1, 0) gives a slope of only 3.

##### Points with no derivative

ReLU has a kink at 0, and so does |w| in L1 regularisation. Neither has a true derivative there. A **subgradient** is any slope that stays below the function at that point. For |w| at 0, anything from −1 to 1 qualifies. In practice, frameworks simply pick one value, such as 0 for ReLU at 0, and this causes little trouble as inputs rarely land exactly on the kink.

Next: automatic differentiation and Taylor series and curvature.

## In practice

### In practice

#### Gradients in practice

- **Autodiff:** PyTorch, JAX and TensorFlow record the computation graph in the forward pass and apply the chain rule backwards automatically (reverse-mode automatic differentiation).

- **Cost:** reverse mode computes the gradient of one scalar loss with respect to all parameters for a small constant multiple of the forward cost (Goodfellow et al. §6.5), which is why it beats finite differences by a factor of n.

- **Loss and activation choices:** cross-entropy with a sigmoid gives ∂L/∂z = a − y, cancelling the saturating σ′ term; squared error with a sigmoid doesn't. That's one reason classifiers use cross-entropy (see Entropy & KL).

- **Gradient checking:** compare backprop to finite differences on a tiny model when you write custom layers.

### The answer that sounds right

#### "Estimate each partial derivative by nudging each weight"

Finite differences, (L(w + h) − L(w))/h, work for one weight and are a great way to **check** a gradient. But a model with n weights needs n + 1 forward passes per step: for a 7-billion-parameter model, 7 billion passes to take one step. They're also numerically fragile: too large an h is inaccurate, too small loses precision to rounding. Backpropagation gets all n partial derivatives exactly for the price of roughly one forward and one backward pass.

## Say it

### How does backpropagation use the chain rule?

#### The interviewer pushes further

Follow-up 1 of 3

Derive ∂L/∂z for sigmoid + cross-entropy.

L = −[y log a + (1 − y) log(1 − a)], a = σ(z): ∂L/∂a = (a − y)/(a(1 − a)), ∂a/∂z = a(1 − a), so ∂L/∂z = a − y.

Follow-up 2 of 3

Why reverse mode, not forward mode?

Reverse mode costs about one backward pass per scalar output, whatever the number of inputs: ideal for one loss and millions of parameters. Forward mode costs one pass per input.

Follow-up 3 of 3

What causes vanishing and exploding gradients?

Multiplying many local derivatives: values below 1 shrink exponentially (saturated sigmoids/tanh), above 1 grow. Fixes: ReLU-type activations, careful initialisation, normalisation, residual connections, gradient clipping.

#### The 30-second answer

A derivative measures how much an output changes for a small change in an input; with many parameters, the gradient is the vector of partial derivatives and points in the direction of steepest increase of the loss, so we step against it. Models are compositions of simple functions, and the chain rule says the derivative through a composition is the product of local derivatives. Backpropagation applies the chain rule from the loss backwards over the computation graph, reusing intermediate products, so all parameter gradients cost about one extra pass. Saturating activations make local derivatives tiny, which causes vanishing gradients.

**Go further**

#### What not to say

- "Backprop is an optimisation algorithm." It computes gradients; the optimiser (SGD, Adam) uses them.

- "The gradient points to the minimum." It points to the steepest local increase.

**Key terms and sources**

Derivatives as sensitivity, partial derivatives, the gradient vector, the chain rule, computational graphs, and backpropagation on a single neuron · built from Deisenroth et al., _Mathematics for Machine Learning_ (ch. 5), Goodfellow et al., _Deep Learning_ (ch. 6.5) and Rumelhart, Hinton & Williams (1986) · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Derivative** | Local rate of change of a function. |
| **Partial derivative** | Rate of change in one variable, others fixed. |
| **Gradient** | Vector of partials; points uphill. |
| **Chain rule** | Derivative of a composition = product of local derivatives. |
| **Backpropagation** | Reverse-mode chain rule over a computation graph. |
| **Vanishing gradient** | Products of small local slopes shrink the gradient towards 0. |

#### Sources

1. M. P. Deisenroth, A. A. Faisal & C. S. Ong, _Mathematics for Machine Learning_, CUP 2020, [mml-book.github.io](https://mml-book.github.io/) (ch. 5).

2. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, §6.5, [deeplearningbook.org](https://www.deeplearningbook.org/).

3. D. Rumelhart, G. Hinton & R. Williams, "Learning representations by back-propagating errors", _Nature_ 323, 1986.
