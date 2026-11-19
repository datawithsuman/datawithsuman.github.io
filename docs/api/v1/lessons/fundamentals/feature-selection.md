# Feature Selection

> How do you choose which features to keep, and how can selecting features leak information?

- Track: Fundamentals › Classical ML › Data and features
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/feature-selection/
- Before this: Feature Engineering (`fundamentals/feature-engineering`), Cross-Validation & Data Leakage (`fundamentals/cross-validation-and-leakage`)
- Quiz topic: `feat`

## Intuition

### The situation

A colleague has 1,000 candidate features and 50 rows. They pick the 10 most correlated with the label, then cross-validate, and report 90% accuracy. You rerun it with shuffled labels, and it still scores far above 50%. The interviewer asks:

> How do you choose which features to keep, and how can selecting features leak information?

#### Why it matters

This error is easy to make and it produces beautiful results that vanish in production. In production, each feature also has a cost to compute and monitor. This builds on cross-validation.

### The idea

Think of picking the best stock pickers from 1,000 people after the year is over, then saying they beat the market that year. Of course they did: that's how you picked them. To test them fairly, you must choose first, then watch next year.

[Figure: Three families. Filters score features one by one. Wrappers try subsets with the model. Embedded methods select during training.]

_Whichever you use, selection must happen inside each fold._

### Play

**Try to break it.** Raise the noise features to 3,000. Then keep fewer of them.

#### Select from pure noise

Our seeded simulation, averaged over 8 runs. All features are random, and so are the labels. It uses 5-fold cross-validation, and a nearest-centroid classifier on the features with the largest correlation with the label.

Raise the noise features: the wrong method looks better and better, with no signal at all. The right method stays near the true **50%**. It's often slightly below, as holding out a fold tips the class balance a little against it. If your results depend on which way you do it, the higher number is the false one.

**Now say why:** why can a model look good when there's no signal at all?

## Maths

### Maths

#### In one breath

Fewer features can mean a simpler, cheaper and sometimes better model. **Filter** methods score features one at a time. **Wrapper** methods try subsets with the model. **Embedded** methods select during training, as Lasso does. The classic trap is **choosing features using all the data, and then cross-validating**: with enough noise features, you can score far above chance on pure randomness. Selection must happen inside each fold.

#### Three families

| Family | Examples | Good | Weak |
|---|---|---|---|
| **Filter** | Correlation, chi-squared, mutual information | Fast, and independent of the model. | Looks at one feature at a time, so it misses interactions and redundancy. |
| **Wrapper** | Forward selection, recursive elimination | Uses the actual model, and catches interactions. | Slow, and easy to overfit. |
| **Embedded** | Lasso, tree importance | Happens during training. | Tied to that model, and unstable with correlated features. |

##### The leak

1. Take thousands of features that are pure noise.

2. Pick those most correlated with the label, using all the rows. By chance, some look strong.

3. Cross-validate on just those. They look predictive, because they were chosen using the same labels you're now testing on.

The fix is simple: make selection a **step inside the fold**, computed only from training rows. A pipeline makes this automatic. Hastie, Tibshirani and Friedman call this the wrong and the right way to do cross-validation.

##### Do you need selection at all?

- **For accuracy:** regularised models and boosting often cope well with extra features, so selection may add little.

- **For cost and simplicity:** this is often the real reason. Fewer features means less to compute, monitor and explain.

- **For stability:** a feature that drifts or breaks is a risk. Removing fragile ones can make a model safer.

##### Correlated features

If two features carry the same signal, either can be dropped, and which one is chosen can change between runs. So a removed feature isn't necessarily useless. It may only be redundant.

#### The maths

$$ \min_w \|Xw - y\|^2 + \lambda \|w\|_1, \qquad \text{Gain}(j \mid S) = \text{score}(S \cup \{j\}) - \text{score}(S) $$

Whichever method you use, keep a test set out of it, or run the whole selection inside each fold.

- **Lasso**: An embedded method. The L1 penalty pushes some weights to exactly zero.

- **forward selection’s gain**: How much a feature adds, given those already chosen.

- **score with the feature**: Must be measured on validation data.

- **score without it**: Stop when added features no longer help.

## In practice

### In practice

#### In practice

- **Use a pipeline:** put selection inside it, so cross-validation refits it on each fold.

- **Start by removing the obvious:** constant columns, near duplicates, IDs and anything unavailable at serving time.

- **Group features:** judge related features together, by source or cost. Dropping a whole source saves more than dropping one column.

- **Check it holds up:** if the chosen set changes a lot across folds or time, the selection isn't reliable.

- **Be careful with importance:** correlated features can hide each other, so test by removing and retraining.

### The answer that sounds right

#### "We selected features first, so the model is simpler and the score is fair"

It sounds right, as cross-validation came afterwards. But the test folds' labels already helped choose the features, so those rows were never unseen. With enough features, this produces high scores from pure noise. Put selection inside the pipeline, so it's refit in every fold.

## Say it

### How do you choose which features to keep, and how can selecting features leak information?

#### The interviewer pushes further

Follow-up 1 of 3

Why does selecting before cross-validation give optimistic scores?

The labels of future test folds influenced which features were chosen. With many features, some correlate with those labels by chance. So test rows aren't really unseen. With random labels and many features, you can get scores far above chance. Selecting inside each fold fixes it.

Follow-up 2 of 3

Would you remove a feature with a low importance score?

Not without testing. It may be correlated with another feature, hiding its value, or matter only for some groups. I'd remove it, retrain and compare on validation data, and also weigh the cost of computing and maintaining it.

Follow-up 3 of 3

Filter methods missed a useful pair of features. How?

They score features one at a time. With an XOR-style pattern, each is useless alone, and together they predict perfectly. Trees and wrapper methods can find that pair, since they evaluate features in combination.

There are three families. Filter methods score each feature alone, which is fast, but misses interactions and redundancy. Wrapper methods try subsets with the model, which is slow and can overfit. Embedded methods like Lasso select during training. The main trap is selecting with all the data, then cross-validating: with many noise features, you can score far above chance on random labels. So I'd make selection a step inside each fold. Accuracy often isn't the main reason to select. Cost and reliability often are.

**Key terms and sources**

Filter, wrapper and embedded methods, why selection can leak into your evaluation, and when you shouldn't bother.

#### Sources

- Hastie, Tibshirani and Friedman, The Elements of Statistical Learning

- scikit-learn on feature selection

- ISLR

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
