# Learning Curves and Debugging Models

> Your model isn't good enough. How do you decide whether to get more data, or change the model?

- Track: Fundamentals › Classical ML › Core concepts
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/fundamentals/learning-curves-and-debugging/
- Before this: The Bias–Variance Trade-off (`fundamentals/bias-variance`), Cross-Validation & Data Leakage (`fundamentals/cross-validation-and-leakage`)
- Quiz topic: `mlcore`

## Intuition

### The situation

Your model's validation error is too high. Your manager offers budget to double the labelled data. An engineer wants a much bigger model instead. Nobody has checked which problem you have. The interviewer asks:

> Your model isn't good enough. How do you decide whether to get more data, or change the model?

#### Why it matters

Teams can spend months on the wrong fix. This is a common interview question, as it shows whether you diagnose before acting. It builds on bias and variance.

### The idea

Think of a student who failed an exam. If they also fail the practice papers, more papers of the same kind won't help them. They need better teaching. If they ace the practice papers but fail the exam, they memorised answers, so they need more varied practice. Check which it is before you act.

[Figure: Three patterns. Both errors high means underfitting. A large gap means overfitting. Both near the noise floor means you may be near the limit.]

_Diagnose first, as the fixes for these are opposites._

### Play

**Try to break it.** Add rows at degree 1. Then try degree 12 with few rows.

#### Diagnose a model

Our seeded simulation: y = sin(3x) plus noise, with x between −1 and 1, fitted by least squares. Errors are mean squared errors, and the median of 15 runs. Validation uses 500 new rows. The diagnosis uses simple thresholds, as a guide.

The dashed line marks the noise floor, the vertical line marks the rows you have, and the bottom axis counts rows. Start at degree **1**, and add rows: nothing improves. Now try degree **12** with few rows: there's a large gap, which closes as rows grow. Degree **5** gets close to the floor, and no model goes reliably below it.

**Now say why:** why doesn't more data help a straight line fit a curve?

## Maths

### Maths

#### In one breath

Plot training and validation error **as data grows**. If both are high and close together, the model is too simple, and **more data won't help**. If training error is low and there's a large gap, it's overfitting, and **more data or regularisation should help**. If both level off near the noise in your labels, you may be near the limit. It saves weeks of collecting data that was never going to help.

#### Reading the curves

| What you see | Diagnosis | Helps | Doesn't help |
|---|---|---|---|
| Both errors high and close | **Underfitting** | Better features, a more flexible model, less regularisation. | More rows. |
| Training low, large gap | **Overfitting** | More rows, regularisation, simpler model, fewer features. | A more flexible model. |
| Both low and close | **Good fit** | Check slices and production behaviour. | More tuning, probably. |
| Both level off, even with flexible models | **Noise or missing information** | Cleaner labels, new information. | More tuning. |
| Good offline, poor in production | **Shift or leakage** | Check leakage and drift. | Any of the above. |

##### Why it works: a little learning theory

Training minimises the error on your sample, called **empirical risk**. What you want is low error on new data. The gap between them grows with a model's **capacity**, meaning how many patterns it could fit, and shrinks as data grows. Measures like **VC dimension** make this formal. It's why a flexible model needs more data.

##### Modern exception

Large neural networks can fit training data perfectly and still generalise, which classic capacity bounds don't explain well. So use these curves for diagnosis, rather than treating the theory as a law. See bias and variance, which covers double descent.

##### A debugging order

1. **Check the data:** read rows and labels. Check the splits, and whether any feature leaks.

2. **Set a baseline:** compare against a simple rule, or a simple model.

3. **Try to overfit a small sample:** if a flexible model can't, there's a bug, or the features carry no signal.

4. **Plot the learning curve:** decide between more data and a better model.

5. **Look at the errors:** group mistakes by segment. A few causes often explain many errors.

6. **Estimate the ceiling:** how well could an expert do? It tells you how much gain remains.

#### The maths

$$ {\text{Validation error}} \approx {\text{Training error}} + {\text{Gap}(\text{capacity},\, n)}, \qquad {\text{Error} \geq \text{noise}} $$

This is a way to think about it, not an exact equation. Formal bounds exist, and are often loose in practice.

- **what you care about**: Error on data that the model hasn’t seen.

- **what you can reduce directly**: If it’s high, the model is underfitting.

- **the gap**: It grows with capacity, and shrinks with more data.

- **the floor**: Label noise sets a limit that no model can beat on average.

## In practice

### In practice

#### In practice

- **Use sampled subsets:** train on 10%, 25%, 50% and 100% of your rows. That's cheap, and often enough to see the trend.

- **Keep validation fixed:** otherwise the curves aren't comparable.

- **Check for label noise:** have two people label the same rows. Their disagreement suggests a realistic ceiling.

- **Split time correctly:** if the data changes over time, a random split will make things look better than they are.

- **Fix one thing at a time:** keep a log, so that you know what actually helped.

### The answer that sounds right

#### "More data always helps"

It sounds right, as more data rarely hurts. But if the model is too simple, the errors are already close together, and adding rows changes almost nothing. You'd spend the budget and see no gain. A learning curve from your current data tells you this cheaply.

## Say it

### Your model isn't good enough. How do you decide whether to get more data, or change the model?

#### The interviewer pushes further

Follow-up 1 of 3

Your boss wants to double the labelled data. How do you decide?

Plot a learning curve using subsets of the current data. If validation error is still falling as rows grow, more data should help, and you can roughly extend the trend. If it's flat, spend the money on features, labels or a different approach.

Follow-up 2 of 3

Why try to overfit a small sample?

A flexible model should nearly memorise a small sample. If it can't, something's broken: mislabelled data, a bug in the pipeline, a bad learning rate, or features with no signal. It's a quick test that rules out many problems.

Follow-up 3 of 3

Training error is lower than the label noise. Is that a problem?

It means the model is fitting noise, at least partly, because noise can't really be predicted. Validation error will tell you how much it matters. Some overfitting like this can be harmless, as with some large models, so judge by validation performance.

#### The 30-second answer

I'd plot training and validation error as the data grows. If both are high and close, it's underfitting, so more rows won't help, and I'd add features or flexibility. If training is low with a large gap, it's overfitting, so more rows or regularisation should help. If both level off near the label noise, I'd improve the labels, or find new information. Before that, I'd check the data and leakage, compare with a baseline, and try overfitting a small sample to rule out bugs. Then I'd look at the errors by segment.

**Key terms and sources**

Reading train and validation curves, what capacity means, when more data helps, and a step-by-step way to debug a model. · checked 6 Nov 2026

#### Sources

- [scikit-learn on validation and learning curves](https://scikit-learn.org/stable/modules/learning_curve.html)

- [CS229 syllabus](https://cs229.stanford.edu/syllabus-summer2019.html)

- [ISLR](https://www.statlearning.com/)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
