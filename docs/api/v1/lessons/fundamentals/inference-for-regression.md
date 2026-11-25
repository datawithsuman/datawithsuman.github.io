# Inference for Regression

> How do you interpret a regression coefficient, its p-value and R², and how do you check the model's assumptions?

- Track: Fundamentals › Maths for ML › Statistics
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/inference-for-regression/
- Before this: T-Tests and Z-Tests (`fundamentals/t-tests-and-z-tests`), Linear Independence, Basis and Rank (`fundamentals/linear-independence-basis-and-rank`)
- Related: Linear Regression (`fundamentals/linear-regression`)
- Quiz topic: `stats`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: c7e14a3301

## Intuition

### The situation

A regression on delivery time shows distance with a coefficient of 3 and p below 0.001, with R² of 0.85. A manager concludes that the model is excellent and that distance causes delays. Its residual plot shows a clear curve. The interviewer asks:

> How do you interpret a regression coefficient, its p-value and R², and how do you check the model's assumptions?

#### Why it matters

Often you need to explain a model, not just predict: which factors matter, and by how much? This is where regressions are most often misread. See linear regression for how it's fitted.

### The idea

Think of a weather forecast with a score. A good score says the forecast tracks the temperature overall. It doesn't say why, or where it goes wrong. For that, you look at its errors: if it's always too cold in summer, the score hid a pattern. Residuals are those errors.

[Figure: Reading a regression. The coefficient is the expected change per unit. The standard error is how noisy it is. Residuals show whether the model fits.]

_Numbers summarise a fit, and residuals show what they miss._

### Play

**Try to break it.** Switch to curved data with low noise. Then try the funnel.

#### Fit a line, then read the residuals

Our seeded simulation, using ordinary least squares with x from 0 to 10. Left: data and fit. Right: residuals against predictions. Standard errors are the classic kind, which assume constant noise.

Switch to the **curved** pattern, with low noise. R² looks strong, and the slope is highly significant, yet the residuals show an obvious curve. The numbers said it's good, and the plot says the model's wrong. Always look at both.

**Now say why:** how can R² be high while the model is wrong?

## Maths

### Maths

#### In one breath

A regression gives a **coefficient** for each feature: the expected change in the outcome per unit, **holding the others fixed**. Its **standard error** tells you how noisy that is, which gives a t-test and a confidence interval. **R²** is the share of variance explained, not whether the model is right. Check **residual plots**: patterns there reveal missing curves or unequal noise. And a significant coefficient doesn't prove cause.

#### Reading the output

| Output | What it says | What it doesn't say |
|---|---|---|
| **Coefficient** | Expected change in y per unit of x, with other features held fixed. | That x causes it. That it's the most important feature. |
| **Standard error** | How much the coefficient would vary across samples. | That the model is correctly specified. |
| **p-value** | How surprising this coefficient is if the true value is zero. | How large or useful the effect is. |
| **R²** | The share of variance in y explained. | Whether the model's right, or will predict well on new data. |

##### Worked reading

Say delivery time = 12 + 3 × distance in km, with a standard error of 1 on the slope. Each extra km is linked to about 3 more minutes, for similar orders. t = 3 ÷ 1 = 3, and the 95% interval is about 1 to 5 minutes.

##### What residual plots tell you

Residuals should look like shapeless noise. Plot them against predictions.

| You see | It means | Try |
|---|---|---|
| A curve | A straight line doesn't fit. | Transform features, or add terms. |
| A funnel | Noise grows with size (heteroscedasticity). Standard errors are wrong. | Robust standard errors, or a log transform. |
| Long tails or a few far points | Outliers, which may have high influence. | Investigate, or use a robust loss. |
| A pattern over time | Errors aren't independent. | Time-series methods, or clustered standard errors. |

##### Common traps

- **Correlated features:** collinearity inflates standard errors, so each feature can look insignificant, while the model predicts well.

- **Comparing sizes:** a coefficient's size depends on units. Standardise features before comparing them.

- **R² always rises:** adding any feature raises training R². Use adjusted R² or a test set.

- **Significance with huge data:** a tiny, useless effect can have a small p-value. Look at the interval.

#### The maths

$$ {\hat\beta} \pm t^* \cdot {SE(\hat\beta)}, \qquad {SE(\hat\beta)} = \frac{{\hat\sigma}}{{\sqrt{\sum_i (x_i - \bar x)^2}}}, \qquad {R^2 = 1 - \frac{\sum_i (y_i - \hat y_i)^2}{\sum_i (y_i - \bar y)^2}} $$

This is for a single feature. With many, the standard error also grows with collinearity, by the variance inflation factor.

- **the coefficient and its interval**: The estimate, plus or minus a margin of about two standard errors.

- **the standard error**: Noise in the slope.

- **residual noise**: More scatter around the line means a less certain slope.

- **the spread of x**: A wide range of x pins the slope down better. More data helps here as well.

- **R squared**: 1 minus the share of variance left in the residuals.

## In practice

### In practice

#### In practice

- **Say "linked to", not "causes":** a coefficient describes an association, unless the design supports a causal claim. See causal inference.

- **Robust standard errors:** when noise isn't constant, they correct your intervals, without changing the fit.

- **Regularised models:** ridge and lasso coefficients are biased on purpose, so these simple p-values don't apply.

- **Tree models:** use permutation importance or SHAP, but remember these also describe the model, not causes.

- **Test data:** high R² in training says little about new data. Use a test set when the goal's prediction.

### The answer that sounds right

#### "High R² and low p-values mean the model is right"

It sounds right, since both numbers look good. But a straight line can explain a lot of a curve, with a strong slope, while being clearly the wrong shape. And with lots of data, even tiny effects give small p-values. Look at residuals, and test on new data.

## Say it

### How do you interpret a regression coefficient, its p-value and R², and how do you check the model's assumptions?

#### The interviewer pushes further

Follow-up 1 of 3

How do you interpret a coefficient of 3 on distance?

Each extra km is linked to about 3 more minutes, holding the other features fixed. It's not necessarily causal, and it may not hold outside the data's range. Its interval tells you how certain you are, and its size depends on the units used.

Follow-up 2 of 3

Is a high R² always good?

No. It can be high with a wrong model, as with curved data, or on training data from overfitting. And a low R² can still be useful: in noisy behaviours, a small explained share can be valuable. Look at residuals, a test set and what the decision needs.

Follow-up 3 of 3

A feature's p-value is high. Should you drop it?

Not automatically. It could be collinear with another feature, which inflates its standard error, so together they may matter. Or it may have a real but small effect, with too little data. Check VIF, look at the interval, and compare models on validation data.

#### The 30-second answer

A coefficient is the expected change in the outcome per unit of that feature, holding the others fixed. Its standard error gives a t-test and an interval: about plus or minus two standard errors. R squared is the share of variance explained, not proof that the model's right. So I'd check residual plots: a curve means a straight line doesn't fit, and a funnel means noise varies, so standard errors are off. Collinearity inflates standard errors. And I'd say a feature's linked to the outcome, not that it causes it, unless the design supports that.

**Key terms and sources**

Reading coefficients and their standard errors, confidence intervals, what R² does and doesn't say, residual plots, and common traps. · checked 6 Nov 2026

#### Sources

- [Diez, Çetinkaya-Rundel and Barr, OpenIntro Statistics](https://www.openintro.org/book/os/)

- [Bruce, Bruce and Gedeck, Practical Statistics for Data Scientists, contents excerpt](https://toc.uni.li/FLMF048415.pdf)

- Linear regression on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
