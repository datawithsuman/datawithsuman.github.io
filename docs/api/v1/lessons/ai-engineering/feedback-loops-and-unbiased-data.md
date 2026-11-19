# Feedback Loops and Unbiased Training Data

> Your recommender is retrained on its own clicks every week, and it keeps showing the same few items. Why, and how do you get data it can learn from?

- Track: AI Engineering › MLOps › Lessons
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/ai-engineering/feedback-loops-and-unbiased-data/
- Before this: Retraining Pipelines and Continuous Training (`ai-engineering/retraining-pipelines`), Bandits vs A/B Tests (`fundamentals/bandits-vs-ab-tests`)
- Quiz topic: `mlops`

## Intuition

### The situation

Your recommender is retrained weekly on its own click logs. Each version looks better offline, but users see the same few items, and new items never take off. The interviewer asks:

> Your recommender is retrained on its own clicks every week, and it keeps showing the same few items. Why, and how do you get data it can learn from?

#### Why it matters

Many models choose what happens next: what's recommended, which loans are approved, which transactions are reviewed. Their logs record outcomes only for the choices they made. Sculley et al. listed these hidden feedback loops as a form of technical debt in ML systems. Interviewers ask about them in recommender, ads, pricing and fraud designs.

### The idea

Think of a restaurant critic who only revisits places they already like. They'll never find out the new place down the road is better, and their list gets shorter every year. Trying somewhere new now and then is the only way to learn.

[Figure: Three fixes. Explore a little. Log the chance of each choice. Keep a holdout.]

_You only learn about what you chose._

### Play

**Try to break it.** Run with no exploration. Then add 5%, then 20%.

#### A model that can't learn it was wrong

Illustrative, with expected values and no noise. 10,000 users a day. Real click rates: A 4%, B 6%, C 3%, D 2%, E 5%. The old model believes A 4.5%, B 2%, C 3%, D 2%, E 1%. Exploration spreads its share evenly over all five items, and the model updates its beliefs from each day's clicks.

With **no exploration**, the model keeps showing item A at 400 clicks a day. It never shows B, so it never learns B gets 6%, and it loses 6,000 clicks in 30 days. With **5% exploration**, one day of data reveals B, the model switches, and it gets 590 clicks a day, losing 490 over the month, mostly on day one and the exploration itself. **20% exploration** learns just as fast but keeps paying for it: 560 a day. So explore a little, all the time, and log the chances.

**Now say why:** why does a little exploration beat a lot?

## How it works

### How it works

#### In one breath

A recommender only sees clicks on what it showed. If it thinks item B is poor, it never shows B, so it never learns B is actually the best. Retraining on its own logs makes this worse each week, which is a **feedback loop**. The fixes: spend a small share of traffic on **exploration**, so every option gets some data; keep a **holdout** group served without the model; and **log the probability** that each shown item was chosen, so later training and evaluation can correct for what the old model preferred.

#### How loops form

##### You only see outcomes for what you chose

- **Recommenders:** unshown items get no clicks, so they look unpopular.

- **Lending:** you never learn whether rejected applicants would have repaid.

- **Fraud review:** only flagged transactions get checked, so labels cover what the model already suspects.

- **Policing and inspections:** Ensign et al. showed that sending patrols where incidents were recorded, and recording incidents where patrols go, can run away from the true rates.

##### Greedy models narrow fastest

Jiang et al. at DeepMind simulated recommenders acting on users whose interests shift with what they see. A model that always picked its current best items narrowed users onto a handful of items fastest. Random exploration and a growing pool of new items slowed this. Chaney et al. found that training on data shaped by an earlier recommender made recommendations more alike across users, and less useful.

##### The fixes

- **Exploration:** show a small share of traffic other options, randomly or with a bandit, so every option keeps getting data. See bandits.

- **Log the chance of each action:** record the probability that each shown item was chosen. Bottou et al. showed how such logs let you estimate how a different policy would have done, by weighting outcomes by one over that probability.

- **Holdouts:** keep a small group served without the model, or with an older one, to measure its real effect.

- **Watch diversity:** track how many distinct items are shown, and how concentrated exposure is.

#### The maths

$$ \hat{V}(\pi) = \frac{1}{n}\sum_{i=1}^{n} r_i\,\frac{\pi(a_i \mid x_i)}{p_i} $$

Inverse propensity scoring. It only works for actions the old system sometimes took, which is why exploration matters: with no exploration, many chances are zero.

- **value of a new policy**: How a policy you haven’t deployed would have done, estimated from old logs.

- **the outcome**: For example, a click on what was shown.

- **new policy’s chance**: How likely the new policy is to take the logged action.

- **logged chance**: How likely the old system was to take it. You must log this when serving, and it must never be zero.

## In practice

### In practice

#### In practice

- **Log propensities at serving time:** the probability of each shown action, plus what else was eligible. You can't recover them later.

- **Keep a small exploration budget:** a few percent, controlled and measured, rather than none.

- **Hold out a group:** to measure the model's real effect against a simple baseline over time.

- **Evaluate offline with care:** logs from the old model favour it, so weight by propensities, or confirm with an A/B test.

- **Track diversity and coverage:** how many items get shown, and whether new items ever get a chance.

### The answer that sounds right

#### "Retrain on the latest clicks, and it'll fix itself"

It sounds right, since fresh data usually helps. But the clicks come only from items the model chose to show, so retraining reinforces its own picks. Explore a little, log the chances, and evaluate with weights or a holdout.

## Say it

### Your recommender is retrained on its own clicks every week, and it keeps showing the same few items. Why, and how do you get data it can learn from?

#### The interviewer pushes further

Follow-up 1 of 3

Your offline evaluation says the new recommender is worse, but it's never been shown to users. Can you trust that?

Not fully. The logs come from the old model, so they only have outcomes for items it liked. Weight by logged propensities if you have them, or run an A/B test.

Follow-up 2 of 3

Why not explore by showing random items to everyone sometimes?

Uniform random exploration is costly for users. Use a small share, a bandit that explores where it's uncertain, or explore within a shortlist of reasonable items.

Follow-up 3 of 3

A loan model approves fewer people each year, and its defaults look great. What's wrong?

You only see repayment for approved applicants, so the model never learns about the ones it rejects. Approve a small, controlled sample near the threshold to get unbiased labels.

A model that chooses what users see only gets feedback on its own choices, so an item it wrongly rates low never gets shown, and retraining on its logs locks the mistake in. DeepMind's simulations showed greedy recommenders narrow fastest, while exploration and new items slow it down. I'd spend a few percent of traffic on exploration, log the probability of each shown action so I can weight outcomes later, keep a holdout group to measure real impact, and track how many distinct items get shown.

**Key terms and sources**

How models that act on the world shape their own training data, why a greedy system can never learn it was wrong, and the fixes: exploration, holdouts, logging the chance each action was taken, and correcting for it.

#### Sources

- Sculley et al., Hidden Technical Debt in Machine Learning Systems, NeurIPS 2015

- Jiang et al., Degenerate Feedback Loops in Recommender Systems

- Bottou et al., Counterfactual Reasoning and Learning Systems

- Ensign et al., Runaway Feedback Loops in Predictive Policing

- Chaney, Stewart and Engelhardt, How Algorithmic Confounding in Recommendation Systems Increases Homogeneity

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and provider policies change.
