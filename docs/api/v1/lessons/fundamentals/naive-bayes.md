# Naive Bayes

> Its core assumption is almost always wrong. Why does it still classify so well?

- Track: Fundamentals › Classical ML › Other classic classifiers
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/naive-bayes/
- Before this: Probability Basics & Bayes' Rule (`fundamentals/probability-and-bayes`)
- Quiz topic: `clf`

## Intuition

### The situation

You're building a spam filter from 100 messages. Almost every message is unique, so you can't just count how often each whole message is spam. The interviewer asks:

> What is naive about naive Bayes?

**Running example:** a small spam filter. Its training mail has 40 spam and 60 ham messages, and a vocabulary of six words. The counts below are illustrative (made up to be easy to follow), and every probability on the page is computed live from them. Later chapters use simulated numeric data for Gaussian naive Bayes.

#### Reverse the question

| word | free | win | offer | meeting | project | lunch | total |
|---|---|---|---|---|---|---|---|
| **count in spam** | 30 | 20 | 25 | 2 | 3 | 0 | 80 |
| **count in ham** | 4 | 1 | 5 | 30 | 35 | 25 | 100 |

We want P(spam | this message). That's hard to estimate directly: almost every message is unique. The reverse is easy to count: how often does the word "free" appear in spam? Bayes' rule turns the easy direction into the one we need. The only obstacle is that a message has many words, and counting every combination of words is hopeless. Naive Bayes removes that obstacle with one bold assumption.

### The idea

Think of a detective who treats every clue as if it were independent of the others. That's rarely true, because clues are often linked. But it makes the case easy to work through, and the detective usually names the right suspect, just with too much confidence.

[Figure: The words free, offer and meeting each multiply the spam score and the ham score separately, giving a 76 percent chance of spam.]

_From the lesson's spam example, with Laplace smoothing._

### Play

**Try to break it.** Build a message with the word "lunch" in it, and set the smoothing as low as it goes. Then raise it.

#### One unseen word must not veto everything

"lunch" never appeared in our spam, so the raw estimate P(lunch | spam) = 0/80 = 0. Any message containing "lunch" then gets P(spam) = 0, however spammy its other words. The fix is to add α imaginary occurrences of every word:

$$ {\hat\theta_{yi}} = ({N_{yi}} + {\alpha}) \,/\, ({N_y + \alpha n}) $$

scikit-learn: the smoothing priors "account for features not present in the learning samples and prevent zero probabilities" [naive Bayes guide](https://scikit-learn.org/stable/modules/naive_bayes.html).

- **smoothed estimate**: P(word i | class y) used by Multinomial naive Bayes.

- **count of word i in y**: How many times word i appeared in class-y training mail. 0 for lunch in spam.

- **pseudo-count**: α = 1 is Laplace smoothing; α < 1 is Lidstone smoothing. Treat it as a hyperparameter.

- **total words in y, plus α per word**: N_y + αn: n is the vocabulary size (6 here), so the probabilities still sum to 1.

Bars: each word's log-likelihood ratio, log P(word | spam) − log P(word | ham). Right = evidence for spam, left = for ham. Set α = 0 and pick "free win lunch".

With α = 0, "free win lunch" scores P(spam) = **0**, a certain "ham", even though two of its three words are strongly spammy: "lunch" vetoes the spam class. With α = 0.1 it's 0.41, and with Laplace α = 1 it's **0.76**. Words that are never seen in _either_ class at prediction time are simply skipped.

**Now say why:** why can one unseen word overrule everything else in the message?

## Maths

### Maths

#### In one breath

Naive Bayes classifies by asking "which class makes this input most likely?", using Bayes' rule. It makes one big simplification: given the class, every feature is **independent**, so the likelihood is just a product of one-feature probabilities you can count from data. That makes it tiny, instant to train, and good with little data, which is why it was the classic spam filter. Two practical fixes are mandatory: **smoothing** (an unseen word must not zero out a class) and **log space** (products of many small numbers underflow). The independence assumption is almost always false, yet the **ranking** of classes often survives; the **probabilities** don't: they're pushed towards 0 and 1. What you'll be able to do after this: classify a message by hand, explain smoothing with a concrete failure, pick the right variant, and explain why naive Bayes can be accurate but badly calibrated.

#### Bayes' rule, term by term

$$ {P(y \mid x)} = {P(y)}\;{P(x \mid y)} \,/\, {P(x)} $$

- **posterior**: What we want: the probability the message is class y (spam or ham) given its words x.

- **prior**: How common the class is before reading anything: 40 of 100 training messages were spam, so P(spam) = 0.4.

- **likelihood**: How probable these words are if the message were class y. This is the part we have to model.

- **evidence**: P(x): the same for every class, so for choosing the class we can ignore it and just compare numerators.

#### Given the class, treat every feature as independent

$$ {\hat y} = \arg\max_y\ {P(y)}\ {\prod_{i=1}^{n}} {P(x_i \mid y)} $$

scikit-learn: naive Bayes applies Bayes' theorem "with the 'naive' assumption of conditional independence between every pair of features given the value of the class variable" [naive Bayes guide](https://scikit-learn.org/stable/modules/naive_bayes.html).

- **predicted class**: Pick the class with the biggest score. P(x) is dropped because it's the same for all classes.

- **prior**: Class frequency in training data.

- **the naive product**: Instead of one impossible joint probability, multiply one small probability per feature. With 50,000 words that's 50,000 numbers per class instead of 2^50,000.

- **one-feature likelihood**: Estimated by counting: how often word i appears in class y. Gaussian NB uses a per-class mean and variance instead.

1. A new message with three words from our vocabulary.

2. Start each class with its prior: 40% of training mail was spam, 60% ham.

3. Multiply by P("free" | class). With Laplace smoothing (try it in the Play lab): spam (30 + 1)/(80 + 6), ham (4 + 1)/(100 + 6).

4. Then "offer" and "meeting", each as if it were independent of the others given the class.

5. Compare the two products. Divide each by their sum to get probabilities: about 0.76 spam. "free" and "offer" pull towards spam; "meeting" pulls hard towards ham.

#### Products underflow; sums don't

A 1,000-word email multiplies 1,000 probabilities, each maybe 0.001. The product, 10−3000, is far below the smallest positive double (about 10−308), so the computer stores 0 for both classes and can't compare them. Taking logs turns the product into a sum, which keeps the comparison exact:

$$ {\text{score}(y)} = {\log P(y)} + {\sum_{i} \log P(x_i \mid y)} $$

- **class score**: A log score per class: compare these, the biggest wins. Exponentiate and normalise (softmax) only if you want probabilities.

- **log prior**: log 0.4 for spam, log 0.6 for ham.

- **sum of log likelihoods**: Each word adds its log probability. The bars in the lab are differences of these terms between the two classes.

Seen this way, Multinomial naive Bayes is a **linear model** in the word counts: each word has a weight (its log probability per class). It's the same functional form as logistic regression; only the way the weights are found differs (counting vs optimising).

#### Gaussian naive Bayes: one bell curve per feature per class

$$ {P(x_i \mid y)} = {(2\pi\sigma_{y}^2)^{-1/2}}\ \exp\!\Bigl({-(x_i - \mu_{y})^2 / (2\sigma_{y}^2)}\Bigr) $$

scikit-learn's GaussianNB likelihood (σ and μ per class and feature) [naive Bayes guide](https://scikit-learn.org/stable/modules/naive_bayes.html).

- **one-feature likelihood**: For numeric feature i: how likely its value is under class y.

- **normaliser**: Makes the bell curve integrate to 1; it depends on the class variance.

- **squared distance from the class mean**: Measured in units of that class's standard deviation for this one feature. Means and variances are estimated by maximum likelihood.

Multiplying per-feature bell curves is a Gaussian with a **diagonal** covariance: its contours are ellipses aligned with the axes. It can't represent "these two features move together". Raise the correlation below and compare with a full-covariance Gaussian model (quadratic discriminant analysis), which can:

Shading: Gaussian NB's decision regions. Ellipses: the 2σ contour each model fits for each class (orange dashed = NB, axis-aligned; violet = full covariance). Simulated: 200 training and 4,000 test points.

With uncorrelated features both models score 76.1%. At correlation 0.95, naive Bayes gets **95.0%** and the full model **99.9%**: the classes are separated along a diagonal direction that only the correlation reveals. Naive Bayes still does reasonably, which is the theme of this page: wrong assumption, decent decisions.

For shared and full covariances, see LDA and QDA.

## In practice

### In practice

#### Generative vs discriminative

There are two ways to build a classifier. **Discriminative** models (logistic regression, SVMs, trees) learn P(y | x) or the boundary directly. **Generative** models learn how each class produces data, P(x | y) and P(y), then use Bayes' rule. Naive Bayes is the simplest generative classifier. Ng & Jordan (2001) compared it with its discriminative twin, logistic regression: logistic regression has the lower error with lots of data, but naive Bayes "may also approach its (higher) asymptotic error much faster" [NIPS 2001](https://papers.nips.cc/paper/2001/hash/7b7a53e239400a13bd6be6c91c4f6c4e-Abstract.html). With little data naive Bayes often wins; with lots, logistic regression catches up and passes it.

#### The naive Bayes family

| Variant | Feature type | Notes |
|---|---|---|
| **GaussianNB** | Continuous | Per-class mean and variance per feature |
| **MultinomialNB** | Counts (word counts, TF-IDF also works in practice) | The classic text classifier; smoothing α |
| **BernoulliNB** | Binary present/absent | "explicitly penalizes the non-occurrence of a feature i that is an indicator for class y, where the multinomial variant would simply ignore a non-occurring feature" |
| **ComplementNB** | Counts, imbalanced classes | Uses statistics from the complement of each class; "regularly outperforms MNB (often by a considerable margin) on text classification tasks" (Rennie et al. 2003) |
| **CategoricalNB** | Categorical (ordinal-encoded) | Its own categorical distribution per feature |

All from scikit-learn's naive Bayes guide [docs](https://scikit-learn.org/stable/modules/naive_bayes.html). Every variant supports `partial_fit`, so it can learn from a stream in batches.

#### A text classifier, step by step

1. **Vectorise**: word counts (CountVectorizer) or TF-IDF.

2. **Choose the variant**: Multinomial or Complement for counts, Bernoulli for short texts as presence/absence, Gaussian for numeric features.

3. **Tune α** by cross-validation (try 0.01–1).

4. **Train**: one pass of counting, O(n × features).

5. **Calibrate** if you'll threshold or average the probabilities.

#### When to use it

##### Use naive Bayes when

- Text classification baseline: spam, topics, sentiment, routing tickets

- Very little training data, or data arrives as a stream

- You need training and prediction to be nearly free

##### Reach for something else when

- You need trustworthy probabilities (calibrate or use logistic regression)

- Features interact strongly: trees, boosting

- Plenty of data: logistic regression, boosting or fine-tuned transformers usually win on text

### The answer that sounds right

#### "Just count P(x | y) for whole messages"

Modelling P(x | y) exactly means estimating the probability of every possible combination of words. With only our 6 words treated as present/absent there are 26 = 64 combinations per class; with a realistic 50,000-word vocabulary there are 250,000. You will never see most combinations even once, so their counted probability is 0, and any new message would get probability zero under both classes. Exact Bayes is right in theory and impossible in practice.

#### Correlated features are counted twice

Suppose a tokenizer produces "free", "FREE" and "free!" as separate features, and they always appear together. They're one piece of evidence, but naive Bayes treats them as three independent ones and multiplies the same likelihood ratio three times. The class it picks often stays the same; the confidence explodes.

Simulated: one numeric feature, class 0 ~ N(0, 1), class 1 ~ N(1.5, 1), equal priors. Violet: the true probability. Red: naive Bayes after copying the feature k times. Same 0.5 crossing, so the same decisions; a steeper, overconfident curve.

Accuracy stays at **77.4%** for any number of copies, while log loss rises from 0.47 to 1.02 at 5 copies, and the predictions it is "more than 95% sure" about are right only 83.8% of the time. This is Domingos & Pazzani's point: naive Bayes can be optimal under zero–one loss even when the independence assumption is clearly violated, because classification only needs the right class to come out on top, not the right probability [Machine Learning 29](https://doi.org/10.1023/A:1007413511361). scikit-learn: naive Bayes "is known to be a decent classifier, [but] it is known to be a bad estimator, so the probability outputs from predict_proba are not to be taken too seriously" [naive Bayes guide](https://scikit-learn.org/stable/modules/naive_bayes.html).

##### The fix when you need probabilities

Calibrate the outputs on held-out data (`CalibratedClassifierCV` with isotonic or sigmoid calibration), or switch to logistic regression. Ranking metrics like ROC-AUC are unaffected by this kind of overconfidence; log loss and Brier score are not. See Probability metrics.

#### Caveats

##### Strengths

- Trains in one counting pass; predicts instantly; tiny model

- "require a small amount of training data" (scikit-learn)

- Handles thousands of sparse features; streams with partial_fit

- A strong, honest baseline for text

##### Weaknesses

- Overconfident, poorly calibrated probabilities

- Double-counts correlated features

- Can't model interactions ("free" is spammy unless next to "lunch")

- Usually beaten by logistic regression or boosting once data is plentiful

## Say it

### What is naive about naive Bayes?

#### The interviewer pushes further

Follow-up 1 of 6

Why is it called "naive"?

Because of the conditional independence assumption: given the class, knowing one feature tells you nothing about another. It's almost never true (words co-occur), but it turns an impossible estimation problem into many easy ones.

Follow-up 2 of 6

What is Laplace smoothing and why do you need it?

Adding α pseudo-counts to every feature count (α = 1 is Laplace). Without it, a word never seen with a class gives that class probability zero for any message containing it, no matter what else the message says.

Follow-up 3 of 6

Why does it classify well if the assumption is wrong?

Classification needs only the correct class to have the highest score. Violated independence distorts the scores, often by pushing them to extremes in the same direction, so the argmax frequently survives (Domingos & Pazzani 1997). The probabilities don't.

Follow-up 4 of 6

Naive Bayes vs logistic regression?

A generative–discriminative pair: Multinomial NB is linear in the counts, like logistic regression. NB fits weights by counting, LR by optimising the conditional likelihood. NB converges faster with little data; LR reaches lower error with more data and gives better-calibrated probabilities (Ng & Jordan 2001).

Follow-up 5 of 6

Multinomial vs Bernoulli NB?

Multinomial models word counts and ignores absent words. Bernoulli models presence/absence and penalises the absence of an indicative word. Bernoulli can do better on short texts; Multinomial on longer documents.

Follow-up 6 of 6

How do you handle continuous features?

Gaussian NB (per-class mean and variance per feature), or discretise into bins and use Categorical/Multinomial NB. Strongly non-Gaussian features may need a transform first.

#### The 30-second answer

Naive Bayes is a generative classifier: it uses Bayes' rule, P(y | x) ∝ P(y) P(x | y), and assumes the features are conditionally independent given the class, so P(x | y) factorises into a product of per-feature probabilities that you estimate by counting. You smooth the counts so unseen features don't give zero probability, and you compute in log space to avoid underflow. It's very fast and works well with little data, especially for text, but because the independence assumption is usually wrong, it double-counts correlated evidence and its probabilities are overconfident even when its classifications are good.

**Go further**

#### What not to say

- "Naive Bayes assumes features are independent." Conditionally independent _given the class_.

- "Its predict_proba is a reliable risk score." It's typically overconfident; calibrate first.

- "Smoothing is optional." Without it, one unseen word zeroes out a class.

**Key terms and sources**

Bayes' rule, the independence assumption, Laplace smoothing, log space, Gaussian/Multinomial/Bernoulli/Complement variants, why it classifies well but estimates badly · built from scikit-learn's naive Bayes guide, Domingos & Pazzani (1997), Ng & Jordan (2001) and Rennie et al. (2003) · checked 28 Oct 2026

#### Why a wrong model works

##### Optimal decisions despite violated independence

Domingos & Pazzani (1997) showed that the naive Bayes classifier is optimal under zero–one loss for a far larger set of problems than those where independence holds, because it only needs the true class to get the highest score. Their experiments on UCI datasets found it competitive with decision-tree and rule learners even where features were clearly dependent [Machine Learning 29](https://doi.org/10.1023/A:1007413511361). They also note the corollary: the probability estimates themselves can be far off.

##### Faster to its (higher) error than logistic regression

Ng & Jordan (2001): discriminative logistic regression has the lower asymptotic error, but generative naive Bayes approaches its own asymptote with far fewer examples; in their analysis, a number that grows only logarithmically with the number of features, versus linearly for logistic regression. On UCI datasets they observed the two regimes: naive Bayes ahead at small training sizes, logistic regression ahead later [NIPS 2001](https://papers.nips.cc/paper/2001/hash/7b7a53e239400a13bd6be6c91c4f6c4e-Abstract.html).

##### This page's simulations

log loss, 1 copy of the feature

0.47

log loss, 3 copies

0.68

log loss, 5 copies

1.02

Accuracy was 77.4% in all three. Lower log loss is better. Illustrative simulation, from the double-counting lab.

#### Key terms

| Term | Meaning |
|---|---|
| **Prior / likelihood / posterior** | P(y), P(x \| y), P(y \| x). |
| **Conditional independence** | Given the class, features carry no information about each other. |
| **Laplace / Lidstone smoothing** | Add α (= 1 / < 1) pseudo-counts so nothing has probability 0. |
| **Generative vs discriminative** | Model P(x \| y) and P(y) vs model P(y \| x) directly. |
| **Calibration** | Whether predicted probabilities match observed frequencies. |

#### What this page is built from

1. scikit-learn, [Naive Bayes user guide](https://scikit-learn.org/stable/modules/naive_bayes.html) (assumption, decision rule, Gaussian/Multinomial/Bernoulli/Complement/Categorical variants, smoothing, "bad estimator" caveat).

2. P. Domingos & M. Pazzani, "On the optimality of the simple Bayesian classifier under zero-one loss", _Machine Learning_ 29, 103–130, 1997, [doi:10.1023/A:1007413511361](https://doi.org/10.1023/A:1007413511361).

3. A. Ng & M. Jordan, "On discriminative vs. generative classifiers: a comparison of logistic regression and naive Bayes", [NIPS 2001](https://papers.nips.cc/paper/2001/hash/7b7a53e239400a13bd6be6c91c4f6c4e-Abstract.html).

4. J. Rennie, L. Shih, J. Teevan & D. Karger, "Tackling the poor assumptions of naive Bayes text classifiers", ICML 2003 (Complement NB; cited by scikit-learn).

Word counts are illustrative; numeric data is simulated with fixed seeds; every probability on the page is computed live in your browser.
