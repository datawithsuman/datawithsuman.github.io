# Feature Engineering

> How would you create useful features for a model, and how do you avoid leaking the future?

- Track: Fundamentals › Classical ML › Data and features
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/feature-engineering/
- Before this: Missing Values & Feature Scaling (`fundamentals/missing-values-and-scaling`), Encoding Categorical Features (`fundamentals/categorical-encoding`)
- Quiz topic: `feat`

## Intuition

### The situation

You're predicting orders per hour. A linear model using the raw hour does badly, as it can only draw one straight line through the day. A teammate's new "average orders this week" feature gives a huge jump in score. The interviewer asks:

> How would you create useful features for a model, and how do you avoid leaking the future?

#### Why it matters

On tabular data, better features often help more than a fancier model. They're also a very common topic in practical interviews. This follows encoding and missing values and scaling.

### The idea

Think of giving someone directions. "Walk 3 km north-north-east" and "go to the station" point to the same place, but one is far easier to act on. Features work the same way: the same information, expressed so the model can use it.

[Figure: Three common recipes. Ratios allow fair comparisons. Windows capture recent behaviour. Cycles keep 11 pm near midnight.]

_Every feature must be computed as of the prediction time._

### Play

**Try to break it.** Use only the raw hour. Then try each of the other options alone.

#### Help a linear model learn the day

Our seeded simulation: orders per hour with lunch and dinner peaks, plus noise. It's fitted with linear regression on 2,000 rows, and scored on 2,000 others. The dashed line is the true pattern, and the orange line is the model.

Try each option on its own. The model and the data haven't changed, only how the hour is expressed. A tree could find these peaks with raw hour, by splitting several times, but it would still need enough data to do so.

**Now say why:** why does the same model do so much better with the same information?

## Maths

### Maths

#### In one breath

A model can only learn from what you give it, and the way you express something decides how easily it can use it. Good features come from **asking how the outcome really happens**: ratios, recency, counts over time, and cycles like hour of day. Tree models find many interactions themselves, while linear models need more help. The big danger is **leakage**: any feature using information you wouldn't have at prediction time looks great, then fails in production.

#### Common recipes

| Type | Example | Why it helps |
|---|---|---|
| **Ratios** | Cancelled orders ÷ total orders | Comparable across big and small users. |
| **Recency** | Days since the last order | Recent behaviour often predicts best. |
| **Windows** | Orders in the last 7 and 30 days | Captures level and trend. |
| **Cycles** | Sine and cosine of the hour | 11 pm and midnight are close, though 23 and 0 aren't. |
| **Interactions** | Distance × rain | One feature's effect depends on another's. |
| **Transforms** | Log of income | Tames long tails, particularly for linear models. |
| **Aggregates** | A restaurant's average preparation time | Brings in group-level knowledge. |
| **Missing flags** | "No phone given" | Being missing can itself be a signal. |

##### Different models need different help

- **Linear models:** only add up what they're given, so they need interactions, curves and scaling.

- **Trees and boosting:** handle thresholds and many interactions, and ignore scale. But they struggle to make a smooth ratio, or to extrapolate a trend.

- **Neural networks:** learn features from raw text and images, and on tabular data they still benefit from good inputs.

##### Leakage: the main way this goes wrong

A feature leaks if it contains information you wouldn't have at prediction time.

- **From the future:** a 30-day average that includes days after the prediction moment.

- **From the label:** a "refund issued" field in a model that predicts complaints.

- **From the test set:** computing averages or target encodings on all the data, before splitting.

Always compute a feature **as of the prediction time**. If a new feature gives a huge, sudden jump in score, suspect leakage first. See cross-validation and leakage.

#### The maths

$$ x_{\sin} = \sin\!\left(\frac{2\pi \cdot \text{hour}}{24}\right), \qquad x_{\cos} = \cos\!\left(\frac{2\pi \cdot \text{hour}}{24}\right), \qquad x_{7d}(t) = \sum_{k=1}^{7} \text{orders}(t - k) $$

With a cycle encoding, a linear model can represent a single daily peak. Two daily peaks need a second pair at 12 hours, as the lab shows.

- **the sine part**: Places each hour on a circle, so 23:00 and 00:00 end up near each other.

- **the cosine part**: Both are needed, as sine alone gives two hours the same value.

- **a window feature**: It only counts days before t. Including t or later would leak the future.

## In practice

### In practice

#### In practice

- **Start from the domain:** ask someone who knows the process what would predict the outcome, before generating thousands of features.

- **Same code in training and serving:** computing a feature differently in each causes training-serving skew.

- **Fit inside the fold:** anything learned from data, like means or encodings, must be computed from training folds only.

- **Keep a baseline:** add features in groups, and check the validation score, so you can see what actually helps.

- **Count the cost:** each feature needs computing, monitoring and maintaining in production.

### The answer that sounds right

#### "The new feature raised our score a lot, so ship it"

It sounds right, as that's the goal. But a sudden large jump is the classic sign of leakage. An average that includes the current week contains the very thing you're predicting. Check when each value is really known, and test on a strictly later period, before you trust it.

## Say it

### How would you create useful features for a model, and how do you avoid leaking the future?

#### The interviewer pushes further

Follow-up 1 of 3

How would you encode hour of day?

Sine and cosine of a 24-hour cycle, so 23:00 and 00:00 are close. With a tree, a raw hour often works, as it can split on ranges. If there are several daily peaks, add a 12-hour cycle, or flags for known peaks, which a linear model can use directly.

Follow-up 2 of 3

A new feature raised AUC from 0.75 to 0.99. What do you do?

Suspect leakage. Check when that value becomes known compared with the prediction time, and how it's computed. Look at importance, read some rows, and try it on a strictly later time period. Real features rarely produce a jump that large.

Follow-up 3 of 3

Do tree models need feature engineering?

Less than linear models, as they don't need scaling, and they find thresholds and many interactions. But they can't easily make ratios, as this needs many splits, and they can't extrapolate trends. Good domain features still often help the most.

I'd start by asking how the outcome really happens, then express that: ratios for fair comparisons, recency, windows of counts, cycles for time, and interactions. Linear models need more of this, while trees find thresholds and interactions, but not smooth ratios or trends. The main risk is leakage, so I'd compute every feature as of the prediction time, and fit anything learned from data on training folds only. If a feature gives a sudden huge jump, I'd suspect a leak first. I'd use the same code in training and serving.

**Key terms and sources**

Turning raw data into signal: ratios, dates and cycles, aggregates and interactions, what different models need, and how to avoid leakage.

#### Sources

- scikit-learn user guide

- Google Machine Learning Crash Course

- Géron, Hands-On Machine Learning, contents

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
