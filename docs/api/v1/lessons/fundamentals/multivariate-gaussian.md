# The Multivariate Gaussian

> What does the covariance matrix do to a multivariate Gaussian, and what are its useful properties?

- Track: Fundamentals › Maths for ML › Probability
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/multivariate-gaussian/
- Before this: Expectation, Variance & Covariance (`fundamentals/expectation-and-variance`), Eigenvalues & Eigenvectors (`fundamentals/eigenvalues-and-eigenvectors`)
- Related: Principal Component Analysis (`fundamentals/pca`)
- Quiz topic: `prob`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: 111c641505

## Intuition

### The situation

You've fitted a Gaussian to two related features, height and weight. A teammate treats them separately, flagging only points far out on one feature. An odd combination, tall yet very light, gets missed. The interviewer asks:

> What does the covariance matrix do to a multivariate Gaussian, and what are its useful properties?

#### Why it matters

This is the most used distribution in ML, from PCA and Gaussian processes to VAEs and diffusion models. It's also where eigenvectors and positive definite matrices meet probability.

### The idea

Think of a spray of paint on a wall. The mean is where you aim. The covariance is the shape of the spray: round, stretched or tilted. A tilted spray tells you that knowing how far right a drop landed helps you guess how high it landed.

[Figure: What sets the Gaussian's shape. The mean sets the centre. The variances set the widths. The correlation sets the tilt.]

_The eigenvectors of the covariance give the ellipse's axes._

### Play

**Try to break it.** Set the correlation to 0, then near 1. Compare the green and purple lines.

#### Shape a two-dimensional Gaussian

Contours at 1 and 2 standard deviations, with zero mean. Purple is the main eigenvector, and green is the conditional mean of y. They usually differ, as they answer different questions.

Notice that the green and purple lines differ. Regression's line predicts y from x, while PCA's axis follows the most spread. That's why PCA and linear regression don't give the same answer, even on the same data.

**Now say why:** why does regression's line differ from PCA's axis?

## Maths

### Maths

#### In one breath

A **multivariate Gaussian** has a mean, which sets its centre, and a **covariance matrix**, which sets its shape. The contours are ellipses, whose axes are the covariance's **eigenvectors**, with widths from the square roots of its eigenvalues. It has rare properties: **marginals and conditionals are Gaussian too**, and for jointly Gaussian variables, uncorrelated means independent. To sample, turn standard noise z into μ + Lz, using the Cholesky factor. That same idea appears in VAEs and diffusion.

#### Reading the shape

##### What each part does

- **Diagonal of Σ:** each variable's variance, or how wide it spreads along its own axis.

- **Off-diagonal of Σ:** how two variables move together, which tilts the ellipse.

- **Eigenvectors of Σ:** the axes of the ellipse. This is exactly what PCA finds.

- **Determinant of Σ:** the overall volume of the spread.

##### Why it's so convenient

| Property | What it means |
|---|---|
| **Marginals** | Ignore some variables, and the rest are Gaussian. Just drop those rows and columns. |
| **Conditionals** | Fix some values, and the rest are Gaussian. The mean shifts in a straight line. |
| **Linear maps** | Ax + b is Gaussian, with mean Aμ + b and covariance AΣAᵀ. |
| **Independence** | For jointly Gaussian variables, zero covariance means independent. That's not true in general. |

##### Distance that respects shape

The exponent contains the **Mahalanobis distance**, which measures distance in units of spread along each direction. A point may be close in plain distance yet far in Mahalanobis distance, if it goes against the correlation. That's why it's useful for anomaly detection.

##### Sampling

Factor Σ = LLᵀ using Cholesky, draw z from a standard Gaussian, and take x = μ + Lz. The randomness is now separate from the parameters, which is the reparameterisation trick that lets gradients flow in VAEs.

#### The maths

$$ {p(x)} = \frac{1}{{\sqrt{(2\pi)^d |\Sigma|}}} \exp\Big(-\tfrac{1}{2}{(x-\mu)^\top \Sigma^{-1} (x-\mu)}\Big), \qquad {\mu_{y|x} = \mu_y + \rho\frac{\sigma_y}{\sigma_x}(x - \mu_x)} $$

The conditional variance is σ²ᵧ(1 − ρ²), so a stronger correlation leaves less uncertainty about y once you know x.

- **the density**: Highest at the mean, and falling away in ellipses.

- **the normaliser**: Makes the total probability 1. The determinant measures the volume of the spread.

- **Mahalanobis distance**: Distance from the mean, adjusted for shape. Equal values form an ellipse.

- **the conditional mean**: In two dimensions, knowing x shifts your guess for y along a straight line. That’s where linear regression’s slope comes from.

## In practice

### In practice

#### In practice

- **Diagonal covariance:** full covariance needs about d²/2 numbers. VAEs and many mixtures use a diagonal, needing just d, at the cost of ignoring correlations.

- **Check the assumption:** marginals can each look Gaussian without the joint being Gaussian.

- **High dimensions:** most of a high-dimensional Gaussian's mass lies in a thin shell, far from the mean, not at its peak. Intuition from two dimensions can mislead you.

- **Adding noise:** diffusion models repeatedly add Gaussian noise, and linear maps of Gaussians staying Gaussian makes this tractable.

- **Unstable matrices:** estimating a large covariance from few samples gives a matrix that's near singular. Regularise it, or add a little to the diagonal.

### The answer that sounds right

#### "Zero correlation means they're independent"

It sounds right, and it's true for jointly Gaussian variables. But in general, correlation only measures straight-line relationships. If x is symmetric around zero, and y = x², they have zero correlation, while y depends entirely on x. So don't assume independence from a correlation table alone.

## Say it

### What does the covariance matrix do to a multivariate Gaussian, and what are its useful properties?

#### The interviewer pushes further

Follow-up 1 of 3

Are uncorrelated variables always independent?

No. It's only guaranteed if they're jointly Gaussian. For example, if x is symmetric around zero and y = x², they have zero correlation, but y is completely determined by x. Correlation only measures linear relationships.

Follow-up 2 of 3

Why are the regression line and PCA's first axis different?

Regression minimises vertical errors in y, so it predicts y given x. PCA minimises perpendicular distance, treating variables symmetrically, to follow the most spread. Their slopes usually differ, and they match when the correlation is perfect. Regression's line is the conditional mean of the Gaussian, not its main axis.

Follow-up 3 of 3

How would you sample from a Gaussian with covariance Σ?

Factor Σ = LLᵀ with Cholesky, draw z from a standard normal, and return μ + Lz. The covariance of Lz is LLᵀ = Σ. If Σ isn't numerically positive definite, add a small amount to the diagonal first.

#### The 30-second answer

A multivariate Gaussian has a mean for its centre, and a covariance matrix for its shape. Contours are ellipses, whose axes are the covariance's eigenvectors, with widths from the square roots of the eigenvalues, which is what PCA finds. Its marginals and conditionals are Gaussian, linear maps stay Gaussian, and uncorrelated variables are independent. To sample, I'd factor sigma as L L transpose, and take mu plus L z. Separating the noise this way is the reparameterisation trick used in VAEs.

**Key terms and sources**

The Gaussian in many dimensions: the mean and covariance as a shape, marginals and conditionals, sampling, and its links with PCA and generative models. · checked 6 Nov 2026

#### Sources

- [Deisenroth, Faisal and Ong, Mathematics for Machine Learning](https://mml-book.github.io/)

- [Murphy, Probabilistic Machine Learning: An Introduction](https://probml.github.io/pml-book/book1.html)

- Gaussian mixture models on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
