# Stationarity, ARIMA and Exponential Smoothing

> What is stationarity, and how do ARIMA and exponential smoothing produce a forecast?

- Track: Fundamentals › Classical ML › Time series
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/stationarity-arima-and-smoothing/
- Before this: Time-Series Forecasting Basics (`fundamentals/forecasting-basics`)
- Quiz topic: `ts`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: e9d72098a6

## Intuition

### The situation

You have two years of daily orders, and a benchmark to beat. A colleague fits a model on the raw series, and reports a great fit, but its residuals still show a clear pattern. Another keeps differencing until the plot looks flat. The interviewer asks:

> What is stationarity, and how do ARIMA and exponential smoothing produce a forecast?

#### Why it matters

Forecasting Basics covers benchmarks and honest backtests. Interviewers often go further, and ask what stationarity means, or how you'd choose p, d and q. These two model families are also strong choices for a single series with little data.

### The idea

Think of steering a car. Exponential smoothing is like checking your position often, and trusting recent checks most. ARIMA is more like correcting from how far you've drifted and how wrong your last corrections were. Both work best once you've removed the road's overall slope.

[Figure: Three ideas. Differencing removes trend and season. ARIMA uses past values and past errors. Exponential smoothing tracks level, trend and season.]

_Neither family contains the other, so compare them with a backtest._

### Play

**Try to break it.** Difference a series at φ = 0. Then try α near 0 and α = 1.

#### See stationarity, then smooth a series

Our seeded simulation of 300 steps: today = φ × yesterday + noise, plus the trend. φ = 1 is a random walk. The top chart shows the series, and the bars show the ACF at lags 1 to 10.

Our seeded simulation: a level of 50 jumps to 70 halfway through, with noise. Catching up means getting within 2 of the new level.

In the first lab, tick **difference** at φ = 1, and the slow ACF disappears. Then set φ to **0**, which is already stationary, and keep the tick: a false pattern appears at lag 1. That's why over-differencing is a real mistake. In the second lab, try α near 0 and α = 1, and find the balance between smoothing and reacting.

**Now say why:** why does differencing a stationary series create a false pattern?

## Maths

### Maths

#### In one breath

A series is **stationary** if its behaviour doesn't depend on when you look, so trends and seasons break it. **Differencing** usually fixes that. **ARIMA** then predicts a differenced series from its own past values and past errors. **Exponential smoothing** takes another route, and tracks a level, a trend and a season using weighted averages that favour recent data. Forecast uncertainty grows with the horizon, so a single number is never the whole answer.

#### The pieces

##### Stationarity

In a stationary series, the statistical properties don't depend on the time you observe it. So a series with a trend or a season isn't stationary. Cycles of no fixed length can be, as you can't predict where the peaks will be.

**Differencing** replaces each value with its change from the one before, which removes a changing level. A **seasonal difference** subtracts the value one season ago, such as the same weekday last week. More than two ordinary differences is almost never needed, and too many add false patterns.

##### Reading ACF and PACF

The **ACF** gives the correlation between a series and itself at each lag. The **PACF** gives the same after removing the effect of the lags in between.

| What you see | What it suggests |
|---|---|
| ACF falls slowly, and the first value is large | Not stationary, so difference it. |
| ACF decays, and PACF has a last clear spike at lag p | AR(p): an ARIMA(p, d, 0). |
| PACF decays, and ACF has a last clear spike at lag q | MA(q): an ARIMA(0, d, q). |
| Both decay | A mix of the two. The plots can't give p and q, so compare models. |

##### Choosing the model

- **d:** use a test. KPSS assumes the series is stationary, so a small p-value suggests differencing. ADF assumes the opposite, so a large p-value suggests differencing.

- **p and q:** minimise AICc, for models with the same d. Differencing changes the data being fitted, so AICc can't compare different d.

- **Check:** residuals should look like noise, with no ACF pattern left.

##### Exponential smoothing

| Method | Tracks | Its forecast looks like |
|---|---|---|
| **Simple** | Level | A flat line. |
| **Holt** | Level and trend | A straight line. |
| **Damped trend** | Level and a fading trend | A line that flattens out. |
| **Holt-Winters** | Level, trend and season | A repeating pattern. Additive if the swings stay constant, and multiplicative if they grow with the level. |

**ETS** is the statistical version of these methods. It gives the same point forecasts, and adds prediction intervals.

##### ARIMA or exponential smoothing?

Neither family contains the other. Linear smoothing models are special cases of ARIMA, and simple smoothing matches ARIMA(0, 1, 1). But multiplicative smoothing models have no ARIMA equivalent, and some ARIMA models have no smoothing equivalent. AICc can't compare across the two families, so compare them with a backtest.

##### Why intervals widen

Errors build up as you forecast further ahead. For a naive forecast, the spread grows with the square root of the horizon. As an illustration, if the one-step standard deviation is 10 orders, a 95% interval is about ±20 at one step, and about ±39 at four steps.

#### The maths

$$ {y'_t} = {c} + {\sum_{i=1}^{p}\phi_i\, y'_{t-i}} + {\sum_{j=1}^{q}\theta_j\, e_{t-j}} + {e_t}, \qquad {\ell_t = \alpha y_t + (1-\alpha)\,\ell_{t-1}} $$

From Hyndman and Athanasopoulos, Forecasting: Principles and Practice, chapters 8 and 9.

- **the differenced series**: The value after differencing d times. This is the I in ARIMA.

- **a constant**: Together with d, this sets the long-run behaviour of the forecast.

- **the AR part**: Today depends on the last p values.

- **the MA part**: Today also depends on the last q forecast errors.

- **the new shock**: The part of today that nothing could have predicted.

- **simple smoothing**: The new level mixes the latest value with the old level. A large α reacts quickly, and a small α smooths more.

## In practice

### In practice

#### In practice

- **Plot first:** a transform like a log can steady a series whose swings grow with its level.

- **Start with a benchmark:** a model that can't beat seasonal naive isn't worth keeping.

- **One series or many:** these models fit one series at a time. With thousands of related series, boosting on lag features often does better, and is simpler to run as one model.

- **Use a damped trend for long horizons:** a straight line continues forever, which is rarely believable.

- **Report intervals:** check they contain the actual values about as often as they claim.

### The answer that sounds right

#### "Keep differencing until the series looks flat"

It sounds right, as stationarity is the goal. But each extra difference adds noise, and can create patterns that aren't real. A stationary series gets a false lag-1 correlation of about −0.5 if you difference it. One or two differences are almost always enough, and a test can tell you when to stop.

## Say it

### What is stationarity, and how do ARIMA and exponential smoothing produce a forecast?

#### The interviewer pushes further

Follow-up 1 of 3

How would you tell if a series is stationary?

Plot it, and look for a trend, a season or changing spread. Look at the ACF too: a slow decay suggests non-stationary. Then confirm with a test such as KPSS, where a small p-value suggests differencing, or ADF, where the null hypothesis is the opposite.

Follow-up 2 of 3

Why not just keep differencing until it looks flat?

Too many differences add false patterns, and increase the variance. If you difference a stationary series, you get a lag-1 correlation of about −0.5. One or two differences are almost always enough.

Follow-up 3 of 3

What's the difference between AR and MA?

AR predicts from past values, so a shock's effect fades gradually. MA predicts from past errors, so a shock's effect ends after q steps. That's why the ACF of an MA(q) series has a last clear spike at lag q, while an AR series decays.

#### The 30-second answer

A stationary series behaves the same whenever you look at it, so trends and seasons break it, and differencing usually fixes that. ARIMA predicts the differenced series from its past values and past errors. I'd choose d with a test, read p or q from the ACF and PACF if the pattern is clear, and otherwise compare AICc for the same d. Exponential smoothing tracks a level, trend and season with weighted averages. Neither family contains the other, so I'd compare them with a backtest, against seasonal naive, and report intervals, which widen with the horizon.

**Key terms and sources**

Stationarity, differencing, ACF and PACF, what AR, MA and ARIMA models do, exponential smoothing from simple to Holt-Winters, and why intervals widen. · checked 6 Nov 2026

#### Sources

- [Hyndman and Athanasopoulos, Forecasting: Principles and Practice, ARIMA (chapter 9)](https://otexts.com/fpp3/arima.html)

- [Same book, exponential smoothing (chapter 8)](https://otexts.com/fpp3/expsmooth.html)

- [Same book, prediction intervals (section 5.5)](https://otexts.com/fpp3/prediction-intervals.html)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
