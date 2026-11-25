# Sampling and Bias

> What sampling methods would you use, and how can selection or survivorship bias ruin a dataset?

- Track: Fundamentals › Maths for ML › Statistics
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/sampling-and-bias/
- Before this: Descriptive Statistics and Outliers (`fundamentals/descriptive-statistics-and-outliers`)
- Quiz topic: `stats`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: 4b7874d15e

## Intuition

### The situation

You built a churn model using only customers active today, and it looks great. In production, it fails. A survey of a million users also reports high satisfaction, while reviews are getting worse. The interviewer asks:

> What sampling methods would you use, and how can selection or survivorship bias ruin a dataset?

#### Why it matters

Most ML failures in the real world begin here. A model learns from the data it's given, and a very large biased dataset simply gives you a confident wrong answer. See correlation vs causation for a related problem.

### The idea

Think of checking a soup. A random spoonful tells you about the whole pot, if it's stirred, and more spoonfuls make you surer. But if you only taste from the top, and the salt has sunk to the bottom, a thousand spoonfuls will still be wrong. Bias is the unstirred pot.

[Figure: Two kinds of error. Random noise shrinks as the sample grows. Bias stays the same however large the sample.]

_A bigger sample can't fix who's missing._

### Play

**Try to break it.** Raise the sample to 100,000. Then set the appearing chance to 1.

#### Sample with a rare group

Illustrative: the main group's mean is 10, and the rare group's is 30, both with a standard deviation of 5. The two noise figures are standard errors without any bias.

Raise the sample to **100,000**. Noise nearly disappears, while the biased estimate doesn't move at all. You're now very sure of a wrong answer. Set the appearing chance to **1**, and the bias is gone.

**Now say why:** why doesn't a larger sample fix the estimate?

## Maths

### Maths

#### In one breath

A sample is only useful if it represents the population you care about. **Random error** shrinks with more data, but **bias doesn't**. **Stratified sampling** guarantees rare groups are represented, and reduces noise. **Cluster sampling** saves money, at the cost of more noise. The big risk is **selection bias**: data you have because of some process that also relates to the outcome. Survivorship bias, feedback loops and non-response are all forms of it.

#### Getting a fair sample

| Method | How | Use it when | Watch out for |
|---|---|---|---|
| **Simple random** | Everyone has an equal chance. | You have a full list, and no rare groups. | Rare groups may barely appear. |
| **Stratified** | Split into groups, and sample within each. | Groups differ, or some are rare. | You need to know the groups, and reweight if you oversample. |
| **Cluster** | Pick whole groups, like cities. | Reaching individuals is costly. | People within a cluster are alike, so you get less information per person. |
| **Systematic** | Take every kth item. | Simple logging streams. | A pattern in the data can line up with k. |

##### Bias you'll meet in ML

| Bias | What happens | Example |
|---|---|---|
| **Selection** | Who's in the data depends on something related to the outcome. | A loan model only sees repayment for people who were approved. |
| **Survivorship** | You only see those who lasted. | Studying only customers who stayed, to explain why people churn. |
| **Non-response** | Those who answer differ from those who don't. | Ratings come mostly from very happy or very unhappy users. |
| **Feedback loop** | The model decides which data you collect next. | A recommender only learns about items it already shows. |
| **Time** | Your sample period isn't typical. | Training on festival-week orders. |

##### What helps

- **Ask who's missing** before looking at any results.

- **Random exploration:** serving some random choices gives unbiased data for feedback loops.

- **Reweight:** if you know how groups differ from the population, use inverse-probability weights.

- **Compare with a known total:** check your sample's mix against what you know about all users.

#### The maths

$$ {\text{Error}^2} = {\text{Bias}^2} + {\frac{\sigma^2}{n}}, \qquad {SE_{\text{strat}}} = \sqrt{\frac{\sigma_{\text{within}}^2}{n}}, \qquad {SE_{\text{random}}} = \sqrt{\frac{\sigma_{\text{within}}^2 + \sigma_{\text{between}}^2}{n}} $$

This is why a survey of a million biased responses can be worse than one of a thousand random ones.

- **total squared error**: How far your estimate tends to be from the truth.

- **the bias term**: Doesn’t depend on n. More data won’t reduce it.

- **the sampling noise**: Shrinks as n grows, and this is the only part more data can fix.

- **stratified sampling**: Removes the differences between groups from its noise, with proportional allocation.

- **simple random sampling**: Noise also includes how much the groups differ.

## In practice

### In practice

#### In practice

- **Train and serve mismatch:** if training data comes from a different source than production, measure it with drift checks.

- **Stratified splits:** with rare labels, split so each fold keeps the same share. See cross-validation.

- **Oversampling:** sampling rare classes more often for training is fine, but the model's probabilities then need correcting.

- **LLM logs:** feedback comes from people who bother to respond. Evaluate on a random sample of traffic as well.

- **Sensitive decisions:** a model trained only on past approvals may never learn about groups that were rarely approved.

### The answer that sounds right

#### "We have millions of rows, so it's representative"

It sounds right, as big samples feel safe. But size only removes random noise. If your data comes from those who stayed, or from items you already show, millions of rows give a precise picture of the wrong group. Ask who's missing, whatever the size.

## Say it

### What sampling methods would you use, and how can selection or survivorship bias ruin a dataset?

#### The interviewer pushes further

Follow-up 1 of 3

How would you check for survivorship bias?

Ask what would make something disappear from your data, and whether that's linked to what you're measuring. Then find a source that includes those who left, like sign-up logs. For a churn model, sample users as of a past date, including those who've since gone, and not just today's active users.

Follow-up 2 of 3

Stratified or cluster sampling: what's the difference?

Stratified sampling takes some from every group, so it reduces noise when groups differ. Cluster sampling takes whole groups, and skips the others, to save cost, and it increases noise, as people within a group are alike. A stratified sample covers all groups, and a cluster sample doesn't.

Follow-up 3 of 3

You have a million ratings. Why might they still be misleading?

Those who rate aren't typical, often being very happy or unhappy, and the system only shows some items. So a big sample shrinks noise, but not that bias. I'd compare against a random survey, and model who's likely to respond, or weight by exposure.

#### The 30-second answer

I'd start with who the population is, and who might be missing. Random error shrinks with more data, but bias doesn't. Simple random sampling suits most cases. Stratified sampling guarantees rare groups appear and removes between-group noise. Cluster sampling is cheaper, but noisier. The main risk is selection bias, where being in the data depends on something related to the outcome. For example, a loan model only sees outcomes for approved people. I'd use some random exploration, reweighting and checks against known totals.

**Key terms and sources**

Random, stratified and cluster sampling, how selection, survivorship and non-response bias arise, and why training data so often differs from the real world. · checked 6 Nov 2026

#### Sources

- [Diez, Çetinkaya-Rundel and Barr, OpenIntro Statistics](https://www.openintro.org/book/os/)

- [Bruce, Bruce and Gedeck, Practical Statistics for Data Scientists, contents excerpt](https://toc.uni.li/FLMF048415.pdf)

- [DataCamp statistics interview questions](https://www.datacamp.com/blog/statistics-interview-questions)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
