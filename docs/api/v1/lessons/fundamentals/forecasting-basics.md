# Time-Series Forecasting Basics

> Can your forecasting model beat 'same as last week'? And are you measuring it honestly?

- Track: Fundamentals › Classical ML › Time series
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/forecasting-basics/
- Before this: Linear Regression (`fundamentals/linear-regression`), Cross-Validation & Data Leakage (`fundamentals/cross-validation-and-leakage`)
- Quiz topic: `ts`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-20 · Version: 1b62daa0b8

## Intuition

### The situation

Your team needs a 14-day order forecast every week to plan rider shifts. A teammate shuffles the days and cross-validates, and the score looks great. The interviewer asks:

> How would you build a forecast for a time series?

**Running example:** daily orders for one city over two years (728 days, simulated): a steady upward trend, a strong **weekly** pattern (Fridays and Saturdays are 12–25% above average, Mondays 14% below), a gentle **yearly** wave, and random day-to-day noise. The team needs a 14-day forecast every week to plan rider shifts.

#### Predicting the future of a series, honestly

Rider shifts, kitchen stock and marketing budgets all depend on next fortnight's demand. Time series break the usual ML assumption that rows are independent: today depends on yesterday, Saturdays look like Saturdays, and the only data you'll ever have at prediction time is the past. That changes how you build features, which baseline you must beat, and how you validate.

### The idea

Think of predicting this Saturday's rush. Your first answer should be "about the same as last Saturday". A fancier model has to beat that, and it has to be tested the way real life works: using only the past to predict the future.

[Figure: Daily orders over time with a weekly wave. A vertical line marks today. A model trains only on the past to the left and is tested on the future to the right.]

_Illustrative. A rolling-origin backtest repeats this split at several cut-offs._

### Play

**Try to break it.** Compare mean, naive and seasonal naive, and then the regression. Watch the backtest MAE and the MASE.

#### Six forecasters, one backtest

Plot: the last 8 weeks before the final cut-off (teal), the next 14 days (green) and the forecast (orange). The numbers average 12 cut-offs, one per week over the last 12 weeks.

| Forecaster | mean | naive | drift | seasonal naive | trend + weekday | + yearly wave |
|---|---|---|---|---|---|---|
| Backtest MAE | 260.0 | 211.6 | 212.9 | 58.6 | 60.0 | 45.2 |
| MASE | 4.74 | 3.86 | 3.88 | 1.07 | 1.09 | 0.82 |

Anything that ignores the weekly pattern (mean, naive, drift) is useless here. The first regression, trend plus day-of-week fitted on the last 26 weeks, **fails to beat seasonal naive** (60.0 vs 58.6): it can't follow the yearly wave. Adding a yearly sine/cosine pair and fitting on all history wins clearly (45.2, MASE 0.82). The noise alone would give an MAE of about 36, so there's limited room left.

**Now say why:** why is such a simple seasonal rule so hard to beat here?

## Maths

### Maths

#### In one breath

Forecasting predicts future values of a series from its own past (and known future inputs like holidays). Most series are a **trend** plus a repeating **seasonal** pattern plus noise. Start with **benchmarks**: the seasonal naive forecast ("same as last week") is often surprisingly hard to beat, and any model that doesn't beat it isn't worth using. Then add structure: regression on trend and calendar features, exponential smoothing, ARIMA, or gradient-boosted trees on lag features. Evaluate with a **rolling-origin backtest** (train only on the past, forecast the next window, roll forward), never shuffled cross-validation, and report **scale-free errors** like MASE. What you'll be able to do after this: decompose a series, run the four benchmarks, build a calendar-feature regression, backtest it honestly, and choose an error metric.

#### Trend, seasonality, remainder

$$ {y_t} = {T_t} \times {S_{t}} + {R_t} $$

Classical decomposition (additive or multiplicative); FPP3 ch. 3 [otexts.com/fpp3](https://otexts.com/fpp3/decomposition.html). In practice STL does this robustly.

- **orders on day t**: What we observe.

- **trend**: The slow-moving level: growth of the app in this city, plus the yearly wave.

- **seasonal factor**: The repeating weekly pattern: about 1.25 on Saturdays, 0.86 on Mondays. Multiplicative here, because busier months have bigger weekend peaks.

- **remainder**: What’s left: weather, a cricket match, noise. Forecasts can’t predict it; they can only be honest about it.

#### Beat the benchmark, measured the way you'll use it

FPP3 uses four simple methods as benchmarks: "any forecasting methods we develop will be compared to these simple methods … If not, the new method is not worth considering" [FPP3 §5.2](https://otexts.com/fpp3/simple-methods.html):

- **Mean:** "the forecasts of all future values are equal to the average … of the historical data".

- **Naive:** "set all forecasts to be the value of the last observation".

- **Seasonal naive:** "each forecast to be equal to the last observed value from the same season" (here: same weekday last week).

- **Drift:** the last value plus the average historical change per day.

And "measured the way you'll use it" means: forecast 14 days ahead from a cut-off, using only data before the cut-off, repeated over many cut-offs.

#### MAE, RMSE, MAPE and MASE

$$ {\mathrm{MASE}} = {\tfrac{1}{h}\sum_{j=1}^{h} |y_{T+j} - \hat y_{T+j}|} \,/\, {\tfrac{1}{T-m}\sum_{t=m+1}^{T} |y_t - y_{t-m}|} $$

Hyndman & Koehler, "Another look at measures of forecast accuracy", _International Journal of Forecasting_ 22, 2006; FPP3 §5.8 [otexts.com/fpp3](https://otexts.com/fpp3/accuracy.html).

- **MASE**: Mean absolute scaled error: below 1 means better than the seasonal naive method’s typical one-step error; comparable across series of different sizes.

- **forecast errors**: Average absolute error of your forecasts over the test period.

- **seasonal naive in-sample error**: Average |y_t − y_{t−m}| over the training data, with m = 7 for weekly seasonality: the error of “same as last week”.

- **MAE** is in orders/day and easy to explain; **RMSE** punishes big misses more (see Regression Metrics).

- **MAPE** (percentage error) is popular with business users but explodes near zero (slow stores, night hours) and penalises over-forecasts and under-forecasts asymmetrically.

- **MASE** is scale-free and safe at zero, so you can average it across thousands of stores.

- For planning, also evaluate **prediction intervals** (do 90% intervals contain 90% of actuals?) and the business cost of over- vs under-staffing.

#### Lags, calendars, ETS, ARIMA and boosting

- **Lag features** (orders 7 and 14 days ago), **rolling statistics** (last 4 weeks' mean for this weekday), **calendar** (weekday, holidays, paydays, festivals), **known future inputs** (planned promotions, weather forecast). Every feature must be available at forecast time for the whole horizon: a 14-day forecast can't use yesterday's orders for day 14 unless you forecast recursively.

- **ETS** (exponential smoothing) and **ARIMA** model one series at a time and give principled prediction intervals; strong for few, long, regular series.

- **Gradient boosting** trains one model across many series (all cities, all restaurants) with lag and calendar features; this is what dominated M5.

- **Hierarchies:** forecasts for city, zone and restaurant should add up (reconciliation).

To see how ARIMA and exponential smoothing work, see Stationarity, ARIMA and Exponential Smoothing.

## In practice

### In practice

#### The forecasting toolbox

| Family | Idea | Tools |
|---|---|---|
| **Benchmarks** | Mean, naive, seasonal naive, drift | statsforecast, fable |
| **Exponential smoothing (ETS)** | Weighted averages with decaying weights; level + trend + season | statsmodels, statsforecast |
| **ARIMA** | Regression on past values and past errors, after differencing | statsmodels, pmdarima |
| **Regression with calendar features** | Trend, day-of-week, holidays, Fourier terms for yearly cycles | scikit-learn, Prophet |
| **Gradient boosting on lag features** | Lags, rolling means, calendar, many related series at once | LightGBM, XGBoost |
| **Deep learning / foundation models** | N-BEATS, DeepAR, TFT; pretrained models like Chronos, TimesFM | various |

Competition evidence: in M4 (100,000 series), combinations and hybrid methods led, the top two using ML components; in M5 (Walmart sales, 2020), the top solutions were machine-learning based, most built on LightGBM with lag and calendar features across many series [survey, arXiv:2401.13912](https://arxiv.org/abs/2401.13912). Gradient boosting shines with many related series; for one short series, simple methods remain hard to beat.

#### The whole recipe

1. **Plot** the series; decompose it (STL) to see trend and seasonal periods.

2. **Run benchmarks** (seasonal naive at least) with a rolling-origin backtest at your real horizon.

3. **Add structure**: calendar and holiday features, ETS/ARIMA, or gradient boosting on lags for many series.

4. **Compare by MASE/MAE** on the same backtest; keep a model only if it beats the benchmark.

5. **Produce intervals**, and monitor forecast error weekly in production.

#### Scenarios

##### "Forecast demand for 5,000 restaurants, 7 days ahead"

One LightGBM model across all restaurants with lags ≥ 7 days, rolling means, calendar and restaurant features; seasonal naive as benchmark; MASE averaged across restaurants.

##### "Our new model's MAPE looks great"

Check: shuffled CV? lag features unavailable at the horizon? low-volume stores dominating MAPE? Re-run a rolling-origin backtest against seasonal naive.

### The answer that sounds right

#### "Shuffle the days and cross-validate like any other dataset"

Random K-fold puts Tuesday in the test set and Monday and Wednesday in training, so the model interpolates between neighbours it will never have in real life. Hyndman & Athanasopoulos define time-series cross-validation so that "the corresponding training set consists only of observations that occurred prior to the observation that forms the test set. Thus, no future observations can be used in constructing the forecast" [FPP3 §5.10](https://otexts.com/fpp3/tscv.html). scikit-learn's guide agrees: shuffled splits on time-ordered data give "a model that is overfit and an inflated validation score" (see Cross-Validation & Leakage). The Backtesting section measures how much.

#### Rolling origin vs shuffled CV

Each row is one evaluation round over the two years (for the backtest, every other cut-off is shown): teal = training days, orange = days scored.

Same model, two evaluations: the honest rolling-origin backtest says **45.2**; shuffled 5-fold CV says **42.3**, about 7% too optimistic, because test days sit between training days and the model never has to extrapolate. With lag features (yesterday's orders) the gap is usually far bigger, since a shuffled test day's neighbours are literally its inputs. scikit-learn's `TimeSeriesSplit` implements expanding-window splits; add a `gap` equal to your forecast horizon when features use recent lags.

#### Caveats

- Structural breaks (a new competitor, a lockdown, an app redesign) invalidate history; no backtest on old data reveals them.

- One-off events (festivals on shifting dates like Diwali) need explicit holiday features.

- Forecasts influence the future: more riders scheduled → faster deliveries → more orders.

- Point forecasts hide uncertainty; plan with intervals or quantiles.

## Say it

### How would you build a forecast for a time series?

#### The interviewer pushes further

Follow-up 1 of 4

Why not regular K-fold for time series?

It trains on the future and tests on days surrounded by training days, so the score is optimistic; time-series CV trains only on data before each test window.

Follow-up 2 of 4

MAPE vs MASE?

MAPE is intuitive but undefined or huge near zero and asymmetric; MASE scales by the naive seasonal error, works at zero and compares across series.

Follow-up 3 of 4

How would you use ML (e.g. LightGBM) for forecasting?

Frame it as supervised regression: target = value at t + h, features = lags (≥ h), rolling stats, calendar, known future covariates, series identifiers; train across many series; backtest with rolling origins.

Follow-up 4 of 4

Direct vs recursive multi-step forecasting?

Recursive: one 1-step model fed its own predictions (errors compound). Direct: a separate model or target per horizon (no compounding, more models). Multi-output models are a middle ground.

#### The 30-second answer

I'd decompose the series into trend and seasonality, then start with simple benchmarks, especially seasonal naive, because a model that can't beat "same as last week" isn't worth deploying. Then I'd add structure: calendar and holiday features in a regression, exponential smoothing or ARIMA for single series, or gradient boosting on lag and calendar features across many related series, using only features available at forecast time for the full horizon. I'd evaluate with a rolling-origin backtest at the real horizon, never shuffled cross-validation, and compare models with a scale-free metric like MASE, plus prediction-interval coverage if it drives planning.

**Go further**

#### What not to say

- "Our model has 3% MAPE" without a benchmark.

- "I used yesterday's value as a feature for a 2-week forecast."

- "Shuffled CV on daily data."

**Key terms and sources**

Trend and seasonality, simple benchmarks (mean, naive, seasonal naive, drift), regression with calendar features, rolling-origin backtesting, MAE / MAPE / MASE, and where ARIMA, ETS and gradient boosting fit · built from Hyndman & Athanasopoulos, _Forecasting: Principles and Practice_ (3rd ed.), Hyndman & Koehler (2006) and the M4/M5 competitions · checked 28 Oct 2026

#### Evidence

##### 14-day backtest MAE (this page's simulation; lower is better)

mean

260.0

naive

211.6

seasonal naive

58.6

trend + weekday regression

60.0

+ yearly wave

45.2

Illustrative simulated series. The same "+ yearly wave" model scored 42.3 under shuffled CV.

#### Key terms

| Term | Meaning |
|---|---|
| **Trend / seasonality** | Long-run level / repeating pattern of fixed period. |
| **Seasonal naive** | Forecast = value one season ago. |
| **Horizon** | How far ahead you forecast. |
| **Rolling-origin backtest** | Repeatedly train on the past, forecast the next window, move forward. |
| **MASE** | MAE scaled by the seasonal naive in-sample MAE. |
| **ETS / ARIMA** | Classical statistical forecasting model families. |

#### What this page is built from

1. R. Hyndman & G. Athanasopoulos, _Forecasting: Principles and Practice_, 3rd ed., [otexts.com/fpp3](https://otexts.com/fpp3/) (decomposition, simple methods §5.2, accuracy §5.8, time-series CV §5.10).

2. R. Hyndman & A. Koehler, "Another look at measures of forecast accuracy", _International Journal of Forecasting_ 22, 2006 (MASE).

3. S. Makridakis, E. Spiliotis & V. Assimakopoulos, M4 (2018/2020) and M5 (2022) competition papers, _International Journal of Forecasting_; summarised in [arXiv:2401.13912](https://arxiv.org/abs/2401.13912).

4. scikit-learn, [TimeSeriesSplit](https://scikit-learn.org/stable/modules/cross_validation.html#time-series-split).

The order series is simulated with a known trend, weekly pattern and yearly wave; every forecast and backtest is computed live in your browser.
