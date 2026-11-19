# Design Ad Click Prediction

> An ads platform must predict, for every ad it might show, the chance that this user clicks. The prediction sets prices in the auction, so it must be accurate and calibrated. Design it.

- Track: System Design › Ads and Search Ranking › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-ad-click-prediction/
- Before this: Logistic Regression (`fundamentals/logistic-regression`), Probability Metrics (`fundamentals/probability-metrics`)
- Quiz topic: `sdrec`

## Intuition

### The situation

A social network shows ads chosen by targeting, not search queries, to hundreds of millions of people. For each candidate ad, the system must predict the chance of a click; that prediction, times the bid, runs the auction. The interviewer asks:

> An ads platform must predict, for every ad it might show, the chance that this user clicks. The prediction sets prices in the auction, so it must be accurate and calibrated. Design it.

#### Ask before designing

- **How ads are chosen:** by targeting (demographics, interests), not a search query, so many ads are eligible for each request.

- **What's predicted:** the probability of a click for each candidate ad, used with the bid in the auction.

- **Scale:** hundreds of millions of impressions a day, and a tight latency budget per request.

- **Must never happen:** systematically over- or under-predicting clicks, which misprices the auction for advertisers.

- **Success metrics:** normalised cross-entropy (log loss relative to always predicting the average click rate), calibration, and revenue and advertiser outcomes online.

### The idea

Think of a bookmaker setting odds. Getting the order of favourites right isn't enough: if the odds are off, the house loses money on every bet. Fresh form matters more than old reputation, and odds are rechecked every day.

[Figure: Cheap models narrow the ads. Boosted trees turn features into leaf indices. A logistic regression, updated online, predicts the click. Downsampled training is recalibrated.]

_Ranking right isn't enough; the probability must be right too._

### Play

**Try to break it.** Switch between the three models. Turn on daily retraining. Then drag the share of non-clicks down to 2.5%.

#### Model, freshness and sampling

From the paper: Table 1 (model structures, relative to trees only), section 3.2 (about 1% from weekly to daily training) and section 6.3 (recalibration q = p / (p + (1 − p) / w)). Adding effects together is our simplification.

Switch models: the combination wins. Then turn on daily retraining: freshness alone gives about 1%, which is large in this world, where most feature work gains a fraction of a percent. Now downsample the non-clicks: training is far cheaper, but the model's probabilities are inflated, so **convert them back** before the auction uses them.

**Now say why:** why must you recalibrate after downsampling non-clicks?

## Architecture

### Architecture

#### In one breath

Click prediction feeds the auction, so the **probability itself** must be right, not just the ranking. Use a **cascade**: cheap models narrow the ads, and the last model predicts click-through for a small set. A strong recipe: **boosted trees turn raw features into leaf indices**, and a **logistic regression trained online** on fresh data sits on top. **Historical features** about the user and ad matter most. Downsample negatives to save compute, then **recalibrate** the probabilities.

#### A cascade, then a precise final model

1. **Candidates:** targeting rules and cheap models narrow millions of ads to a few hundred for this request.

2. **Features:** contextual ones like time of day and device, and historical ones like this ad's click rate last week or this user's average click rate.

3. **Tree transform:** boosted decision trees, trained in batch, map each impression to the leaf it lands in for every tree. Those leaf indices become sparse binary features.

4. **Linear model:** a logistic regression over those features, updated online as new clicks arrive, predicts the click probability.

5. **Auction:** the predicted probability times the bid ranks the ads.

##### Why trees plus a linear model?

Trees learn useful non-linear splits and feature combinations automatically; a linear model on top can be retrained cheaply and often. Together they beat either alone.

##### The online joiner

To train online you need labels fast: join each impression with its click, if one arrives within a waiting window. Too short a window loses late clicks; too long delays training and needs more memory.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Impressions a day | given | **500 million** |
| Clicks a day | 500 million × 1% | **5 million** |
| Training rows after keeping 2.5% of non-clicks | 5 million + 495 million × 2.5% | **about 17 million** |
| Final-model predictions a second | 50,000 requests × 200 ads | **10 million** |

Downsampling shrinks the training data about 30× while keeping every click, which is what makes daily retraining affordable.

## In practice

### In practice

#### What every click-prediction design gets asked

- **Metric:** normalised cross-entropy and calibration, not just AUC. AUC ignores whether probabilities are right, and the auction needs them right.

- **Features:** historical features (past click rates) carry most of the signal; contextual ones still matter for new users and new ads.

- **How many trees and features:** gains flatten quickly; a few hundred trees and the top features capture most of the value, which keeps serving cheap.

- **Learning rates for online updates:** per-coordinate learning rates work best, since popular features see far more updates than rare ones.

- **Safety for online training:** if the click stream breaks, the joiner produces data with almost no clicks and the model learns to predict zero. Detect sudden shifts and stop online training automatically.

- **Today:** many systems now use deep models with feature embeddings and interaction layers, but the lessons about freshness, calibration and sampling still hold.

##### Rollout

Compare a new model offline on next-day data, then run an online test on revenue and advertiser outcomes, watching calibration closely.

#### What the real system reported

- **Context:** over 750 million daily active users and over 1 million active advertisers; ads chosen by targeting, with a cascade of classifiers of increasing cost.

- **Model:** boosted trees as feature transforms plus logistic regression beat either alone by over 3% in normalised entropy.

- **Freshness:** going from weekly to daily training reduced normalised entropy by about 1%; an online joiner fed real-time training data to an online linear model.

- **Features and size:** the top 10 features gave about half the total importance; historical features beat contextual ones; almost all gains came from the first 500 trees.

- **Data volume:** 10% of the data cost only about 1% in accuracy; the best negative downsampling rate was 0.025, followed by recalibration.

From the paper (ADKDD 2014).

### The answer that sounds right

#### "AUC went up, so the model is better"

It sounds right, since AUC measures ranking. But the auction uses the probability itself: a model that predicts twice the real click rate can have the same AUC and still overcharge advertisers. Track calibration and normalised cross-entropy too.

## Say it

### An ads platform must predict, for every ad it might show, the chance that this user clicks. The prediction sets prices in the auction, so it must be accurate and calibrated. Design it.

#### The interviewer pushes further

Follow-up 1 of 3

Why does calibration matter more here than in many ranking problems?

The predicted probability is multiplied by the bid to price the auction. If predictions are twice too high, advertisers pay too much even if the ranking is right. AUC wouldn't notice; normalised entropy and calibration do.

Follow-up 2 of 3

You downsample non-clicks to 2.5%. What breaks?

The model now sees a much higher click rate than reality, so its raw probabilities are inflated. Convert them back with q = p / (p + (1 − p) / w), where w is the sampling rate, before using them.

Follow-up 3 of 3

How do you handle a brand-new ad with no history?

Lean on contextual and advertiser-level features, give it some exploration traffic, and let historical features build up quickly with fresh retraining.

First I'd clarify how ads are selected, the scale, the latency budget, and that the auction needs calibrated probabilities. I'd use a cascade: targeting and cheap models narrow to a few hundred ads, and the final model predicts click probability. Features are contextual, like device and time, and historical, like past click rates for the ad and user; historical ones carry most signal. A strong design uses boosted trees to turn raw features into leaf indices, with a logistic regression on top that's updated online from an impression–click joiner, because fresher data clearly helps. I'd measure normalised cross-entropy and calibration, not just AUC. To save compute I'd keep all clicks and a small share of non-clicks, then recalibrate the probabilities. Online training needs guards, so a broken click stream can't teach the model to predict zero. New models are compared offline on next-day data, then tested online on revenue and calibration.

**Key terms and sources**

Based on a social network's published paper: "Practical Lessons from Predicting Clicks on Ads at Facebook" (ADKDD 2014). The lab uses the paper's own numbers; the estimate is ours. The paper is from 2014, so treat the model as a strong baseline rather than today's state of the art. Uses logistic regression, gradient boosting and probability metrics.
