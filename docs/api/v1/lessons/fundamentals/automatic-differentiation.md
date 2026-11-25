# Automatic Differentiation

> How does automatic differentiation work, and why does training use reverse mode?

- Track: Fundamentals › Maths for ML › Calculus and optimisation
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/automatic-differentiation/
- Before this: Derivatives, Gradients & the Chain Rule (`fundamentals/derivatives-and-chain-rule`)
- Related: Backpropagation Through a Network (`fundamentals/backpropagation`)
- Quiz topic: `calc`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: 3dfc7805bc

## Intuition

### The situation

A model has a million weights and one loss. A teammate suggests working out each gradient by nudging each weight, since it's so simple. Elsewhere, your model trains fine at inference size, but it runs out of memory as soon as you turn training on. The interviewer asks:

> How does automatic differentiation work, and why does training use reverse mode?

#### Why it matters

Every training framework is built on this. Understanding it explains why training needs far more memory than inference, what a computation graph is, and why some operations break gradients. It follows on from the chain rule.

### The idea

Think of a chain of factories, and you want to know how each raw material affects the final price. You could change one material at a time and rerun everything. Or you could run once, then walk backwards from the price, asking each factory how much it passed on. One walk answers it for every material.

[Figure: Three ways to get a gradient. Numerical nudges each input, and is slow and inexact. Symbolic manipulates formulas, which can grow huge. Automatic applies the chain rule to each operation, and is exact and fast.]

_Reverse-mode automatic differentiation is what frameworks use to train._

### Play

**Try to break it.** Change x and y, and check the gradients by hand. Then compare passes with many weights and many outputs.

#### Trace both passes

The top half computes the worked example exactly. The bottom half counts passes for a full gradient. A backward pass usually costs a small multiple of a forward pass, and it needs stored values.

Set the weights to **10** and the outputs to **100**. Now forward mode needs fewer passes. So forward mode isn't bad: it's right when inputs are few and outputs are many. Training is simply the opposite case.

**Now say why:** why does a backward pass need values from the forward pass?

## Maths

### Maths

#### In one breath

**Automatic differentiation** breaks a program into small operations with known derivatives, then applies the chain rule by machine. It gives exact gradients, unlike nudging values, and it doesn't produce giant formulas. **Forward mode** pushes derivatives along with values, one input at a time. **Reverse mode** runs the program, then goes backwards from the output. With millions of inputs and one loss, **reverse mode gets every gradient in one backward pass**. The cost is memory, because intermediate values must be stored.

#### Three ways to get a gradient

| Method | How | Problem |
|---|---|---|
| **Numerical** | Nudge each input, and see what changes. | One or two runs per input, and rounding errors. Good for checking. |
| **Symbolic** | Manipulate formulas, like in algebra software. | Formulas can grow huge, and code with loops is hard to handle. |
| **Automatic** | Apply the chain rule to each operation as the code runs. | Exact up to rounding, at a small multiple of the run's cost. |

##### Worked example: f(x, y) = xy + x, at (2, 3)

| Step | Value (forward pass) | How much f changes with it (backward pass) |
|---|---|---|
| a = xy | 6 | df/da = 1 |
| f = a + x | 8 | df/df = 1 |
| y | 3 | df/dy = df/da × x = 2 |
| x | 2 | df/dx = df/da × y + 1 = 4 |

One forward pass and one backward pass gave both gradients.

##### Forward or reverse?

- **Forward mode:** carries a derivative with each value. One pass gives the effect of **one input on all outputs**.

- **Reverse mode:** records operations, then works back from the output. One pass gives the effect of **all inputs on one output**.

Training has millions of inputs and one loss, so reverse mode wins by a huge margin. Backpropagation is reverse mode applied to a neural network.

##### What can break it

- **Steps with no useful gradient:** argmax, rounding and sampling have zero or undefined gradients. Hence tricks like softmax and reparameterisation.

- **Leaving the graph:** converting to another library, or detaching a tensor, stops gradients flowing.

- **In-place changes:** changing a stored value can make the backward pass wrong, so frameworks often raise an error.

#### The maths

$$ {\frac{\partial L}{\partial \theta}} = {v^\top} J_k J_{k-1} \cdots J_1, \qquad {\text{reverse: } (v^\top J_k) J_{k-1} \cdots}, \qquad {\text{forward: } J_k \cdots (J_1 u)} $$

Same product, different order. With many inputs and one output, multiplying from the output keeps things small. See the shapes lesson on why order changes cost.

- **the gradient**: What the chain rule gives: a product of one Jacobian per step.

- **the starting vector**: For a single loss, it’s just 1.

- **reverse mode**: Multiply from the left. Each step is a vector times a matrix, so you never hold a whole Jacobian. One pass gives every weight’s gradient.

- **forward mode**: Multiply from the right, starting with one input direction u. It needs a pass for each input.

## In practice

### In practice

#### In practice

- **Memory:** the backward pass needs values from the forward pass, so training uses much more memory than inference. That's why large models run out of memory only in training.

- **Gradient checkpointing:** store only some values and recompute the rest. You trade compute for memory.

- **Disable it for inference:** turning off gradient tracking saves the memory and time of recording operations.

- **Accumulating gradients:** frameworks add to existing gradients, so clear them each step, or use this on purpose to simulate larger batches.

- **Hessian-vector products:** running reverse over forward mode gives curvature information, without building the full Hessian.

### The answer that sounds right

#### "Autodiff is just numerical differentiation done quickly"

It sounds right, since both give numbers rather than formulas. But numerical differentiation nudges inputs and needs a run per input, with rounding error. Automatic differentiation applies exact derivative rules to each operation, and needs one backward pass. They're different methods, and numerical is mainly useful for checking the other.

## Say it

### How does automatic differentiation work, and why does training use reverse mode?

#### The interviewer pushes further

Follow-up 1 of 3

Is automatic differentiation the same as numerical differentiation?

No. Numerical nudges inputs and measures the change, needing a run per input, with rounding error. Automatic applies exact derivative rules to each operation. Numerical differentiation is still useful for checking that automatic gradients are right.

Follow-up 2 of 3

Why does training use so much more memory than inference?

The backward pass needs values from the forward pass, so they must stay in memory until used. Inference discards them as it goes. Gradient checkpointing reduces this by storing only some, and recomputing the rest.

Follow-up 3 of 3

When is forward mode better?

When there are few inputs and many outputs, such as measuring how one hyperparameter affects many values. Also for a Jacobian-vector product, where you only need one direction. Forward mode uses little extra memory, as it doesn't store a record for a backward pass.

#### The 30-second answer

Automatic differentiation breaks a program into simple operations with known derivatives, and applies the chain rule to them. It's exact, unlike numerical differentiation, and avoids the formula growth of symbolic methods. Forward mode gives the effect of one input on all outputs per pass. Reverse mode records the operations, then goes back from the output, giving the effect of all inputs on one output. Training has millions of weights and one loss, so reverse mode gets every gradient in a single backward pass. The cost is memory, as it must store intermediate values.

**Key terms and sources**

Computational graphs, forward and reverse mode, why training uses reverse mode, how it differs from numerical and symbolic differentiation, and its memory cost. · checked 6 Nov 2026

#### Sources

- [Deisenroth, Faisal and Ong, Mathematics for Machine Learning](https://mml-book.github.io/)

- Backpropagation on this site

- Matrix calculus on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
