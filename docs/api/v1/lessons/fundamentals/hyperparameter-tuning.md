# Hyperparameter Tuning

> Grid, random or Bayesian: how do you spend 30 expensive training runs?

- Track: Fundamentals › Classical ML › Core concepts
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/hyperparameter-tuning/
- Before this: Cross-Validation & Data Leakage (`fundamentals/cross-validation-and-leakage`)
- Quiz topic: `mlcore`

## Intuition

### The situation

Each trial of your ETA model means training it and running 5-fold cross-validation, so you can only afford a few dozen trials. The interviewer asks:

> How do you tune hyperparameters efficiently?

**Running example:** tuning the food-delivery app's ETA model. Each trial means training the model with one setting and scoring it with 5-fold CV, which takes minutes, so the budget is a few dozen trials. The labs use stand-in validation-loss functions with a known optimum (simulated) so we can measure exactly how close each search method gets.

#### Expensive, noisy, black-box optimisation

You want the settings that minimise validation loss, but you can't take a gradient of "train a model and cross-validate it" with respect to the learning rate; each evaluation costs real time; and the result is noisy (fold randomness). So tuning is a search problem with a tiny budget. The question is how to spend each trial.

### The idea

Think of finding the best dish in a city with only a few meals to spare. A grid keeps returning to the same few streets. Random search covers more ground. Bayesian optimisation heads towards what's been good so far, and successive halving takes one bite of many dishes before committing.

[Figure: Left, a grid of nine trials that tests only three distinct values of each setting. Right, nine random trials that test nine distinct values.]

_Illustrative. If only one setting really matters, random search tests far more values of it._

### Play

**Try to break it.** Compare grid and random at 9, 16 and 25 trials. Watch the distinct values of the setting that matters, and the best loss.

#### Spend each trial on new information

Background shading: validation loss, which depends only on the horizontal setting (the vertical one is irrelevant). The tick marks on the bottom axis show which values of the important setting each method actually tested.

Over 2,000 simulated problems with a random optimum, the average best loss with 9 trials was 0.075 for the grid and **0.049** for random search; with 25 trials, 0.027 vs **0.006**. Bergstra & Bengio (2012) showed the same on real models: random search found models "as good or better within a small fraction of the computation time", because the score functions have "low effective dimensionality" [JMLR 13](https://jmlr.org/papers/v13/bergstra12a.html).

**Now say why:** why does the same budget go further when the trials aren't lined up in a grid?

## Maths

### Maths

#### In one breath

Hyperparameters (learning rate, depth, regularisation strength…) are set before training, so you choose them by trying settings and scoring each with cross-validation. **Grid search** tries every combination, which wastes trials when only one or two parameters matter. **Random search** samples settings and, for the same budget, explores many more distinct values of the parameters that matter. **Bayesian optimisation** fits a cheap model of "score as a function of settings" and picks the next trial where improvement looks most likely. **Successive halving / Hyperband** start many settings on a small budget and only keep training the promising ones. Whatever you use, tune on validation folds and judge the winner on data the search never saw. What you'll be able to do after this: explain why random beats grid, describe the BO loop and expected improvement, explain successive halving's budget trick, and set up tuning without fooling yourself.

#### Parameters, hyperparameters, search spaces

- **Parameters** are learned from data by training (weights, split thresholds). **Hyperparameters** are chosen before training (λ, max_depth, learning rate, number of trees, k in k-NN).

- **Search space:** a range for each hyperparameter, and a **scale**. Rates and regularisation strengths vary over orders of magnitude, so search them on a **log scale** (λ ∈ 10−4…102), not linearly.

- **Objective:** the cross-validated metric you actually care about (scikit-learn's `scoring=`).

#### Model the score, then choose where to look

Random search ignores what earlier trials revealed. Bayesian optimisation (BO) fits a **surrogate model** to the trials so far, usually a Gaussian process (GP) that gives, for every untried setting, a predicted loss and an uncertainty. An **acquisition function** then trades off "predicted to be good" (exploit) against "we know little here" (explore). The classic choice is expected improvement:

$$ {\mathrm{EI}(x)} = {(y^{*} - \mu(x))}\,{\Phi(z)} + {\sigma(x)\,\varphi(z)}, \qquad z = (y^{*} - \mu(x))/\sigma(x) $$

Expected improvement for minimisation with a GP surrogate (μ mean, σ standard deviation, y* best observed), as used by Snoek, Larochelle & Adams, "Practical Bayesian optimization of machine learning algorithms", NeurIPS 2012 [arXiv:1206.2944](https://arxiv.org/abs/1206.2944).

- **expected improvement**: How much better than the current best we expect setting x to be, averaging over the surrogate’s uncertainty. Run the next trial where this is largest.

- **predicted gain**: Best loss so far minus the predicted loss at x. Large when the surrogate thinks x is good.

- **chance it’s better**: Φ(z): probability that x beats the current best under the surrogate.

- **uncertainty bonus**: σ(x) φ(z): large where the surrogate is unsure, which pulls trials into unexplored regions.

Dashed grey: the true validation loss over log₁₀ λ (unknown to the optimiser; it has a second, worse dip on the left). Orange: GP mean ± 2σ. Violet (bottom): expected improvement; the next trial goes at its peak.

Averaged over 100 runs from random starts, BO's distance from the best possible loss shrank to 0.0005 by the 8th trial and to zero by the 10th; random search was still 0.014 away after 15 trials. On cheap or high-dimensional problems the advantage shrinks, and BO's own overhead grows with the number of trials (a GP is cubic in trials). Popular tools often use a tree-structured Parzen estimator (TPE, Bergstra et al. 2011, the default in Optuna) instead of a GP; same loop, different surrogate.

#### Successive halving and Hyperband

Many trials are hopeless after a few epochs. Successive halving starts many settings with a small budget, keeps the best fraction, and multiplies their budget: scikit-learn calls it "a tournament among candidate parameter combinations", where in each round "the number of resources per candidate is multiplied by `factor` and the number of candidates is divided by the same factor" [docs](https://scikit-learn.org/stable/modules/grid_search.html#successive-halving-user-guide).

81 settings; rounds of 81 × 1 epoch, 27 × 3, 9 × 9, 3 × 27, 1 × 81 (factor 3). Grey: curves of settings that were dropped; green: survivors.

Averaged over 500 simulated problems, successive halving used 405 epochs (6% of training all 81 to completion) and picked a setting with final loss 0.217, against 0.205 for the true best; random search with the same 405 epochs (5 full runs) picked 0.268. On any single problem either can win (in problem C above, one of random search's five full runs happened to be the best setting); the average is what matters. The risk: a slow starter (low learning rate, strong regularisation) gets cut early. **Hyperband** (Li et al.) hedges by running several successive-halving "brackets" with different aggressiveness, and reported "over an order-of-magnitude speedup" over Bayesian optimisation on deep-learning and kernel problems [JMLR 18, arXiv:1603.06560](https://arxiv.org/abs/1603.06560).

## In practice

### In practice

#### The search methods

| Method | Idea | Tools |
|---|---|---|
| **Grid search** | All combinations of chosen values | `GridSearchCV` |
| **Random search** | Sample settings from distributions | `RandomizedSearchCV` |
| **Bayesian optimisation** | Model score vs settings, pick the most promising next trial | Optuna (TPE), scikit-optimize, SMAC, Ax |
| **Successive halving / Hyperband** | Many settings on small budgets, keep the best, give them more | `HalvingRandomSearchCV`, Optuna pruners, Ray Tune |

scikit-learn lists two advantages of random search: "A budget can be chosen independent of the number of parameters and possible values" and "Adding parameters that do not influence the performance does not decrease efficiency" [model-selection guide](https://scikit-learn.org/stable/modules/grid_search.html).

#### The tuned score is optimistic

The best CV score among many trials is biased upward: some of its lead is luck on those folds (the Cross-Validation lesson shows 1,000 coin-flip models reaching 70% on a validation set). scikit-learn: "it is recommended to split the data into a development set (to be fed to the GridSearchCV instance) and an evaluation set to compute performance metrics" [docs](https://scikit-learn.org/stable/modules/grid_search.html). With small data, use nested CV. And watch the leaderboard of trials: if the top 20 settings score within noise of each other, pick the simplest or most regularised one.

#### The whole recipe

1. **Start from good defaults** and tune only the hyperparameters that matter most (learning rate, regularisation, capacity).

2. **Define ranges on the right scale** (log for rates and penalties).

3. **Random search** for a quick, robust baseline (30–60 trials); **Bayesian optimisation** when trials are expensive and dimensions few; **successive halving / pruning** for iterative learners (boosting rounds, epochs).

4. **Score with CV** using the metric you care about; use early stopping inside each trial for boosting and neural nets.

5. **Evaluate the final pick once** on held-out data.

#### Scenarios

##### "Each training run takes 2 hours, 4 hyperparameters"

Bayesian optimisation (TPE/GP) with ~30 trials, plus pruning on intermediate validation loss.

##### "LightGBM, 1M rows, quick runs"

Random search (50–100 trials) with early stopping on boosting rounds; tune on a subsample first, confirm on full data.

### The answer that sounds right

#### "Try every combination on a grid"

A 3 × 3 grid over two hyperparameters costs 9 trials, but tests each hyperparameter at only **3** distinct values. If only one of the two really matters (common: Bergstra & Bengio found that "for most data sets only a few of the hyper-parameters really matter"), six of those nine trials are repeats of the same three values of the important one. Grids also grow exponentially: 5 values × 6 hyperparameters = 15,625 fits, before cross-validation multiplies that by 5.

#### Caveats

- Tuning rarely beats better data or features; gains over sensible defaults are often small for gradient boosting.

- Random search's advantage relies on low effective dimensionality; with one hyperparameter, a fine grid is fine.

- BO needs sensible priors/ranges and struggles with many dimensions, categorical choices and parallel trials (TPE handles these better than GPs).

- Early-stopping methods assume early performance predicts final performance; resource-dependent hyperparameters (e.g. learning rate schedules) break that.

## Say it

### How do you tune hyperparameters efficiently?

#### The interviewer pushes further

Follow-up 1 of 4

Why is random search better than grid search?

With low effective dimensionality, a grid tests the important hyperparameter at only √n (for 2-D) distinct values; random search tests n. It also lets you set the budget independently of dimension (Bergstra & Bengio 2012).

Follow-up 2 of 4

How does Bayesian optimisation work?

Fit a surrogate (GP/TPE) to (settings, score) pairs; compute an acquisition function (expected improvement, UCB) that balances predicted quality and uncertainty; evaluate the maximiser; refit; repeat.

Follow-up 3 of 4

What is Hyperband?

Successive halving run in several brackets with different trade-offs between number of configurations and budget per configuration, so you don't have to guess how aggressive to be.

Follow-up 4 of 4

How do you avoid overfitting during tuning?

Score with CV on a development set, evaluate the final model once on a held-out set (or nested CV), prefer simpler settings when scores tie, and limit the number of trials relative to data size.

#### The 30-second answer

Hyperparameters are chosen by searching settings and scoring each with cross-validation. Grid search is exhaustive but wasteful, because usually only a few hyperparameters matter and a grid tests each at few distinct values; random search with the same budget explores many more values and is a strong default. Bayesian optimisation fits a surrogate model, such as a Gaussian process or TPE, to past trials and uses an acquisition function like expected improvement to pick the next one, which helps when trials are expensive. Successive halving and Hyperband start many configurations cheaply and only continue the promising ones. I search rates and penalties on a log scale, use early stopping inside trials, and evaluate the chosen model on data the search never touched.

**Go further**

#### What not to say

- "I tune on the test set." Then the test score is no longer honest.

- "Grid search is the most thorough, so it's best." Not per trial spent.

- "Search the learning rate from 0.001 to 0.3 in steps of 0.01." Use a log scale.

**Key terms and sources**

Grid vs random search, Bayesian optimisation with a Gaussian process and expected improvement, successive halving and Hyperband, and honest evaluation of tuned models · built from Bergstra & Bengio (2012), Snoek, Larochelle & Adams (2012), Li et al. (2018) and scikit-learn's model-selection guide · checked 28 Oct 2026

#### Evidence

##### Kernel classifier on CIFAR-10 (Li et al., Hyperband paper)

In the time Bayesian optimisers evaluated about 3 configurations, Hyperband's first bracket evaluated over 250 and found a good one in about 20 minutes; the paper reports it "over 30× faster than Bayesian optimization methods and 70× faster than random search" on this task, and around 6× faster on a random-features task [pp. 18–19](https://arxiv.org/pdf/1603.06560#page=18). The authors also note their most aggressive bracket alone often beat full Hyperband.

##### This page's simulations

grid, 9 trials (avg best loss)

0.075

random, 9 trials

0.049

grid, 25 trials

0.027

random, 25 trials

0.006

Lower is better; one important and one irrelevant hyperparameter. Illustrative.

#### Key terms

| Term | Meaning |
|---|---|
| **Hyperparameter** | Setting chosen before training. |
| **Surrogate model** | Cheap model of score vs settings (GP, TPE, random forest). |
| **Acquisition function** | Rule for choosing the next trial (EI, UCB). |
| **Successive halving** | Keep the best 1/η, multiply their budget by η, repeat. |
| **Hyperband** | Several successive-halving brackets with different starting budgets. |
| **Pruning** | Stopping unpromising trials early (Optuna's term). |

#### What this page is built from

1. J. Bergstra & Y. Bengio, "Random search for hyper-parameter optimization", _JMLR_ 13, 2012, [jmlr.org](https://jmlr.org/papers/v13/bergstra12a.html).

2. J. Snoek, H. Larochelle & R. Adams, "Practical Bayesian optimization of machine learning algorithms", NeurIPS 2012, [arXiv:1206.2944](https://arxiv.org/abs/1206.2944).

3. L. Li, K. Jamieson, G. DeSalvo, A. Rostamizadeh & A. Talwalkar, "Hyperband: a novel bandit-based approach to hyperparameter optimization", _JMLR_ 18, 2018, [arXiv:1603.06560](https://arxiv.org/abs/1603.06560).

4. scikit-learn, [Tuning the hyper-parameters of an estimator](https://scikit-learn.org/stable/modules/grid_search.html) (random search, successive halving, development/evaluation split).

5. J. Bergstra, R. Bardenet, Y. Bengio & B. Kégl, "Algorithms for hyper-parameter optimization", NeurIPS 2011 (TPE; background); T. Akiba et al., "Optuna", KDD 2019 (background).

Loss functions are simulated with known optima; every search runs live in your browser.
