# Discriminant Analysis: LDA and QDA

> How do LDA and QDA classify, and when would you choose them over logistic regression or naive Bayes?

- Track: Fundamentals › Classical ML › Other classic classifiers
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/discriminant-analysis/
- Before this: Naive Bayes (`fundamentals/naive-bayes`), Logistic Regression (`fundamentals/logistic-regression`)
- Quiz topic: `clf`

## Intuition

### The situation

You have a small dataset with a few numeric features and three classes. Logistic regression's weights jump between samples, as the classes are well separated. A colleague suggests a model that describes each class as a bell curve instead. The interviewer asks:

> How do LDA and QDA classify, and when would you choose them over logistic regression or naive Bayes?

#### Why it matters

These are simple, fast baselines, and they show how generative classifiers work. Interviewers also like the comparison with logistic regression and naive Bayes. One warning: LDA can also mean Latent Dirichlet Allocation, a topic model. That's something different.

### The idea

Think of describing each team by the average player and how players vary. To place a new player, ask which team's description fits best. If you assume all teams vary the same way, you need few numbers and get a straight dividing line. Let each team vary in its own way, and the line can curve, but you need more data.

[Figure: Three assumptions. LDA shares one covariance. QDA gives each class its own. Naive Bayes keeps only the diagonal.]

_More flexible needs more data, so it's a bias-variance choice._

### Play

**Try to break it.** Set the classes' correlations to opposite values. Then lower the rows to 5.

#### Which assumption fits?

Our seeded simulation: two Gaussian classes. Scores are averaged over 20 runs, each tested on 2,000 new points. The chart shows one run.

Set class B's correlation to **−0.7**, and see QDA's curved boundary pull ahead. Now return it to 0.7, and lower rows to **5**: LDA's simpler estimate is more reliable. Naive Bayes ignores correlation, so it trails whenever correlation matters.

**Now say why:** why does a shared covariance give a straight boundary?

## Maths

### Maths

#### In one breath

Instead of learning a boundary directly, these models describe each class as a **Gaussian**, then use Bayes' rule. **LDA** gives every class the same covariance, so its boundaries are straight. **QDA** gives each class its own, so its boundaries are curved, but it has many more numbers to estimate. **Gaussian naive Bayes** is QDA with only the diagonal of each covariance. The choice is a bias-variance trade-off, and LDA can also project data down to at most K − 1 dimensions.

#### One family, three assumptions

| Model | Covariance | Boundary | Numbers to estimate for covariance |
|---|---|---|---|
| **LDA** | One, shared by all classes | Straight | p(p + 1) / 2 |
| **QDA** | One per class | Curved | K × p(p + 1) / 2 |
| **Gaussian naive Bayes** | One per class, diagonal only | Curved, but ignores correlation | K × p |

With 50 features and 2 classes, for example, LDA estimates 1,275 covariance numbers, QDA 2,550, and naive Bayes 100. That's why more flexible isn't always better on small data.

##### Why LDA's boundary is straight

Each class's score contains a term that's quadratic in x. With a shared covariance, that term is the same for all classes, so it cancels when you compare them. Only a linear part remains. In QDA, the covariances differ, so it stays.

##### LDA or logistic regression?

Both draw straight boundaries, but they fit them differently.

- **LDA** assumes Gaussian classes with a shared shape. If that's close to true, it uses data efficiently, which helps with few rows. It stays stable when classes are well separated, where logistic regression's weights can run away.

- **Logistic regression** makes fewer assumptions. It's usually safer with outliers, categorical features or non-Gaussian data.

##### Too many features

The covariance estimate becomes unreliable when features approach the number of rows. **Shrinkage** pulls it towards a simpler matrix, which often helps a lot.

##### LDA for dimensionality reduction

With K classes, the class means lie in at most K − 1 dimensions, so LDA can project onto those. Unlike PCA, it uses the labels: it looks for directions that separate classes, rather than directions with the most variance. It's the same LDA used differently, so the number of dimensions you keep doesn't affect its predictions.

#### The maths

$$ \delta_k(x) = -\tfrac12 \log|\Sigma_k| - \tfrac12 (x-\mu_k)^{\top}\Sigma_k^{-1}(x-\mu_k) + \log \pi_k, \qquad \delta_k(x) = x^{\top}\Sigma^{-1}\mu_k - \tfrac12\mu_k^{\top}\Sigma^{-1}\mu_k + \log\pi_k $$

Both come from Bayes’ rule with Gaussian classes, as in the scikit-learn guide. π is the share of each class.

- **the QDA score**: Each class has its own covariance. Choose the class with the highest score.

- **the LDA score**: With one shared Σ, the quadratic term cancels, and the score is linear in x.

## In practice

### In practice

#### In practice

- **Scale for the shrinkage:** LDA's predictions don't depend on scale, but shrinkage towards a simpler matrix can.

- **Check the assumption loosely:** heavy outliers or categorical features suit logistic regression or trees better.

- **Use shrinkage with many features:** especially if features are close to the number of rows.

- **Try QDA only with enough rows per class:** it estimates a full covariance for each class.

- **Remember the base rates:** the class share π is part of the score, so a change in class balance changes decisions.

### The answer that sounds right

#### "QDA is more flexible, so it's always better"

It sounds right, as curves can fit anything a line can. But QDA estimates a full covariance for each class. With few rows, those estimates are noisy, and a simpler model does better on new data, even if its assumption is slightly wrong. Compare them on validation data.

## Say it

### How do LDA and QDA classify, and when would you choose them over logistic regression or naive Bayes?

#### The interviewer pushes further

Follow-up 1 of 3

Why is LDA limited to K − 1 dimensions?

It only uses the directions that separate the class means. K points lie in a space of at most K − 1 dimensions. Two classes give one direction, however many features you have.

Follow-up 2 of 3

LDA vs PCA?

Both project data onto fewer dimensions. PCA ignores labels, and keeps the directions with the most variance. LDA uses labels, and keeps the directions that best separate classes. So PCA could keep a high-variance direction that says nothing about the class.

Follow-up 3 of 3

How is naive Bayes related to QDA?

Gaussian naive Bayes is QDA with each covariance restricted to its diagonal. That removes correlations, so it estimates far fewer numbers. It's more stable with little data, but it can't use correlation between features.

LDA and QDA are generative: they model each class as a Gaussian, and use Bayes' rule. LDA shares one covariance across classes, so the quadratic term cancels, and boundaries are straight. QDA gives each class its own, so boundaries curve, but it has far more to estimate, so it needs more data. Gaussian naive Bayes is QDA with diagonal covariances. Compared with logistic regression, LDA is more efficient if the Gaussian assumption holds, while logistic regression is safer if it doesn't. With many features, I'd use shrinkage. LDA can also project data to at most K minus 1 dimensions.

**Key terms and sources**

Modelling each class as a Gaussian: shared or separate covariance, linear or curved boundaries, shrinkage, LDA as dimensionality reduction, and how they compare.

#### Sources

- scikit-learn on linear and quadratic discriminant analysis

- ISLR, chapter on classification

- CS229 syllabus, generative learning

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
