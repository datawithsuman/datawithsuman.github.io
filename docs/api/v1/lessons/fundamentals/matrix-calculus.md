# Matrix Calculus

> How do you differentiate a matrix expression, like the least-squares loss?

- Track: Fundamentals › Maths for ML › Linear algebra
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/matrix-calculus/
- Before this: Matrix Multiplication and Tensor Shapes (`fundamentals/matrix-multiplication-and-tensor-shapes`), Derivatives, Gradients & the Chain Rule (`fundamentals/derivatives-and-chain-rule`)
- Related: Backpropagation Through a Network (`fundamentals/backpropagation`)
- Quiz topic: `la`

## Intuition

### The situation

In an interview, you're asked to derive the least-squares solution on a whiteboard. Your hand-written gradient for a custom loss also trains badly, and you suspect a missing transpose. The interviewer asks:

> How do you differentiate a matrix expression, like the least-squares loss?

#### Why it matters

Interviews often ask you to derive a gradient, and every training loop relies on them. Thinking in shapes turns a messy sum into a few lines. This uses derivatives and the chain rule and tensor shapes.

### The idea

Think of a mixing desk with hundreds of sliders, and one volume meter. The gradient tells you, for each slider, how much the meter moves if you nudge it. Calculus works as usual, one slider at a time. Matrices are just tidy bookkeeping, and their shapes tell you when you've made a mistake.

[Figure: Derivatives by shape. A scalar of a vector has a gradient. A vector of a vector has a Jacobian. The second derivative of a scalar has a Hessian.]

_The shape tells you which derivative you've got._

### Play

**Try to break it.** Move the weights towards (1, 2), and compare the formula with the numerical value.

#### Check the formula numerically

Fixed example: X = [[1, 0], [1, 1], [1, 2]] and y = (1, 3, 5), which fits exactly at w = (1, 2). The numerical gradient nudges each weight by 0.0001 either way. This check also finds bugs in hand-written gradients.

Move the weights towards **(1, 2)**, and the gradient falls to zero as the loss does. Comparing against nudged values like this is called a **gradient check**, and it's the standard way to test a gradient written by hand.

**Now say why:** why does the gradient vanish exactly at the best fit?

## Maths

### Maths

#### In one breath

Matrix calculus is ordinary calculus, organised by **shape**. A scalar function of a vector has a **gradient**, the same shape as the vector. A vector function of a vector has a **Jacobian**. The second derivative of a scalar gives a **Hessian**. A few identities cover most ML, like ∇‖Xw − y‖² = 2Xᵀ(Xw − y). Setting this to zero derives least squares, and multiplying Jacobians is all **backpropagation** does.

#### Derivatives by shape

| Input → output | Derivative | Shape | Example |
|---|---|---|---|
| Vector → scalar | **Gradient** | n | Loss with respect to weights. |
| Vector → vector | **Jacobian** | m × n | A layer's outputs with respect to its inputs. |
| Vector → scalar, twice | **Hessian** | n × n | The curvature of the loss. |

##### Identities worth knowing

| Function | Gradient with respect to x |
|---|---|
| aᵀx | a |
| xᵀx | 2x |
| Ax | A (a Jacobian) |
| xᵀAx | (A + Aᵀ)x, or 2Ax when A is symmetric |
| ‖Ax − b‖² | 2Aᵀ(Ax − b) |

A helpful check: in one dimension, ax² has derivative 2ax. The matrix version looks similar, and the shapes tell you where the transpose goes.

##### Deriving least squares

1. Loss: L(w) = ‖Xw − y‖².

2. Gradient: ∇L = 2Xᵀ(Xw − y).

3. Set to zero: XᵀXw = Xᵀy, the normal equations.

4. Hessian: 2XᵀX, which is semi-definite. So the loss is convex, and this is a true minimum.

##### Why backpropagation runs backwards

The chain rule multiplies Jacobians: J₃J₂J₁. Each may be enormous. Starting from the output, you keep a vector and multiply it by one Jacobian at a time. This is called a **vector-Jacobian product**, and it doesn't require forming any full Jacobian. So one backward pass costs about as much as a forward pass, however many parameters there are.

#### The maths

$$ {L(w)} = \|Xw - y\|^2 \;\Rightarrow\; {\nabla L} = 2X^\top{(Xw - y)}, \qquad {\nabla^2 L} = 2X^\top X $$

Layout warning: books differ on whether a gradient is a row or a column. This site uses columns, which is the common convention in ML. Let shapes guide you.

- **the loss**: A single number from n weights, so its gradient has n entries.

- **the gradient**: Xᵀ maps the errors back to one value per weight. Shapes: [n, m] × [m] gives [n].

- **the residual**: The current errors. When they’re orthogonal to X’s columns, the gradient is zero, matching the projection picture.

- **the Hessian**: It doesn’t depend on w, so curvature is the same everywhere. It’s semi-definite, so the loss is convex.

## In practice

### In practice

#### In practice

- **Check shapes first:** most mistakes show up as a shape mismatch, so write shapes under each step.

- **Gradient check:** compare hand-written gradients against finite differences, using central differences with a small step.

- **Autograd does the rest:** frameworks compute these for you, but you still need this to debug them, reason about memory and read papers.

- **Hessians are huge:** n weights give n² entries, so large models use Hessian-vector products, or approximations, instead.

- **Forward vs reverse mode:** reverse suits many inputs and few outputs, like a loss. Forward suits few inputs and many outputs.

### The answer that sounds right

#### "Autograd does this, so I don't need it"

It sounds right, since frameworks compute gradients for you. But interviews ask you to derive them, and debugging exploding gradients, memory use and custom losses all need this understanding. You'll also read papers written in this notation. Autograd saves effort, but it doesn't replace understanding.

## Say it

### How do you differentiate a matrix expression, like the least-squares loss?

#### The interviewer pushes further

Follow-up 1 of 3

What's the gradient of xᵀAx when A isn't symmetric?

(A + Aᵀ)x. Only the symmetric part of A contributes to the value, so that's what appears. When A is symmetric, it simplifies to 2Ax. Example: for A = [[2, 1], [1, 3]] and x = (1, 1), the gradient is (6, 8).

Follow-up 2 of 3

Why is reverse mode used for training?

There are millions of inputs (weights) and one output (loss). Reverse mode computes all those gradients in a single backward pass. Forward mode would need one pass per weight. The cost is memory, as you have to store intermediate values from the forward pass.

Follow-up 3 of 3

How would you find a bug in a gradient?

Run a gradient check: nudge each weight by a small amount in each direction, compute the loss change, and compare with the gradient. Use a small random model and a few weights, as it's slow. Differences usually come from a wrong transpose, a missing factor of two, or a non-smooth function.

#### The 30-second answer

I'd think in shapes. A scalar loss of n weights has an n-length gradient. For L equals the norm of Xw minus y squared, the gradient is 2 X transpose times Xw minus y. Shapes confirm it: n by m times m gives n. Setting it to zero gives the normal equations, and the Hessian, 2 X transpose X, is semi-definite, so it's a true minimum. For a vector output, you get a Jacobian. Backprop is a chain of Jacobians, multiplied from the output, so you only keep a vector and never form the full matrices.

**Key terms and sources**

Gradients, Jacobians and Hessians, the key identities, layout conventions, deriving least squares and why backpropagation multiplies from the output. · checked 6 Nov 2026

#### Sources

- [Kolter and Do, CS229 Linear Algebra Review](https://cs229.stanford.edu/section/cs229-linalg.pdf)

- [Deisenroth, Faisal and Ong, Mathematics for Machine Learning](https://mml-book.github.io/)

- Backpropagation on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
