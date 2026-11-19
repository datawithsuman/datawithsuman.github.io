# Orthogonality and Projections

> Why is least squares a projection, and why are orthogonal matrices so useful?

- Track: Fundamentals › Maths for ML › Linear algebra
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/orthogonality-and-projections/
- Before this: Vectors, Dot Products & Cosine Similarity (`fundamentals/vectors-and-cosine-similarity`), Linear Independence, Basis and Rank (`fundamentals/linear-independence-basis-and-rank`)
- Related: Linear Regression (`fundamentals/linear-regression`)
- Quiz topic: `la`

## Intuition

### The situation

You're asked to explain least squares without the usual calculus. Your dataset's predictions can only be combinations of its features, and no combination hits y exactly. The interviewer asks:

> Why is least squares a projection, and why are orthogonal matrices so useful?

#### Why it matters

This single picture explains linear regression, PCA, residuals, and why QR is the stable way to solve least squares. Once you see it as geometry, the formulas become easy to remember. See rank and dot products first.

### The idea

Think of the sun straight overhead, casting a pole's shadow on flat ground. The shadow is the closest point on the ground to the top of the pole, and the line from pole top to shadow makes a right angle with the ground. Regression's predictions are y's shadow on what your features can produce.

[Figure: Least squares as a projection. Xw can only reach the column space. Predictions are the closest point to y in that space. The residual is at right angles to it.]

_The residual at right angles is the whole idea._

### Play

**Try to break it.** Rotate the line through the point, then at right angles to it. Move the point anywhere.

#### Project a point onto a line

Blue is the line, green is the projection and red is the residual. Move anything: the residual · line value stays at zero.

Rotate the line until it passes through the point. The error falls to **zero**, which is like a regression fitting perfectly because y is in the column space. Now rotate it to be at right angles to the point: the projection is zero, meaning the feature tells you nothing about y.

**Now say why:** why must the shortest error be at right angles to the line?

## Maths

### Maths

#### In one breath

Vectors are **orthogonal** if their dot product is zero: they share no direction. **Projection** finds the closest point on a line or subspace, and the error is always at right angles to it. **Least squares is exactly this**: your predictions are the projection of y onto the space of what your features can produce. **Orthogonal matrices** only rotate or reflect, keeping lengths, which makes them very stable.

#### The closest point

##### Why right angles

To find the closest point to b on a line, drop a perpendicular. Any other point on the line is farther away. So the leftover error, b minus the projection, must be orthogonal to the line. That single condition gives every formula here.

##### From a line to least squares

1. Xw can only produce vectors in X's column space.

2. y usually isn't in that space, so no w fits exactly.

3. The closest achievable point is y's projection onto the column space.

4. The residual y − Xw must be orthogonal to every column of X: Xᵀ(y − Xw) = 0.

5. Rearranging gives the **normal equations**: XᵀXw = Xᵀy.

That explains a fact about regression with an intercept: residuals sum to zero, because the residual is orthogonal to the all-ones column.

##### Orthogonal matrices

Q has orthonormal columns, and QᵀQ = I. So its inverse is just its transpose, and it never changes a vector's length. It can't amplify errors, which makes it numerically stable.

##### Gram-Schmidt and QR

Take the columns one at a time. Subtract each column's projection onto those before it, then scale to length 1. This gives an orthonormal basis Q, and the coefficients form an upper triangular R, so **A = QR**. Least squares then becomes the easy triangular system Rw = Qᵀy.

#### The maths

$$ \hat b = \frac{a^\top b}{a^\top a}\,a, \qquad P = X(X^\top X)^{-1}X^\top, \qquad \hat y = Py $$

Example: project b = (2, 3) onto a = (1, 0). The result is (2, 0), and the residual (0, 3) is orthogonal to a.

- **the projection**: The closest point to b along the direction a.

- **how much b points along a**: The dot product measures overlap.

- **normalising**: Divides out a’s own length, so scaling a doesn’t change the result.

- **projection matrix**: Projects onto X’s column space. Applying it twice changes nothing: P² = P.

- **predictions**: Regression predictions are y projected onto what X can produce.

## In practice

### In practice

#### In practice

- **Use QR for regression:** solving through XᵀX squares the condition number, so QR is more stable. See solving Ax = b.

- **Check residuals:** if residuals correlate with a feature, the fit isn't really least squares, or there's a bug.

- **PCA:** PCA projects onto the directions that keep the most variance.

- **Orthogonal initialisation:** starting a layer's weights as orthogonal keeps signal lengths steady, which helps deep and recurrent networks.

- **Orthogonal features:** if features are orthogonal, each weight can be computed separately, and removing one doesn't change the others.

### The answer that sounds right

#### "Just solve the normal equations"

It sounds right, since they're the textbook formula, and for small, well-behaved problems they're fine. But forming XᵀX squares the condition number, which can destroy accuracy on correlated features. QR uses the same geometry on X itself, and that's why libraries use it.

## Say it

### Why is least squares a projection, and why are orthogonal matrices so useful?

#### The interviewer pushes further

Follow-up 1 of 3

Why do the residuals sum to zero in regression with an intercept?

The intercept column is all ones, and the residual is orthogonal to every column. A dot product with all ones is just the sum, so it must be zero. Without an intercept, this needn't hold.

Follow-up 2 of 3

What's the difference between orthogonal and uncorrelated?

Orthogonal means the dot product is zero. Uncorrelated means the covariance is zero, which is the dot product after subtracting the means. So for centred data, they're the same. For uncentred data, they can differ.

Follow-up 3 of 3

Why is P squared equal to P?

Once a point is in the space, it's already its own closest point, so projecting again doesn't move it. Algebraically, the middle XᵀX cancels with its inverse. It's a useful test of whether a matrix is a projection.

Xw can only produce vectors in the column space of X. y usually isn't there, so least squares finds the closest point, which is y's projection onto that space. The residual must be orthogonal to every column, giving X transpose times y minus Xw equals zero, which is the normal equations. Orthogonal matrices have Q transpose Q equal to the identity, so they keep lengths, and their inverse is just the transpose. That's why QR, built with Gram-Schmidt, is a stable way to solve least squares.

**Key terms and sources**

Orthogonal vectors and matrices, projecting onto a line and subspace, least squares as a projection, Gram-Schmidt and QR.

#### Sources

- Deisenroth, Faisal and Ong, Mathematics for Machine Learning

- Boyd and Vandenberghe, Introduction to Applied Linear Algebra

- Strang, Linear Algebra and Learning from Data

- Linear regression on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
