# Correlation vs Causation

> When the data says the opposite of the truth: confounders and Simpson's paradox.

- Track: Fundamentals › Maths for ML › Statistics
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/correlation-vs-causation/
- Before this: Hypothesis Tests, p-values & A/B Testing (`fundamentals/hypothesis-testing-and-ab-tests`)
- Quiz topic: `stats`

## Intuition

### The situation

Customers who use live order tracking reorder far more often, and someone wants to push tracking on everyone. The interviewer asks:

> How can correlation mislead you, and how do you estimate a causal effect?

**Running example:** the food-delivery app notices that customers who use live order tracking reorder far more often. Should it push tracking on everyone to increase reorders? A simulation where we control the truth answers it: tracking has **no effect** on reordering, but engaged customers are more likely both to use tracking and to reorder. A real medical dataset shows the same trap in Simpson's paradox.

#### Prediction questions vs intervention questions

"Which customers will reorder?" is a prediction question: any correlated signal helps. "Will customers reorder more _if we make them_ use tracking?" is a causal question: only the effect of changing tracking matters. ML engineers are asked the second kind constantly, and answering it with the tools for the first is one of the most expensive mistakes in industry.

### The idea

Think of umbrellas and wet streets. They rise and fall together, but handing out umbrellas won't make it rain. Rain causes both. A hidden common cause like this can make two things look linked when neither affects the other.

[Figure: Engagement sits at the top with arrows to using tracking and to reordering. A dashed line between tracking and reordering shows a correlation with no arrow of cause.]

_From the lesson's simulation: engagement drives both tracking use and reordering._

### Play

**Try to break it.** Look at all patients, then split them by stone size.

#### Simpson's paradox: kidney stones

| | Open surgery (A) | Percutaneous nephrolithotomy (B) |
|---|---|---|
| Small stones | 93% (81/87) | 87% (234/270) |
| Large stones | 73% (192/263) | 69% (55/80) |
| All patients | 78% (273/350) | 83% (289/350) |

A was better for small stones _and_ for large stones, yet worse overall. The confounder is stone size: doctors gave the riskier open surgery mostly to large, harder cases, so A's overall rate is dragged down by case mix. The study was observational, not randomised, so even the subgroup comparison isn't proof Charig et al., BMJ 1986. Which table to trust depends on the causal story, not on the numbers: here stone size affects both treatment choice and outcome, so compare within size.

**Now say why:** how can one treatment win in both groups and still lose overall?

## How it works

### How it works

#### In one breath

Two things moving together doesn't mean one causes the other. A hidden **confounder** can drive both (engaged customers both use live tracking _and_ reorder more), the arrow can point the other way (**reverse causation**), or the data may only include a skewed subset (**selection bias**). Confounding can even flip a comparison: in **Simpson's paradox** a treatment wins in every subgroup and loses overall. **Randomisation** (A/B tests) breaks every hidden link and is the gold standard; without it you must adjust for the confounders you can measure and argue there are no others. ML models learn correlations, so they predict well but don't tell you what will happen if you _intervene_.What you'll be able to do after this: name the ways correlation misleads, explain Simpson's paradox with real numbers, say why randomisation works, and keep "predictive" and "causal" claims apart in interviews.

#### Four ways a correlation can mislead

1. The data shows that tracking users reorder more.

2. **Confounding:** engagement causes both. Tracking may do nothing, yet the correlation is strong.

3. **Reverse causation:** customers who already order often are the ones who find and use the feature.

4. **Selection bias:** if the dataset only includes some customers (survey responders, retained users), correlations inside it can be created by who got in. A fourth trap is pure chance across many tested pairs.

5. **Randomisation** assigns tracking by coin flip, so nothing about the customer can influence who gets it. Any remaining difference must be caused by tracking (or noise).

#### How to get a causal answer

1. **Randomised experiment (A/B test):** the gold standard; treatment can't depend on anything about the unit (A/B Testing).

2. **Adjust for observed confounders:** stratification, regression with the confounders as inputs, matching, or inverse-propensity weighting. Valid only if there are no _unmeasured_ confounders, an assumption you must argue from domain knowledge.

3. **Natural experiments:** difference-in-differences (a policy changed in one city but not another), instrumental variables, regression discontinuity (a sharp eligibility cut-off).

4. **Causal diagrams:** draw the assumed causes (Pearl's DAGs) to decide which variables to adjust for, and which _not_ to (adjusting for a consequence of the treatment, a mediator or a collider, creates bias).

Hernán & Robins, _Causal Inference: What If_ (free online); Pearl & Mackenzie, _The Book of Why_.

#### Pearson, Spearman, and going further

- **Pearson** measures straight-line relationships. Outliers can strongly affect it.

- **Spearman** is Pearson on ranks, so it measures any steadily rising or falling relationship, and it's robust to outliers.

Example: for x = 1 to 5 and y = x³, Spearman is exactly 1, as the order always agrees, while Pearson is about 0.94. A zero correlation of either kind doesn't mean no relationship: y = x² on symmetric x has a Pearson of 0.

When you can't run an experiment, see causal inference without an experiment.

## In practice

### In practice

#### What this means for models

- **Feature importance isn't causal:** a feature can be important because it's a proxy for a confounder (zip code for income). Changing it won't change the outcome.

- **Shortcut learning:** models latch onto spurious correlations (a hospital's scanner model predicting disease) that break when the setting changes.

- **Feedback loops:** a recommender's training data is caused by its own past recommendations; observed clicks reflect exposure, not only preference.

- **Uplift modelling:** to decide _whom to treat_ (send a coupon), model the difference in outcome with vs without treatment, trained on randomised data.

### The answer that sounds right

#### "Tracking users reorder 25 points more, so tracking drives reorders"

20,000 simulated customers per study. Engagement drives both tracking use and reordering; in the second setting tracking also has a real positive effect.

With **no** real effect, the naive comparison shows a 25.5-point lift. Comparing customers of similar engagement shrinks it to 2.6 points (some confounding remains within the coarse bands), and the randomised test shows 0.8 points, within noise. With a real effect, the naive estimate (33.7) is still far too high, while randomisation (8.5) recovers the true size. Adjusting only works for confounders you _measured_; randomisation also handles the ones you didn't.

## Say it

### How can correlation mislead you, and how do you estimate a causal effect?

#### The interviewer pushes further

Follow-up 1 of 3

Users who use feature X retain better. How would you test if X causes retention?

Randomised rollout or encouragement design (randomly prompt some users to try X); if impossible, compare similar users with matching/propensity scores, look for a natural experiment, and state the unmeasured-confounder risk.

Follow-up 2 of 3

Explain Simpson's paradox with an example.

Kidney stones: open surgery had higher success for small and for large stones, but lower overall, because it was mostly used on large stones, which have worse outcomes regardless.

Follow-up 3 of 3

Should you control for every variable you have?

No: controlling for mediators removes part of the effect you want, and controlling for colliders creates bias. Use a causal diagram to choose.

#### The 30-second answer

Correlation can come from a confounder that causes both variables, from reverse causation, from selection bias, or from chance. Confounding can even reverse a comparison, as in Simpson's paradox, where a treatment wins in every subgroup but loses overall because of case mix. The cleanest way to estimate a causal effect is randomisation, because nothing about the unit can influence assignment. Without it, adjust for measured confounders with stratification, regression, matching or propensity weighting, and argue there are no unmeasured ones, or use natural experiments like difference-in-differences. Predictive models learn correlations, so feature importance isn't a causal effect.

**Go further**

#### What not to say

- "The model shows feature X drives churn." It shows association.

- "More data will remove confounding." Bias doesn't shrink with sample size.

**Key terms and sources**

Confounders, Simpson's paradox, selection bias and reverse causation, randomisation, adjusting for observed confounders, and what it means for ML models and feature importance · built from Charig et al., _BMJ_ (1986), Pearl & Mackenzie, _The Book of Why_ (2018), Hernán & Robins, _Causal Inference: What If_ (2020) and Kohavi et al. (2020) · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Confounder** | A common cause of treatment and outcome. |
| **Simpson's paradox** | A trend in every subgroup reverses when groups are combined. |
| **Selection bias** | Distortion from how units entered the data. |
| **Randomised controlled trial** | Treatment assigned by chance; breaks confounding. |
| **Collider** | A common effect; conditioning on it creates spurious association. |

#### Sources

1. C. Charig, D. Webb, S. Payne & J. Wickham, "Comparison of treatment of renal calculi by open surgery, percutaneous nephrolithotomy, and extracorporeal shockwave lithotripsy", _BMJ_ 292, 1986, PMC1339981.

2. J. Pearl & D. Mackenzie, _The Book of Why_, Basic Books 2018.

3. M. Hernán & J. Robins, _Causal Inference: What If_, Chapman & Hall/CRC 2020, free online.

4. R. Kohavi, D. Tang & Y. Xu, _Trustworthy Online Controlled Experiments_, CUP 2020.

The tracking example is simulated with a known (zero or positive) effect; kidney-stone figures are from Charig et al. (1986).
