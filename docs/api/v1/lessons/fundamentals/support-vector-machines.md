# Support Vector Machines

> Of all the lines that separate the data, why pick the one with the widest street?

- Track: Fundamentals › Classical ML › Other classic classifiers
- Type: Concept · 35 min
- Page: https://aimlrounds.com/tracks/fundamentals/support-vector-machines/
- Before this: Logistic Regression (`fundamentals/logistic-regression`)
- Quiz topic: `clf`

## Intuition

### The situation

Many lines separate your pass and fail parts perfectly, but a little sensor noise pushes parts over some of those lines. The interviewer asks:

> What does an SVM optimise, and what are support vectors?

**Running example:** a factory's quality check with two sensor readings per part (both standardised), labelled pass (+1) or fail (−1). Three simulated versions of it appear: a clean batch where the classes don't overlap (24 parts), a noisy batch where they do (80 parts), and a batch with a curved boundary (120 parts, "two moons"). Every model on this page is trained live in your browser by a small SMO solver, and test accuracy uses fresh simulated parts.

#### Infinitely many lines separate the data. Which one?

When two classes can be split by a straight line, there are usually infinitely many such lines. Some pass a hair away from a training point; nudge that part's readings slightly (sensor noise) and it lands on the wrong side. We want the line that is **least fragile**: the one that stays as far as possible from both classes. That one idea, plus two extensions (forgiving some mistakes, and bending the boundary), is the whole SVM.

### The idea

Think of laying the widest possible road between two groups of houses. Only the houses right at the road's edge decide where it can go. Move any other house, and the road doesn't change.

[Figure: Two groups of points separated by a wide empty street. Only the points on the street's edges are ringed, because they alone decide where it goes.]

_Illustrative. The ringed points on the edges are the support vectors._

### Play

**Try to break it.** Push γ up to 100 and watch the boundary. Then bring it down to 0.1 and compare the test accuracy.

#### γ sets how far each support vector reaches

The RBF (Gaussian) kernel K(x, z) = exp(−γ‖x − z‖²) is the default in scikit-learn's SVC. The score becomes a sum of bumps centred on support vectors. scikit-learn: "gamma defines how much influence a single training example has. The larger gamma is, the closer other examples must be to be affected" [SVM guide](https://scikit-learn.org/stable/modules/svm.html).

Pale band: inside the street (|f| < 1). Try γ = 0.1 (bumps so wide the boundary is nearly straight: underfits), γ = 1 (follows the moons), γ = 100 (a bump around nearly every point: overfits).

At C = 1 on this batch: γ = 0.1 gives 80.7% test accuracy, γ = 1 gives **89.3%**, and γ = 100 gives 99% training but only **79.8%** test, with 115 of the 120 points as support vectors. A support-vector count close to n is itself a warning sign of overfitting. C and γ interact (a large γ with a small C can still be smooth), so scikit-learn advises searching them together, "spaced exponentially far apart" [SVM guide](https://scikit-learn.org/stable/modules/svm.html).

##### What breaks without scaling

The RBF kernel uses Euclidean distance, so a feature measured in large units dominates every distance and the others are ignored; the margin in a linear SVM is also distorted. scikit-learn: "Support Vector Machine algorithms are not scale invariant, so it is highly recommended to scale your data", with the same scaling applied to test data, easiest inside a `Pipeline(StandardScaler(), SVC())` [SVM guide](https://scikit-learn.org/stable/modules/svm.html). The k-NN lesson measures the damage on the same moons data.

**Now say why:** why does a huge γ score well on training parts but worse on new ones, and what happens to the support-vector count?

## Maths

### Maths

#### In one breath

Many lines separate two classes; an SVM picks the one with the **widest street** (margin) between them. Only the points on the edge of the street, the **support vectors**, decide where it goes. Real data overlaps, so a **soft margin** lets some points break the rule at a price set by **C** (small C: wide, forgiving street; large C: narrow, strict). The **kernel trick** swaps every dot product for a similarity K(x, z), which is the same as drawing a straight street in a richer feature space without ever building that space; with the RBF kernel, **γ** sets how far each point's influence reaches. Scale your features, tune C and γ together on a log grid, and remember that training cost grows between n² and n³. What you'll be able to do after this: derive the margin, explain C and γ, read the hinge loss, explain the kernel trick on a 1-D example, and say when an SVM is (and isn't) the right tool.

#### A linear score, and the distance to the line

A linear classifier computes a score f(x) = w·x + b and predicts the class by its sign. The boundary is where f(x) = 0. The margin of a point is how far it sits from that boundary, measured on the correct side:

$$ {\gamma_i} = {y_i}\,{(w^{\top}x_i + b)} \,/\, {\lVert w\rVert} $$

Standard geometry; see Cortes & Vapnik (1995), §2 [Machine Learning 20](https://doi.org/10.1007/BF00994018).

- **geometric margin**: The signed distance from point i to the boundary. Positive means correctly classified; bigger means safer.

- **true label ±1**: Multiplying by the label flips the sign for class −1, so correct points are always positive.

- **the score**: w·x + b, the raw output of the linear model at point i.

- **length of w**: Dividing by ‖w‖ turns the score into a real distance. Scaling w and b by 10 changes the score but not the line, and not the distance.

Because w and b can be rescaled freely, SVMs fix the scale by asking the closest points to have score exactly ±1. Then the street between the lines w·x + b = +1 and w·x + b = −1 has width **2 / ‖w‖**. A wide street means a short w.

#### Widest street; only the edge points matter

1. Seven passing parts, six failing parts, cleanly separable.

2. Many lines separate them. Each one is a valid classifier with zero training error.

3. The SVM chooses the line with the widest empty street around it. The street's edges are where the score is +1 and −1; its width is 2/‖w‖.

4. Only three parts touch the edges of the street. These are the **support vectors**: the solution is a weighted sum of them alone.

5. Move any other part (without crossing into the street) and the line doesn't move at all. That's why SVMs are "memory efficient": the model keeps only the support vectors.

Maximising 2/‖w‖ is the same as minimising ½‖w‖², which gives a clean convex problem, the **hard-margin SVM**:

$$ \min_{w,b}\ {\tfrac12\lVert w\rVert^2} \quad \text{s.t.}\quad {y_i\,(w^{\top}x_i + b) \ge 1}, \quad {i = 1,\dots,n} $$

The optimal-margin classifier of Boser, Guyon & Vapnik (1992); Cortes & Vapnik (1995) Eq. 1–4 [Machine Learning 20](https://doi.org/10.1007/BF00994018).

- **make the street wide**: Minimising ½‖w‖² maximises the width 2/‖w‖. The ½ and the square only make the maths tidy; it is a convex quadratic.

- **everyone outside the street**: Each point must have score at least +1 on its own side (score × label ≥ 1). No point is allowed inside the street.

- **for every training point**: n constraints, one per part. Points where the constraint is tight (= 1) are the support vectors.

#### Real data overlaps: pay for each violation

On the noisy batch, no line separates the classes, so the hard-margin problem has no solution. Cortes & Vapnik's fix (the paper that named it the "support-vector network") gives every point a **slack** ζi: how far it is allowed to cross its edge of the street, at a cost:

$$ \min_{w,b,\zeta}\ {\tfrac12\lVert w\rVert^2} + {C}\,{\textstyle\sum_i \zeta_i} \quad\text{s.t.}\quad {y_i(w^{\top}x_i+b) \ge 1-\zeta_i},\ \ {\zeta_i \ge 0} $$

scikit-learn's primal SVC problem (with φ(x) = x for the linear case) [SVM guide](https://scikit-learn.org/stable/modules/svm.html); Cortes & Vapnik (1995) §3.

- **wide street**: Same as before: prefer a short w, a wide margin.

- **price per unit of violation**: C trades the two goals. scikit-learn: “A low C makes the decision surface smooth, while a high C aims at classifying all training examples correctly.”

- **total slack**: ζ_i = 0 for points outside the street; 0 < ζ_i ≤ 1 inside the street but on the right side; ζ_i > 1 misclassified.

- **relaxed constraint**: Each point may fall short of score 1 by its slack.

- **slack is never negative**: Being far outside the street earns no credit.

Ringed points are support vectors: every point on or inside the street, plus every misclassified one. Small C: a wide street with many support vectors (each paying a little). Large C: a narrow street that tries to fix individual violations.

On this batch, support vectors fall from 65 at C = 0.01 to about 25 at C = 1, and test accuracy sits in a narrow band (83–87%), best near C = 1. The noise sets a ceiling no C can beat. scikit-learn's advice: "C is 1 by default and it's a reasonable default choice. If you have a lot of noisy observations you should decrease it" [SVM guide](https://scikit-learn.org/stable/modules/svm.html).

#### The hinge loss: only the street pulls

At the optimum each slack equals exactly max(0, 1 − yif(xi)). Substituting turns the soft-margin SVM into ordinary regularised loss minimisation, the form `SGDClassifier(loss="hinge")` uses:

$$ \min_{w,b}\ \frac1n\sum_i {\max\bigl(0,\ 1 - {y_i f(x_i)}\bigr)} + {\tfrac{\lambda}{2}\lVert w\rVert^2} $$

- **hinge loss**: Zero once a point is safely outside the street (y·f ≥ 1); grows linearly the further it intrudes.

- **the functional margin**: y_i f(x_i): positive and large is good. Called the margin on the plot below.

- **L2 regulariser**: λ = 1/(nC) up to scaling: large C means weak regularisation.

Both hinge and logistic loss are convex stand-ins for the 0–1 loss (the thing we actually count). The difference: logistic loss is never exactly zero, so every training point keeps pulling a little. Hinge loss is **exactly zero** past the street, so far-away points drop out of the solution. That is where the sparsity (support vectors) comes from.

#### Bend the boundary by lifting the data

1. One sensor reading. Parts in the middle pass; extreme readings on either side fail. No single threshold works.

2. Add a feature: x². Each point is lifted onto a parabola. The middle points stay low; the extremes rise.

3. In this two-feature space, one straight line separates them perfectly.

4. Projected back to the original line, that straight line becomes two thresholds: a non-linear rule from a linear model.

5. The trick: the SVM's training and prediction only ever use dot products between points. Replace each dot product with a function K(x, z) that equals φ(x)·φ(z), and you never compute φ at all. The RBF kernel's φ is infinite-dimensional, yet K costs one exponential.

Why do only dot products appear? Solving the soft-margin problem through its **dual** gives w = Σ αiyixi, a weighted sum of training points with αi > 0 only for support vectors. Plug that into the score:

$$ f(x) = {\sum_{i\in SV}} {\alpha_i}\,{y_i}\,{K(x_i, x)} + {b} $$

scikit-learn's decision function for SVC, and its kernel list (linear, polynomial, RBF, sigmoid) [SVM guide](https://scikit-learn.org/stable/modules/svm.html). The kernel idea for maximum-margin classifiers is from Boser, Guyon & Vapnik (1992).

- **sum over support vectors**: Only points with α_i > 0 contribute; the rest of the training set can be thrown away after training.

- **learned weight**: α_i is between 0 and C (box constraint). α_i = C means the point is inside the street or misclassified.

- **its label**: Pass parts vote +, fail parts vote −.

- **similarity**: K(x_i, x): the kernel. Linear: x_i·x. RBF: exp(−γ‖x_i − x‖²). Polynomial: (γ x_i·x + r)^d.

- **offset**: The intercept; predicted class = sign of the whole thing.

**Go deeper: the dual problem and what makes a valid kernel**

The Lagrangian dual of the soft-margin SVM is: maximise Σαi − ½ΣΣ αiαjyiyjK(xi, xj) subject to 0 ≤ αi ≤ C and Σαiyi = 0. The data appear only through K. A function is a valid kernel (it equals φ(x)·φ(z) for some φ) when every Gram matrix it produces is symmetric positive semi-definite (Mercer's condition). The sigmoid "kernel" can fail this, which is one reason it's rarely used.

The SMO algorithm (Platt, 1998), the basis of libsvm, solves the dual by repeatedly optimising two α's at a time in closed form. The solver on this page is a simplified SMO.

#### Support vector regression: a tube instead of a street

SVMs can also predict numbers. Classification wants points outside the street. Regression does the opposite: it wants points **inside a tube** of width ε around the prediction, and errors within it cost nothing.

$$ \min_{w,b,\zeta,\zeta^*}\ {\tfrac12\lVert w\rVert^2} + {C\sum_i(\zeta_i + \zeta_i^*)} \quad \text{s.t.} \quad {|y_i - f(x_i)| \le \varepsilon + \text{slack}} $$

Written compactly. The full form has separate slacks above and below, as in scikit-learn’s guide.

- **keep it flat**: A short w gives a flatter, simpler function.

- **pay for leaving the tube**: ζ and ζ* measure how far a point lies above or below the tube. C sets the price.

- **the ε-tube**: Errors smaller than ε are ignored completely.

**A worked example, with illustrative numbers.** Take ε = 2 minutes and a prediction of 30. An actual of 31 costs 0, as it's inside the tube. An actual of 35 is 5 away, so it costs 5 − 2 = 3.

- **Support vectors:** points on or outside the tube. Points inside it don't affect the solution, as with points beyond the street in classification.

- **Larger ε:** a wider tube, fewer support vectors and a simpler fit.

- **Larger C:** stricter about points outside the tube, so it fits more closely.

- **Kernels and scaling:** these work as in classification. So do the training costs, so large data needs a linear version.

- **Outliers:** the penalty grows linearly, not with the square, so one far point has less pull than in least squares.

Source: [scikit-learn on SVR](https://scikit-learn.org/stable/modules/svm.html#svm-regression).

## In practice

### In practice

#### Where SVMs sit among linear classifiers

| Method | Loss it minimises | What you get |
|---|---|---|
| **Perceptron** | Mistakes only (any separating line) | Some line; depends on order |
| **Logistic regression** | Log loss: every point pulls a little | Calibrated-ish probabilities |
| **Linear SVM** | Hinge loss + ‖w‖²: only points inside the street pull | The max-margin line; sparse in the data (support vectors) |
| **Kernel SVM** | Same, with K(x, z) instead of x·z | Curved boundaries; cost grows ~n² to n³ |

In scikit-learn: `SVC` (libsvm, any kernel), `LinearSVC` (liblinear, linear only, scales to large n) and `SGDClassifier(loss="hinge")` for very large or streaming data [SVM guide](https://scikit-learn.org/stable/modules/svm.html).

#### Training cost, and scores that aren't probabilities

##### Training cost

Kernel SVMs solve a quadratic program over n points. scikit-learn: the libsvm solver "scales between O(nfeatures × nsamples2) and O(nfeatures × nsamples3)" [SVM guide](https://scikit-learn.org/stable/modules/svm.html). Double the data, roughly 4–8× the training time; past a few hundred thousand rows kernel SVC becomes impractical. Linear SVMs (liblinear, SGD) scale roughly linearly, and kernel approximations (Nyström, random Fourier features) feed a linear SVM.

##### No native probabilities

The SVM score is a distance, not a probability. With `probability=True`, scikit-learn fits Platt scaling (a logistic regression on the scores) with an extra cross-validation, which is expensive, and "the probability estimates may be inconsistent with the scores": predict can say positive while predict_proba says below 0.5 [SVM guide](https://scikit-learn.org/stable/modules/svm.html). If you only need a ranking, use `decision_function`.

#### Training an SVM, end to end

1. **Scale** every feature (StandardScaler), fitted on training data only.

2. **Pick the kernel:** linear when features are many and sparse (text, nfeatures ≫ n) or n is large; RBF otherwise.

3. **Grid-search C and γ** on a log scale (e.g. C ∈ 10−2…3, γ ∈ 10−4…1) with cross-validation.

4. **Imbalanced classes:** `class_weight="balanced"` scales C per class.

5. **Need probabilities?** Calibrate separately (CalibratedClassifierCV) or use decision_function for ranking.

6. **Check the support-vector count:** close to n means overfitting or a poor kernel.

Multi-class: SVC trains one-vs-one classifiers (k(k−1)/2 of them); LinearSVC uses one-vs-rest [SVM guide](https://scikit-learn.org/stable/modules/svm.html).

#### When to use it

##### Use an SVM when

- n is small to medium (up to tens of thousands) and you want a strong, tunable model

- Features are many and sparse (text): a linear SVM is fast and strong

- You need a margin-based, convex, reproducible model

##### Reach for something else when

- Millions of rows: linear models, SGD, or gradient boosting

- Mixed-type tabular data: gradient-boosted trees are the default

- Images, audio, raw text: deep networks

- You need calibrated probabilities: logistic regression or a calibrated model

### The answer that sounds right

#### "Any line that separates the training data is fine"

The perceptron (Rosenblatt, 1958) does exactly this: it nudges the line whenever a point is on the wrong side, and stops at the first line with zero training errors. Which line it stops at depends on the order it sees the parts. Shuffle the order and look:

Dashed red: perceptron line. Violet: the maximum-margin line and its street. Both have 100% training accuracy. Test accuracy uses 3,000 new parts.

Over 30 shuffles, the perceptron's test accuracy ranged from **94.5% to 98.9%** (mean 97.4%); the maximum-margin line scored **98.5%**, and 8 of the 30 perceptron lines happened to beat it. So the honest claim is not "max margin always wins on test". It's that max margin gives **one unique answer** that never hugs a training point, which removes the worst cases. The theory backs this up: a wider margin means a smaller capacity term in the generalisation bound [Cortes & Vapnik 1995](https://doi.org/10.1007/BF00994018).

#### Caveats

##### Strengths

- Convex problem: one global optimum, no random restarts

- "Effective in high dimensional spaces", even when features outnumber samples (scikit-learn)

- Sparse solution: prediction uses only support vectors

- Kernels give flexible boundaries with two knobs (C, γ)

##### Weaknesses

- n² to n³ training: slow beyond ~105 rows for kernel SVC

- Needs feature scaling and a joint C/γ search

- No native probabilities; Platt scaling is costly and can disagree with predict

- A kernel model is hard to interpret; you can't read feature effects off it

## Say it

### What does an SVM optimise, and what are support vectors?

#### The interviewer pushes further

Follow-up 1 of 6

What happens as C → ∞? C → 0?

C → ∞ forbids violations: the hard-margin SVM (no solution if the data isn't separable; very sensitive to outliers). C → 0 makes violations free, so the margin grows huge and almost every point becomes a support vector; the model underfits.

Follow-up 2 of 6

Why does the kernel trick work?

In the dual, data appear only as dot products xi·xj, and prediction is ΣαiyiK(xi, x) + b. Any positive semi-definite K equals a dot product in some feature space (Mercer), so we get a linear separator there for the cost of evaluating K.

Follow-up 3 of 6

SVM vs logistic regression?

Both are linear with a convex loss. Hinge loss is zero past the margin, so SVMs are sparse in the data and focus on the boundary; log loss gives every point some weight and produces probabilities. With good regularisation their accuracy is usually similar; logistic regression is preferred when you need probabilities, SVM with kernels when the boundary is non-linear and n is moderate.

Follow-up 4 of 6

How do you choose γ for RBF?

Cross-validated log-scale grid jointly with C. Large γ: narrow bumps, wiggly boundary, many SVs (overfit). Small γ: nearly linear (underfit). scikit-learn's default gamma="scale" is 1 / (n_features × Var(X)).

Follow-up 5 of 6

Does an SVM output probabilities?

Not natively. Platt scaling fits a sigmoid on cross-validated scores; it costs extra training and can disagree with predict. Use decision_function for ranking, or calibrate separately.

Follow-up 6 of 6

How does an SVM do multi-class?

By combining binary SVMs: SVC uses one-vs-one (k(k−1)/2 classifiers, majority vote); LinearSVC uses one-vs-rest.

#### The 30-second answer

An SVM finds the separating hyperplane with the largest margin, which means minimising ½‖w‖² subject to every point having score at least 1 on its side. Only the points on or inside the margin, the support vectors, determine the solution. For overlapping data, the soft margin adds slack penalised by C, which is equivalent to hinge loss plus L2 regularisation. Small C gives a wide, smooth margin; large C fits the training points. The kernel trick replaces dot products with a kernel such as RBF, giving non-linear boundaries without building the feature map. Gamma controls how local each support vector's influence is. Scale features first, tune C and gamma together, and remember training is between quadratic and cubic in n.

**Go further**

#### What not to say

- "The SVM maps data to infinite dimensions." With RBF the implicit space is infinite-dimensional, but nothing is ever mapped; only K is computed.

- "All training points define the boundary." Only support vectors do.

- "Higher C is always better." It lowers training error and often raises test error.

- "SVMs don't need scaling." They do; kernels and margins are distance-based.

**Key terms and sources**

Maximum margin, soft margin and C, hinge loss, the kernel trick, RBF γ · built from Cortes & Vapnik (1995), Boser, Guyon & Vapnik (1992) and scikit-learn's SVM guide · checked 28 Oct 2026

#### The 1995 digit results that made SVMs famous

##### USPS handwritten digits: test error by polynomial degree

Cortes & Vapnik, Table 2. 7,300 training and 2,000 test images of 16×16 pixels. Lower is better.

degree 1 (linear) · 200 SVs

12.0%

degree 2 · 127 SVs

4.7%

degree 3 · 148 SVs

4.4%

degree 4 · 165 SVs

4.3%

degree 6 · 185 SVs

4.2%

degree 7 · 190 SVs

4.3%

Degree 5 also gave 4.3% (175 SVs). Going from linear to quadratic cut the error by more than half; higher degrees changed little, and the number of support vectors grew only slowly. [Machine Learning 20](https://doi.org/10.1007/BF00994018)

##### Against other methods on the same USPS data (Table 1)

human performance

2.5%

SVM, polynomial (best)

4.2%

LeNet1 (conv net)

5.1%

best 2-layer neural net

6.6%

C4.5 decision tree

16%

CART decision tree

17%

The comparison figures are as reported in the paper, from other authors' runs. On the larger NIST digits (60,000 training images) a degree-4 polynomial SVM reached 1.1% test error. The authors stress the SVM used no knowledge of images: it "would do as well if the image pixels were encrypted" [Cortes & Vapnik 1995](https://doi.org/10.1007/BF00994018).

##### A bound you can read off the solution

Leave-one-out argument from the paper: the expected test error is at most E[number of support vectors] / n. Removing a non-support vector doesn't change the solution, so it can't be misclassified in leave-one-out. On USPS the ratio was as low as 0.03 [Cortes & Vapnik 1995](https://doi.org/10.1007/BF00994018). That's why "fewer support vectors" is a healthy sign.

##### Update · my check

Those comparisons are from 1995. Convolutional networks trained on far more data and compute now dominate image recognition, and gradient-boosted trees usually win on tabular data. SVMs remain a strong, well-understood choice for small-to-medium datasets, high-dimensional sparse features (linear SVMs on text), and as a baseline.

#### Key terms

| Term | Meaning |
|---|---|
| **Margin** | Distance from the boundary to the closest points; the street is 2/‖w‖ wide. |
| **Support vectors** | Training points with α > 0: on the street's edge, inside it, or misclassified. |
| **Slack ζ** | How far a point violates its margin. |
| **C** | Price of violations. Low: smooth, wide margin. High: fit the training points. |
| **Hinge loss** | max(0, 1 − y·f(x)). |
| **Kernel** | K(x, z) = φ(x)·φ(z): a dot product in a feature space you never build. |
| **γ (RBF)** | Inverse reach of each support vector's bump. |
| **Dual / SMO** | The optimisation over α's; SMO solves it two α's at a time. |

#### What this page is built from

1. C. Cortes & V. Vapnik, "Support-vector networks", _Machine Learning_ 20, 273–297, 1995, [doi:10.1007/BF00994018](https://doi.org/10.1007/BF00994018) (soft margin, USPS/NIST results, Tables 1–2, the support-vector bound).

2. B. Boser, I. Guyon & V. Vapnik, "A training algorithm for optimal margin classifiers", COLT 1992 (maximum margin with kernels).

3. scikit-learn, [Support Vector Machines user guide](https://scikit-learn.org/stable/modules/svm.html) (formulations, kernels, C and γ, complexity, scaling, Platt scaling caveats, multi-class).

4. J. Platt, "Sequential Minimal Optimization", Microsoft Research TR-98-14, 1998 (SMO; background).

5. F. Rosenblatt, "The perceptron", _Psychological Review_, 1958 (the naive baseline; background).

All datasets are simulated with fixed seeds; every SVM on this page is trained live in your browser by a simplified SMO solver.
