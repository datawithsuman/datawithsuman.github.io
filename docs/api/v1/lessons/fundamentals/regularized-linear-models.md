# Regularized Linear Models

> Ridge vs Lasso vs Elastic Net: why does L1 zero out weights while L2 only shrinks them?

- Track: Fundamentals › Classical ML › Linear models
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/regularized-linear-models/
- Before this: Linear Regression (`fundamentals/linear-regression`), Maximum Likelihood & MAP (`fundamentals/mle-and-map`)
- Quiz topic: `lin`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-20 · Version: b3a9115acd

## Intuition

### The situation

With 22 flats and 10 features, your model says each extra bedroom makes a flat cheaper. The interviewer asks:

> What is the difference between Ridge and Lasso?

**Running example:** predicting flat prices again (continuing Linear Regression), but now with only **22 flats** and **10 features**: five real ones (size, bedrooms, age, floor, distance to metro) and five pure junk (the flat number's last digit, listing weekday, photos in the ad, owner's birth month, agent ID parity). Size and bedrooms are 95% correlated. Data is simulated so we know the truth; test error is measured on 400 fresh flats.

#### Least squares believes every feature, even the useless and the redundant

Fit ordinary least squares (OLS) to the 22 flats and something odd happens: it says each extra **bedroom makes a flat cheaper**. That's not economics, it's collinearity. Size and bedrooms carry almost the same information, so OLS can trade one off against the other freely, and small quirks of the sample decide the split. Draw a different 22 flats and watch:

Coefficients on standardised features (₹ lakh per standard deviation). The true effects are positive for both. OLS's split between size and bedrooms jumps around, and even goes negative. Ridge (λ = 0.3) keeps both positive and stable from sample to sample.

Two problems at once: **variance** (weights swing with the sample) and **overfitting** (with 10 features and 22 rows, OLS also fits the junk). Tibshirani's diagnosis from 1996 still holds: OLS estimates "often have low bias but large variance; prediction accuracy can sometimes be improved by shrinking or setting to 0 some coefficients" [Tibshirani 1996, p. 267](https://sites.stat.washington.edu/courses/stat527/s13/readings/j_royal_stat_soc_b1996.pdf#page=2).

### The idea

Think of charging a model for its weights. Ridge charges more for bigger weights, so every weight shrinks but none disappears. Lasso charges the same for every unit, so small weights can't justify the cost and drop to exactly zero.

[Figure: Left: a diamond for Lasso, with the best point landing on a corner, so one weight is exactly zero. Right: a circle for Ridge, with the best point on the curve, so both weights shrink but neither reaches zero.]

_Tibshirani's picture: the budget's shape decides whether the best point lands on a zero._

### Play

**Try to break it.** Choose Ridge and raise the strength, then do the same with Lasso. Watch how many features are kept, and how many junk ones survive.

#### Turn the dial and watch the weights

Bars: coefficients on standardised features; the hollow tick is the OLS value. Bottom chart: test MSE on 400 fresh flats versus α for the chosen method (dot = current α). Simulated data with known truth: price rises with size and bedrooms, falls with age and metro distance, rises slightly with floor; the last five features are pure noise. Fitted by coordinate descent with scikit-learn's objective scaling.

Things to look for. **Ridge** pulls size and bedrooms toward each other and shrinks junk, but zeros nothing; its best test MSE (about α = 0.1) beats OLS clearly. **Lasso** around α ≈ 1–2 keeps size, age, floor and metro distance, drops the junk (all five are gone by α = 2), and drops bedrooms too (it picks one of the correlated pair). It gets the best test error of the three. **Elastic Net** keeps size and bedrooms together, the grouping effect, at the cost of keeping some junk at these settings. Push any of them too far and everything shrinks to nothing: high bias, rising test error.

**Now say why:** why does Lasso reach exact zeros when Ridge never does?

## Maths

### Maths

#### In one breath

Plain least squares trusts every feature completely, so with many or correlated features its weights become huge, unstable and overfit. Regularization adds a price on the size of the weights. **Ridge** (an L2 penalty) shrinks all of them smoothly and fixes collinearity. **Lasso** (an L1 penalty) shrinks and sets some to exactly zero, so it selects features. **Elastic Net** mixes both, so correlated features enter or leave together. One knob, λ, trades bias for variance, and you choose it by cross-validation. What you'll be able to do after this: explain why L1 gives zeros and L2 doesn't (geometrically and algebraically), pick between the three, and tune them properly.

#### Three ideas you need first

##### Bias–variance trade-off

Test error ≈ bias² + variance + noise. OLS is unbiased but, with few rows and many correlated features, has huge variance. Accepting a little bias (pulling weights toward zero) can cut variance a lot, and lower total error.

##### Standardise the features

A penalty on weight size only makes sense if features share a scale. Otherwise "size in m²" and "size in km²" get penalised completely differently. Subtract each feature's mean, divide by its standard deviation, and don't penalise the intercept.

##### Norms: two ways to measure "how big are the weights"

**L2**: ‖β‖₂² = β₁² + β₂² + … (the squared length). **L1**: ‖β‖₁ = |β₁| + |β₂| + … (the sum of absolute values). They sound similar. The difference in their shapes (a circle versus a diamond) is the whole story of the Lasso section.

#### Fit the data, but pay for every unit of weight

$$ \min_{\beta}\ {\|\mathbf y - X\beta\|_2^2} + {\lambda}\,{P(\beta)} \quad\Longleftrightarrow\quad {\min_\beta \|\mathbf y - X\beta\|_2^2 \ \text{ s.t. } P(\beta)\le t} $$

The penalised and constrained forms are equivalent; Tibshirani defines the lasso in the constrained form [p. 268](https://sites.stat.washington.edu/courses/stat527/s13/readings/j_royal_stat_soc_b1996.pdf#page=3).

- **fit the data**: The usual least-squares error. Alone, it lets weights grow as large as they like.

- **the price**: λ ≥ 0 sets how expensive weight is. λ = 0 gives back OLS; λ → ∞ forces every weight to 0.

- **how weight is measured**: The norm of the weights: L2 for Ridge, L1 for Lasso, a mix for Elastic Net. The shape of this norm decides the behaviour.

- **same thing, as a budget**: Equivalently: minimise the error subject to the weights staying inside a budget t. Each λ matches some t. This view gives the geometry in the Lasso section.

#### An L2 penalty, and a matrix that's always invertible

$$ {\hat\beta_{\text{ridge}}} = \big({X^{\top}X} + {\lambda I}\big)^{-1}{X^{\top}\mathbf y} $$

Minimiser of ‖y − Xβ‖² + λ‖β‖²; scikit-learn's `Ridge` objective [docs](https://scikit-learn.org/stable/modules/linear_model.html).

- **ridge weights**: The solution has a closed form, just like OLS.

- **the features' overlap**: XᵀX, the same matrix as in the normal equation. With collinear features it is nearly singular, so its inverse explodes.

- **the ridge**: Adding λ to the diagonal (the ridge) makes the matrix well conditioned and always invertible, even with more features than rows.

- **feature–target overlap**: Unchanged from OLS.

That's why Ridge fixes the sign flip from the start of this lesson. scikit-learn: with ridge, "the coefficients become more robust to collinearity." Zou and Hastie give a nice reading of it: the ridge operator is "decorrelation followed by direct scaling shrinkage": it shrinks the correlations between features by 1/(1 + λ), then scales [Zou & Hastie 2005, p. 308](https://sites.stat.washington.edu/courses/stat527/s13/readings/zouhastie05.pdf#page=8). Correlated features end up sharing the credit roughly equally.

##### What it can't do

Ridge "does not set any coefficients to 0 and hence does not give an easily interpretable model" [Tibshirani 1996, p. 267](https://sites.stat.washington.edu/courses/stat527/s13/readings/j_royal_stat_soc_b1996.pdf#page=2). The five junk features get small weights, but never zero. Try it in the Play lab, in the Intuition tab.

#### Why L1 lands on exact zeros: the diamond

Swap the squares for absolute values, and Lasso does something Ridge never does: it sets weights to **exactly** zero. Tibshirani's picture explains why [§2.3, p. 270](https://sites.stat.washington.edu/courses/stat527/s13/readings/j_royal_stat_soc_b1996.pdf#page=5):

1. Two weights, β₁ and β₂. On the left the budget is an L1 budget; on the right, an L2 budget.

2. OLS sits at the unconstrained best point, outside the budget in both cases.

3. Moving away from OLS, the squared error rises in elliptical contours: every point on one ellipse has the same error.

4. The allowed region: a **diamond** for L1 (|β₁| + |β₂| ≤ t), a **circle** for L2.

5. The solution is where the growing ellipses first touch the region. The diamond has corners on the axes, and an ellipse often hits a corner first, which means one weight is exactly zero. The circle has no corners, so the touching point almost never lies on an axis. In more dimensions the diamond has even more corners and edges, so many weights hit zero.

##### The same thing algebraically

With uncorrelated (orthonormal) features you can solve both exactly, and the difference is plain. Ridge _scales_ each OLS weight by a constant factor; Lasso _subtracts_ a constant and stops at zero ("soft thresholding") [Tibshirani 1996, §2.2](https://sites.stat.washington.edu/courses/stat527/s13/readings/j_royal_stat_soc_b1996.pdf#page=4):

$$ {\hat\beta^{\text{ridge}}_j = \hat\beta_j \,/\, (1+\lambda)} \qquad {\hat\beta^{\text{lasso}}_j = \operatorname{sign}(\hat\beta_j)\,\big(|\hat\beta_j| - \lambda\big)}{_{+}} $$

Orthonormal design (XᵀX = I), with the penalties scaled to give these simple forms · hover any symbol.

- **ridge: scale**: Divide the OLS weight by 1 + λ. Big or small, every weight shrinks by the same proportion, and never reaches zero.

- **lasso: shift and cut**: Move the OLS weight λ closer to zero; if it would cross zero, stop at zero. Any weight smaller than λ is deleted.

- **the cut-off**: (·)₊ means max(·, 0). This is where exact zeros come from.

x-axis: the OLS weight. y-axis: what each method returns. Dashed: OLS (no shrinkage). Everything inside the green flat zone (|β̂| ≤ λ) becomes exactly zero under Lasso.

#### Why Lasso alone isn't enough

Zou and Hastie list three situations where Lasso struggles [Zou & Hastie 2005, p. 302](https://sites.stat.washington.edu/courses/stat527/s13/readings/zouhastie05.pdf#page=2):

1. **More features than rows (p > n):** "the lasso selects at most n variables before it saturates." With 20,000 genes and 70 patients, it can keep at most 70.

2. **Correlated groups:** "the lasso tends to select only one variable from the group and does not care which one is selected." In our flats it keeps size and drops bedrooms.

3. **Correlated features, n > p:** "the prediction performance of the lasso is dominated by ridge regression."

Elastic Net adds a little L2 to the L1. The L1 part still produces zeros; the L2 part makes the problem strictly convex, which produces the grouping effect: "strongly correlated predictors tend to be in or out of the model together" [abstract](https://sites.stat.washington.edu/courses/stat527/s13/readings/zouhastie05.pdf#page=1). The authors' image: "like a stretchable fishing net that retains 'all the big fish'".

$$ \min_{\beta}\ {\tfrac{1}{2n}\|\mathbf y - X\beta\|_2^2} + {\alpha}{\rho\,\|\beta\|_1} + {\alpha}{\tfrac{1-\rho}{2}\|\beta\|_2^2} $$

scikit-learn's `ElasticNet` objective, with `l1_ratio` = ρ [docs](https://scikit-learn.org/stable/modules/linear_model.html). Zou and Hastie also rescale the naive solution by (1 + λ₂) to undo "double shrinkage" [p. 307](https://sites.stat.washington.edu/courses/stat527/s13/readings/zouhastie05.pdf#page=7).

- **fit, averaged**: Mean squared error with a ½ (scikit-learn's scaling: 1/(2n)).

- **overall strength**: α: how much penalty in total.

- **the L1 share**: ρ (l1_ratio) of the penalty is L1: this part creates zeros. ρ = 1 is pure Lasso.

- **the L2 share**: The remaining 1 − ρ is ridge: it stabilises the fit and groups correlated features. ρ = 0 is a ridge penalty.

scikit-learn's one-line summary: "Lasso is likely to pick one of these at random, while elastic-net is likely to pick both" [docs](https://scikit-learn.org/stable/modules/linear_model.html).

## In practice

### In practice

#### Three penalties, one recipe

| Method | Penalty | Origin | What it does |
|---|---|---|---|
| **Ridge** | λ‖β‖₂² | Hoerl & Kennard, 1970 | Shrinks every weight smoothly; never exactly zero; fixes collinearity |
| **Lasso** | λ‖β‖₁ | Tibshirani, 1996 | Shrinks and sets some weights to exactly zero: feature selection |
| **Elastic Net** | mix of both | Zou & Hastie, 2005 | Sparse like Lasso, but keeps correlated groups together |

In scikit-learn they're `Ridge`, `Lasso` and `ElasticNet`, with `RidgeCV`, `LassoCV` and `ElasticNetCV` to pick the strength by cross-validation. The same penalties appear everywhere else in ML: `LogisticRegression` is L2-regularised by default, and "weight decay" in neural networks is an L2 penalty. [scikit-learn docs](https://scikit-learn.org/stable/modules/linear_model.html)

#### λ is a hyperparameter: pick it with cross-validation

The training error always prefers λ = 0 (OLS fits the training rows best). So you can't choose λ on training error. Standard practice is k-fold cross-validation over a grid of λ values (log-spaced, as in the lab), then refit on all the training data with the winner. Two common choices: the λ with the lowest CV error, or the largest λ within one standard error of it (the "one-standard-error rule", a simpler model at almost the same accuracy). `RidgeCV`, `LassoCV` and `ElasticNetCV` do this for you.

##### Classic mistakes

- Not standardising: the penalty then punishes features for their units.

- Fitting the scaler on all data before splitting: test-set information leaks into training.

- Penalising the intercept: shifts every prediction toward zero for no reason (libraries don't, if you let them fit it).

- Comparing α across libraries or models: scikit-learn's Ridge has no 1/n factor, its Lasso has 1/(2n), and LogisticRegression uses C = 1/strength [docs](https://scikit-learn.org/stable/modules/linear_model.html).

**Go deeper: the Bayesian view**

Regularised least squares is maximum a posteriori estimation. A Gaussian prior on each weight (most weights small, any value possible) gives Ridge; a Laplace prior (a sharp peak at zero with heavier tails) gives Lasso. The sharp peak at zero is the probabilistic version of the diamond's corners. λ corresponds to how tight the prior is relative to the noise. This is standard textbook material (e.g. ESL ch. 3).

#### Regularised regression, start to finish

1. Split off a test set. Build a pipeline: impute → one-hot → **standardise** → model, so scaling is learned on training folds only.

2. Pick the penalty from your goal: stability with correlated features → Ridge; a small, readable model → Lasso; many correlated features or p > n → Elastic Net.

3. Cross-validate α (and ρ for Elastic Net) on a log grid.

4. Refit on all training data, evaluate once on the test set.

5. Interpret carefully: Lasso's zeros mean "not needed given the others", not "no effect"; which of two correlated features survives can change between samples.

#### Pick by goal

| Situation | Start with |
|---|---|
| Many correlated features, you want stable predictions, all features plausible | **Ridge** |
| You believe only a few features matter and want a short, readable model | **Lasso** |
| More features than rows, or groups of correlated features (genes, sensors, one-hot blocks) | **Elastic Net** |
| Lots of data, few well-chosen features | Plain OLS is fine; a light ridge rarely hurts |
| Not sure | Elastic Net with ρ cross-validated over [0.1, 0.5, 0.9, 1] covers all three |

### The answer that sounds right

#### "Just drop the bad features by hand" (subset selection)

The classic fix is to try subsets of features and keep the best one (forward, backward or best-subset selection). It gives a small, readable model. But it's all-or-nothing, and that makes it unstable:

##### What breaks: a discrete choice is a jumpy choice

"Subset selection provides interpretable models but can be extremely variable because it is a discrete process: regressors are either retained or dropped from the model. Small changes in the data can result in very different models being selected and this can reduce its prediction accuracy" [Tibshirani 1996, p. 267](https://sites.stat.washington.edu/courses/stat527/s13/readings/j_royal_stat_soc_b1996.pdf#page=2). Best-subset search also grows as 2p: 10 features means 1,024 models, 40 means about a trillion.

Regularization replaces "in or out" with a continuous dial.

#### What to keep

**The lesson:** regularization trades a little bias for a lot less variance by charging for weight. The shape of the charge decides the behaviour: L2's round ball shrinks smoothly, and L1's corners produce exact zeros.

- **Lasso selection isn't stable inference.** Which of two correlated features survives can flip between samples. Use stability selection or the bootstrap if you need to trust the selected set.

- **Shrunken coefficients are biased.** Good for prediction, misleading for effect sizes. A common trick is to refit OLS on Lasso's selected features ("relaxed lasso").

- **No penalty fixes a wrong model.** If the relationship is non-linear, regularising a linear model just makes it a more stable wrong model.

- **The simulation here is small** (22 rows, 10 features), chosen to make the effects visible. With lots of data and few features, OLS and the regularised fits converge.

## Say it

### What is the difference between Ridge and Lasso?

#### The interviewer pushes further

Follow-up 1 of 6

Why does L1 produce zeros and L2 doesn't?

Geometrically, the L1 ball is a diamond with corners on the axes, and the error contours usually touch it first at a corner. The L2 ball is round, so the touching point is almost never on an axis. Algebraically, the L1 penalty's gradient doesn't vanish near zero (it's ±λ), so small weights get pushed all the way to zero (soft thresholding). The L2 gradient 2λβ fades as β → 0, so it only scales weights down.

Follow-up 2 of 6

Why must you standardise before regularising?

The penalty compares weights across features. If one feature is in metres and another in millimetres, the same effect needs weights 1000× apart, so the penalty would crush one and ignore the other. Standardising puts all features on a common scale, so the penalty is fair. Fit the scaler on training data only.

Follow-up 3 of 6

What happens as λ → 0 and λ → ∞?

λ → 0 gives OLS (low bias, high variance). λ → ∞ drives every coefficient to zero, so the model predicts the mean (high bias, zero variance). The best λ, found by CV, sits in between.

Follow-up 4 of 6

Lasso with two highly correlated features?

It tends to keep one and zero the other, somewhat arbitrarily, and which one can change with the sample. Ridge splits the weight between them. Elastic Net keeps both with similar weights (the grouping effect).

Follow-up 5 of 6

Can you use Lasso for feature selection, then OLS?

Yes, that's the relaxed lasso or post-lasso OLS: it reduces Lasso's shrinkage bias on the kept features. But the selection itself is noisy, so validate the final model on held-out data, and don't treat the p-values of the refit as if the features had been chosen in advance.

Follow-up 6 of 6

How does this relate to neural networks?

Weight decay is an L2 penalty on the weights (with a subtlety: for adaptive optimisers like Adam, AdamW applies decoupled weight decay rather than adding λ‖w‖² to the loss). L1 penalties are used less but appear in sparsity work. Same idea everywhere: limit capacity to generalise better.

#### The 30-second answer

Regularized regression adds a penalty on weight size to least squares to cut variance and overfitting. Ridge uses an L2 penalty: it shrinks all coefficients smoothly, never to zero, and handles collinearity because XᵀX + λI is always invertible. Lasso uses L1: its diamond-shaped constraint has corners on the axes, so it sets some coefficients exactly to zero and does feature selection, but with correlated features it arbitrarily keeps one and can select at most n features. Elastic Net mixes the two to get sparsity plus grouping. You standardise features and tune λ by cross-validation.

**Go further**

#### The 2-minute walkthrough

Problem: OLS has high variance with many or correlated features (show the sign flip). Bias–variance framing. Penalised objective ‖y − Xβ‖² + λP(β), equivalent to a budget. Ridge: closed form (XᵀX + λI)⁻¹Xᵀy, decorrelates and shrinks. Lasso: diamond geometry, soft thresholding in the orthonormal case, exact zeros. Elastic Net: Zou & Hastie's three Lasso failures and the grouping effect. Practicalities: standardise, don't penalise the intercept, cross-validate λ, beware α conventions. Evidence: prostate data, Elastic Net 0.381 vs OLS 0.586 test MSE.

#### What not to say

- "Ridge does feature selection." It never zeros a weight.

- "Lasso tells you which features truly matter." It tells you a small set that predicts well; with correlated features the choice is fragile.

- "Regularization always improves test error." Only if λ is tuned; too much λ underfits.

- "You don't need to scale features for Lasso." You do.

**Key terms and sources**

Ridge, Lasso and Elastic Net · built from Tibshirani (1996), Zou & Hastie (2005) and scikit-learn's docs · checked 28 Oct 2026

#### A real benchmark: prostate cancer data

Zou and Hastie compared all the methods on a classic dataset: predicting log prostate-specific antigen from 8 clinical measures, 67 training patients, 30 test patients, tuning by tenfold cross-validation [Zou & Hastie 2005, Table 1](https://sites.stat.washington.edu/courses/stat527/s13/readings/zouhastie05.pdf#page=11):

##### Test mean squared error (↓ better)

OLS · all 8 variables

0.586

Ridge · all 8

0.566

Lasso · 5 variables

0.499

Elastic Net · 5 variables

0.381

Standard errors are large (0.105–0.188) with a 30-patient test set, so treat the ranking as indicative, not definitive. The authors conclude "the elastic net is the winner among all the competitors in terms of both prediction accuracy and sparsity. OLS is the worst method."

And Tibshirani's original claim for the lasso: simulations "suggest that the lasso enjoys some of the favourable properties of both subset selection and ridge regression. It produces interpretable models like subset selection and exhibits the stability of ridge regression" [abstract, p. 267](https://sites.stat.washington.edu/courses/stat527/s13/readings/j_royal_stat_soc_b1996.pdf#page=2).

#### Glossary

| Term | Meaning |
|---|---|
| **Regularization** | Adding a penalty on model complexity (here, weight size) to the training loss. |
| **Ridge / L2** | Penalty λΣβ²; smooth shrinkage, never zero. |
| **Lasso / L1** | Penalty λΣ\|β\|; shrinkage plus exact zeros (feature selection). |
| **Elastic Net** | Weighted mix of L1 and L2 (α, l1_ratio). |
| **Soft thresholding** | sign(b)·max(\|b\| − λ, 0): Lasso's update. |
| **Grouping effect** | Correlated features get similar weights and enter or leave together. |
| **Multicollinearity** | Features that are nearly linear combinations of each other. |
| **Coordinate descent** | Optimise one weight at a time; the standard Lasso / Elastic Net solver. |
| **Weight decay** | The neural-network name for an L2 penalty. |

#### What this page is built from

1. R. Tibshirani, [Regression Shrinkage and Selection via the Lasso](https://sites.stat.washington.edu/courses/stat527/s13/readings/j_royal_stat_soc_b1996.pdf), JRSS-B 58 (1996) 267–288: motivation, orthonormal case, geometry.

2. H. Zou & T. Hastie, [Regularization and Variable Selection via the Elastic Net](https://sites.stat.washington.edu/courses/stat527/s13/readings/zouhastie05.pdf), JRSS-B 67 (2005) 301–320: Lasso's limits, grouping effect, prostate benchmark.

3. A. Hoerl & R. Kennard, "Ridge Regression: Biased Estimation for Nonorthogonal Problems", _Technometrics_ 12 (1970): origin of ridge (background, not quoted).

4. scikit-learn, [Linear models user guide](https://scikit-learn.org/stable/modules/linear_model.html): objectives and α scaling, collinearity, Lasso vs Elastic Net.

5. Hastie, Tibshirani & Friedman, _The Elements of Statistical Learning_, ch. 3: shrinkage methods (background).

6. Interview angle: [Interview Query, Lasso vs Ridge](https://interviewquery.com/learning-paths/modeling-and-machine-learning-interview/generalized-linear-models-and-regression/lasso-vs-ridge).

The flats data is simulated with a fixed random seed (known true effects) and fitted live in this page.
