# Linear Regression

> What does least squares actually minimise, and when does it break?

- Track: Fundamentals › Classical ML › Linear models
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/linear-regression/
- Quiz topic: `lin`

## Intuition

### The situation

You have 12 flats with their size and price, and you need to predict the price of a new one. You could draw endless lines through them. The interviewer asks:

> What is linear regression, and how is it fitted?

**Running example:** 12 flats in one city, size in m² and price in ₹ lakh (illustrative numbers). Goal: predict the price of a flat from its size.

#### Draw the "best" straight line through a cloud of points

You have flats you know the price of, and a new flat you don't. Plot price against size and the points roughly follow a line. Linear regression turns "roughly follows a line" into a precise answer: _which_ line, and _why_ that one.

1. Twelve flats. Bigger flats cost more, but not perfectly: the points scatter around a trend.

2. A candidate line: price ≈ 0.85 lakh per m² × size + 9.6 lakh. Any line makes a prediction ŷ for every size.

3. The vertical gaps between each point and the line are the errors, called **residuals**: y − ŷ.

4. Least squares squares each residual (literally: the red squares) and adds them up. Big misses count much more than small ones.

5. The fitted line is the one with the smallest total squared error. For these 12 flats, no other straight line does better.

That's the whole idea. Everything else on this page is _how_ to find that line, _why_ squares, and _when_ to distrust it.

### The idea

Think of a stiff rod held by a spring to every data point. The further away a point is, the harder its spring pulls. The rod settles where the total pull balances out, and that's the least-squares line.

[Figure: Points scattered around a straight line, with a short vertical gap from each point to the line.]

_Illustrative. Squaring the gaps means big misses count far more than small ones._

### Play

**Try to break it.** Drag the slope and intercept until the red squares are as small as you can get them. Then snap to the least-squares line.

#### Feel the bowl: move the line, watch the loss

Illustrative data: 12 flats. The red squares are the squared residuals; their total area (÷ 12) is the MSE. Notice that slope and intercept trade off: a steeper slope needs a lower intercept.

**Now say why:** why does a steeper slope need a lower intercept, and how close did you get to the best line?

## Maths

### Maths

#### In one breath

Linear regression predicts a number as a weighted sum of features, ŷ = w·x + b, and picks the weights that make the **sum of squared errors** as small as possible. There's a closed-form answer (the normal equation) and an iterative one (gradient descent). Under Gaussian noise, least squares is exactly maximum likelihood. It's simple, fast and interpretable, and it breaks in predictable ways: outliers, curved relationships, and correlated features. What you'll be able to do after this: derive and explain the loss, solve it two ways, read the assumptions, spot when the line is lying to you, and answer the classic follow-ups.

#### A weighted sum of features

With one feature, the model is a line: slope w and intercept b. With many features (size, floor, age, distance to metro), it's the same idea in more dimensions: each feature gets a weight, and the prediction is the weighted sum plus a bias.

$$ {\hat{y}} = {w_1}{x_1} + {w_2}{x_2} + \dots + {b} \qquad {\hat{\mathbf y} = X\theta} $$

CS229 writes hθ(x) = θ⊤x with x0 = 1 standing in for the bias [CS229 §1](https://cs229.stanford.edu/main_notes.pdf) · hover any symbol.

- **prediction**: The model's guess: the predicted price ŷ.

- **weights**: One number per feature: how much the price moves when that feature goes up by one unit, holding the others fixed. Here about 0.85 lakh per m².

- **features**: The inputs for one flat: size, and any other columns you have.

- **bias / intercept**: The prediction when every feature is zero. Often not meaningful on its own (a 0 m² flat), but it lets the line sit at the right height.

- **all rows at once**: Stack every flat as a row of X, with an extra column of 1s for the bias. Then all predictions are one matrix product: ŷ = Xθ.

"Linear" means linear in the **weights**, not necessarily in the raw inputs. You can feed in x², log(x) or a product of two features and it is still linear regression.

#### Choose the weights that minimise the sum of squared residuals

$$ {J(\theta)} = {\tfrac12\sum_{i=1}^{n}}{\big(}{\theta^{\top}x^{(i)}} - {y^{(i)}}{\big)^2} $$

The least-squares cost function, CS229 §1 [CS229 notes](https://cs229.stanford.edu/main_notes.pdf). The mean squared error (MSE) is the same thing divided by n.

- **the cost**: One number that scores a choice of weights θ. Lower is better.

- **prediction**: The model's prediction for example i: θᵀx⁽ⁱ⁾.

- **the truth**: The real price of flat i.

- **squared miss**: Square the residual: no cancelling, and big misses cost much more than small ones.

- **over all examples**: Add up across all n training flats. The ½ is just there so the derivative comes out clean.

J is a bowl: a smooth, convex function of the weights with a single lowest point. That's why linear regression always has one best answer (or a flat valley of equally good answers when features are redundant), and why the methods below can find it reliably.

#### The normal equation: set the slope of the bowl to zero

At the bottom of a bowl, the gradient is zero. Differentiate J, set it to zero, and you get a linear system you can solve in one shot [CS229 §1.2](https://cs229.stanford.edu/main_notes.pdf):

$$ {\theta^{*}} = {(X^{\top}X)^{-1}}\,{X^{\top}\mathbf{y}} \qquad {\text{if } X^{\top}X \text{ is invertible}} $$

From X⊤Xθ = X⊤y, CS229 §1.2 and footnote 3 on invertibility.

- **best weights**: The weights that minimise J exactly.

- **undo the feature overlap**: XᵀX shows how the features move together (p × p). Its inverse untangles how much each feature contributes on its own.

- **feature–target overlap**: How much each feature moves together with the target.

- **needs an inverse**: Only works if XᵀX is invertible: fails when features are perfectly redundant (size in m² and in ft²) or when there are more features than rows. Nearly redundant features make it numerically shaky; that's what Ridge fixes.

1. Think of all 12 prices as one vector in 12-dimensional space. Every choice of weights gives a prediction vector Xθ, and all of them lie on a flat surface: the space spanned by the feature columns.

2. The real prices y are almost never on that surface. No line passes through every point.

3. The best you can do is the point on the surface closest to y. That's ŷ = Xθ*.

4. "Closest" means the leftover error is perpendicular to the surface: Xᵀ(y − Xθ) = 0. Rearranged, that is exactly the normal equation. Least squares is a projection.

##### What breaks: cost and conditioning

Inverting XᵀX costs about p³ operations, fine for hundreds or thousands of features, painful for millions. And when features are nearly collinear, tiny changes in the data swing the weights wildly; scikit-learn: the least-squares estimate "becomes highly sensitive to random errors in the observed target, producing a large variance" [scikit-learn docs](https://scikit-learn.org/stable/modules/linear_model.html). Libraries solve via QR or SVD rather than an explicit inverse for stability.

#### Gradient descent: small steps against the slope

Instead of solving the system, start anywhere and repeatedly nudge each weight in the direction that lowers J. For least squares the update is the **LMS rule**: move each weight by the error times its feature [CS229 §1.1](https://cs229.stanford.edu/main_notes.pdf).

$$ {\theta_j} := {\theta_j} + {\alpha}\,{\big(y^{(i)} - h_\theta(x^{(i)})\big)}\,{x^{(i)}_j} $$

- **one weight**: Weight j, updated in place.

- **learning rate**: Step size α. Too small: painfully slow. Too big: overshoots and diverges.

- **the error**: How wrong the prediction was on this example: truth minus prediction.

- **the feature**: Weights on features that were large for this example move more. That's also why feature scale matters so much.

##### Try it: learning rate and feature scaling

Full-batch gradient descent on our 12 flats, starting from w = b = 0. With raw sizes (45–170), the slope and the intercept need wildly different step sizes, so any learning rate small enough not to blow up crawls on the intercept. Standardise the feature (subtract the mean, divide by the standard deviation) and the bowl becomes round: a few steps suffice.

#### Least squares = maximum likelihood under Gaussian noise

Assume each price is the true line plus random noise ε that is Gaussian, independent, and has the same spread σ for every flat. Ask which weights make the observed prices most probable. Take the log of that probability and you get [CS229 §1.3](https://cs229.stanford.edu/main_notes.pdf):

$$ {\ell(\theta)} = {n\log\tfrac{1}{\sqrt{2\pi}\,\sigma}} - {\tfrac{1}{\sigma^{2}}}\cdot{\tfrac12\sum_{i}\big(y^{(i)} - \theta^{\top}x^{(i)}\big)^2} $$

- **log-likelihood**: How probable the data is under weights θ (on a log scale). Higher is better.

- **a constant**: Depends on n and σ, not on θ. It doesn't affect which θ wins.

- **a positive scale**: Also doesn't change which θ wins.

- **the least-squares cost**: Maximising the likelihood means minimising exactly this sum of squares. Squared error isn't arbitrary: it's what Gaussian noise implies.

This also explains the weakness. Gaussian noise almost never produces a point far from the line, so least squares treats a far point as very informative and bends to reach it:

Dashed line: the original fit. One mislabelled or unusual flat drags the whole line. Fixes: inspect residuals, use a robust loss (Huber, absolute error), or transform the target (e.g. log price).

## In practice

### In practice

#### Two ways to the same answer, plus a statistics toolkit

| Approach | How | When |
|---|---|---|
| **Closed form** (normal equation, or QR / SVD) | Solve XᵀXθ = Xᵀy directly | Up to a few thousand features; exact answer in one shot. scikit-learn's `LinearRegression` uses a least-squares solver |
| **Gradient descent** / SGD | Repeatedly step the weights downhill on the loss | Huge data or many features; streaming data; the same machinery that trains neural nets |
| **Statistical inference** (e.g. statsmodels) | Same fit, plus standard errors, p-values, confidence intervals | When you need to explain or test the coefficients, not just predict |

All three minimise the same squared-error loss. scikit-learn's docs: `LinearRegression` "fits a linear model with coefficients w = (w₁, …, wp) to minimize the residual sum of squares" [scikit-learn docs](https://scikit-learn.org/stable/modules/linear_model.html).

#### R²: how much of the variation the line explains

$$ {R^{2}} = 1 - {\textstyle\sum_i (y_i - \hat y_i)^2} \,\big/\, {\textstyle\sum_i (y_i - \bar y)^2} $$

- **R²**: Share of the target's variance explained by the model. 1 is perfect; 0 means no better than predicting the mean.

- **what the model misses**: Sum of squared residuals around the fitted line.

- **what a dumb model misses**: Sum of squared differences from the mean of y: the error of always predicting the average.

For our flats R² ≈ 0.99 (the illustrative points are very linear). Anscombe's sets all score 0.67 while being completely different, so R² alone is never enough. Report an error in the target's units too (RMSE or MAE: "off by ₹3 lakh on average"), and evaluate on held-out data. Training R² always goes up when you add a feature, even a useless one.

#### Fitting a linear regression you can trust

1. **Plot first.** Scatter the target against key features; Anscombe's lesson.

2. **Split the data** into train and test (or use cross-validation) before anything else.

3. **Engineer features:** logs for skewed quantities like prices, polynomial or interaction terms where the relationship bends, one-hot encoding for categories.

4. **Scale features** if you use gradient descent or regularization (not needed for plain closed-form OLS predictions).

5. **Fit** by least squares (closed form for small p, gradient descent for big data).

6. **Check residuals:** residuals vs fitted (curve? funnel?), outliers, high-leverage points.

7. **Evaluate on held-out data** with RMSE or MAE in real units, plus R².

8. **If the weights are unstable or there are many features,** move to Ridge, Lasso or Elastic Net.

#### Use it, or reach for something else?

##### Use linear regression when

- You need a fast, explainable baseline for a numeric target

- You need coefficients you can explain to stakeholders

- Data is small, or features are already well engineered

- The relationship is roughly linear (or linear after a log)

##### Reach for something else when

- Many correlated features or p ≈ n → Ridge / Lasso / Elastic Net

- Strong non-linearities and interactions → gradient boosting, random forests

- Heavy outliers → Huber or quantile regression

- A yes/no target → logistic regression

### The answer that sounds right

#### "Make the errors add up to zero" picks terrible lines

The obvious first idea: choose the line whose errors sum to zero, so the misses above and below cancel out. Try it. Every line through the average point (102.75 m², ₹97.2 lakh) has residuals that sum to exactly zero, no matter how wrong its slope is:

The first number stays at 0 for every slope, even a flat or downhill line. Positive and negative errors cancel, so "sum of errors" can't tell a good line from a bad one. Absolute or squared errors can't cancel, so they can.

##### What breaks: errors that cancel

You need a loss where every miss counts as a cost. The two natural choices are |error| (least absolute deviations) and error² (least squares). Least squares won historically because it's smooth, has a closed-form solution, and matches the maths of Gaussian noise (see the Maths tab). Its price is sensitivity to outliers, since a miss of 10 costs 100.

#### Same line, same R², four completely different stories

In 1973 the statistician Francis Anscombe built four small datasets that share the same mean of x (9), mean of y (7.50), correlation (0.816), regression line (y = 3.00 + 0.500x) and R² (0.67). Fit linear regression to each and the software reports the same numbers four times. Now look at them:

–

Real data: [Anscombe's quartet](https://en.wikipedia.org/wiki/Anscombe%27s_quartet) (Anscombe, 1973). The orange line is the fitted line, identical for all four.

The assumptions behind the usual statistics (standard errors, p-values, prediction intervals) are often remembered as **LINE**:

| Assumption | Means | How to check / fix |
|---|---|---|
| **L**inearity | The mean of y really is linear in the features | Residuals vs fitted plot shows no curve; add x², logs, interactions (set II) |
| **I**ndependence | Errors don't depend on each other | Watch for time series and grouped data; use time-aware or mixed models |
| **N**ormality | Errors are roughly Gaussian | Q-Q plot of residuals; matters mostly for small-sample inference, not for the fit itself |
| **E**qual variance | Error spread is the same for all x (homoscedasticity) | Funnel-shaped residuals → transform y (log) or use weighted least squares |

Plus two practical ones: no extreme outliers or high-leverage points (sets III and IV), and features not too collinear (see the normal equation in the Maths tab, and the Regularized Linear Models lesson). For pure prediction you need fewer of these. For interpreting coefficients, you need the right form and independent errors, and equal variance for the usual standard errors. Normal errors matter mainly with small samples.

#### Why least squares, and what can bias it

##### Gauss-Markov: why least squares is a good default

Suppose the model's form is right, errors average zero whatever the features are, errors have equal variance and aren't correlated, and no feature is a perfect mix of the others. Then least squares has the lowest variance among all **linear, unbiased** estimators. Normal errors aren't needed.

Note those two words. A biased method like ridge can still have lower total error, by accepting some bias for less variance.

##### Omitted-variable bias

Leave out a feature that affects y **and** is correlated with a feature you kept, and the coefficient you kept absorbs part of its effect.

$$ {\tilde\beta_1} = {\beta_1} + {\beta_2}\,{\delta} $$

The standard result for two features, in expectation.

- **the slope you get**: From a model that leaves out x₂.

- **the true effect of x₁**: Holding x₂ fixed.

- **the left-out feature’s effect**: How much x₂ moves y.

- **how they’re linked**: The slope when you regress x₂ on x₁. If it’s zero, there’s no bias.

**A worked example, with illustrative numbers.** Say price truly rises ₹0.7 lakh per m², and being central adds ₹20 lakh. Central flats tend to be smaller, so "central" falls by 0.005 per extra m². Leave out "central", and the slope becomes 0.7 + 20 × (−0.005) = 0.6. The model now understates what size is worth.

- **For prediction:** this may do no harm, as long as the link between the features stays the same in production.

- **For explanation:** it can be badly misleading, and can even flip a sign. No test on your data can reveal a variable you never measured, so this needs domain knowledge, or an experiment or causal design.

- **Correlated features:** to measure this problem, see VIF in inference for regression.

#### Polynomial features: more wiggle, and the overfitting trap

Add x², x³, … as extra columns and fit them with the same least squares. The model is still linear in its weights, but can now bend. Each extra degree lowers the training error. Watch what happens on new data:

–

Illustrative data: a smooth curve plus noise. ● training points, ● test points. With degree 9 and 10 points, the curve passes through every training point (training error 0) and swings wildly in between.

##### Two fixes

Choose the complexity with held-out data (cross-validation), or keep the flexible model and penalise large weights. The second fix is Ridge, Lasso and Elastic Net, the next lesson.

#### What to keep

**The lesson:** linear regression is a projection: it finds the closest prediction a weighted sum of features can make, measured by squared error. It is exact, fast and explainable, and it is the base that ridge, lasso, logistic and softmax regression (and every neural network's last layer) build on.

- **Coefficients are "holding the others fixed".** With correlated features, a coefficient can even flip sign compared with a one-feature fit. Don't read them as causal effects.

- **Squared loss is outlier-sensitive.** One bad row can move the line (see the outlier lab in the Maths tab).

- **Linear in weights ≠ linear world.** If residuals curve, add features or use a more flexible model.

- **Extrapolation is risky.** The line knows nothing outside the range of x it saw.

## Say it

### What is linear regression, and how is it fitted?

#### The interviewer pushes further

Follow-up 1 of 6

Why squared error and not absolute error?

Squared error is smooth and convex with a closed-form solution, and it's the maximum-likelihood loss under Gaussian noise. Absolute error (least absolute deviations) is the MLE under Laplace noise, is more robust to outliers, and predicts the conditional median instead of the mean, but it has no closed form and isn't differentiable at zero.

Follow-up 2 of 6

When does the normal equation fail?

When XᵀX isn't invertible: perfectly collinear features (e.g. a one-hot encoding with every category kept plus an intercept, the "dummy variable trap"), or more features than examples. Near-collinearity makes it numerically unstable. Fixes: drop or combine features, use the pseudo-inverse (SVD), or add a ridge penalty, which makes XᵀX + λI invertible.

Follow-up 3 of 6

Normal equation or gradient descent?

Normal equation for small to medium p (exact, no tuning). Gradient descent or SGD when n or p is huge, data streams in, or the model is part of something bigger. Gradient descent needs scaled features and a tuned learning rate.

Follow-up 4 of 6

What are the assumptions, and which matter for prediction?

Linearity, independent errors, normal errors, equal variance (LINE), plus limited multicollinearity and no extreme outliers. For pure prediction, linearity (a correct functional form) and representative data matter most. Normality and equal variance matter mainly for valid standard errors, p-values and intervals.

Follow-up 5 of 6

How do you interpret a coefficient?

The expected change in y for a one-unit increase in that feature, holding the other features constant. Correlated features make that "holding constant" unrealistic and the coefficients unstable, so be careful with interpretation and never read them as causal without a causal design.

Follow-up 6 of 6

Does adding a feature always increase R²?

On training data, yes (or keeps it the same), even for pure noise. That's why you use adjusted R² or, better, held-out error.

#### The 30-second answer

Linear regression models the target as a weighted sum of features plus a bias, and fits the weights by minimising the sum of squared residuals. That has a closed-form solution, the normal equation θ = (XᵀX)⁻¹Xᵀy, which is a projection of y onto the span of the features, or you can use gradient descent at scale. If the noise is Gaussian, least squares is exactly maximum likelihood. Its weak spots are outliers, non-linearity, and collinear features, which is where regularization comes in.

**Go further**

#### The 2-minute walkthrough

Start with the model ŷ = Xθ and why we need a loss where errors can't cancel. Write J(θ) = ½Σ(θᵀx − y)², a convex bowl. Solve two ways: normal equation (exact, about p³ cost, needs XᵀX invertible) or gradient descent (LMS update, needs feature scaling and a sensible learning rate). Justify squares via Gaussian maximum likelihood, and note the price: outlier sensitivity. Then the assumptions (LINE), why R² alone can lie (Anscombe), and polynomial features with the overfitting trade-off that motivates Ridge and Lasso.

#### What not to say

- "Linear regression can only fit straight lines." It's linear in the weights; polynomial and log features bend it.

- "The features need to be normally distributed." The assumption is about the _errors_, not the features.

- "High R² means the model is right." See Anscombe's quartet.

- "A bigger coefficient means a more important feature." Only if the features are on the same scale, and not under strong collinearity.

**Key terms and sources**

Built from Stanford CS229 notes (§1), scikit-learn's linear-model docs and Anscombe (1973) · checked 28 Oct 2026

#### Glossary

| Term | Meaning |
|---|---|
| **Residual** | y − ŷ for one example. |
| **OLS** | Ordinary least squares: minimise the sum of squared residuals. |
| **Normal equation** | XᵀXθ = Xᵀy, the closed-form solution. |
| **Design matrix X** | One row per example, one column per feature (plus a column of 1s). |
| **Learning rate** | Step size in gradient descent. |
| **Multicollinearity** | Features that are (nearly) linear combinations of each other. |
| **Homoscedasticity** | Error variance that's the same everywhere. |
| **R² / RMSE / MAE** | Share of variance explained / root mean squared error / mean absolute error. |
| **Overfitting** | Fitting training noise so well that new-data error goes up. |

#### What this page is built from

1. A. Ng, T. Ma et al., [Stanford CS229 lecture notes](https://cs229.stanford.edu/main_notes.pdf), §1: LMS, the normal equations, the probabilistic interpretation.

2. scikit-learn, [Linear models user guide](https://scikit-learn.org/stable/modules/linear_model.html): OLS objective, collinearity note.

3. F. J. Anscombe, "Graphs in Statistical Analysis", _The American Statistician_, 1973; data via [Anscombe's quartet](https://en.wikipedia.org/wiki/Anscombe%27s_quartet).

4. Hastie, Tibshirani & Friedman, _The Elements of Statistical Learning_, ch. 3 (linear methods for regression), background.

5. Interview angle: [Interview Query, linear regression questions](https://interviewquery.com/p/linear-regression-interview-questions); [Analytics Vidhya](https://www.analyticsvidhya.com/blog/2025/11/linear-regression-interview-questions/).

Flat sizes and prices, the polynomial dataset and the gradient-descent runs are illustrative and computed live in this page.
