# Positive Definite Matrices

> What is a positive definite matrix, and where does it show up in ML?

- Track: Fundamentals › Maths for ML › Linear algebra
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/positive-definite-matrices/
- Before this: Eigenvalues & Eigenvectors (`fundamentals/eigenvalues-and-eigenvectors`)
- Related: Convexity & Local Minima (`fundamentals/convexity-and-local-minima`)
- Quiz topic: `la`

## Intuition

### The situation

Your Gaussian process crashes with "matrix not positive definite". Separately, you built a correlation matrix from data with missing values, and an optimiser is rejecting it. The interviewer asks:

> What is a positive definite matrix, and where does it show up in ML?

#### Why it matters

This one idea connects covariance, convexity, kernels and numerical stability. Whenever a library complains that a matrix "isn't positive definite", this is what it means, and it's usually a real data problem. See eigenvalues first.

### The idea

Think of a valley with a single lowest point. Walk any direction from the bottom, and you go up. That's positive definite. A long flat trough is semi-definite, and a mountain pass, up one way and down another, is indefinite. The matrix describes the shape of the land.

[Figure: Three shapes. Positive definite is a bowl with all eigenvalues positive. Semi-definite is a trough with some eigenvalues zero. Indefinite is a saddle with mixed signs.]

_The signs of the eigenvalues decide the shape._

### Play

**Try to break it.** Raise b from 1 to 2.5, then lower a below zero.

#### Shape the bowl

The curve shows points where xᵀAx = 1. An ellipse means positive definite. Open curves mean a saddle or flat direction. Ridge shows the λ that would lift the lowest eigenvalue just above zero.

Raise b from **1** to **2.5**. The features are now "too correlated" for those variances, and one eigenvalue goes negative. A real covariance matrix can't do that, so if yours does, something's wrong with how it was computed.

**Now say why:** why can't a real covariance matrix have a negative eigenvalue?

## Maths

### Maths

#### In one breath

A symmetric matrix is **positive definite** if xᵀAx is above zero for every non-zero x, which means all its eigenvalues are positive. Picture a bowl with one lowest point. **Semi-definite** allows flat directions, and **indefinite** gives a saddle. That's why this matters: a **positive definite Hessian means a true minimum**, covariance matrices are always semi-definite, and you can factor these matrices quickly with Cholesky.

#### Bowls and saddles

| Type | Eigenvalues | Shape of xᵀAx | Meaning for a Hessian |
|---|---|---|---|
| **Positive definite** | All above 0 | A bowl | A true local minimum |
| **Semi-definite** | All 0 or above | A trough with flat directions | Flat directions, so it's not unique |
| **Indefinite** | Mixed signs | A saddle | A saddle point |
| **Negative definite** | All below 0 | An upside-down bowl | A local maximum |

##### How to test for it

- **Try Cholesky:** the practical method. It succeeds if and only if the matrix is positive definite, and it's cheap.

- **Eigenvalues:** check they're all positive. This is clear, but slower.

- **For a 2 × 2:** the top-left entry and the determinant must both be positive.

##### Where it shows up

- **Covariance:** xᵀΣx is the variance of a combination of features, and variance can't be negative. So Σ is always semi-definite.

- **Gram matrices:** XᵀX is always semi-definite, and it's positive definite when X has full column rank.

- **Ridge regression:** adding λI lifts every eigenvalue by λ, which makes XᵀX + λI positive definite, so it always has an inverse.

- **Kernels:** a valid kernel must produce a semi-definite matrix, as if it were dot products in some space.

- **Sampling:** if Σ = LLᵀ, then Lz has covariance Σ when z is standard normal.

#### The maths

$$ {x^\top A x} > 0 \;\; \forall x \neq 0 \;\iff\; {\lambda_i(A) > 0} \;\iff\; {A = LL^\top} $$

These three statements are equivalent for symmetric matrices. Example: [[2, 1], [1, 2]] has eigenvalues 3 and 1, so it’s positive definite. [[1, 2], [2, 1]] has eigenvalues 3 and −1, so it’s indefinite.

- **the quadratic form**: A single number from a vector and a matrix. It’s positive in every direction.

- **the eigenvalues**: All are positive, as each one is the value of the form along an eigenvector.

- **Cholesky exists**: The matrix factors into a lower triangular L times its transpose, like a matrix square root.

## In practice

### In practice

#### In practice

- **"Matrix not positive definite" errors:** common causes are duplicate rows, features with more columns than rows, or rounding errors. Check your data before anything else.

- **Add jitter:** adding a small value to the diagonal, like 1e-6, is a standard fix for numerical problems in Gaussian processes. It's a repair for rounding, not for bad data.

- **Pairwise deletion breaks it:** computing correlations with missing data on different rows can produce a matrix that's no longer semi-definite.

- **In deep learning:** real Hessians are usually indefinite, with many saddle points and flat directions, so these tidy guarantees rarely hold.

- **Use Cholesky when you can:** it takes about half the work of LU, and it's stable for these matrices.

### The answer that sounds right

#### "All entries are positive, so it's positive definite"

It sounds right, given the name. But it's about directions, not entries. [[1, 2], [2, 1]] has only positive entries, yet its eigenvalues are 3 and −1, so it's indefinite. And [[2, −1], [−1, 2]] has negative entries, and it's positive definite. Check the eigenvalues, or try Cholesky.

## Say it

### What is a positive definite matrix, and where does it show up in ML?

#### The interviewer pushes further

Follow-up 1 of 3

Why is a covariance matrix always positive semi-definite?

For any weights w, wᵀΣw is the variance of the combination wᵀx, and variance can't be negative. It's only semi-definite, not definite, if some combination has zero variance, like when one feature is an exact mix of the others.

Follow-up 2 of 3

How does ridge regression help with a singular matrix?

Adding λI adds λ to every eigenvalue. A zero eigenvalue becomes λ, so the smallest eigenvalue is at least λ, and the matrix is positive definite and invertible. It also reduces the condition number, which makes the solution more stable.

Follow-up 3 of 3

Your Gaussian process fails with a Cholesky error. What do you check?

First, duplicate or almost-duplicate points, since those make rows nearly identical. Then the kernel's length scale, as very long scales make everything look alike. Adding a small jitter to the diagonal fixes pure rounding problems, but check the data first.

#### The 30-second answer

A symmetric matrix is positive definite if x transpose A x is positive for every non-zero x, which is the same as all eigenvalues being positive. Geometrically, it's a bowl with one minimum. Semi-definite allows flat directions, and indefinite is a saddle. It appears in many places. A positive definite Hessian means a true local minimum. Covariance matrices are always semi-definite, because variance can't be negative. Ridge's lambda I makes X transpose X positive definite. The practical test is Cholesky, which succeeds only for positive definite matrices.

**Key terms and sources**

Quadratic forms, positive definite and semi-definite matrices, how to test for them, and their role in covariance, convexity, kernels and sampling. · checked 6 Nov 2026

#### Sources

- [Kolter and Do, CS229 Linear Algebra Review](https://cs229.stanford.edu/section/cs229-linalg.pdf)

- [Strang, Linear Algebra and Learning from Data](https://math.mit.edu/~gs/learningfromdata/)

- [Deisenroth, Faisal and Ong, Mathematics for Machine Learning](https://mml-book.github.io/)

- Convexity on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
