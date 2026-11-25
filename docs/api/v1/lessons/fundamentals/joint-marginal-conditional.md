# Joint, Marginal and Conditional Distributions

> What's the difference between joint, marginal and conditional distributions, and what is conditional independence?

- Track: Fundamentals › Maths for ML › Probability
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/joint-marginal-conditional/
- Before this: Probability Basics & Bayes' Rule (`fundamentals/probability-and-bayes`)
- Related: Naive Bayes (`fundamentals/naive-bayes`)
- Quiz topic: `prob`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: fab2fc286f

## Intuition

### The situation

You have delivery logs with weather and whether each order was late. A colleague finds that late orders cluster on the same days, and treats them as independent evidence anyway. A Naive Bayes model built on them is very overconfident. The interviewer asks:

> What's the difference between joint, marginal and conditional distributions, and what is conditional independence?

#### Why it matters

Real models have many variables at once. These three views, plus the sum and product rules, sit behind almost every probabilistic model. This follows probability and Bayes' rule.

### The idea

Think of a spreadsheet of counts, with weather across the top and on-time or late down the side. The inner cells are the joint. The totals in the margins are, literally, the marginals. Looking at one row alone, then rescaling it, gives a conditional.

[Figure: Three views. The joint gives each combination. The marginal sums out a variable. The conditional takes a slice and rescales it.]

_Three views of one table._

### Play

**Try to break it.** Set both late chances to 0.40. Then pull them apart.

#### Build a joint table

Illustrative. Assumes two orders are independent given the weather, so P(both late) = P(rain)P(late | rain)² + P(dry)P(late | dry)².

Set both late chances to **0.40**. The last two cards now match, as the weather no longer links the orders. Move them apart, and the gap between those cards grows, even though each order is independent once you know the weather.

**Now say why:** why can two orders be linked overall, yet independent once you know the weather?

## Maths

### Maths

#### In one breath

The **joint** distribution gives the chance of every combination of values. Add across a variable to remove it, and you get a **marginal**. Fix a variable, and rescale, and you get a **conditional**. Two things can look linked yet be **independent once you know a third**: late orders are linked to each other through rain, but given the weather, they're not. That's **conditional independence**, the assumption that makes models like Naive Bayes workable.

#### Three views of one table

Say a delivery can be on time or late, on a rainy or a dry day. Illustrative numbers:

| | Late | On time | Marginal for weather |
|---|---|---|---|
| **Rain** | 0.18 | 0.12 | 0.30 |
| **Dry** | 0.14 | 0.56 | 0.70 |
| **Marginal for delivery** | 0.32 | 0.68 | 1.00 |

- **Joint:** the inner cells. P(rain, late) = 0.18.

- **Marginal:** the totals. P(late) = 0.18 + 0.14 = 0.32. Adding across a variable is the **sum rule**.

- **Conditional:** one row or column, rescaled. P(late | rain) = 0.18 ÷ 0.30 = 0.6.

The **product rule** rebuilds the joint: P(rain, late) = P(rain) × P(late | rain). Bayes' rule is just this written two ways.

##### Independent, or conditionally independent?

- **Independent:** knowing one tells you nothing about the other. P(A, B) = P(A)P(B).

- **Conditionally independent:** once you know C, A tells you nothing more about B. P(A, B | C) = P(A | C)P(B | C).

Neither implies the other. Two orders can both be late because of rain, so they're linked overall, yet independent given the weather. The opposite also happens: two unrelated causes of a late order become linked once you know that it was late, because ruling out one makes the other more likely.

##### Why this matters at scale

A full joint over 30 yes-or-no variables needs over a billion numbers. Assuming features are conditionally independent given the class cuts this to 30 per class, plus the class probabilities. That's the "naive" part of Naive Bayes.

#### The maths

$$ {p(x)} = \sum_y {p(x, y)}, \qquad {p(y \mid x)} = \frac{p(x, y)}{p(x)}, \qquad {p(x, y \mid z) = p(x \mid z)\,p(y \mid z)} $$

These three rules, sum, product and Bayes, handle nearly every manipulation in probabilistic ML.

- **the marginal**: Sum the joint over the variable you don’t care about. For continuous variables, it’s an integral.

- **the joint**: The chance of each combination.

- **the conditional**: Take the matching slice of the joint, and rescale it to add up to 1.

- **conditional independence**: Given z, the joint of x and y splits into separate pieces.

## In practice

### In practice

#### In practice

- **Hidden variables:** marginalising a hidden variable is what mixture models and VAEs do, and it's usually where the hard integral comes from.

- **Simpson's paradox:** a trend in each group can reverse in the marginal, because combining groups hides a third variable.

- **Feature leakage:** a feature may predict the label only through another variable. Conditional independence is how you reason about what a feature really adds.

- **Correlated features:** Naive Bayes counts correlated features as separate evidence, so its probabilities can be overconfident, even if the ranking is fine.

### The answer that sounds right

#### "They're independent given the weather, so they're independent"

It sounds right, but it's a different claim. Two late orders are independent given the weather, yet overall they're linked: seeing one late order makes rain more likely, which makes the other more likely. The reverse also happens: independent causes become linked once you know their shared effect.

## Say it

### What's the difference between joint, marginal and conditional distributions, and what is conditional independence?

#### The interviewer pushes further

Follow-up 1 of 3

Does independence imply conditional independence?

No. Two independent causes can become dependent once you condition on a shared effect. A late order could come from traffic or a busy kitchen, which are unrelated. But if you know it's late and there was no traffic, a busy kitchen becomes more likely. This is called explaining away.

Follow-up 2 of 3

How many numbers does a full joint over 30 binary variables need?

2³⁰ − 1, over a billion, since the probabilities must add up to 1. With Naive Bayes and two classes, you need one per feature per class plus the class prior: 61. That's why conditional independence assumptions are so useful.

Follow-up 3 of 3

Why does Naive Bayes work well even though its assumption is wrong?

Classification only needs the right class to score highest, not accurate probabilities. Errors in the probability estimates may not change the ranking. So it can classify well while being badly overconfident, and that's why you'd calibrate it if you need real probabilities.

#### The 30-second answer

The joint gives the chance of each combination. Summing over a variable gives a marginal, and fixing one and rescaling gives a conditional. Those are the sum and product rules, and Bayes' rule follows from them. Conditional independence means that once you know z, x tells you nothing more about y. It's different from plain independence: two late orders are linked through rain, but independent given the weather. It matters because a full joint grows exponentially, and assuming conditional independence, as in Naive Bayes, makes it workable.

**Key terms and sources**

How to describe several random variables together, how to move between joint, marginal and conditional distributions, and why conditional independence powers Naive Bayes. · checked 6 Nov 2026

#### Sources

- [Deisenroth, Faisal and Ong, Mathematics for Machine Learning](https://mml-book.github.io/)

- [Murphy, Probabilistic Machine Learning: An Introduction](https://probml.github.io/pml-book/book1.html)

- [Blitzstein and Hwang, Introduction to Probability](https://www.oreilly.com/library/view/-/9781466575578/)

- Naive Bayes on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
