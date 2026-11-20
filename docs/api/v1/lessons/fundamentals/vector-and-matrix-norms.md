# Vector and Matrix Norms

> What's the difference between L1 and L2 norms, and why does L1 give sparse weights?

- Track: Fundamentals › Maths for ML › Linear algebra
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/vector-and-matrix-norms/
- Before this: Vectors, Dot Products & Cosine Similarity (`fundamentals/vectors-and-cosine-similarity`)
- Related: Regularized Linear Models (`fundamentals/regularized-linear-models`)
- Quiz topic: `la`

## Intuition

### The situation

Your regression has 500 features, and you want most of the weights to go to zero. A teammate switches between L1 and L2 penalties and gets very different results. You also want to stop exploding gradients. The interviewer asks:

> What's the difference between L1 and L2 norms, and why does L1 give sparse weights?

#### Why it matters

The norm you choose decides what "small" means. That choice sets which weights regularisation removes, when gradient clipping activates and how far a layer can amplify its input. This builds on vectors and length.

### The idea

Think of getting from one place to another in a city. L2 is the straight-line distance, as a bird flies. L1 is the distance by road on a grid, adding every block. L∞ only cares about your longest stretch. It's the same trip, measured by different rules.

[Figure: Three norms for the vector 3, minus 4. L1 is 7, the sum of absolute values. L2 is 5, the straight-line length. L infinity is 4, the largest value.]

_The same vector, (3, −4), measured three ways._

### Play

**Try to break it.** Set the vector to (3, 0), then (3, 3). Then lower the clip limit.

#### Compare the unit balls

Diamond is L1, circle is L2 and square is L∞, each drawn at radius 2. The dot is your vector. Clipping scales the whole vector, so the direction is unchanged.

Set the vector to **(3, 0)**: all three norms agree, because only one value is non-zero. Set it to **(3, 3)**, and they differ. L1 counts every value, while L∞ only sees the biggest.

**Now say why:** why do the three norms agree when only one value isn't zero?

## Maths

### Maths

#### In one breath

A **norm** measures size. **L2** is straight-line length, **L1** adds absolute values, and **L∞** takes the largest entry. Each has a different "unit ball". L1's is a diamond with corners on the axes, so penalised solutions tend to land where some weights are exactly zero. For matrices, **Frobenius** treats all entries like one long vector, and the **spectral norm** is the most a matrix can stretch any vector.

#### Measuring size

| Norm | How | Where it's used |
|---|---|---|
| **L2** | Square root of the sum of squares. | Ridge and weight decay, gradient clipping, Euclidean distance. |
| **L1** | Sum of absolute values. | Lasso, for sparse weights. Less sensitive to single large values. |
| **L∞** | The largest absolute value. | Limits on any single value, like adversarial attacks. |
| **Frobenius** | L2 of all a matrix's entries. | Low-rank error, matrix factorisation. |
| **Spectral** | The largest singular value. | How much a layer can amplify. Spectral normalisation in GANs. |

##### Why L1 gives zeros

Regularisation asks for the lowest loss inside a norm's ball. The loss's contours usually first touch L1's diamond at a corner, and corners sit on an axis, where other weights are exactly zero. L2's circle has no corners, so its weights shrink but rarely reach zero.

The gradient tells the same story. L2's pull weakens as a weight approaches zero. L1's pull stays constant, so it can push a small weight all the way to zero.

##### A rule every norm follows

- It's zero only for the zero vector.

- Scaling a vector scales its norm.

- The triangle inequality holds: going directly is never longer than going via another point.

#### The maths

$$ {\|x\|_p} = \Big(\sum_i |x_i|^{{p}}\Big)^{1/p}, \qquad {\|A\|_F} = \sqrt{\sum_i \sigma_i^2}, \qquad {\|A\|_2} = \sigma_{\max} $$

Worked example: for x = (3, −4), L1 = 7, L2 = 5 and L∞ = 4. See the SVD lesson for singular values.

- **the p-norm**: One formula covers them all. p = 1 gives L1, p = 2 gives L2, and as p grows it approaches the largest entry.

- **the power**: A higher p gives more weight to the largest entries.

- **Frobenius norm**: Treats a matrix as one long vector. It also equals the square root of the sum of squared singular values.

- **spectral norm**: The most the matrix stretches any unit vector, equal to its largest singular value.

## In practice

### In practice

#### In practice

- **Gradient clipping:** if the gradient's L2 norm exceeds a limit, scale the whole gradient down. Direction stays the same, and only the step size changes.

- **Scale your features:** norms add values across features, so a feature in large units can dominate. Standardise before using a norm penalty.

- **Normalise embeddings:** dividing by the L2 norm makes the dot product equal cosine similarity.

- **Spectral normalisation:** dividing a layer's weights by its spectral norm limits how much it can amplify.

- **Check for divergence:** tracking the norm of weights and gradients is a quick health check during training.

### The answer that sounds right

#### "L2 is better because it's smooth"

It sounds right, since smooth functions are easier to optimise. But they do different jobs. L2 shrinks all weights and keeps them, while L1 removes some entirely. If you want a small set of features, L2 won't give you one. Choose by the outcome you want, and consider elastic net for both.

## Say it

### What's the difference between L1 and L2 norms, and why does L1 give sparse weights?

#### The interviewer pushes further

Follow-up 1 of 3

Why does gradient clipping use the norm rather than clipping each value?

Clipping each value separately changes the gradient's direction, whereas scaling by the norm keeps it. Per-value clipping is simpler, and some use it, but norm clipping keeps pointing where the gradient said to go, with only a smaller step.

Follow-up 2 of 3

Lasso picks one of two highly correlated features. Why?

The L1 penalty doesn't care how weight is split, in total, between two identical features, so it can land on either, often zeroing the other. Which one it picks can change between samples. Elastic net adds some L2, which spreads weight more evenly.

Follow-up 3 of 3

When would you prefer the spectral norm to Frobenius?

When you care about the worst case: the most a matrix can stretch any input. That matters for stability and Lipschitz limits. Frobenius is about total energy across all directions, which is what matters for low-rank approximation error.

#### The 30-second answer

A norm measures size. L2 is straight-line length, and L1 is the sum of absolute values. L1 gives sparse weights because its unit ball is a diamond with corners on the axes, so the loss's contours tend to touch it where some weights are exactly zero. In terms of gradients, L1 keeps a constant pull towards zero, while L2's pull fades. For matrices, Frobenius treats all entries as one vector, and the spectral norm is the largest singular value, which limits how much a layer can amplify.

**Key terms and sources**

L1, L2 and max norms for vectors, Frobenius and spectral norms for matrices, and how they drive regularisation, gradient clipping and stability. · checked 6 Nov 2026

#### Sources

- [Deisenroth, Faisal and Ong, Mathematics for Machine Learning](https://mml-book.github.io/)

- [Kolter and Do, CS229 Linear Algebra Review](https://cs229.stanford.edu/section/cs229-linalg.pdf)

- [Strang, Linear Algebra and Learning from Data](https://math.mit.edu/~gs/learningfromdata/)

- Regularised linear models on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
