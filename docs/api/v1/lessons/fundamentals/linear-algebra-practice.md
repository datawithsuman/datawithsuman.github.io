# Linear Algebra Practice

> Shapes, rank, eigenvalues, least squares, SVD and gradients: can you do them by hand?

- Track: Fundamentals › Maths for ML › Linear algebra
- Type: Interview · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/linear-algebra-practice/
- Before this: SVD & Low-Rank Approximation (`fundamentals/svd-and-low-rank`)
- Quiz topic: `la`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-19 · Version: 13588701d3

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your approach out loud, then open the answer and compare the method, not just the number.

**Tools for this page:** check shapes first, then ask what's independent. For symmetric matrices, the eigenvalues add up to the trace and multiply to the determinant, which is a quick check.

Question 1 · Easy · shapes

### A is 3 × 4, and B is 4 × 2. What shape is AB? Can you compute BA?

Answer: **AB is 3 × 2. BA isn't defined.**

1. For AB, the inner sizes match: 4 and 4. The result takes the outer sizes: 3 × 2.

2. For BA, the inner sizes are 2 and 3, which don't match.

Even when both are defined, AB usually differs from BA.

Question 2 · Easy · rank

### What's the rank of [[1, 2], [2, 4]]?

Answer: **1**

1. The second row is twice the first, so there's only one independent row.

2. Check: the determinant is 1 × 4 − 2 × 2 = 0, so it can't have rank 2.

Rows and columns always have the same rank.

Question 3 · Easy · cosine

### What's the cosine similarity between (1, 0) and (1, 1)?

Answer: **About 0.707**

1. Dot product: 1 × 1 + 0 × 1 = 1.

2. Lengths: 1 and √2.

3. Cosine: 1 / √2 ≈ 0.707, an angle of 45°.

Length doesn't affect cosine similarity.

Question 4 · Medium · eigenvalues

### Find the eigenvalues of [[2, 1], [1, 2]]. Is the matrix positive definite?

Answer: **3 and 1, so yes**

1. Solve (2 − λ)² − 1 = 0, so 2 − λ = ±1.

2. λ = 3 with eigenvector (1, 1), and λ = 1 with eigenvector (1, −1).

3. All eigenvalues are positive, so it's positive definite.

The eigenvalues add up to the trace, 4, and multiply to the determinant, 3. That's a quick check.

Question 5 · Medium · least squares

### You fit one constant w to y = (1, 2, 6), using least squares. What's w, and how does this relate to projection?

Answer: **w = 3, the mean**

1. X is the all-ones column, so XᵀX = 3, and Xᵀy = 9.

2. w = 9 / 3 = 3.

3. The prediction (3, 3, 3) is y's projection onto the all-ones direction, and the residual (−2, −1, 3) sums to zero, so it's orthogonal to it.

This is why the mean minimises squared error.

Question 6 · Medium · multiplication cost

### A is 10 × 100, B is 100 × 5 and C is 5 × 50. How much do (AB)C and A(BC) cost?

Answer: **7,500 and 75,000 multiplications**

1. (AB)C: 10 × 100 × 5 = 5,000, then 10 × 5 × 50 = 2,500. Total: 7,500.

2. A(BC): 100 × 5 × 50 = 25,000, then 10 × 100 × 50 = 50,000. Total: 75,000.

Same result, at ten times the cost.

Question 7 · Hard · SVD

### A matrix has singular values 5, 3 and 1. What's the error of its best rank-2 approximation, and what share of the energy does it keep?

Answer: **Error 1, and about 97% of the energy**

1. The best rank-2 keeps 5 and 3, and drops 1 (Eckart-Young).

2. Frobenius error: √(1²) = 1. Spectral error: 1.

3. Energy kept: (25 + 9) / (25 + 9 + 1) = 34/35 ≈ 97.1%.

Energy uses squared singular values, not the values themselves.

Question 8 · Hard · gradient

### What's the gradient of f(x) = xᵀAx, with A = [[2, 1], [1, 3]] at x = (1, 1)?

Answer: **(6, 8)**

1. A is symmetric, so ∇f = 2Ax.

2. Ax = (2 + 1, 1 + 3) = (3, 4).

3. 2Ax = (6, 8).

Check numerically: f(1, 1) = 7. Nudging x₁ by 0.01 gives f ≈ 7.0602, a slope of about 6.

**More practice and sources**

8 interview questions, easy to hard · answers hidden until you click · checked 6 Nov 2026

Keep practising

Review vectors, rank, SVD and matrix calculus.
