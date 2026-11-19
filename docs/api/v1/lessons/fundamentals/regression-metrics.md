# Regression Metrics

> RMSE went up 9× but MAE barely moved. Is the model worse?

- Track: Fundamentals › Classical ML › Evaluation metrics
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/regression-metrics/
- Before this: Linear Regression (`fundamentals/linear-regression`)
- Quiz topic: `metrics`

## Intuition

### The situation

Two orders get stuck in traffic. Your ETA model's RMSE jumps ninefold, while its MAE barely moves. The interviewer asks:

> How do you choose between RMSE and MAE?

**Scenarios:** food-delivery ETA (minutes), house prices (₹), demand forecasting for a slow-moving item (units per day), salary prediction, stocking inventory to a service level, energy load. Data is illustrative; every metric is computed live.

#### "RMSE went up 9×, but MAE barely changed. Is the model worse?"

A delivery app's ETA model is off by about 2 minutes on a normal day. Then two orders get stuck in a traffic jam: 95 and 80 minutes instead of the predicted 33 and 30. RMSE jumps from 1.8 to 17.1 minutes; MAE goes from 1.7 to 6.6; the median error doesn't move at all. All three are "correct". They just answer different questions, and choosing between them is choosing what you want the model to be good at.

### The idea

Think of a restaurant's average bill. One huge party drags the mean up, but barely moves the median. RMSE behaves like the mean: a few huge misses dominate it. MAE behaves like the median.

[Figure: On a normal day RMSE is 1.8 and MAE is 1.7 minutes. With two orders stuck in traffic, RMSE jumps to 17.1 while MAE only reaches 6.6.]

_From the lesson's ETA example, in minutes._

### Play

**Try to break it.** Slide the constant prediction and find where each metric is lowest.

#### Each metric is minimised by a different summary of the target

If you could only predict one number for every case, which number would each metric reward? MSE is minimised by the **mean**, MAE by the **median**, pinball loss at level α by the **α-quantile**. That's the deep reason the metric choice matters: it decides what your model is trained and judged to predict. Drag the constant and watch each loss bottom out at a different place:

23 right-skewed delivery times (most 20–35 min, a few long ones). Curves scaled to a common height. The long tail pulls the mean above the median; a service-level target ("promise a time we beat 90% of the time") is a quantile. scikit-learn calls these "strictly consistent scoring functions": pick the metric for the statistic you want predicted docs.

**Now say why:** why does each metric reward a different number, and what does that mean for what your model will learn to predict?

## Maths

### Maths

#### In one breath

Every regression metric is a different way to average errors, and each one quietly rewards a different prediction. **MSE/RMSE** square errors, so big misses dominate and the best constant prediction is the **mean**. **MAE** treats every unit of error equally and rewards the **median**. **Pinball loss** rewards a chosen **quantile** (e.g. "enough stock 90% of days"). **R²** compares you with predicting the average and can go negative. **MAPE** is a percentage but explodes near zero and favours under-forecasting; **WAPE** and **MASE** fix that for demand forecasting. **RMSLE** cares about ratios and punishes under-prediction more.What you'll be able to do after this: pick the metric that matches what the business actually wants predicted (mean, median, quantile, ratio), and explain why a model's RMSE and MAE can tell opposite stories.

#### Errors, and three ways to average them

$$ \text{MAE} = \tfrac1n\textstyle\sum|y_i - \hat y_i| \qquad \text{MSE} = \tfrac1n\textstyle\sum(y_i - \hat y_i)^2 \qquad \text{RMSE} = \sqrt{\text{MSE}} $$

- **MAE**: Mean absolute error: the average size of a miss, in the target's own units (“off by 1.7 minutes”). Every minute of error counts the same.

- **MSE**: Mean squared error: squares each miss first, so a 10-minute miss costs 100 and a 1-minute miss costs 1. Units are squared (minutes²), hard to read.

- **RMSE**: Square root of MSE: back in minutes, but still dominated by the biggest misses. Always ≥ MAE; the gap tells you how uneven the errors are.

#### R²: better than predicting the average?

$$ R^2 = 1 - \textstyle\sum(y_i-\hat y_i)^2 \,/\, \textstyle\sum(y_i-\bar y)^2 \qquad \bar R^2 = 1 - (1-R^2)\,\tfrac{n-1}{n-p-1} $$

scikit-learn: a constant model that always predicts the average "would get an R² score of 0.0", and R² "can be negative (because the model can be arbitrarily worse)" docs.

- **R²**: Share of the target's variance the model explains. 1 is perfect; 0 equals always predicting the mean; negative means worse than that.

- **your squared errors**: The model's residual sum of squares.

- **the mean's squared errors**: Total sum of squares: the error of the dumbest sensible model, a constant at the average.

- **adjusted R²**: Penalises extra features: with n rows and p features it only rises if a new feature helps more than chance would. Use it to compare models with different feature counts on training data.

##### R² is not comparable across datasets

It depends on how spread out the target is. In the traffic-jam example, R² fell from 0.87 to 0.04 because the jams made the denominator huge, not only because errors grew. A model with RMSE ₹5 lakh can have R² 0.9 on all-India house prices and 0.2 within one housing society. Report an error in real units next to R². scikit-learn also notes that explained variance ignores systematic offset, so R² "should be preferred in general" docs.

#### MAPE, sMAPE, WAPE and MASE for forecasting

Business teams love percentages ("we're 8% off") because they compare across products of different sizes. MAPE averages |error| / |actual|, and that denominator is the problem:

14 days of demand. On a zero-demand day, |error| / 0 is infinite; scikit-learn divides by a tiny ε instead, so a single zero turns MAPE into an astronomical number docs. WAPE divides total error by total demand, so zeros are harmless. MASE divides by the error of a naive "same as yesterday" forecast: below 1 means you beat naive.

##### MAPE's two biases

**Near zero:** tiny actuals give huge percentages. **Asymmetry:** under-forecasting can cost at most 100% (predict 0 for an actual 100), but over-forecasting is unbounded (predict 200 → 100%, 400 → 300%). So optimising MAPE pushes forecasts low, which for inventory means stock-outs.

##### What forecasters use instead

Hyndman and Koehler showed the common measures "can give infinite or undefined values in commonly occurring situations" and proposed **MASE**, the mean absolute scaled error, for comparing accuracy across series Hyndman & Koehler 2006. Retail teams also use **WAPE** (volume-weighted). sMAPE bounds the range but has its own asymmetry.

$$ \text{MASE} = \tfrac1n\textstyle\sum|y_t - \hat y_t| \,\Big/\, \tfrac{1}{T-1}\textstyle\sum_{t=2}^{T}|y_t - y_{t-1}| $$

- **MASE**: Your forecast's MAE divided by a benchmark MAE. Scale-free, works with zeros, and 1 means “as good as naive”.

- **your errors**: Mean absolute error of the forecast on the evaluation period.

- **naive forecast's errors**: The in-sample mean absolute change from one period to the next: the error of predicting “same as last period” (or same as last season for seasonal data).

#### When the business wants a quantile, not an average

An e-grocery store doesn't want to stock the _average_ demand; it wants enough to cover demand on 90% of days. A delivery app promising "arrives by 7:40" wants a time it beats 90% of the time. Train and judge those models with **pinball loss**:

$$ \ell_\alpha(y,\hat y) = \alpha\,\max(y - \hat y, 0) + (1-\alpha)\,\max(\hat y - y, 0) $$

scikit-learn's `mean_pinball_loss`; with α = 0.5 it "equals half of MAE" docs. Use the same α in the training loss (e.g. gradient boosting with `loss="quantile"`).

- **pinball loss at level α**: Asymmetric absolute error. α = 0.5 gives half the MAE (the median); α = 0.9 targets the 90th percentile.

- **under-prediction**: When the actual is above the prediction, pay α per unit: with α = 0.9, running out costs 9× more…

- **over-prediction**: …than overstocking, which costs only 1 − α = 0.1 per unit. The best constant is the point with 90% of outcomes below it.

#### RMSLE, and deviance for counts and claims

##### RMSLE: errors as ratios

RMSE on log(1 + y). Predicting ₹50k for a ₹1 lakh salary and ₹50 lakh for a ₹1 crore salary are the same error. scikit-learn notes it suits targets with exponential growth and "penalizes an under-predicted estimate greater than an over-predicted estimate" docs. Example: actual 100, predict 50 → 0.68; predict 150 → 0.40.

##### Poisson / Gamma / Tweedie deviance

For counts (calls per hour, claims per policy) and positive skewed amounts (claim sizes), use the deviance of the matching distribution. Tweedie with power 0 is MSE, 1 is Poisson, 2 is Gamma; at power 2 the deviance "is thus only sensitive to relative errors" docs. Insurance pricing teams use exactly this.

## In practice

### In practice

#### The metric menu

| Metric | Formula idea | Rewards predicting the… | Scale |
|---|---|---|---|
| **MSE / RMSE** | mean of squared errors | mean | target units (RMSE) |
| **MAE** | mean of absolute errors | median | target units |
| **Median AE, max error** | median / max of \|errors\| | typical case / worst case | target units |
| **Pinball (quantile) loss** | asymmetric absolute error | chosen quantile | target units |
| **R²** | 1 − SSres/SStot | mean (relative to a constant) | unitless, ≤ 1 |
| **MAPE / sMAPE** | mean of \|error\| / \|actual\| | a low-biased forecast | percent |
| **WAPE** | Σ\|error\| / Σ\|actual\| | median-ish, volume-weighted | percent |
| **MASE** | MAE / MAE of a naive forecast | median, scale-free | < 1 beats naive |
| **RMSLE** | RMSE of log(1 + y) | ratios (geometric) | log units |
| **Poisson / Tweedie deviance** | likelihood-based | mean of counts / claims | deviance |

#### Which metric, in which situation

| Scenario | Report | Why |
|---|---|---|
| Delivery ETA | MAE + P90 absolute error (or pinball at 0.9 for the promise) | Customers feel minutes linearly; rare jams shouldn't dominate the headline, but the tail matters for promises |
| House price estimate | MAE in ₹ and median % error; RMSE if big misses are costly | Explainable to buyers; prices are skewed, so percentage errors also help |
| Demand forecasting (retail) | WAPE or MASE; pinball for stocking decisions | Zeros and mixed scales break MAPE; stocking is a quantile decision |
| Energy / load forecasting | RMSE (+ MAPE for reporting) | Large errors cause outages or expensive spot buying, so squaring fits; loads are never near zero |
| Salary, population, prices across orders of magnitude | RMSLE (or MAE on log target) | Ratios matter more than absolute rupees |
| Insurance claims, call volumes | Poisson / Tweedie deviance | Counts and zero-inflated amounts |
| Reporting to non-technical stakeholders | MAE (or WAPE) in real units + a baseline | "Off by 1.7 minutes, vs 4.2 for the old rule" |

### The answer that sounds right

#### "RMSE is the standard, report RMSE"

Same model, same 20 ordinary orders. RMSE is dominated by the two jams; the median absolute error ignores them completely; MAE sits in between. R² collapses because the jams also blow up the spread of actual times. None of these is "wrong": RMSE is right if a 60-minute miss really is 3,600× worse than a 1-minute one (it rarely is), MAE if every minute late costs the same.

#### What to keep

- **Train with the loss you'll be judged on.** A model trained on MSE predicts means; judging it on MAE or a quantile will look worse than a model trained for that target.

- **Always show a baseline**: predicting the mean (R² = 0), the median, last period's value (MASE = 1).

- **Look at the error distribution** (by segment, by size, the tail), not just one average.

- **Scale-dependent metrics** (MAE, RMSE) can't be compared across products or datasets; use scale-free ones (MASE, WAPE, R²) with care.

## Say it

### How do you choose between RMSE and MAE?

#### The interviewer pushes further

Follow-up 1 of 4

MAE vs RMSE: when each?

RMSE when large errors are disproportionately bad (squaring) or you need the mean; MAE when every unit of error costs the same and you want robustness to outliers (it targets the median). RMSE ≥ MAE always; a big gap signals a few large errors.

Follow-up 2 of 4

Why is MAPE problematic?

Division by the actual: undefined at zero and huge near zero, and asymmetric. Under-forecasts are capped at 100% while over-forecasts are unbounded, so minimising MAPE biases forecasts low. Use WAPE, MASE or sMAPE (with care).

Follow-up 3 of 4

Can R² be negative?

Yes, on data where the model does worse than predicting the mean (typically test data, or models without an intercept). Training R² of OLS with an intercept is between 0 and 1.

Follow-up 4 of 4

How would you evaluate a model that sets inventory levels?

As a quantile problem: choose the service level (say 95%), train with pinball loss at α = 0.95, evaluate with pinball loss and actual coverage (did demand exceed the forecast about 5% of days?), and translate into stock-out and holding costs.

#### The 30-second answer

The metric decides what the model should predict. MSE and RMSE are minimised by the mean and are dominated by large errors; MAE is minimised by the median and is robust to outliers; pinball loss targets a chosen quantile, which is what you want for service levels or stocking. R² compares against predicting the mean and isn't comparable across datasets. For forecasting, MAPE breaks near zero and favours under-forecasting, so I'd use WAPE or MASE, and RMSLE when ratios matter. I always report the error in real units against a simple baseline.

**Go further**

#### What not to say

- "RMSE is the best regression metric." It's best for one goal (predicting means, punishing big misses).

- "R² of 0.6 is bad." It depends on the domain and the target's spread.

- "MAPE is fine, it's a percentage." Not with zeros, and not if under-forecasting is costly.

**Key terms and sources**

MAE, MSE, RMSE, R², MAPE, sMAPE, WAPE, MASE, RMSLE, pinball loss and more · built from scikit-learn's docs and Hyndman & Koehler (2006) · checked 28 Oct 2026

#### Glossary

| Term | Meaning |
|---|---|
| **MAE / MSE / RMSE** | Mean absolute / squared / root mean squared error. |
| **MedAE, max error** | Median and worst absolute error. |
| **R², adjusted R²** | Variance explained vs a constant; adjusted for feature count. |
| **MAPE, sMAPE** | Mean (symmetric) absolute percentage error. |
| **WAPE** | Σ\|error\| / Σ\|actual\|. |
| **MASE** | MAE relative to a naive forecast's in-sample MAE. |
| **RMSLE** | RMSE on log(1 + y). |
| **Pinball / quantile loss** | Asymmetric absolute error targeting a quantile. |
| **Tweedie deviance** | Family covering MSE (0), Poisson (1), Gamma (2). |

#### What this page is built from

1. scikit-learn, Metrics and scoring: regression metrics (R², MAPE ε, MSLE, pinball, Tweedie, D², consistent scoring functions).

2. R. J. Hyndman & A. B. Koehler, Another look at measures of forecast accuracy, International Journal of Forecasting 22 (2006).

3. Interview angle: Interview Query; DataLemur.

Delivery, demand and skewed-time data are illustrative.
