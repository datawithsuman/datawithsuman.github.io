# Mutual Information

> What is mutual information, and when would it find a relationship that correlation misses?

- Track: Fundamentals › Maths for ML › Information theory
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/mutual-information/
- Before this: Entropy, Cross-Entropy & KL Divergence (`fundamentals/entropy-cross-entropy-kl`), Joint, Marginal and Conditional Distributions (`fundamentals/joint-marginal-conditional`)
- Related: Decision Trees (`fundamentals/decision-trees`)
- Quiz topic: `info`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: 79dff987d8

## Intuition

### The situation

You're choosing features for a model. A correlation table says that time of day has no relationship with orders, yet the plot clearly shows peaks at lunch and dinner. A colleague filters features one at a time, and drops two that work only together. The interviewer asks:

> What is mutual information, and when would it find a relationship that correlation misses?

#### Why it matters

Correlation only sees straight lines. Mutual information gives a general way of asking whether two things are related, and it appears in decision trees, feature selection, clustering scores and contrastive learning. It builds on entropy and joint distributions.

### The idea

Think of playing 20 questions. A good question halves your uncertainty, and a bad one tells you nothing. Mutual information measures how many of those questions one variable answers about another. It doesn't care about straight lines, only how much you've learned.

[Figure: Correlation against mutual information. Correlation sees straight-line links, and misses a U-shape. Mutual information sees any link, and is harder to estimate.]

_Mutual information is zero only when the variables are independent._

### Play

**Try to break it.** Compare the U-shape with none. Then raise the noise.

#### Correlation against mutual information

Our seeded simulation with 5,000 points. Mutual information is estimated from a 12 × 12 histogram, which has a small upward bias, as you'll see on the "none" setting. The number depends on the bins, so treat it as a guide.

The **U-shape** has a correlation near zero, though y clearly depends on x. Now pick **none**: both are near zero, and the small mutual information you see is estimation bias. Raise the noise on the U-shape, and mutual information falls, as x tells you less about y.

**Now say why:** why is the correlation near zero for a U-shape?

## Maths

### Maths

#### In one breath

**Mutual information** measures how much knowing one variable reduces uncertainty about another: I(X; Y) = H(Y) − H(Y | X). It's zero **only if they're independent**, so unlike correlation, it catches curved and other non-linear relationships. It's the same as **information gain** in decision trees. It helps with feature selection, though it looks at features one at a time, and it's hard to estimate in high dimensions.

#### Reduced uncertainty

##### Building it up

| Quantity | Question |
|---|---|
| **H(Y)** | How uncertain is Y? |
| **H(Y \| X)** | How uncertain is Y, on average, once I know X? |
| **I(X; Y)** | How much did knowing X help? |

It's symmetric: X tells you as much about Y as Y tells you about X. It's also the KL divergence between the joint distribution and the product of the marginals, or how far the pair is from being independent.

##### In decision trees

Say half of the orders are late, so H(Y) = 1 bit. A feature splits them into two equal groups, where 90% are late in one, and 10% in the other. H(Y | X) = 0.469 bits, so the **information gain** is 0.531 bits. That's exactly mutual information, and trees pick the split with the most.

##### Mutual information or correlation?

| | Correlation | Mutual information |
|---|---|---|
| **Detects** | Straight-line relationships | Any relationship |
| **Zero means** | No linear link | Independent |
| **Direction** | Shows the sign | Doesn't show it |
| **Estimating** | Easy, and stable | Harder, and needs more data |

##### Using it for feature selection

- **It's a filter:** rank features by their mutual information with the label.

- **Redundancy:** two copies of a good feature both score high, though the second adds nothing.

- **Interactions:** with XOR, each feature alone has zero mutual information with the label, while together they predict it perfectly. A one-at-a-time filter drops both.

##### Rules worth knowing

- **Data processing inequality:** processing a signal can't add information about the source. Each network layer can only keep or lose information about the input, though it can make it easier to use.

- **InfoNCE:** contrastive learning maximises a lower bound on mutual information between views. The bound can't exceed log N for N examples, one reason why larger batches can help. See contrastive learning.

- **Clustering:** normalised mutual information compares clusters with labels, ignoring how clusters are named.

#### The maths

$$ {I(X; Y)} = {H(Y)} - {H(Y \mid X)} = {\sum_{x,y} p(x, y) \log \frac{p(x, y)}{p(x)\,p(y)}} $$

For jointly Gaussian variables, I = −½ log(1 − ρ²). So for those, correlation tells you everything, and mutual information adds nothing.

- **mutual information**: Uncertainty removed. It’s never negative, and it’s zero only when they’re independent.

- **uncertainty about Y**: Before you know anything else.

- **uncertainty left**: Averaged across values of X.

- **as a KL divergence**: Compares the real joint with what independence would predict.

## In practice

### In practice

#### In practice

- **Estimating it is hard:** histograms depend on bin choices, and they fail in high dimensions. Nearest-neighbour methods or neural estimators help, with their own bias.

- **Small samples inflate it:** estimates are often biased upward, so a permutation test helps show whether a value is real.

- **High-cardinality features:** a user ID has very high mutual information with the label in training, and it's useless on new users. Be careful with features that have many values.

- **Start simple:** a model's validation score after adding a feature is often a better test than any filter.

### The answer that sounds right

#### "Zero correlation means no relationship"

It sounds right, as correlation is the usual check. But it only measures straight-line relationships. A U-shape can have a correlation of zero while x nearly determines y. Always plot your data, and consider mutual information or a flexible model when you need to catch other patterns.

## Say it

### What is mutual information, and when would it find a relationship that correlation misses?

#### The interviewer pushes further

Follow-up 1 of 3

Why can information gain favour features with many values?

A feature with many unique values, such as a user ID, can split the data into tiny groups, each perfectly pure, for very high gain, without generalising at all. C4.5's gain ratio divides by the split's own entropy to correct for this. Also, validation data catches it.

Follow-up 2 of 3

Give an example with zero correlation but high mutual information.

Let x be symmetric around zero, and y = x². Knowing x determines y exactly, so mutual information is high, while the correlation is zero, as the rising and falling sides cancel out. Correlation only measures the straight-line part of a relationship.

Follow-up 3 of 3

How does mutual information relate to contrastive learning?

InfoNCE maximises a lower bound on the mutual information between two views of the same item. The bound can't exceed log N with N examples. However, research suggests a good representation isn't only about more mutual information: the encoder and the views matter a lot too.

#### The 30-second answer

Mutual information is how much knowing X reduces uncertainty about Y: H of Y minus H of Y given X. Equivalently, it's the KL divergence between the joint and the product of the marginals. So it's zero only if they're independent, which means it catches non-linear relationships that correlation misses, like a U-shape. It's the same as information gain in decision trees. For feature selection, it misses redundancy and interactions, as with XOR, since it looks at one feature at a time, and it's hard to estimate in high dimensions.

**Key terms and sources**

Joint and conditional entropy, mutual information and how to estimate it, information gain in trees, feature selection, and the link with InfoNCE. · checked 6 Nov 2026

#### Sources

- [Murphy, Probabilistic Machine Learning: An Introduction, chapter 6](https://probml.github.io/pml-book/book1.html)

- [Deep Learning Interviews (Kashani and Ivry)](https://arxiv.org/pdf/2201.00650)

- Decision trees on this site

- Contrastive learning on this site

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
