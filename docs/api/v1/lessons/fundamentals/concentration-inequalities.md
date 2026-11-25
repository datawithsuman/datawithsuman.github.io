# Concentration Inequalities

> What do Markov, Chebyshev and Hoeffding inequalities tell you, and how many test samples do you need?

- Track: Fundamentals › Maths for ML › Probability
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/concentration-inequalities/
- Before this: Law of Large Numbers and Central Limit Theorem (`fundamentals/law-of-large-numbers-and-clt`)
- Quiz topic: `prob`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: 52789210a3

## Intuition

### The situation

Your model scored 92% on a test set of 500 examples. A manager asks how sure you are, and how big the test set should be to get within ±2%. A teammate has tried 50 models on that same test set. The interviewer asks:

> What do Markov, Chebyshev and Hoeffding inequalities tell you, and how many test samples do you need?

#### Why it matters

Why should your test accuracy reflect real accuracy? These results are the formal answer. They're also behind generalisation bounds and bandit algorithms like UCB. They build on the central limit theorem.

### The idea

Think of insuring against the worst case. Knowing only the average, you can rule out a little. Knowing how spread out things are, you can rule out more. Knowing values can't go beyond fixed limits, you can rule out nearly everything far from the average, once you have enough samples.

[Figure: Three inequalities. Markov uses only the mean. Chebyshev adds the variance. Hoeffding uses bounded independent values, and it falls exponentially with n.]

_More assumptions give tighter bounds._

### Play

**Try to break it.** Compare the bounds at n = 100, then at n = 1,000. Then shrink ε.

#### Compare the bounds

The chance a fair coin's sample average is at least ε from 0.5. Chebyshev uses σ² = 0.25. These are upper limits, and bounds above 100% are shown as 100%, as they tell you nothing.

At **n = 100**, Chebyshev is slightly tighter than Hoeffding. Raise n to **1,000**: Hoeffding falls well below Chebyshev. Exponential decay beats 1/n in the end, which is why it dominates theory.

**Now say why:** why does Hoeffding eventually beat Chebyshev?

## Maths

### Maths

#### In one breath

The central limit theorem is an approximation. **Concentration inequalities** give guarantees that hold for any sample size, using very little information. **Markov** uses only the mean. **Chebyshev** adds the variance. **Hoeffding** uses a bounded range, and its bound shrinks **exponentially** with the sample size. More assumptions give tighter bounds. They answer practical questions, like how large a test set needs to be, and they underlie generalisation theory.

#### More information, tighter bound

| Inequality | Needs | Says | How it shrinks |
|---|---|---|---|
| **Markov** | X ≥ 0, and its mean | P(X ≥ a) ≤ E[X] / a | Slowly, with a |
| **Chebyshev** | Mean and variance | P(\|X − μ\| ≥ kσ) ≤ 1/k² | As 1/k² |
| **Hoeffding** | Independent values, bounded in [0, 1] | P(\|X̄ − μ\| ≥ ε) ≤ 2e^(−2nε²) | Exponentially in n |

##### Reading them

- **Markov:** if average order value is ₹500, at most 10% of orders can reach ₹5,000. Otherwise, the average would be higher.

- **Chebyshev:** any distribution with finite variance has at most 1/9 of its values beyond 3σ. The real share for a Normal is far smaller.

- **Hoeffding:** for accuracy on n test examples, a value bounded between 0 and 1, it bounds how far the measured value can be from the true one.

##### How large must a test set be?

Set Hoeffding's bound to a failure chance δ, and solve: **n ≥ ln(2/δ) / (2ε²)**. To measure accuracy within ±2% with 95% confidence, n ≥ ln(40) ÷ (2 × 0.0004), or about 4,600 examples. It's valid regardless of the true accuracy, and a little conservative.

##### Why the test set must stay untouched

The bound holds for one fixed model. If you try many models on the same test set, and keep the best, you've had many chances for a lucky result. Accounting for k models means replacing δ with δ/k, which adds ln(k) to the sample needed. Heavy reuse makes test scores optimistic, which is why a separate validation set exists.

#### The maths

$$ {P(X \ge a) \le \frac{\mathbb{E}[X]}{a}}, \qquad {P(|\bar X - \mu| \ge \varepsilon) \le \frac{\sigma^2}{n\varepsilon^2}}, \qquad {P(|\bar X - \mu| \ge \varepsilon) \le 2e^{-2n\varepsilon^2}} $$

They’re upper bounds, so the real chance is usually far smaller. Their strength is that they hold for finite n, with few assumptions.

- **Markov**: Only needs a non-negative variable and its mean. It’s loose, and it’s the foundation of the others.

- **Chebyshev**: Adds the variance. It applies to averages too, as the variance of an average is σ²/n.

- **Hoeffding**: For independent values in [0, 1]. It falls exponentially with n, which is much faster.

## In practice

### In practice

#### In practice

- **Use the Normal approximation for daily work:** intervals from the central limit theorem are tighter, and usually fine. Use these bounds when you need a guarantee, or in theory.

- **Check independence:** Hoeffding assumes independent samples. Duplicate or near-duplicate test examples mean you have less evidence than you think.

- **Slices are smaller:** a test set of 10,000 might have just 200 in a small group. So error bars on slices are far wider.

- **Bandits:** UCB adds a Hoeffding-style bonus for uncertainty, so rarely tried options get explored.

### The answer that sounds right

#### "It scored 92%, so its true accuracy is 92%"

It sounds right, as that's what you measured. But 92% is an estimate from one sample. With 500 examples, the error bar is around ±2.4% by the Normal approximation. And if you picked the best of 50 models on that set, the score is probably inflated too.

## Say it

### What do Markov, Chebyshev and Hoeffding inequalities tell you, and how many test samples do you need?

#### The interviewer pushes further

Follow-up 1 of 3

How large a test set do you need to measure accuracy within ±1% with 95% confidence?

By Hoeffding, n ≥ ln(40) ÷ (2 × 0.0001), which is about 18,445. It's conservative, as the Normal approximation gives about 9,600 in the worst case of 50% accuracy, and fewer when accuracy is high.

Follow-up 2 of 3

Why would you use Hoeffding if the central limit theorem gives tighter answers?

The central limit theorem is only an approximation for large n, with no direct guarantee at a given size. Hoeffding holds for every n, for any bounded distribution. That makes it the right tool for proofs, and for algorithms that need a guaranteed bound, like UCB.

Follow-up 3 of 3

Why does reusing the test set inflate performance?

You're selecting the model that did best on those particular examples, which picks up some luck. With more comparisons, the best score is more likely to be inflated. This adaptive reuse breaks the assumption of a fixed model, so keep a final test set you use only once.

#### The 30-second answer

These give guarantees on how far a value can stray from its mean, using little information. Markov needs only a non-negative variable and its mean. Chebyshev adds the variance, with a bound of one over k squared. Hoeffding needs independent, bounded values, and its bound falls exponentially with n. That gives a test-set size: n at least log of 2 over delta, divided by 2 epsilon squared. For plus or minus 2% at 95% confidence, it's about 4,600. If you reuse a test set across many models, the guarantee weakens.

**Key terms and sources**

Guarantees on how far an average can stray: Markov, Chebyshev and Hoeffding, how they compare, and what they say about test-set size and generalisation. · checked 6 Nov 2026

#### Sources

- [Blitzstein and Hwang, Introduction to Probability](https://www.oreilly.com/library/view/-/9781466575578/)

- [Murphy, Probabilistic Machine Learning: An Introduction](https://probml.github.io/pml-book/book1.html)

- Train, test and cross-validation on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
