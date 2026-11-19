# Generalised Linear Models

> How would you predict counts or insurance costs, and what do linear and logistic regression have in common?

- Track: Fundamentals › Classical ML › Linear models
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/generalised-linear-models/
- Before this: Logistic Regression (`fundamentals/logistic-regression`), Maximum Likelihood & MAP (`fundamentals/mle-and-map`)
- Quiz topic: `lin`

## Intuition

### The situation

You're predicting support calls per hour. A linear regression gives good overall error, but predicts minus two calls at quiet times. Some teams were also observed for ten days, and others for a hundred. The interviewer asks:

> How would you predict counts or insurance costs, and what do linear and logistic regression have in common?

#### Why it matters

Not everything is a number on a straight line. Calls per hour can't be negative. Costs have long tails. GLMs handle these simply, stay explainable, and are widely used in insurance and demand modelling. They also explain why logistic regression has the loss it has.

### The idea

Think of a score and a translator. The model always produces a simple linear score. The link is the translator that turns it into the right kind of answer: a probability, a positive count or any number. Change the translator, and the same machinery handles a new problem.

[Figure: One recipe, three models. Linear regression uses no link. Logistic regression uses a logit for probabilities. Poisson regression uses a log for counts.]

_All three share a linear score. They differ in the distribution and the link._

### Play

**Try to break it.** Raise the growth to 0.6. Then set it to 0.

#### Fit a line and a GLM to counts

Our seeded simulation. Counts are drawn from a Poisson distribution with a mean of exp(−1 + b × x), for x from 0 to 10. The GLM is fitted by iteratively reweighted least squares.

The orange line is least squares, and the green curve is the GLM. Set growth to **0**: both are then flat, and agree. The bigger the growth, the worse a straight line fits. Add rows, and the multiplier gets closer to the true value.

**Now say why:** why can the GLM never predict a negative count?

## Maths

### Maths

#### In one breath

A **GLM** has three parts: a distribution for the outcome, a linear score, and a **link** that connects them. Linear regression uses a normal distribution and no link. Logistic regression uses Bernoulli and the logit. **Poisson regression** uses counts and the log, so predictions can't be negative, and each coefficient multiplies the rate. The loss in each case comes from maximum likelihood.

#### One recipe, many models

| Outcome | Distribution | Link | Model | Loss |
|---|---|---|---|---|
| Any real number | Normal | Identity | Linear regression | Squared error |
| Yes or no | Bernoulli | Logit | Logistic regression | Log loss |
| Counts | Poisson | Log | Poisson regression | Poisson deviance |
| Positive, long-tailed | Gamma | Log | Gamma regression | Gamma deviance |

##### What a coefficient means with a log link

The prediction is exp(score), so a coefficient b **multiplies** the rate by eb for each unit. If b = 0.4, each unit multiplies the rate by about 1.49. It's an increase of 49%, however large the rate already is.

##### Why not fit a line to counts?

- A line can predict negative counts.

- Counts often grow by percentages, which a line can't capture.

- The spread of counts grows with their mean, so the equal-spread assumption fails.

##### Two practical details

**Exposure.** If one shop was observed for 10 days and another for 100, more counts in the second doesn't mean a higher rate. Add log(exposure) to the score with a fixed coefficient of 1. This is called an **offset**.

**Overdispersion.** Poisson assumes the variance equals the mean. Real counts often vary more, which makes standard errors too small. A quasi-Poisson or negative binomial model handles it.

##### GLM or trees?

Boosting usually predicts better when there are many interactions, and many libraries offer a Poisson objective too. A GLM is simpler and easier to explain, which matters when regulators or stakeholders ask questions.

#### The maths

$$ y \sim \text{Poisson}(\mu), \qquad \log \mu = w^\top x, \qquad \mu = \exp(w^\top x) $$

Weights are fitted by maximum likelihood, commonly using iteratively reweighted least squares. With a log link, a weight’s effect is multiplicative.

- **the distribution**: What kind of outcome this is. Here, counts.

- **the link**: Connects the mean of the outcome to the score.

- **the linear score**: Features and weights, as in linear regression.

- **the prediction**: The inverse of the link. An exponential is always positive.

## In practice

### In practice

#### In practice

- **Match the outcome:** counts suit Poisson, and positive long-tailed amounts suit Gamma.

- **Handle exposure:** use an offset whenever observation time or population differs.

- **Check dispersion:** compare the variance with the mean. If it's much bigger, consider negative binomial.

- **Watch for excess zeros:** many more zeros than Poisson expects can mean two processes, such as "never buys" and "buys sometimes".

- **Evaluate with the right metric:** squared error can mislead for counts, so check deviance too.

### The answer that sounds right

#### "For counts, just take the log of y and use linear regression"

It sounds right, as it's simple, and it often looks fine. But log(0) is undefined, and counts often include zeros. It also models the mean of the log, rather than the log of the mean, so converting back gives biased predictions. A Poisson GLM avoids both problems.

## Say it

### How would you predict counts or insurance costs, and what do linear and logistic regression have in common?

#### The interviewer pushes further

Follow-up 1 of 3

What's the difference between a GLM and a linear regression on log(y)?

Log(y) models the mean of the log, while a GLM models the log of the mean. These aren't the same. Log(y) also fails when y is zero, which is common in counts. A Poisson GLM handles zeros naturally.

Follow-up 2 of 3

Your Poisson model's coefficient for a promotion is 0.3. What does that mean?

With a log link, the promotion multiplies the expected count by e^0.3, about 1.35, holding other features fixed. That's roughly a 35% rise, whatever the starting rate. It's an association unless the promotion was randomised.

Follow-up 3 of 3

How do you handle different observation periods?

Add log(exposure) as an offset, with its coefficient fixed at 1. The model then predicts a rate per unit of exposure. Without it, shops observed for longer would simply look busier.

A GLM has three parts: a distribution for the outcome, a linear score, and a link between them. Linear regression is normal with an identity link, and logistic regression is Bernoulli with a logit. For counts, I'd use Poisson with a log link: predictions stay positive, and each coefficient multiplies the rate by e to the b. I'd add log exposure as an offset if observation time differs, and check for overdispersion, which makes standard errors too small. If there is, I'd use negative binomial.

**Key terms and sources**

One framework for linear, logistic and Poisson regression: a distribution, a link and a linear score, plus exposure and overdispersion.

#### Sources

- ISLR, including Poisson regression

- scikit-learn on generalized linear models

- CS229 syllabus

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
