# Ensembles: Voting, Stacking and Bagging vs Boosting

> Why does combining models help, when does it stop helping, and how would you build a stack?

- Track: Fundamentals › Classical ML › Tree-based models
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/ensembles-voting-and-stacking/
- Before this: Random Forest (`fundamentals/random-forest`), Gradient Boosting (`fundamentals/gradient-boosting`), Cross-Validation & Data Leakage (`fundamentals/cross-validation-and-leakage`)
- Quiz topic: `trees`

## Intuition

### The situation

Your team has a boosting model, a forest and a logistic regression, each with similar scores. Someone suggests averaging them. Someone else wants a stack, and has trained the final model on each model's training predictions. It's giving all its weight to the most overfit one. The interviewer asks:

> Why does combining models help, when does it stop helping, and how would you build a stack?

#### Why it matters

Interviewers ask this to see if you understand why random forests and boosting work. Ensembles also do well in practice, though each extra model adds cost and complexity.

### The idea

Think of asking several people to guess the number of sweets in a jar. Their errors partly cancel, so the average beats most guesses. But if they all copied one person, you'd really only have one guess. Independence is what makes a crowd useful.

[Figure: Three ways to combine. Bagging trains in parallel and lowers variance. Boosting trains in sequence and lowers bias. Stacking learns how to combine predictions.]

_Models must beat chance, and make different mistakes._

### Play

**Try to break it.** Set accuracy to 0.4. Then raise sharing to 0.5, with 25 models.

#### Majority vote

Illustrative, exact calculation. Two classes, and each model is right with this probability. Otherwise, models are independent. The sharing slider is a simple way to model correlated mistakes.

Set accuracy to **0.4**: more models make things worse, as the majority is now reliably wrong. Back at 0.7, raise sharing to **0.5** with 25 models: the vote gets stuck near 84%, and more models barely help. Variety matters as much as count.

**Now say why:** why do more models stop helping when they share mistakes?

## Maths

### Maths

#### In one breath

Combining models helps when they're **better than chance and make different mistakes**. **Bagging** averages models trained on resampled data, which lowers variance. **Boosting** trains models in sequence on earlier errors, which lowers bias. **Voting** combines finished models directly. **Stacking** trains a small model on their predictions, and those must be **out-of-fold**, or it will simply trust whichever base model overfit most.

#### Four ways to combine

| Method | How it trains | Mainly lowers | Example |
|---|---|---|---|
| **Voting or averaging** | Finished models combined directly. | Variance | Average three different models. |
| **Bagging** | In parallel, each on a resampled dataset. | Variance | Random forest. |
| **Boosting** | In sequence, each fixing earlier errors. | Bias, then variance | Gradient boosting. |
| **Stacking** | A small model learns from others' predictions. | Both, sometimes | Logistic regression over a forest and boosting. |

##### Why they must differ

Copies of the same model add nothing, as they all make the same mistakes. Variety can come from different data, features, seeds or model types. Random forests pick random features at each split for exactly this reason.

##### Hard and soft voting

- **Hard voting:** take the most common class.

- **Soft voting:** average predicted probabilities. It keeps information about confidence, so it often works better, but it needs reasonably calibrated models.

##### Stacking without leakage

1. Split the training data into folds.

2. For each fold, train every base model on the other folds, and predict this one.

3. These **out-of-fold predictions** become the inputs of the final model, usually a simple one.

4. Retrain the base models on all the training data, to use in production.

If you use in-sample predictions instead, the final model sees the base models at their most flattering, and trusts the most overfit.

##### When not to bother

Each model must be trained, served, monitored and explained. A stack of 20 that gains very little is often a poor trade in production, particularly with tight latency budgets.

#### The maths

$$ {\mathrm{Var}(\bar f)} = {\rho\,\sigma^2} + {\frac{1 - \rho}{N}\,\sigma^2}, \qquad {\hat y = g\big(f_1^{\text{oof}}(x), \dots, f_N^{\text{oof}}(x)\big)} $$

The variance formula is for N identically distributed models with pairwise correlation ρ, as in Hastie, Tibshirani and Friedman’s explanation of random forests.

- **variance of the average**: How much the combined prediction wobbles.

- **the part that stays**: With correlation ρ between models, adding models can’t remove this.

- **the part that shrinks**: More models reduce this towards zero.

- **a stack**: The final model g learns from out-of-fold predictions.

## In practice

### In practice

#### In practice

- **Start with one strong model:** on tabular data, a tuned gradient boosting model is often hard to beat by much.

- **Pick different kinds:** a linear model with trees usually adds more than two similar boosting models.

- **Check how correlated they are:** if their errors nearly match, combining won't help.

- **Keep the final model simple:** a regularised linear model is the usual choice, as it's less likely to overfit.

- **Weigh the gain against the cost:** serving several models adds latency, and more can break.

Comparing XGBoost, LightGBM and CatBoost? See Gradient Boosting, which also covers bagging against boosting.

### The answer that sounds right

#### "More models always make it better"

It sounds right, as averaging reduces noise. But if models share their mistakes, adding more barely helps, and if they're worse than chance, a majority vote makes things worse. Add models only if they're different enough to matter, and worth the extra cost in production.

## Say it

### Why does combining models help, when does it stop helping, and how would you build a stack?

#### The interviewer pushes further

Follow-up 1 of 3

Why must stacking use out-of-fold predictions?

In-sample predictions look best for the most overfit model, so the final model would rely on it, and fail on new data. Out-of-fold predictions show how each base model does on rows it didn't train on, which is what happens in production.

Follow-up 2 of 3

If each model is 45% accurate, should you ensemble them?

Not by majority vote: with independent models, the majority gets reliably worse as you add more. In a two-class problem, you'd be better off flipping their answers. It's the same maths that makes a vote helpful above 50%.

Follow-up 3 of 3

Why doesn't adding more trees to a random forest overfit, while boosting can?

A forest averages, so more trees only reduce the variance, down to the limit set by correlation. Boosting keeps fitting the remaining errors, so eventually it fits noise. That's why boosting needs a learning rate and early stopping.

#### The 30-second answer

Ensembles help when models beat chance and make different mistakes. The variance of an average has a part that shrinks with more models and a part set by their correlation, so variety matters. Bagging trains in parallel on resampled data, which lowers variance. Boosting trains in sequence on earlier errors, which lowers bias first. Stacking trains a small model on the base models' predictions, and these must be out-of-fold, or it trusts the most overfit one. In production, I'd weigh any gain against the extra cost.

**Key terms and sources**

Why many models beat one, why they must differ, how voting, bagging, boosting and stacking compare, and how to avoid leakage in a stack. · checked 6 Nov 2026

#### Sources

- [scikit-learn on ensembles, voting and stacking](https://scikit-learn.org/stable/modules/ensemble.html)

- [Hastie, Tibshirani and Friedman, The Elements of Statistical Learning](https://hastie.su.domains/ElemStatLearn/)

- [ISLR](https://www.statlearning.com/)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
