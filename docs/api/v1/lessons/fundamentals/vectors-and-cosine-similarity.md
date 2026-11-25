# Vectors, Dot Products & Cosine Similarity

> Why does search use the angle between embeddings, not the distance?

- Track: Fundamentals › Maths for ML › Linear algebra
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/vectors-and-cosine-similarity/
- Related: RAG End to End (`ai-engineering/rag-end-to-end`)
- Quiz topic: `la`
- Sources checked: 2026-10-28 · Text last changed: 2026-11-20 · Version: 48ad58aaa9

## Intuition

### The situation

Your food app recommends the same popular restaurant to almost everyone, even people whose taste points elsewhere. The interviewer asks:

> What is the difference between a dot product and cosine similarity, and which would you use here?

**Running example:** the food-delivery app describes each customer and each restaurant with two taste numbers: how much they lean towards **spicy** food and towards **healthy** food. A customer who likes both equally is (1, 1); one who loves spicy, healthy food is (4, 3). Real systems use hundreds of dimensions learned by a model (embeddings), but the maths is identical and 2-D lets us draw it.

#### "How similar are these two things?" as a number

To recommend restaurants, retrieve documents for a RAG system or find near-duplicate products, you need one number that says how alike two items are. Once items are vectors, similarity becomes arithmetic. The choice of arithmetic decides who gets recommended.

### The idea

Think of two arrows. Cosine only asks whether they point the same way. The dot product also rewards length, so a very long arrow can win even when it points the wrong way.

[Figure: Three arrows from one point. The customer and the small restaurant point almost the same way. The popular restaurant is much longer but points elsewhere.]

_You (1, 1). Popular (4, 0.5). Small (1, 1.2). Dot product picks popular, 4.5 against 2.2. Cosine picks small, 0.996 against 0.79._

### Play

**Try to break it.** Make the restaurant much longer without changing its angle. Then rotate it until it sits at 90° from the customer.

#### Move the vectors, watch the three measures

Make the restaurant longer without changing its angle: the dot product grows, the cosine doesn't move, and the distance changes. Rotate it to 90° from the customer: the dot product and cosine hit zero.

**Now say why:** which measure ignored the extra length, and why did two of them hit zero at 90°?

## Maths

### Maths

#### In one breath

In ML every item (a customer, a restaurant, a sentence) becomes a **vector**: a list of numbers. The **dot product** a·b multiplies matching entries and adds them; geometrically it is |a| |b| cos θ, so it grows when vectors point the same way _and_ when they are long. **Cosine similarity** divides out the lengths and keeps only the direction (−1 to 1). **Euclidean distance** measures the straight-line gap. Which one you use changes what "similar" means: dot product favours big, popular items; cosine compares taste regardless of size. Every linear model, attention layer and vector search is built on these three operations. What you'll be able to do after this: compute a dot product, norm and cosine by hand, explain the geometry, and choose between dot product, cosine and Euclidean for a similarity search.

#### Vectors, length and the dot product

$$ {a\cdot b = \textstyle\sum_i a_i b_i} = {\lVert a\rVert\,\lVert b\rVert\cos\theta}, \qquad {\lVert a\rVert = \sqrt{a\cdot a}} $$

Mathematics for Machine Learning §3.1–3.4 (norms, inner products, angles) [mml-book.github.io](https://mml-book.github.io/).

- **dot product**: Multiply matching entries and add: (4, 3)·(2, 1) = 4×2 + 3×1 = 11. One number from two vectors.

- **the same, geometrically**: Length of a times length of b times the cosine of the angle between them. Big when both are long and point the same way; zero when perpendicular; negative when opposite.

- **length (L2 norm)**: ‖a‖ = √(a·a) = √(4² + 3²) = 5: Pythagoras in any number of dimensions.

1. A customer a and a restaurant b, drawn as arrows from the origin.

2. Drop a perpendicular from a's tip onto b's line. The shadow's length is ‖a‖ cos θ: how much of a points along b.

3. The dot product is that shadow times b's length. That's why it measures "agreement in direction, scaled by size".

4. The cosine alone ranges from 1 (same direction) through 0 (unrelated) to −1 (opposite).

#### Cosine = dot product of unit vectors

$$ {\cos\theta} = {a\cdot b} \,/\, {(\lVert a\rVert\,\lVert b\rVert)} $$

- **cosine similarity**: How aligned two vectors are, from −1 to 1, ignoring how long they are.

- **dot product**: The raw agreement.

- **divide out both lengths**: Equivalent to scaling both vectors to length 1 first, then taking the dot product.

#### Three ways to compare vectors

| Measure | Formula | Cares about | Used in |
|---|---|---|---|
| **Dot product** | Σ aᵢbᵢ | Direction and length | Linear models (w·x), attention scores (q·k), matrix-factorisation recommenders, maximum-inner-product search |
| **Cosine similarity** | a·b / (‖a‖‖b‖) | Direction only | Text and sentence embeddings, semantic search, RAG retrieval |
| **Euclidean distance** | ‖a − b‖ | Absolute position | k-NN, k-means, when magnitudes are meaningful |

For unit-length vectors (‖a‖ = ‖b‖ = 1), all three agree on the ranking: ‖a − b‖² = 2 − 2 cos θ. That's why many embedding models normalise outputs, and vector databases then use the cheapest one (dot product).

## In practice

### In practice

#### Dot product vs cosine in recommenders and search

- **Dot product** when vector length carries real signal: in matrix factorisation, a longer item vector often encodes popularity or quality, and ranking by dot product deliberately favours it. Two-tower recommenders typically score by dot product for this reason.

- **Cosine** when length is an artefact: text embeddings of a long vs short document about the same topic should match. Most sentence-embedding models and RAG pipelines use cosine (or normalise and use dot product).

- **Euclidean** when absolute position matters and features are on comparable, scaled units (see k-NN); in high dimensions all distances concentrate, which hurts every measure.

Whatever the embedding model was trained with is the right choice: a model trained with a cosine loss should be queried with cosine.

#### The dot product is everywhere

- **Linear and logistic regression:** the score is w·x + b (Linear Regression).

- **Neural network layers:** each neuron computes a dot product of its weights with its input.

- **Attention:** query·key dot products, scaled by 1/√d, decide which tokens attend to which.

- **Vector search:** nearest neighbours by cosine or inner product over millions of embeddings (HNSW, IVF; see k-NN).

#### Where to go next

- **Other ways to measure length:** vector and matrix norms cover L1, L2 and more, and why L1 gives sparse weights.

- **Dot products and closest points:** orthogonality and projections shows how this idea becomes least squares.

### The answer that sounds right

#### "Recommend whatever has the highest dot product"

The dot product rewards length. If a restaurant's vector is long simply because it's popular (its embedding was trained on many orders), it wins for almost everyone, even customers whose taste points elsewhere. A customer u = (1, 1) who likes spicy and healthy equally gets a dot product of 4.5 with a popular, mostly-spicy restaurant (4, 0.5), but only 2.2 with a small restaurant (1, 1.2) that matches their taste almost exactly. Cosine similarity flips the order: 0.79 vs 0.996. Neither is always right; they answer different questions (see In practice).

#### Caveats

- Cosine ignores magnitude entirely: two customers who order 1 and 100 times a month with the same taste look identical.

- Cosine on raw, unscaled features is dominated by big-unit features, like any distance.

- A zero vector has no direction; cosine is undefined (libraries add a tiny ε).

## Say it

### What is the difference between a dot product and cosine similarity, and which would you use here?

#### The interviewer pushes further

Follow-up 1 of 3

Why does attention divide by √d?

Dot products of random d-dimensional vectors have variance growing with d, so softmax would saturate; dividing by √d keeps scores in a usable range (Vaswani et al. 2017).

Follow-up 2 of 3

How are cosine and Euclidean related?

For unit vectors, ‖a − b‖² = 2 − 2 cos θ, so ranking by one is ranking by the other.

Follow-up 3 of 3

What does orthogonal mean for features?

Zero dot product: the directions share no component. Orthogonal (uncorrelated, centred) features make linear models easier to interpret.

#### The 30-second answer

A dot product multiplies matching entries and sums them; geometrically it's the product of the lengths times the cosine of the angle, so it measures alignment scaled by magnitude. Cosine similarity divides by both lengths, so it compares direction only and ranges from −1 to 1. Euclidean distance measures absolute separation. For normalised vectors they all rank the same. I use cosine for text embeddings where length is an artefact, dot product where magnitude carries signal like popularity in recommenders, and Euclidean for scaled feature spaces like k-NN.

**Go further**

#### What not to say

- "Cosine similarity is a distance." It's a similarity; 1 − cos is a dissimilarity, but not a true metric.

- "Dot product and cosine always give the same ranking." Only for equal-length vectors.

**Key terms and sources**

Vectors as lists of features, length (norm), the dot product, cosine similarity, Euclidean distance, and why embeddings and recommenders run on them · built from Deisenroth, Faisal & Ong, _Mathematics for Machine Learning_ (ch. 2–3) and Goodfellow, Bengio & Courville, _Deep Learning_ (ch. 2) · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **Vector** | An ordered list of numbers; a point or arrow in space. |
| **Norm ‖a‖** | Length; L2 by default, L1 = sum of absolute values. |
| **Dot product** | Σ aᵢbᵢ = ‖a‖‖b‖cos θ. |
| **Cosine similarity** | Dot product of unit vectors; angle only. |
| **Orthogonal** | Dot product 0: perpendicular, unrelated directions. |

#### Sources

1. M. P. Deisenroth, A. A. Faisal & C. S. Ong, _Mathematics for Machine Learning_, Cambridge University Press 2020, free at [mml-book.github.io](https://mml-book.github.io/) (ch. 2–3).

2. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, ch. 2, [deeplearningbook.org](https://www.deeplearningbook.org/).

3. A. Vaswani et al., "Attention is all you need", NeurIPS 2017, [arXiv:1706.03762](https://arxiv.org/abs/1706.03762) (scaled dot-product attention).
