# Bayesian vs Frequentist

> What's the difference between Bayesian and frequentist statistics, and when would you use each?

- Track: Fundamentals › Maths for ML › Statistics
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/bayesian-vs-frequentist/
- Before this: Hypothesis Tests, p-values & A/B Testing (`fundamentals/hypothesis-testing-and-ab-tests`), Bayesian Inference and Conjugate Priors (`fundamentals/bayesian-inference-and-conjugate-priors`)
- Quiz topic: `stats`

## Intuition

### The situation

An A/B test gives a two-sided p-value of 0.08, and a product manager asks: "So what's the chance B is better?" Another colleague says Bayesian tests solve peeking. The interviewer asks:

> What's the difference between Bayesian and frequentist statistics, and when would you use each?

#### Why it matters

This comes up in interviews, and in real decisions about A/B tests. Knowing what each number really means prevents the most common misreadings. See hypothesis tests and Bayesian inference.

### The idea

Think of a weather forecast of 70% rain. A frequentist reading: of days like this, it rains on 70%. A Bayesian reading: given what we know, we're 70% sure it'll rain today. They're different meanings of the same word, and for everyday decisions, they often lead you to the same umbrella.

[Figure: Two questions. Frequentist asks how surprising the data is if there's no effect. Bayesian asks how likely an effect is given the data.]

_They condition in opposite directions._

### Play

**Try to break it.** Raise the prior to 2,000 pretend users. Then raise the users to 10,000.

#### Read one A/B test both ways

Illustrative. Rates are shown as percentages. The prior is the same Beta for both groups, with mean 10%. The chance is computed numerically on a grid, and the p-value uses a pooled two-proportion z-test.

With a weak prior, the chance B beats A is close to 1 minus the one-sided p-value, so they tell a similar story. Now raise the prior to **2,000 pretend users**: it strongly says both are near 10%, so the chance falls. Then raise the users, and the data takes over again.

**Now say why:** why does a strong prior lower the chance that B wins?

## Maths

### Maths

#### In one breath

**Frequentists** treat the true value as fixed, and ask how a procedure behaves across repeated samples. **Bayesians** treat what we don't know as a distribution, and update it with data. So a frequentist reports "p = 0.04", and a Bayesian reports "a 96% chance B is better". With lots of data and weak priors, the numbers often come out close. They differ most with **little data**, or strong prior knowledge. It's a practical choice, not a matter of which is right.

#### Same data, two questions

| | Frequentist | Bayesian |
|---|---|---|
| **Probability means** | Long-run frequency over repeats. | Degree of belief, given what you know. |
| **The unknown value** | Fixed, and not a random thing. | Has a distribution. |
| **Answers** | How surprising is this data, if there's no effect? | How likely is an effect, given this data? |
| **Uses** | p-values and confidence intervals. | Priors, posteriors and credible intervals. |
| **Needs** | A fixed plan: sample size, stopping rule. | A prior, stated openly. |
| **Main risk** | Misreading p-values, and peeking. | A poor prior, and hard computation. |

##### What each number really says

- **p = 0.04:** if there were no effect, a result this extreme would occur 4% of the time. It's not a 4% chance of no effect.

- **95% confidence interval:** this procedure captures the true value in 95% of repeated samples.

- **P(B beats A) = 96%:** given this data and prior, there's a 96% chance B is better. It's what most people want, and it depends on the prior.

##### Does peeking stop mattering for Bayesians?

You'll often hear this, and it's only partly true. The posterior remains valid if your prior is right, but if you stop whenever it looks good, you'll still get more false wins in the frequentist sense. It also doesn't protect against a poor prior. Plan your stopping rules either way.

##### How to choose

- **Frequentist:** a standard for many teams, with clear error control and no prior to agree on, and it scales easily.

- **Bayesian:** useful with little data, when you've strong prior knowledge, or when you want direct statements for decisions, like expected loss.

With plenty of data and weak priors, they often agree closely, so team habits and tools can be a sensible reason to choose.

#### The maths

$$ {p = P(\text{data this extreme} \mid H_0)}, \qquad {P(B > A \mid \text{data}) = \iint_{\theta_B > \theta_A} p(\theta_A, \theta_B \mid \text{data})\, d\theta_A\, d\theta_B} $$

They’re conditioned opposite ways round, and confusing them is the most common error in statistics.

- **the frequentist question**: A chance of the data, assuming no effect. It’s not the chance that there’s no effect.

- **the Bayesian question**: A chance of the hypothesis, given the data. It needs a prior, and it’s found by integrating over the posterior.

## In practice

### In practice

#### In practice

- **Choose the prior from history:** past experiments' effect sizes give a sensible prior, and show how big changes usually are.

- **Report both when it helps:** an interval and a decision-focused chance can sit side by side.

- **Expected loss:** Bayesian tests can answer "how much do I lose if I ship B and I'm wrong?", which suits business decisions.

- **Don't call it "no peeking needed":** whichever you choose, agree stopping rules before you start.

- **ML already mixes both:** L2 regularisation is a Gaussian prior, and cross-validation is frequentist in spirit.

### The answer that sounds right

#### "p = 0.04 means a 96% chance that B is better"

It sounds right, and it's what people want it to mean. But a p-value assumes no effect, and tells you how surprising the data is. It says nothing directly about the chance B is better. For that you need a prior. They're sometimes numerically close, when priors are weak, but they mean different things.

## Say it

### What's the difference between Bayesian and frequentist statistics, and when would you use each?

#### The interviewer pushes further

Follow-up 1 of 3

What does a p-value of 0.04 mean?

If there were truly no effect, a result at least this extreme would occur 4% of the time. It's not a 4% chance that the null is true, nor a 96% chance your idea works. For those, you'd need a prior, and that's a Bayesian question.

Follow-up 2 of 3

Is a Bayesian A/B test immune to peeking?

Not in a practical sense. If you stop as soon as the chance of winning passes a threshold, you'll ship more false wins than that threshold suggests, particularly with a weak or poor prior. So agree on a stopping rule, and don't treat Bayesian as a free pass.

Follow-up 3 of 3

When do the two approaches disagree most?

With little data, a strong prior or stopping rules that matter to one and not the other. For example, a rate from a handful of users gets pulled towards the prior under Bayesian methods, and with sensible priors, this is often more accurate than taking the raw rate at face value.

#### The 30-second answer

Frequentists treat the true value as fixed, and ask how often a procedure would produce a result like this across repeated samples, so p-values are about the data, assuming no effect. Bayesians treat the unknown as a distribution, update it with data and report things like the chance that B beats A, using a prior. With lots of data and weak priors, they tend to agree. They differ most with little data or strong priors. I'd use frequentist tests as a clear default, and Bayesian when data is scarce, or decisions need direct probabilities.

**Key terms and sources**

What each school means by probability, how they answer the same A/B test, when they agree and when they differ, and how to choose. · checked 6 Nov 2026

#### Sources

- [TensorTonic maths topics](https://www.tensortonic.com/ml-math)

- [Wasserman, All of Statistics](https://www.stat.cmu.edu/~larry/all-of-statistics/)

- Bayesian inference on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
