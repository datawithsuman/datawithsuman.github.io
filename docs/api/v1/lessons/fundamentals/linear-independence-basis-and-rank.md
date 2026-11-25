# Linear Independence, Basis and Rank

> What is the rank of a matrix, and why do correlated features break linear regression?

- Track: Fundamentals › Maths for ML › Linear algebra
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/linear-independence-basis-and-rank/
- Before this: Matrices as Transformations (`fundamentals/matrices-as-transformations`)
- Related: Linear Regression (`fundamentals/linear-regression`)
- Quiz topic: `la`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: 5a6cfdb43e

## Intuition

### The situation

Your linear regression has weights in the millions, with opposite signs on height in cm and height in inches. A colleague also one-hot encoded a category with all its columns, and included an intercept. The solver warns about a singular matrix. The interviewer asks:

> What is the rank of a matrix, and why do correlated features break linear regression?

#### Why it matters

Rank explains many practical failures: unstable regression weights, the dummy variable trap, models with more features than rows, and why large embedding matrices can be compressed. See SVD and low rank for how to use this.

### The idea

Think of directions to a friend's house. "Two blocks north, then one east" gets you there. Adding "also go 200 metres north" tells you nothing new, and now there are many ways to describe the same trip. Rank is how many directions really add something.

[Figure: Three cases. Independent features have full rank and unique weights. Near dependent features keep rank, but weights are unstable. Dependent features lose rank, and there are no unique weights.]

_Rank is the number of directions that really add something._

### Play

**Try to break it.** Move the correlation from 0.90 to 0.99, then to exactly 1.00.

#### Correlate two features

Two standardised features. The area is the determinant of the correlation matrix, 1 − ρ². Figures come from the formula, not a simulation. In practice, rank is judged numerically, so very high correlations behave as if rank were lost.

Move from **0.90** to **0.99**. Inflation goes up about ten times, even though the features already looked similar. Then try exactly **1.00**: the rank drops, and no unique weights exist.

**Now say why:** why do weights become unstable before rank is actually lost?

## Maths

### Maths

#### In one breath

Vectors are **independent** if none can be built from the others. The **rank** of a matrix is how many of its columns are truly independent: the real number of dimensions in its data. If a feature is a mix of others, the matrix is **rank-deficient**, and many different weights fit equally well. Nearly-dependent features aren't quite as bad, but they still make weights unstable. Regularisation and removing features both help.

#### Building blocks

| Term | Meaning | Example |
|---|---|---|
| **Span** | All the vectors you can build by mixing a set. | Two non-parallel arrows reach anywhere in a plane. |
| **Independent** | None can be built from the others. | Height in cm and weight. Not height in cm and height in inches. |
| **Basis** | The smallest set that reaches everything in a space. | (1, 0) and (0, 1) for a plane, but other pairs work too. |
| **Rank** | The number of independent columns, which always equals the number of independent rows. | A 1,000 × 50 data matrix has rank 50 at most. |

##### Column space and null space

- **Column space:** every output Ax can produce. If b isn't in it, Ax = b has no exact solution, which is why regression uses least squares.

- **Null space:** every x where Ax = 0. Add one of these to a solution, and you get another solution that fits equally well.

- **Rank-nullity:** rank + null space size = number of columns. Each lost column dimension adds a direction you can't measure.

##### When features break regression

- **Exact dependence:** height in cm and in inches. XᵀX can't be inverted, and there's no single answer.

- **Near dependence:** strongly correlated features. An answer exists, but small changes in data swing the weights.

- **Dummy variable trap:** one-hot columns for all k categories add up to the intercept column. Drop one, or use regularisation.

- **More features than rows:** rank can't exceed the number of rows, so there are infinitely many perfect fits.

#### The maths

$$ {\mathrm{rank}(A)} + {\dim(\mathrm{null}(A))} = {n}, \qquad {\mathrm{VIF}_j} = \frac{1}{1 - R_j^2} $$

As R² approaches 1, VIF grows without limit. At exactly 1, the matrix has lost rank, and the weight isn’t defined.

- **rank**: How many independent directions the columns really cover.

- **null space size**: How many independent directions the matrix wipes out. Weights along these can’t be determined from the data.

- **number of columns**: The two always add up to this.

- **variance inflation factor**: R² is how well other features predict feature j. A VIF of 10 means the variance of its weight is 10 times what it would be, if it were uncorrelated with the others.

## In practice

### In practice

#### In practice

- **Prediction vs explanation:** collinearity may not hurt predictions on similar data, as the mix of weights still works. It does hurt when you try to interpret individual weights.

- **Fixes:** remove one feature, combine them, use ridge, or use PCA.

- **Check:** look at VIF, and at the matrix's singular values. Very small ones mean you're close to losing rank.

- **Numerical rank:** real data rarely has exact zeros. Count singular values above a small threshold.

- **Low-rank data is useful:** many large matrices have a much smaller true rank, which is why compression, recommenders and LoRA work.

### The answer that sounds right

#### "The correlation is only 0.9, so it's fine"

It sounds right, since the features are still different. But at 0.9, each weight's variance is already over five times higher, and at 0.99 it's about fifty times higher. Weights can flip sign between samples. Whether that matters depends on your goal: predictions may hold, while explanations won't.

## Say it

### What is the rank of a matrix, and why do correlated features break linear regression?

#### The interviewer pushes further

Follow-up 1 of 3

Why do the rows and columns always have the same rank?

It's a basic theorem: the number of independent rows always equals the number of independent columns. It's why a 1,000 × 50 matrix can't have rank above 50, and why more features than rows always leaves a non-trivial null space.

Follow-up 2 of 3

Does multicollinearity hurt predictions?

Not much, if new data has the same correlation, because errors in individual weights cancel out in the combination. It hurts interpretation, and predictions when that correlation changes in production. So it matters most for understanding, and for shifting data.

Follow-up 3 of 3

You have 100 rows and 1,000 features. What happens to linear regression?

The rank is at most 100, so there are infinitely many weights that fit perfectly, and no unique solution. Use regularisation, such as ridge or lasso, reduce the features, or use a minimum-norm solution through the pseudoinverse. Each of those picks one answer.

#### The 30-second answer

The rank is the number of truly independent columns, which is the real dimension of the data. If a feature is a mix of others, the matrix loses rank, XᵀX can't be inverted, and many sets of weights fit equally well. That's what the null space means: directions you can't determine from the data. With strong but not perfect correlation, a solution exists, but weights are unstable, with variance inflated by one over one minus R squared. I'd drop or combine features, or use ridge. Predictions may be fine, but weights can't be trusted.

**Key terms and sources**

Linear independence, span, basis, rank, column and null space, and how they explain collinearity, the dummy variable trap and low-dimensional embeddings. · checked 6 Nov 2026

#### Sources

- [Deisenroth, Faisal and Ong, Mathematics for Machine Learning](https://mml-book.github.io/)

- [Kolter and Do, CS229 Linear Algebra Review](https://cs229.stanford.edu/section/cs229-linalg.pdf)

- [Strang, Linear Algebra and Learning from Data](https://math.mit.edu/~gs/learningfromdata/)

- Linear regression on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
