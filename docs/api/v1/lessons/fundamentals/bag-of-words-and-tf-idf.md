# Bag-of-Words, N-grams and TF-IDF

> Why does TF-IDF find the right review when raw counts can't?

- Track: Fundamentals › NLP Fundamentals › Text basics
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/bag-of-words-and-tf-idf/
- Before this: Text Preprocessing (`fundamentals/text-preprocessing`), Vectors, Dot Products & Cosine Similarity (`fundamentals/vectors-and-cosine-similarity`)
- Quiz topic: `nlp`

## Intuition

### The situation

You want the review most similar to one about cold biryani. With raw word counts, it scores 0.64 to 0.79 against every other review, even the one about a rude rider. The interviewer asks:

> Why does TF-IDF find the right review when raw counts can't?

**Running example:** 8 short delivery reviews. For a review that says the biryani was cold, which other review is most similar: one that's also about cold food, or one that merely shares "the", "was" and "and"?

#### Models need fixed-length numbers

Reviews have different lengths and words, but classifiers and similarity measures need vectors of the same size. The simplest idea: one dimension per word in the vocabulary. The question is what number to put in each dimension.

### The idea

Think of people describing their meals. Everyone says "the" and "was", so those tell you nothing about who ate what. Few people say "raita", so hearing it tells you a lot. TF-IDF scores each word by how much it gives away.

[Figure: Word weights for one review. With raw counts, the, was and cold are equally large. With TF-IDF, the and was drop to zero, and cold, raita and biryani carry the review.]

_Illustrative weights for "the biryani was cold and the raita was cold". A word in every review gets zero._

### Play

**Try to break it.** Pick the biryani review and switch between raw counts and TF-IDF, watching the similarities. Then try the paneer review.

#### Which words matter, and which review is most similar?

8 reviews (listed in the table with their cosine similarity to the chosen one). TF-IDF uses tf = raw count and idf = ln(N / df), N = 8.

With raw counts, the cold-biryani review is **0.64–0.79** similar to _every_ other review, including the paneer and the rude-rider ones, because "the", "was" and "and" dominate every vector. With TF-IDF those words get weight **0** and the similarities spread out: **0.35** to the cold, soggy pizza (shares "cold"), 0.10 and 0.08 to the other biryani reviews, and **0.00** to reviews with nothing distinctive in common. The ranking now reflects meaning, not grammar words. Try the paneer review: under TF-IDF its best match scores only 0.22, an honest "nothing very similar here".

**Now say why:** under TF-IDF, the paneer review's best match scores only 0.22. Why is that a good result?

## Maths

### Maths

#### In one breath

**Bag-of-words** turns a document into a vector with one entry per vocabulary word: how many times it appears. Word order is thrown away (hence "bag"); adding **n-grams** (pairs like "not good") keeps some of it. Raw counts are dominated by words like "the" and "was" that appear everywhere. **TF-IDF** multiplies each word's count (**term frequency**) by its **inverse document frequency**, log(N / df): a word in every document gets weight 0, a rare word gets a high weight. Documents are compared with **cosine similarity**. The vectors are huge but **sparse**, and TF-IDF plus a linear model is still a strong, fast baseline for text classification and search. What you'll be able to do after this: build a bag-of-words / TF-IDF vector by hand, explain IDF, use n-grams, and compare documents with cosine similarity.

#### Bag-of-words and n-grams

- **Bag-of-words:** vector entry = how many times the word appears in the document. "the biryani was cold and the raita was cold" → the: 2, was: 2, cold: 2, biryani: 1, raita: 1, and: 1; every other word 0.

- **Sparse:** with a 50,000-word vocabulary a review has maybe 20 non-zero entries, so it's stored as (index, value) pairs.

- **N-grams:** add counts of word pairs (bigrams) or triples. "not good" and "good" become different features, so negation survives. The vocabulary grows fast; **min_df** thresholds or **feature hashing** keep it manageable.

#### TF-IDF: weight words by how distinctive they are

$$ {w_{t,d}} = {\mathrm{tf}_{t,d}} \times {\log\frac{N}{\mathrm{df}_t}} $$

IDF was introduced by Spärck Jones (1972); Salton & Buckley (1988) compared term-weighting schemes. scikit-learn's default uses a smoothed version, ln((1 + N)/(1 + df)) + 1, so no weight is exactly 0, and then L2-normalises each vector. Manning et al. (2008), ch. 6.

- **term frequency**: How often word t appears in document d (often the raw count, or 1 + log(count) to dampen repeats).

- **inverse document frequency**: log of (number of documents ÷ number of documents containing t). A word in every document gets log(1) = 0; a word in 1 of 8 gets log 8 ≈ 2.08.

- **the weight**: Their product: high when a word is frequent in this document but rare across the collection.

## In practice

### In practice

#### When TF-IDF is enough, and when it isn't

- **Strong baseline:** TF-IDF + logistic regression or linear SVM trains in seconds, is easy to explain, and is often within a few points of far bigger models on topic and sentiment classification (next lesson).

- **Search:** TF-IDF's descendant **BM25** is still the default in Lucene/Elasticsearch and a strong retriever for RAG (search & retrieval).

- **Limits:** no notion of synonyms ("cold" vs "chilly" share nothing), little word order, and a vocabulary fixed at training time. Dense embeddings address the first; Transformers address all three.

With no labels at all, read Topic Modelling.

### The answer that sounds right

#### "TF-IDF understands meaning"

It sounds right, since the rankings look so much more sensible. But TF-IDF only matches exact tokens, and "cold" and "chilly" are unrelated to it. It looks like meaning because the grammar words stopped dominating, not because the model knows what a word means. That's the gap dense embeddings fill.

## Say it

### Why does TF-IDF find the right review when raw counts can't?

#### The interviewer pushes further

Follow-up 1 of 3

Why the log in IDF?

To dampen the effect: a word in 1 of a million documents shouldn't be a million times more important than one in every document. The log grows slowly with rarity.

Follow-up 2 of 3

How do you handle a huge n-gram vocabulary?

min_df / max_df thresholds, keeping the top-k features, or the hashing trick (map n-grams into a fixed number of buckets).

Follow-up 3 of 3

Why cosine rather than Euclidean distance for TF-IDF vectors?

Cosine ignores document length; a long review shouldn't look far from a short one just because it has more words.

#### The 30-second answer

Bag-of-words represents a document as a sparse vector of word counts over the vocabulary, ignoring order; n-grams add short sequences like "not good" to keep some order. TF-IDF reweights each count by inverse document frequency, log of the number of documents over the number containing the word, so words that appear everywhere get near-zero weight and distinctive words get high weight; vectors are usually L2-normalised and compared with cosine similarity. It's fast, interpretable and a strong baseline for classification and search, with BM25 as the search-engine version, but it has no synonyms or real word order, which embeddings and Transformers add.

**Go further**

#### What not to say

- "TF-IDF understands meaning." It matches exact tokens; "cold" and "chilly" are unrelated to it.

- "Fit the IDF on all data including test." Fit the vocabulary and IDF on training data only, to avoid leakage.

**Key terms and sources**

Representing documents as word-count vectors, adding n-grams for word order, and TF-IDF weighting that boosts distinctive words and silences common ones; sparse vectors, cosine similarity, and where these features still win · built from Salton & Buckley (1988), Spärck Jones (1972), Manning, Raghavan & Schütze (2008, ch. 6), Jurafsky & Martin (SLP3, ch. 5) and the scikit-learn `TfidfVectorizer` docs · checked 29 Oct 2026

#### Sources

1. K. Spärck Jones, "A statistical interpretation of term specificity and its application in retrieval", _Journal of Documentation_ 28(1), 1972.

2. G. Salton & C. Buckley, "Term-weighting approaches in automatic text retrieval", _Information Processing & Management_ 24(5), 1988.

3. C. Manning, P. Raghavan & H. Schütze, _Introduction to Information Retrieval_, 2008, ch. 6, [nlp.stanford.edu/IR-book](https://nlp.stanford.edu/IR-book/).

4. D. Jurafsky & J. Martin, _Speech and Language Processing_, 3rd ed. draft, ch. 5 (embeddings and TF-IDF), [web.stanford.edu/~jurafsky/slp3](https://web.stanford.edu/~jurafsky/slp3/).

5. scikit-learn documentation, [TF-IDF term weighting](https://scikit-learn.org/stable/modules/feature_extraction.html#tfidf-term-weighting).
