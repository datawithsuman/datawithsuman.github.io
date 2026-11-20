# N-gram Language Models and Perplexity

> How likely is this sentence, and what does perplexity mean?

- Track: Fundamentals › NLP Fundamentals › Language models and tokenisation
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/n-gram-language-models/
- Before this: Probability Basics & Bayes' Rule (`fundamentals/probability-and-bayes`), Entropy, Cross-Entropy & KL Divergence (`fundamentals/entropy-cross-entropy-kl`)
- Quiz topic: `nlp`

## Intuition

### The situation

The review box suggests the next word as customers type, using a bigram model built from 400 past reviews. Then someone types "the paneer was crispy", which it has never seen, and its probability comes out as zero. The interviewer asks:

> How does an n-gram model work, and what do you do about pairs it has never seen?

**Running example:** the app's review box suggests the next word as customers type. "the biryani was …" → "not"? "cold"? "great"? We learn the suggestions from 400 past reviews.

#### How likely is this sentence?

Autocomplete, speech recognition ("recognise speech" vs "wreck a nice beach"), spelling correction and machine translation all need to judge which word sequence is more plausible. We need a model that gives every possible sentence a probability, learned from text alone.

### The idea

Think of guessing the next word from a tally of what followed the last word in past reviews. It's quick and needs no training beyond counting. But if the tally has no entry for a pair, it calls that pair impossible.

[Figure: To guess what follows the biryani was, a bigram model looks only at was. It has counted not most often, then other words. It has never seen was crispy, so that gets zero.]

_Illustrative bars. In the lab, P("not" | "was") is 0.415._

### Play

**Try to break it.** Score "the paneer was crispy" with no smoothing, then with add-1 and add-k. Then score the scrambled sentence, and watch held-out perplexity.

#### A bigram model trained on 400 reviews

Bar chart: the model's top next-word probabilities after "was". Vocabulary = words in 400 training reviews plus <unk>; unseen words map to <unk>. Held-out set: 100 new reviews from the same generator. Fixed seed.

Without smoothing, "the paneer was crispy" gets **infinite** perplexity: "paneer was" and "crispy" never appeared, so one factor is 0. The fluent "the pizza was not soggy" scores **2.91**, and the scrambled "soggy not was pizza the" about **3,700**, even with smoothing: the model has learned word order, not just word frequency. Smoothing is a trade-off. **Add-1** gives the crispy sentence a finite 12.4, but flattens everything else: held-out perplexity rises from 3.09 to **3.76** and P("not" | "was") drops from 0.415 to 0.394. A **small k** (0.05) barely touches seen text (held-out 3.13) but leaves less room for unseen words (crispy: 20.1). Backoff and Kneser–Ney get the best of both by falling back to lower-order counts instead of spreading mass evenly.

**Now say why:** add-1 fixes the infinite perplexity, so why does held-out perplexity get worse?

## Maths

### Maths

#### In one breath

A **language model** assigns a probability to a sequence of words, or equivalently predicts the **next word**. By the chain rule, P(sentence) is the product of P(each word | all previous words). An **n-gram model** simplifies this with the **Markov assumption**: only the last n − 1 words matter, and the probabilities come from **counting** in a corpus. Any word pair never seen in training gets probability 0, which zeroes the whole sentence, so we **smooth**: add-k, backoff, or the best classic method, **Kneser–Ney**. Models are compared by **perplexity**, the exponentiated average negative log-probability on held-out text: lower is better, and it reads as "how many words the model is effectively choosing between". LLMs are next-word predictors too, with a neural network instead of a count table. What you'll be able to do after this: compute bigram probabilities and perplexity, explain why smoothing is needed, and connect n-gram models to modern LLMs.

#### Chain rule, Markov assumption, counts

$$ {P(w_1,\dots,w_n) = \prod_i P(w_i \mid w_1,\dots,w_{i-1})} \;\approx\; {\prod_i P(w_i \mid w_{i-1})}, \qquad {P(w_i\mid w_{i-1}) = \frac{C(w_{i-1}\,w_i)}{C(w_{i-1})}} $$

Shannon (1948) used n-gram approximations of English; Jurafsky & Martin, SLP3 ch. 3. Sentences are padded with start and end tokens <s> and </s>.

- **chain rule**: Exact: the probability of a sentence is the product of each word’s probability given all the words before it.

- **Markov assumption (bigram)**: Approximate that history by just the previous word. A trigram model uses the previous two.

- **maximum-likelihood estimate**: Count how often the pair appears, divided by how often the first word appears. e.g. if “was not” appears 150 times and “was” 400 times, the estimate is 0.375.

## In practice

### In practice

#### Perplexity, and the road to LLMs

$$ \mathrm{PP}(W) = {\exp\!\Big(}-{\frac{1}{N}\sum_{i=1}^{N}\log P(w_i \mid w_{<i})}{\Big)} $$

Perplexity = exp(cross-entropy) on the test set (entropy & cross-entropy). Only compare perplexities computed with the same tokenisation and vocabulary.

- **average log-probability**: Average the log-probability the model gives each word of held-out text.

- **exponentiate the negative**: Perplexity = exp(−average log-probability). A perplexity of 10 means the model is as uncertain as picking uniformly among 10 words at every step.

- **Neural language models** (Bengio et al. 2003) replaced count tables with embeddings and a neural network, so similar words share statistics and there is no zero-count problem.

- RNN and then Transformer LMs extended the context from n − 1 words to thousands of tokens. Modern LLMs are still trained on next-token prediction and evaluated with perplexity, over subword tokens.

- n-gram models still appear in fast on-device keyboards, speech-recognition decoding and data-quality filtering of LLM training corpora.

For one use of language models, read Spelling Correction.

### The answer that sounds right

#### Unseen pairs get probability zero

A customer types "the paneer was crispy". If "was crispy" never appeared in training, the counting estimate is 0, the whole sentence gets probability 0, and perplexity is infinite. With any realistic vocabulary, most plausible word pairs are never seen. **Smoothing** moves a little probability mass to unseen events:

- **Add-k** (Laplace when k = 1): add k to every count. Simple, but add-1 steals far too much mass from seen pairs.

- **Backoff / interpolation:** if the trigram is unseen, fall back to (or mix in) the bigram and unigram estimates.

- **Kneser–Ney** (1995): interpolation with discounting plus a clever lower-order distribution ("how many different contexts does this word follow?"), the best-performing classic method in Chen & Goodman's (1998) comparison.

## Say it

### How does an n-gram model work, and what do you do about pairs it has never seen?

#### The interviewer pushes further

Follow-up 1 of 3

Why not just use a large n?

Data sparsity: most 5-grams are never seen, so estimates are zeros and noise. Storage also explodes.

Follow-up 2 of 3

Why work in log space?

Multiplying many small probabilities underflows; summing logs is stable and turns products into sums.

Follow-up 3 of 3

Can you compare perplexities of two LLMs with different tokenisers?

Not directly: per-token perplexity depends on the token count. Normalise per word or per byte (bits per byte) instead.

#### The 30-second answer

A language model assigns probabilities to word sequences; by the chain rule that's the product of each word's probability given its history. An n-gram model approximates the history with the last n minus one words and estimates probabilities from counts. Unseen n-grams get zero probability, so we smooth, with add-k, backoff or interpolation, or Kneser–Ney, the best classic method. We evaluate with perplexity, the exponential of the average negative log-likelihood on held-out text, lower is better, roughly the effective number of choices per word. Neural LMs replaced count tables with embeddings and longer context, and LLMs are still next-token predictors measured by perplexity.

**Go further**

#### What not to say

- "Lower training perplexity means a better model." Evaluate on held-out text.

- "Add-1 is the standard smoothing." It's a teaching example; it performs poorly.

**Key terms and sources**

Predicting the next word from counts: the chain rule, the Markov assumption, bigram models, the zero-probability problem and smoothing (add-k, backoff, Kneser–Ney), perplexity as the standard metric, and how this leads straight to LLMs · built from Shannon (1948), Jelinek (1997), Chen & Goodman (1998), Kneser & Ney (1995), Jurafsky & Martin (SLP3, ch. 3) and Bengio et al. (2003) · checked 29 Oct 2026

#### Sources

1. C. Shannon, "A Mathematical Theory of Communication", _Bell System Technical Journal_ 27, 1948.

2. R. Kneser & H. Ney, "Improved backing-off for M-gram language modeling", ICASSP 1995.

3. S. Chen & J. Goodman, "An Empirical Study of Smoothing Techniques for Language Modeling", Harvard TR-10-98, 1998.

4. Y. Bengio, R. Ducharme, P. Vincent & C. Jauvin, "A Neural Probabilistic Language Model", _JMLR_ 3, 2003.

5. D. Jurafsky & J. Martin, _Speech and Language Processing_, 3rd ed. draft, ch. 3, [web.stanford.edu/~jurafsky/slp3](https://web.stanford.edu/~jurafsky/slp3/).
