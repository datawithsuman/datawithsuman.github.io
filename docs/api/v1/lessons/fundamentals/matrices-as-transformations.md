# Matrices as Transformations

> What does a matrix actually do to space, and what does its determinant measure?

- Track: Fundamentals › Maths for ML › Linear algebra
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/matrices-as-transformations/
- Before this: Vectors, Dot Products & Cosine Similarity (`fundamentals/vectors-and-cosine-similarity`)
- Quiz topic: `la`

## Intuition

### The situation

Your recommendation model stacks two linear layers with no activation between them, and the second layer adds nothing. The interviewer asks:

> What does a matrix do to a vector, and why do two linear layers act like one?

**Running example:** two customer features, spicy and healthy taste (as in the previous lesson). A layer of a recommendation model multiplies every customer vector by a 2×2 matrix W. We watch what W does to the whole space by tracking the unit square and the two axis arrows.

#### Grids of numbers that nobody can read

Weight matrices, covariance matrices, attention matrices: ML is full of them, and staring at the numbers tells you little. Seeing a matrix as a **transformation of space** turns it into a picture you can reason about: what it stretches, what it destroys, whether it can be undone.

### The idea

Think of a matrix as a rule that moves every point on a rubber sheet. Its columns say where the two axis arrows land. The determinant says how much area changes, and zero means the sheet was flattened onto a line, which can't be undone.

[Figure: A unit square on the left becomes a slanted parallelogram on the right. On the far right, a flattened line shows a matrix with determinant zero.]

_Illustrative. Straight lines stay straight, and the origin stays put._

### Play

**Try to break it.** Pick the squash preset, then drag the entries until the two column arrows point the same way.

#### Drag the entries, watch the plane move

Faint grid: the original space. Coloured grid and square: the same space after W. Teal arrow = first column, orange = second column.

**Now say why:** what happens to the determinant and the rank, and why can't this matrix be undone?

## Maths

### Maths

#### In one breath

A matrix is a **function that moves every vector**: rotate, stretch, shear, squash or flip space, always keeping straight lines straight and the origin fixed. Its **columns** tell you where the two axis arrows land, so you can read a matrix by looking at it. Multiplying matrices = doing one transformation after another. The **determinant** is how much areas get scaled (negative if space is flipped, zero if it's squashed flat). A zero determinant means information is lost: the matrix has **rank** below full and no **inverse**. In ML, every dense layer is a matrix: Wx moves your data into a new space before the non-linearity bends it. What you'll be able to do after this: read a 2×2 matrix as a picture, compute a determinant and say what it means, explain rank and invertibility, and connect W x + b to a layer.

#### Matrix times vector

$$ {W x} = x_1 {\begin{pmatrix} w_{11}\\ w_{21}\end{pmatrix}} + x_2 {\begin{pmatrix} w_{12}\\ w_{22}\end{pmatrix}} $$

The column view of matrix–vector multiplication: Wx is a combination of W's columns with weights x. Strang, _Introduction to Linear Algebra_, ch. 1–2; MML §2.2.

- **the moved vector**: Where customer x lands after the layer.

- **first column**: Where the arrow (1, 0) lands. Multiply it by x’s first coordinate.

- **second column**: Where the arrow (0, 1) lands. Multiply it by x’s second coordinate, then add.

#### The determinant is the area-scaling factor

$$ {\det W} = {w_{11} w_{22}} - {w_{12} w_{21}} $$

- **determinant**: The factor by which W scales every area (volume in higher dimensions).

- **main diagonal**: Stretching along the axes enlarges area.

- **off-diagonal**: Mixing the axes tilts the square into a parallelogram, which takes area away.

det = 0: the unit square collapses to a line or point, so some different inputs map to the same output, and the transformation can't be reversed. The number of dimensions that survive is the **rank**. det < 0: space is flipped like a mirror image.

#### A small zoo of transformations

| Matrix | Does | Determinant |
|---|---|---|
| [[2, 0], [0, 0.5]] | Stretch x by 2, squash y by half | 1 (area kept) |
| [[cos θ, −sin θ], [sin θ, cos θ]] | Rotate by θ | 1 |
| [[1, 1], [0, 1]] | Shear: slide the top sideways | 1 |
| [[1, 2], [0.5, 1]] | Columns parallel: squash onto a line | 0 (rank 1, not invertible) |
| [[0, 1], [1, 0]] | Swap the axes (a reflection) | −1 (orientation flipped) |

#### Composition, order and inverses

- **Composition:** applying B then A is the single matrix AB (read right to left). Determinants multiply: det(AB) = det A · det B.

- **Order matters:** rotate-then-shear and shear-then-rotate land in different places, so in general AB ≠ BA.

- **Inverse:** W⁻¹ undoes W, and exists exactly when det W ≠ 0. For 2×2: W⁻¹ = (1/det) · [[w₂₂, −w₁₂], [−w₂₁, w₁₁]].

- **Stacked linear layers collapse:** W₂(W₁x) = (W₂W₁)x, one matrix. Without a non-linearity between them, a deep linear network is just one linear map, which is why activations matter.

#### Trace and change of basis

##### Trace

The trace is the sum of a matrix's diagonal entries. It looks simple, but it also equals the sum of the eigenvalues, so it doesn't change when you change coordinates. In ML, it appears in the Frobenius norm, since ‖A‖²F = tr(AᵀA), and in the total variance of a dataset, which is the trace of its covariance matrix.

##### Change of basis

The same transformation looks different in different coordinates. If P's columns are the new axes, the matrix in those coordinates is P⁻¹AP. Determinant, trace, rank and eigenvalues all stay the same, as they describe the transformation itself. Picking the eigenvectors as your axes makes the matrix diagonal, which is what eigendecomposition does.

Next: matrix multiplication and shapes, and linear independence and rank.

## In practice

### In practice

#### Matrices in ML

- **Dense layers:** h = σ(Wx + b): a linear transformation, a shift, then a bend.

- **Linear regression:** the normal equations solve (XᵀX)w = Xᵀy; if XᵀX is singular (perfectly correlated features, rank-deficient), there's no unique solution, which is what ridge regularisation fixes (Regularized Linear Models).

- **Covariance matrices:** describe how features vary together; their eigenvectors give PCA (next lesson).

- **Low-rank matrices:** LoRA and recommender embeddings deliberately use rank-r factors (SVD lesson).

### The answer that sounds right

#### "Matrix multiplication is just a recipe of rows times columns"

Memorising row-times-column works for computing, but hides the meaning, and leads to classic mistakes: assuming AB = BA (order matters: rotating then shearing ≠ shearing then rotating), or expecting every matrix to have an inverse. With the transformation view these are obvious: two moves in a different order end in different places, and a move that squashes the plane onto a line can't be undone because points that landed on top of each other can't be separated again.

## Say it

### What does a matrix do to a vector, and why do two linear layers act like one?

#### The interviewer pushes further

Follow-up 1 of 3

What does a determinant of zero mean for linear regression?

XᵀX is singular: some feature is a linear combination of others (perfect multicollinearity), so infinitely many weight vectors fit equally well. Drop a feature or add regularisation.

Follow-up 2 of 3

Why do neural networks need non-linear activations?

A composition of linear maps is linear: W₂W₁ is a single matrix, so without activations depth adds nothing.

Follow-up 3 of 3

What's the rank of a matrix?

The number of linearly independent columns (equivalently rows): the dimension of the output space the matrix can reach.

#### The 30-second answer

A matrix is a linear transformation: its columns say where the basis vectors land, and multiplying a vector combines those columns. Multiplying matrices composes transformations, so order matters. The determinant is the factor by which areas or volumes scale; zero means the space is squashed into fewer dimensions, the matrix is rank-deficient and has no inverse. In ML, every dense layer computes Wx + b, linear regression's normal equations need XᵀX to be invertible, and low-rank structure is exploited by PCA, matrix factorisation and LoRA.

**Go further**

#### What not to say

- "AB equals BA." Generally not.

- "Every square matrix can be inverted." Only if its determinant is non-zero.

**Key terms and sources**

Matrix–vector multiplication, columns as "where the axes go", composition, the determinant, rank and inverses, and why a neural-network layer is a matrix · built from Deisenroth et al., _Mathematics for Machine Learning_ (ch. 2, 4), Strang, _Introduction to Linear Algebra_, and 3Blue1Brown's _Essence of Linear Algebra_ · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Linear transformation** | Keeps lines straight and the origin fixed; any matrix. |
| **Determinant** | Area/volume scaling factor; sign = orientation. |
| **Rank** | Number of independent columns: dimensions that survive. |
| **Singular matrix** | det = 0; not invertible. |
| **Identity I** | The "do nothing" matrix. |

#### Sources

1. M. P. Deisenroth, A. A. Faisal & C. S. Ong, _Mathematics for Machine Learning_, CUP 2020, [mml-book.github.io](https://mml-book.github.io/) (ch. 2, 4.1).

2. G. Strang, _Introduction to Linear Algebra_, 5th ed., Wellesley-Cambridge Press 2016.

3. G. Sanderson (3Blue1Brown), [Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra) (visual intuition for transformations and determinants).
