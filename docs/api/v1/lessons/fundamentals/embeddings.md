# Embeddings and Representation Learning

> How do models learn that biryani is like pulao?

- Track: Fundamentals › Deep Learning › Representation and generative models
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/embeddings/
- Before this: Vectors, Dot Products & Cosine Similarity (`fundamentals/vectors-and-cosine-similarity`), Backpropagation Through a Network (`fundamentals/backpropagation`)
- Related: RAG End to End (`ai-engineering/rag-end-to-end`)
- Quiz topic: `genm`

## Intuition

### The situation

The delivery app wants "more like this" suggestions: order biryani, get pulao rather than fries. A teammate one-hot encodes the dishes, and every dish comes out equally unlike every other. The interviewer asks:

> What is an embedding, and where does its meaning come from?

**Running example (Representation lessons):** the delivery app wants "more like this" suggestions: if you ordered biryani, suggest pulao rather than fries. Nobody labels which dishes are similar; we learn it from how dishes appear in order notes and reviews.

#### One-hot vectors know nothing about similarity

With a vocabulary of 50,000 words, one-hot encoding gives each word a 50,000-long vector with a single 1. Every pair of different words has a dot product of 0: "biryani" is exactly as unlike "pulao" as it is unlike "keyboard". The vectors are huge, sparse and carry no meaning. We want a small, dense vector per item where distance means something.

### The idea

Think of a map of dishes that nobody draws by hand. Dishes that turn up in similar order notes get placed close together. Biryani lands next to pulao and far from fries, just from how the words are used.

[Figure: A map of dishes. Biryani sits next to pulao, pizza near pasta and lasagne, chai near coffee, and fries near nuggets. The groups sit far apart.]

_Illustrative, in two dimensions. Real embeddings use hundreds._

### Play

**Try to break it.** Pick biryani at embedding size 4, and look at its neighbours. Raise the size to 8. Then try chai.

#### Embeddings from 400 order notes

Corpus: 400 generated order notes like "ordered biryani so spicy and rice" or "the pizza and the pasta arrived" (16 dishes from four cuisines, each with its own traits, some shared across cuisines; fixed seed). Co-occurrence window ±2 → positive PMI → SVD, keeping d dimensions. Plot: the first two dimensions; neighbours use all d.

Nobody told the method which dishes belong together. With **d = 4**, the embedding captures the big picture: biryani's nearest neighbours are the other Indian dishes, pizza sits with lasagne and pasta, chai with the other drinks. Raise **d to 8** and finer traits appear: biryani's closest match becomes **pulao (0.91)**, the other rice dish served with raita; chai stays close to **coffee (0.98)**, both hot and served with biscuits, but drifts from cold juice (0.32); fries pair with nuggets (0.94), both crispy with ketchup. Small d groups by cuisine, larger d separates finer meaning, which is the same trade-off real systems tune with hundreds of dimensions.

**Now say why:** why does a small size group dishes by cuisine, while a larger one separates finer meaning?

## Maths

### Maths

#### In one breath

A model can't do maths on the word "biryani"; it needs numbers. **One-hot** vectors make every word equally different from every other. An **embedding** maps each item to a short **dense vector**, learned so that items used in similar ways end up close together: "biryani" near "pulao", "pizza" near "pasta". For words this rests on the **distributional hypothesis** (a word is known by the company it keeps). word2vec learns them by predicting neighbouring words, which amounts to factorising a word–context co-occurrence matrix. Modern models produce **contextual** embeddings that change with the sentence, and embeddings of whole sentences, images, users and products drive **semantic search, RAG and recommendations**.What you'll be able to do after this: explain why embeddings beat one-hot, how they're learned, how to compare them, and where they're used.

#### An embedding is a lookup table you learn

$$ e_{w} = E^{\top}\mathbf{1}_{w}, \quad E \in \mathbb{R}^{V\times d}, \qquad \cos(a,b) = \frac{a\cdot b}{\lVert a\rVert\,\lVert b\rVert} $$

Bengio et al. (2003) learned word vectors jointly with a neural language model. Cosine similarity: Vectors & Cosine Similarity.

- **embedding matrix**: V rows (one per item) by d columns (e.g. 300 for word2vec, 768–4,096 in Transformers). Its values are learned by gradient descent like any other weights.

- **one-hot input**: Multiplying a one-hot vector by E just selects one row, so in practice it’s implemented as a table lookup.

- **cosine similarity**: Compare embeddings by the angle between them: 1 = same direction, 0 = unrelated. Used for nearest-neighbour search.

#### Learning from context: word2vec

- **Skip-gram:** for each word, predict the words around it (within a window of a few words); **CBOW** does the reverse (Mikolov et al. 2013). Trained with negative sampling on billions of words, the hidden-layer weights become the embeddings.

- Famous property: some relations become directions, e.g. vector("king") − vector("man") + vector("woman") ≈ vector("queen").

- **It's matrix factorisation in disguise:** Levy & Goldberg (2014) showed skip-gram with negative sampling implicitly factorises a matrix of shifted **pointwise mutual information** (PMI) between words and contexts. GloVe (Pennington et al. 2014) factorises log co-occurrence counts directly.

The lab in the Intuition tab uses that equivalence: count which words appear near which, convert counts to positive PMI, and factorise with SVD. No neural network needed for the idea.

## In practice

### In practice

#### Contextual embeddings and embeddings of everything

- **Static vs contextual:** word2vec gives "cold" one vector. Transformers give a different vector per occurrence: "cold biryani" vs "a cold" (the illness) get different representations (BERT; Transformers).

- **Sentence and document embeddings:** models such as Sentence-BERT (Reimers & Gurevych 2019) map whole texts to one vector for semantic search; this is the retrieval step of **RAG**.

- **Any item:** users, products, dishes, images (via contrastive learning) can all be embedded; recommendation systems compare user and item vectors.

- **Search at scale:** approximate nearest-neighbour indexes (HNSW, IVF/PQ) find the closest of millions of vectors in milliseconds.

### The answer that sounds right

#### "An embedding stores what the word means"

It sounds right, since similar dishes do end up close. But the vector only reflects how a word is used. The lab counts which words appear near which, and nobody tells it that biryani and pulao are both rice dishes. Individual dimensions rarely mean anything by themselves. And word2vec gives "cold" one vector, whether it's "cold biryani" or "a cold". Telling those apart takes contextual embeddings.

## Say it

### What is an embedding, and where does its meaning come from?

#### The interviewer pushes further

Follow-up 1 of 3

Why cosine rather than Euclidean distance?

Cosine ignores vector length, which often reflects frequency rather than meaning; with normalised vectors the two give the same ranking.

Follow-up 2 of 3

How do you handle words not in the vocabulary?

Sub-word units (fastText character n-grams, BPE tokens in Transformers) so any word can be composed from known pieces.

Follow-up 3 of 3

How would you evaluate embeddings?

Intrinsically (similarity benchmarks, nearest-neighbour checks) and, more importantly, extrinsically: retrieval recall@k or downstream task accuracy.

#### The 30-second answer

An embedding maps a discrete item to a dense, low-dimensional vector, learned so that similar items are close, usually by cosine similarity. It's a lookup table trained by gradient descent. For words, methods like word2vec predict surrounding words, which by the distributional hypothesis puts words used in similar contexts close together; it's equivalent to factorising a shifted PMI co-occurrence matrix. Modern Transformers give contextual embeddings that depend on the sentence, and sentence, image, user and product embeddings power semantic search, RAG retrieval and recommendations, with approximate nearest-neighbour indexes for scale.

**Go further**

#### What not to say

- "Embedding dimensions have fixed meanings." Individual dimensions are rarely interpretable; directions and distances are what carry meaning.

- "One embedding per word is enough." Polysemy needs contextual embeddings.

**Key terms and sources**

Turning discrete things (words, dishes, users) into dense vectors where similar things sit close together: one-hot vs dense, the distributional hypothesis, word2vec as implicit matrix factorisation, contextual embeddings, and how embeddings power search and recommendation · built from Bengio et al. (2003), Mikolov et al. (2013), Levy & Goldberg (NeurIPS 2014), Pennington et al. (GloVe, 2014), Devlin et al. (2019) and Reimers & Gurevych (2019) · checked 29 Oct 2026

#### Sources

1. Y. Bengio, R. Ducharme, P. Vincent & C. Jauvin, "A Neural Probabilistic Language Model", _JMLR_ 3, 2003.

2. T. Mikolov, K. Chen, G. Corrado & J. Dean, "Efficient Estimation of Word Representations in Vector Space", arXiv:1301.3781, 2013.

3. O. Levy & Y. Goldberg, "Neural Word Embedding as Implicit Matrix Factorization", NeurIPS 2014.

4. J. Pennington, R. Socher & C. Manning, "GloVe: Global Vectors for Word Representation", EMNLP 2014.

5. N. Reimers & I. Gurevych, "Sentence-BERT", EMNLP 2019, arXiv:1908.10084.
