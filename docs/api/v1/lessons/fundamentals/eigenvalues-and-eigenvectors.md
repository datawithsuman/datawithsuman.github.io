# Eigenvalues & Eigenvectors

> Which directions does a matrix only stretch, and why does PCA care?

- Track: Fundamentals › Maths for ML › Linear algebra
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/eigenvalues-and-eigenvectors/
- Before this: Matrices as Transformations (`fundamentals/matrices-as-transformations`)
- Related: Principal Component Analysis (`fundamentals/pca`)
- Quiz topic: `la`

## Intuition

### The situation

You're running PCA on customer data where orders and app sessions move together. The interviewer asks:

> What is an eigenvector, and how does PCA use eigenvectors?

**Running example:** the covariance matrix of two customer features, orders per month and app sessions per month, both standardised. They move together (correlation 0.5), so the covariance matrix is [[1, 0.5], [0.5, 1]]. What directions does it single out? (The same data appears in the PCA lesson.)

#### Finding a matrix's natural axes

A matrix mixes coordinates, which makes it hard to understand. But many matrices have a hidden set of axes along which they act simply: stretch this way by 1.5, that way by 0.5, nothing else. Find those axes and the matrix becomes a list of stretches. In ML those axes are the directions of greatest variance in data, the most important pages on the web, or the directions in which training is unstable.

### The idea

Think of stretching a rubber sheet with arrows drawn on it. Most arrows swing to a new direction. A few stay on their own line and only get longer or shorter. Those are eigenvectors, and how much they stretch is the eigenvalue.

[Figure: Three arrows before and after a matrix. Two eigenvector arrows stay on their lines and only change length. A third arrow swings to a new direction.]

_Illustrative, using the lesson's covariance matrix: one direction stretches by 1.5, the other by 0.5._

### Play

**Try to break it.** On the covariance matrix, find the arrows that stay on their line. Then switch to rotation 45° and look for them again.

#### Which arrows stay on their line?

Teal: 24 unit vectors around the circle. Orange: where the matrix sends each one (thin line joins input to output). Green: eigen-directions, where input and output stay on the same line.

For the covariance matrix, every arrow swings towards the diagonal except two: along (1, 1) the matrix stretches by 1.5, along (1, −1) it shrinks to 0.5. Those are the directions in which "orders and sessions together" vary most and least: the first and second principal components, with variances 1.5 and 0.5 (75% and 25% of the total).

**Now say why:** why does the rotation have no such arrows, while the covariance matrix has two perpendicular ones?

## Maths

### Maths

#### In one breath

Most vectors get knocked off their direction when a matrix acts on them. **Eigenvectors** are the special directions that stay on their own line, only stretched or shrunk; the stretch factor is the **eigenvalue** λ, so Av = λv. For a symmetric matrix (like a covariance matrix) the eigenvectors are perpendicular and the eigenvalues real: the matrix is just "stretch along these axes". That is exactly PCA: the eigenvectors of the covariance matrix are the principal components, and the eigenvalues are the variances along them. Repeatedly multiplying by A pulls any vector towards the top eigenvector (**power iteration**), the idea behind PageRank. What you'll be able to do after this: define eigenvectors geometrically, compute them for a 2×2 matrix, explain why covariance eigenvectors are PCA, and describe power iteration.

#### The eigen-equation

$$ {A v} = {\lambda v}, \qquad {\det(A - \lambda I) = 0} $$

MML §4.2; Strang ch. 6. Worked example: A = [[1, 0.5], [0.5, 1]] gives (1 − λ)² − 0.25 = 0, so λ = 1.5 with v = (1, 1)/√2 and λ = 0.5 with v = (1, −1)/√2.

- **the matrix acting on v**: Apply the transformation to a candidate direction v.

- **just a stretched v**: The result points along v itself, scaled by λ. λ > 1 stretches, 0 < λ < 1 shrinks, λ < 0 flips, λ = 0 squashes v to zero.

- **how to find λ**: Av = λv means (A − λI)v = 0 has a non-zero solution, so A − λI must be singular: its determinant is zero. For a 2×2 matrix that’s a quadratic in λ.

#### Symmetric matrices: the spectral theorem

$$ {A} = {Q}\,{\Lambda}\,{Q^{\top}} $$

Spectral theorem for real symmetric matrices: real eigenvalues, orthonormal eigenvectors (MML Theorem 4.15). In practice libraries compute eigen-decompositions with QR-type algorithms (`numpy.linalg.eigh` for symmetric matrices).

- **any symmetric matrix**: For example a covariance matrix.

- **rotate to the eigen-axes**: Q’s columns are orthonormal eigenvectors. Qᵀ rotates the data into eigen-coordinates.

- **stretch along each axis**: Λ is diagonal: the eigenvalues. Nothing but independent stretches.

- **rotate back**: Q rotates back. So A = rotate, stretch, rotate back.

#### Multiply repeatedly and you find the top eigenvector

Write the start vector as a mix of eigenvectors. Each multiplication scales the λ = 1.5 part by 1.5 and the λ = 0.5 part by 0.5, so the smaller part shrinks by a factor of 3 every step relative to the larger; after normalising, the vector swings onto the top eigenvector. The speed depends on the ratio of the top two eigenvalues. Brin & Page's original PageRank is the principal eigenvector of the web's link matrix, computed exactly this way at scale [Brin & Page 1998](http://infolab.stanford.edu/~backrub/google.html).

#### The Rayleigh quotient: why PCA picks the top eigenvector

For a symmetric A, the **Rayleigh quotient** R(x) = xᵀAx / xᵀx says how much A stretches along x. It always lies between the smallest and largest eigenvalues, and it reaches the largest exactly at the top eigenvector.

Example: for A = [[2, 1], [1, 2]], R(1, 0) = 2, while R(1, 1) = 3, the top eigenvalue.

This explains PCA. The variance of data projected onto a unit vector w is wᵀΣw, which is the Rayleigh quotient of the covariance matrix. So the direction of most variance must be Σ's top eigenvector, and that variance is its eigenvalue.

Next: positive definite matrices look at what the signs of the eigenvalues mean.

## In practice

### In practice

#### Eigenvectors in ML

- **PCA:** principal components are eigenvectors of the covariance matrix; eigenvalues are explained variances (PCA).

- **Optimisation:** eigenvalues of the loss Hessian are curvatures; gradient descent diverges when the learning rate exceeds 2/λmax (Gradient Descent), and a large ratio λmax/λmin (condition number) makes it zig-zag.

- **Graphs:** spectral clustering uses eigenvectors of the graph Laplacian; PageRank uses the top eigenvector of the link matrix.

- **RNN stability:** repeatedly multiplying by a recurrent weight matrix explodes or vanishes depending on whether its largest eigenvalue magnitude is above or below 1.

### The answer that sounds right

#### "Every matrix has real eigenvectors you can see"

A rotation by 45° moves every direction; it has no real eigenvectors (its eigenvalues are complex). A shear has only one eigen-direction. Non-symmetric matrices can have eigenvectors that aren't perpendicular. The tidy picture, perpendicular axes and real stretches, is guaranteed only for **symmetric** matrices, which luckily include covariance matrices, Hessians and graph Laplacians: most of the matrices ML cares about.

## Say it

### What is an eigenvector, and how does PCA use eigenvectors?

#### The interviewer pushes further

Follow-up 1 of 3

How is PCA related to eigenvectors?

PCA's components are the eigenvectors of the data's covariance matrix, sorted by eigenvalue; each eigenvalue is the variance along its component. In practice computed via SVD of the centred data.

Follow-up 2 of 3

Can eigenvalues be negative or complex?

Yes in general; rotations have complex ones. Symmetric matrices have real eigenvalues; covariance matrices (positive semi-definite) have non-negative ones.

Follow-up 3 of 3

What's the link to exploding/vanishing gradients?

Multiplying by the same matrix many times scales components by λᵗ: |λ| > 1 explodes, |λ| < 1 vanishes.

#### The 30-second answer

An eigenvector of a matrix is a direction the matrix only stretches, Av = λv, and the eigenvalue is the stretch factor. You find eigenvalues from det(A − λI) = 0. Symmetric matrices, like covariance matrices, have real eigenvalues and perpendicular eigenvectors, so they decompose as QΛQᵀ: rotate, stretch, rotate back. In ML, the covariance eigenvectors are PCA's principal components with eigenvalues as variances, Hessian eigenvalues describe curvature and set the maximum stable learning rate, and power iteration finds the top eigenvector, as in PageRank.

**Go further**

#### What not to say

- "Eigenvectors are always perpendicular." Only guaranteed for symmetric (normal) matrices.

- "An eigenvector is unique." Any non-zero multiple is also an eigenvector; we usually normalise.

**Key terms and sources**

The directions a matrix only stretches, how to find them, symmetric matrices and the spectral theorem, power iteration, and where they power PCA, PageRank and stability analysis · built from Deisenroth et al., _Mathematics for Machine Learning_ (ch. 4), Strang, _Introduction to Linear Algebra_ (ch. 6), and Brin & Page (1998) · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Eigenvector** | A non-zero v with Av = λv: a direction only stretched. |
| **Eigenvalue** | The stretch factor λ. |
| **Characteristic equation** | det(A − λI) = 0. |
| **Spectral theorem** | Symmetric A = QΛQᵀ, orthonormal eigenvectors, real eigenvalues. |
| **Power iteration** | Repeated multiplication + normalisation → top eigenvector. |
| **Condition number** | λmax/λmin (symmetric positive definite): how stretched the problem is. |

#### Sources

1. M. P. Deisenroth, A. A. Faisal & C. S. Ong, _Mathematics for Machine Learning_, CUP 2020, [mml-book.github.io](https://mml-book.github.io/) (ch. 4: eigendecomposition, spectral theorem).

2. G. Strang, _Introduction to Linear Algebra_, 5th ed., 2016, ch. 6.

3. S. Brin & L. Page, "The anatomy of a large-scale hypertextual web search engine", WWW 1998, [stanford.edu](http://infolab.stanford.edu/~backrub/google.html).
