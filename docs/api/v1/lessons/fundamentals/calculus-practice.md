# Calculus Practice

> Derivatives, gradients, step sizes and constraints: can you do them by hand?

- Track: Fundamentals › Maths for ML › Calculus and optimisation
- Type: Interview · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/calculus-practice/
- Before this: Gradient Descent, Momentum & Adam (`fundamentals/gradient-descent`)
- Quiz topic: `calc`

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your approach out loud, then open the answer and compare the method, not just the number.

**Tools for this page:** the chain rule for derivatives, the second derivative to classify flat points, and shapes to check your gradients.

Question 1 · Easy · derivatives

### What's the derivative of f(x) = x³ − 2x at x = 2?

Answer: **10**

1. f′(x) = 3x² − 2.

2. At x = 2: 3 × 4 − 2 = 10.

This is how much f changes per small change in x.

Question 2 · Easy · chain rule

### What's the derivative of (3x + 1)² at x = 1?

Answer: **24**

1. Let u = 3x + 1. The outside derivative is 2u, and the inside is 3.

2. So f′(x) = 6(3x + 1).

3. At x = 1: 6 × 4 = 24.

Backpropagation applies this rule repeatedly.

Question 3 · Easy · gradient

### What's the gradient of f(x, y) = x²y at (3, 2)?

Answer: **(12, 9)**

1. ∂f/∂x = 2xy = 12.

2. ∂f/∂y = x² = 9.

It points in the direction of steepest increase.

Question 4 · Medium · sigmoid

### What's the derivative of the sigmoid σ(x)? Where's it largest, and what does that mean for training?

Answer: **σ′ = σ(1 − σ), largest at x = 0, with a value of 0.25**

1. Differentiating 1/(1 + e⁻ˣ) gives σ(1 − σ).

2. This is largest when σ = 0.5, at x = 0, giving 0.25.

3. For large |x|, it approaches 0.

Multiplying many of these small values is why deep sigmoid networks suffer vanishing gradients.

Question 5 · Medium · gradient descent

### You use gradient descent on f(x) = x², from x = 1, with learning rate 0.1. Where are you after two steps? At what learning rate does it diverge?

Answer: **x = 0.64. It diverges above 1**

1. Each step: x ← x − η(2x) = (1 − 2η)x.

2. With η = 0.1, the factor is 0.8, so x = 0.8, then 0.64.

3. It diverges when |1 − 2η| > 1, which is η > 1.

Here the second derivative is 2, so the limit is 2 ÷ 2 = 1.

Question 6 · Medium · critical points

### Find and classify the critical points of f(x) = x⁴ − x².

Answer: **x = 0 is a local maximum. x = ±1/√2 are minima, with f = −0.25**

1. f′(x) = 4x³ − 2x = 2x(2x² − 1), so x = 0 or x = ±1/√2.

2. f″(x) = 12x² − 2.

3. f″(0) = −2, a maximum. f″(±1/√2) = 4, minima.

This one has two minima of equal depth, and it's not convex.

Question 7 · Hard · Newton's method

### Take one Newton step to minimise f(x) = x⁴ from x = 1. Why is this slower than usual for Newton?

Answer: **x = 2/3. Curvature vanishes at the minimum**

1. f′ = 4x³ and f″ = 12x².

2. Step: x − 4x³ / 12x² = x − x/3 = 2x/3.

3. From x = 1, that's 2/3, and each step only multiplies x by 2/3.

Newton's fast convergence needs positive curvature at the solution. Here, f″(0) = 0, so it's only linear.

Question 8 · Hard · Lagrange

### Maximise xy, with x + y = 10. What's the best value, and what does λ tell you?

Answer: **25, at (5, 5), with λ = 5**

1. ∇(xy) = (y, x) and ∇(x + y) = (1, 1).

2. So y = λ and x = λ, giving x = y = 5, and xy = 25.

3. In general, the best value is c²/4, whose derivative at c = 10 is 5, which equals λ.

Raising the limit by 1 increases the best value by about 5.

**More practice and sources**

8 interview questions, easy to hard · answers hidden until you click · checked 6 Nov 2026

Keep practising

Review derivatives, gradient descent, Newton and Lagrange multipliers.
