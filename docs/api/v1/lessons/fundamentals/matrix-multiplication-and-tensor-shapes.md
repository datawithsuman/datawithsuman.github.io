# Matrix Multiplication and Tensor Shapes

> How do you reason about tensor shapes and the cost of matrix multiplication in a model?

- Track: Fundamentals › Maths for ML › Linear algebra
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/matrix-multiplication-and-tensor-shapes/
- Before this: Matrices as Transformations (`fundamentals/matrices-as-transformations`)
- Related: Self-Attention (Q, K, V) (`fundamentals/self-attention`)
- Quiz topic: `la`

## Intuition

### The situation

Your attention model runs fine on 1,024 tokens, but runs out of memory at 4,096. A teammate says that's only four times longer. Elsewhere, a loss looks fine, yet the model doesn't train, and it turns out to be a shape bug. The interviewer asks:

> How do you reason about tensor shapes and the cost of matrix multiplication in a model?

#### Why it matters

Shape errors are the most common bug in model code, and the cost of multiplication decides your GPU bill. If you can follow the shapes through a model, you can read any architecture, and predict what breaks at a larger scale. This builds on matrices as transformations.

### The idea

Think of shipping containers through a chain of ports. Each crane fits one container size, so the output of one step has to fit the next. And it can be much cheaper to ship in a smart order, even if everything ends up in the same place.

[Figure: Multiplying matrices. Inner sizes must match, the outer sizes give the result, and the cost is m times n times p.]

_Inner sizes must match, and outer sizes give the result._

### Play

**Try to break it.** Double the tokens, and watch the multiplications. Then change the heads.

#### Follow the shapes through attention

Heads shown are 2, 4, 8 and 12, using the nearest head count that divides the embedding size. One attention layer, ignoring the projections. Assumes 4 bytes per score, and no optimised attention methods.

Double the tokens from **1,024** to **2,048**. Multiplications and memory go up four times. Now change the heads: multiplications stay the same, because each head uses a smaller piece of the embedding, but the score matrices take more memory.

**Now say why:** why does doubling the tokens quadruple the cost of attention?

## Maths

### Maths

#### In one breath

To multiply matrices, the **inner sizes must match**: (m × n)(n × p) gives m × p, at a cost of about **m × n × p** multiplications. Most model bugs and cost surprises come from this. **Order matters** for cost, though not for the result. In attention, scores form a T × T matrix for T tokens, so **doubling the length quadruples** the cost.

#### Reading shapes

##### Three ways to see a product

- **Dot products:** each output entry is a row of A dotted with a column of B.

- **Combining columns:** each output column is a mix of A's columns, with weights from B.

- **Composition:** apply B, then A. That's why order matters, and AB usually differs from BA.

##### Shapes in a model

| Step | Shape | Note |
|---|---|---|
| Input batch | [B, d] | Batch dimension first, by convention. |
| Linear layer | [B, d] × [d, k] gives [B, k] | Has d × k weights, plus k for bias. |
| Token sequence | [B, T, d] | Batch, tokens, features. |
| Attention scores | [B, h, T, T] | h heads, comparing every token with every other. |

##### Broadcasting

Libraries stretch dimensions of size 1 automatically. A [B, 1] tensor plus a [1, k] tensor gives [B, k]. It's useful, and it's also a silent source of bugs: [B] minus [B, 1] gives [B, B], not an error.

##### Order changes the cost

(AB)C and A(BC) give the same answer, but can cost very different amounts. Multiply a matrix by a vector first, when you can. That's why backpropagation multiplies from the output backwards, keeping one small vector rather than building full matrices.

#### The maths

$$ \underbrace{A}_{m \times n}\,\underbrace{B}_{n \times p} = \underbrace{C}_{m \times p}, \qquad C_{ij} = \sum_{k=1}^{n} A_{ik}B_{kj}, \qquad \text{cost} \approx mnp $$

Example: A is 10 × 100, B is 100 × 5, C is 5 × 50. (AB)C costs 5,000 + 2,500 = 7,500. A(BC) costs 25,000 + 50,000 = 75,000: ten times more for the same answer.

- **left matrix**: Its number of columns must equal B’s number of rows.

- **right matrix**: Its number of rows must match, and its columns decide the output width.

- **each output entry**: A dot product of a row of A with a column of B, using n multiplications.

- **total cost**: m × p outputs, each with n multiplications. Multiply two n × n matrices, and it’s about n³.

## In practice

### In practice

#### In practice

- **Comment your shapes:** write them next to each line, or use a tool that checks them. It saves hours.

- **Watch for quiet broadcasting:** check shapes before adding or subtracting, particularly with loss functions.

- **Think in batches:** matrix operations on a batch are much faster on a GPU than looping, because they run in parallel.

- **Vector first:** applying A then B to a vector costs far less than computing AB first.

- **Estimate before you scale:** count how cost grows with tokens, batch and width. This is what limits context length.

### The answer that sounds right

#### "It's four times longer, so four times the memory"

It sounds right, since most things grow in proportion. But attention compares every token with every other, so the score matrix grows with the square of the length. Four times the tokens means sixteen times the scores. That's what limits context length, and why people look for more efficient attention methods.

## Say it

### How do you reason about tensor shapes and the cost of matrix multiplication in a model?

#### The interviewer pushes further

Follow-up 1 of 3

How many parameters does a linear layer from 768 to 3072 have?

768 × 3072 = 2,359,296 weights, plus 3,072 for the bias, so 2,362,368. Each output has one weight per input, plus a bias. It's a useful habit for spotting where a model's parameters really are.

Follow-up 2 of 3

Why does adding attention heads not increase the score multiplications?

Each head works on d divided by h features. There are h heads, each costing T² × d/h, and the h cancels. The score matrices do multiply, though, so memory rises. Multi-head attention gives several views at about the same compute.

Follow-up 3 of 3

What goes wrong if you subtract a [B] tensor from a [B, 1] tensor?

Broadcasting makes both [B, B], and you get a B × B matrix of all pairs, with no error. If it's a loss, the value looks reasonable, while the model trains badly. Check shapes, or squeeze the extra dimension first.

For matrices to multiply, the inner sizes must match: m by n times n by p gives m by p, at about m times n times p multiplications. I track shapes through a model with batch first. A linear layer takes B by d to B by k. Attention scores are batch, heads, tokens, tokens, so doubling the tokens quadruples cost. Multiplication is associative, so order doesn't change the result, but it can change the cost hugely. That's why backprop keeps multiplying a vector instead of building whole matrices.

**Key terms and sources**

How to track shapes through a model, what each multiplication costs, how the order matters, and how batches, broadcasting and attention use it.

#### Sources

- Kolter and Do, CS229 Linear Algebra Review

- Strang, Linear Algebra and Learning from Data

- Boyd and Vandenberghe, Introduction to Applied Linear Algebra

- Attention on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
