# Solving Ax = b: LU, QR, Cholesky and the Pseudoinverse

> Why shouldn't you invert a matrix to solve Ax = b, and what is the pseudoinverse?

- Track: Fundamentals › Maths for ML › Linear algebra
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/solving-linear-systems/
- Before this: SVD & Low-Rank Approximation (`fundamentals/svd-and-low-rank`), Orthogonality and Projections (`fundamentals/orthogonality-and-projections`)
- Quiz topic: `la`

## Intuition

### The situation

A teammate's regression code computes the inverse of XᵀX directly. It's slow, and with correlated features the weights come out badly wrong. Some of your problems also have more unknowns than equations. The interviewer asks:

> Why shouldn't you invert a matrix to solve Ax = b, and what is the pseudoinverse?

#### Why it matters

On paper, you write the inverse. Software almost never computes one. Knowing why helps you pick methods, understand numerical warnings and explain what a library's linear regression really does. This uses SVD and QR.

### The idea

Think of finding a word's page. You could copy out the whole dictionary into a lookup table, just to look up one word. Or you could sort things into easy steps and go straight to it. Inverting builds the table. Factoring does the easy steps.

[Figure: Choosing a method. LU suits general square systems. Cholesky suits positive definite matrices at half the cost. QR suits least squares. SVD handles rank problems.]

_Factor into easy pieces, rather than computing an inverse._

### Play

**Try to break it.** Slide ε down to 0.000001, and change b by a tiny amount.

#### Nudge a nearly singular system

Solves A = [[1, 1], [1, 1 + ε]] with b = (2, 2 + ε), whose exact solution is (1, 1), then adds your change to b's second value. Exact arithmetic, using the formula directly. Digits lost is the rule of thumb log₁₀(κ).

Slide ε down to **0.000001**. The two equations are nearly the same, so a tiny change in b sends the solution far away. The maths is correct: the problem itself is unstable. Better methods won't rescue an unstable problem, but regularisation changes the question to one that's stable.

**Now say why:** why can't a better algorithm fix a badly conditioned problem?

## Maths

### Maths

#### In one breath

Don't compute A⁻¹ to solve Ax = b: it's slower and less accurate than **factoring** A into easy pieces. Use **LU** for general square matrices, **Cholesky** for positive definite ones, **QR** for least squares and **SVD** when rank is in doubt. The **condition number** tells you how much errors get amplified. The **pseudoinverse** extends the idea to any matrix, giving the least-squares answer with the smallest weights.

#### Factor, then solve

The idea: split A into matrices that are easy to solve, like triangular or orthogonal ones. Triangular systems take only about n² work, by substituting one line at a time.

| Method | Form | Use it for | Approximate cost |
|---|---|---|---|
| **LU** | A = LU, with row swaps | General square systems. Reuse the factors for many b. | ⅔n³ operations |
| **Cholesky** | A = LLᵀ | Positive definite: covariance, ridge, Gaussian processes. | ⅓n³, half of LU |
| **QR** | A = QR | Least squares, when it's well behaved. | About 2mn² |
| **SVD** | A = UΣVᵀ | Rank-deficient or nearly so. The most robust, and the slowest. | Several times QR |

##### Why not invert?

- **Cost:** computing A⁻¹ then multiplying takes about three times the work of an LU solve.

- **Accuracy:** it generally adds more rounding error.

- **Memory:** the inverse of a sparse matrix is usually dense, so you can lose all the savings.

##### Condition number

The condition number κ is the largest singular value divided by the smallest. It's how much a small change in the data can be amplified in the answer. As a rule of thumb, you lose about log₁₀(κ) digits of accuracy.

**The normal equations square it:** κ(XᵀX) = κ(X)². If κ(X) is 10⁸, XᵀX has about 10¹⁶, which is beyond double precision. That's why libraries use QR or SVD for regression.

##### The pseudoinverse

When there's no inverse, take the SVD, invert the non-zero singular values and leave the zeros at zero. That gives A⁺. It handles every case:

- **Too many equations:** A⁺b is the least-squares answer.

- **Too few equations:** of infinitely many exact answers, A⁺b has the smallest norm.

It also connects to ridge: as λ shrinks to zero, the ridge solution approaches A⁺b.

#### The maths

$$ {A^{+}} = V\,{\Sigma^{+}}\,U^\top, \qquad {\kappa(A)} = \frac{\sigma_{\max}}{\sigma_{\min}}, \qquad {\frac{\|\delta x\|}{\|x\|} \le \kappa(A)\,\frac{\|\delta b\|}{\|b\|}} $$

Example: if κ = 1,000 and your data has 0.1% noise, the answer could be wrong by up to 100%.

- **the pseudoinverse**: Works for any matrix, even non-square ones. If A has an inverse, A⁺ equals it.

- **inverting the singular values**: Each non-zero σ becomes 1/σ, and zeros stay zero. Very small values should be treated as zero, as 1/σ would blow up.

- **the condition number**: How close the matrix is to losing rank. An orthogonal matrix has κ = 1, the best possible.

- **what it means**: A relative error in b can grow by up to κ times in x.

## In practice

### In practice

#### In practice

- **Use a solver:** call solve, not inv. For regression, call a least-squares function.

- **Scale your features:** features in very different units raise the condition number. Standardising is an easy fix.

- **Reuse factors:** if you solve for many b, factor once, then each solve is cheap.

- **Choose a cutoff:** pseudoinverse functions treat tiny singular values as zero. That threshold matters when you're near rank deficiency.

- **Very large systems:** direct methods grow with n³, so use iterative methods such as conjugate gradient, or gradient descent, for huge or sparse problems.

### The answer that sounds right

#### "My matrix isn't singular, so inverting is safe"

It sounds right, since the inverse exists. But being invertible isn't the same as being safe. A nearly singular matrix has an inverse, and it amplifies every rounding error and bit of noise. Check the condition number, and solve by factoring. Regularisation helps where the problem itself is unstable.

## Say it

### Why shouldn't you invert a matrix to solve Ax = b, and what is the pseudoinverse?

#### The interviewer pushes further

Follow-up 1 of 3

Why do the normal equations lose accuracy?

Forming XᵀX squares the condition number. A condition number of 10⁸, which is manageable, becomes 10¹⁶, close to the limit of double precision. QR works on X directly, so it avoids this. Normal equations remain faster, and they're fine for well-conditioned problems.

Follow-up 2 of 3

What does the pseudoinverse give when there are more unknowns than equations?

Of the infinitely many exact solutions, it gives the one with the smallest norm. Interestingly, gradient descent started at zero converges to this same solution for linear regression, which is one way of explaining implicit regularisation.

Follow-up 3 of 3

When would you use gradient descent instead of a direct solve?

When n is so large that n³ or even storing the matrix is too expensive, or when the data is sparse or arrives in batches. Direct methods are exact and can be better for small dense problems. Conditioning still matters, since badly conditioned problems also slow gradient descent.

#### The 30-second answer

I wouldn't invert. Computing the inverse costs about three times an LU solve, and it's less accurate. I'd factor A into easy pieces: LU for general matrices, Cholesky for positive definite ones at half the cost, QR for least squares and SVD if the rank is in doubt. The condition number, largest over smallest singular value, says how much errors get amplified, and normal equations square it, which is why libraries use QR or SVD. The pseudoinverse inverts only the non-zero singular values, giving the least-squares answer with the smallest norm.

**Key terms and sources**

How computers actually solve linear systems: LU, QR, Cholesky and SVD, the condition number, and the Moore-Penrose pseudoinverse. · checked 6 Nov 2026

#### Sources

- [Boyd and Vandenberghe, Introduction to Applied Linear Algebra](https://web.stanford.edu/~boyd/vmls/)

- [Strang, Linear Algebra and Learning from Data](https://math.mit.edu/~gs/learningfromdata/)

- [Deisenroth, Faisal and Ong, Mathematics for Machine Learning](https://mml-book.github.io/)

- [Kolter and Do, CS229 Linear Algebra Review](https://cs229.stanford.edu/section/cs229-linalg.pdf)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
