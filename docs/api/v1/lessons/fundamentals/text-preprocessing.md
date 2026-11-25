# Text Preprocessing

> Stemming, lemmas, stop words: what helps, and what quietly breaks sentiment?

- Track: Fundamentals › NLP Fundamentals › Text basics
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/text-preprocessing/
- Quiz topic: `nlp`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 006bf77033

## Intuition

### The situation

A teammate adds the full pipeline to a review sentiment model: lowercase, strip punctuation, remove stop words, then stem. "Not good, the pizza was cold" now reaches the model as "good pizza cold". The interviewer asks:

> Which preprocessing steps help, and when do they hurt?

**Running example (all NLP lessons):** the food-delivery app collects customer reviews like "_Not good, the pizza was COLD!!_" and "_would order the biryani again_". We want to count, compare, classify and search them.

#### The same word, many spellings

To a computer, "Cold", "cold", "cold!!" and "COLD" are four different strings, and "order", "ordered" and "ordering" are three unrelated words. With a few thousand reviews, most word forms appear only a handful of times, so counts are sparse and a model can't learn that they mean the same thing. Preprocessing groups them.

### The idea

Think of a clerk tidying a messy filing cabinet. Merging "Order", "ordered" and "ORDER!!" into one folder makes things easier to find. But a clerk who bins every small word also bins "not", and the file now says the opposite.

[Figure: The review Not good, the Pizza was COLD becomes not good the pizza was cold, and then, with stop words removed, good pizza cold. The word not has gone.]

_A review from the lesson, run through the lab's steps._

### Play

**Try to break it.** Pick the first review and remove stop words. Then switch between stemming and lemmatisation on the third review, and watch the vocabulary size.

#### What each step does to a review, and to the vocabulary

Lowercasing and punctuation removal are always on. Orange chips were changed by stemming or lemmatisation. Vocabulary = distinct tokens over 400 generated reviews with varied word forms ("ordered", "ordering", "tastes", "better", "best"…; fixed seed), with the same settings.

On 400 reviews, the raw vocabulary is **62** distinct words. Stemming alone brings it to 50 and lemmatisation to 45; removing stop words as well gets to **39** and **36**. But stop-word removal deletes **"not"** from the first review: "not good, the pizza was cold" becomes "good pizza cold", which now _contains_ the positive word "good". For sentiment, negation words must stay. Stemming merges "ordered" and "order" but produces non-words like "tast"; lemmatisation maps "was" → "be" and "better" → "good", cleaner but it needs a dictionary.

**Now say why:** if removing stop words shrinks the vocabulary, why would you ever keep them?

## How it works

### How it works

#### In one breath

Before a classic NLP model can use text, the text has to become a list of tokens. Typical steps: **lowercase** ("Biryani" = "biryani"), strip **punctuation**, split into **tokens**, optionally drop **stop words** (very common words like "the", "and"), and collapse word forms with **stemming** (chop suffixes by rules: "ordered" → "order") or **lemmatisation** (map to the dictionary form using vocabulary and grammar: "was" → "be", "better" → "good"). Each step **shrinks the vocabulary** so counts are less sparse, but each can also **destroy meaning**: removing "not" turns "not good" into "good". Modern Transformer pipelines skip most of this and use subword tokenisers on nearly raw text. What you'll be able to do after this: design a preprocessing pipeline, explain stemming vs lemmatisation, and say which steps to skip for which models.

#### A classic pipeline

| Step | Example | Watch out for |
|---|---|---|
| **Lowercase** | "COLD" → "cold" | "US" (country) vs "us"; names |
| **Remove punctuation** | "cold!!" → "cold" | emoticons, "!!!" can carry sentiment; prices "₹250" |
| **Tokenise** (split into words) | "don't" → "do" + "n't" (Penn Treebank style) | languages without spaces (Chinese, Japanese) |
| **Stop-word removal** | drop "the", "was", "and" | "not", "no" are in most stop lists |
| **Stemming** | "ordered", "ordering" → "order"; "tasted" → "tast" | crude stems that aren't words; over-merging |
| **Lemmatisation** | "was" → "be"; "better" → "good" | needs a dictionary and part-of-speech; slower |

The Porter stemmer (1980) applies a sequence of suffix-stripping rules; lemmatisers (WordNet in NLTK, spaCy) look words up. Manning et al. (2008, §2.2) note that stemming tends to raise recall for search but can lower precision.

## In practice

### In practice

#### Match preprocessing to the model

- **Bag-of-words / TF-IDF models** (next lesson): lowercase, strip punctuation, consider stemming; remove stop words for topic tasks, but keep negations for sentiment.

- **Search engines:** stemming raises recall ("deliveries" finds "delivery"); BM25 already down-weights common words, so stop-word removal matters less (search & retrieval).

- **Transformers and LLMs:** keep the raw text. Their subword tokeniser handles casing, rare words and punctuation, and the model uses all of it: removing stop words or stemming usually _hurts_.

- **Always:** apply exactly the same preprocessing at training and serving time.

### The answer that sounds right

#### "Always remove stop words and stem"

It sounds right, since a smaller vocabulary means less sparsity. But it depends on the task and the model. For sentiment, stop-word lists delete "not". For Transformers and LLMs, removing stop words or stemming usually hurts, because pre-trained models expect raw text. Search is the case where stemming usually pays off, since it raises recall.

## Say it

### Which preprocessing steps help, and when do they hurt?

#### The interviewer pushes further

Follow-up 1 of 3

Stemming or lemmatisation for a search engine?

Stemming is usually enough and much faster; it increases recall. Lemmatisation is worth it when precision matters or for languages with rich morphology.

Follow-up 2 of 3

Should you remove stop words for sentiment analysis?

Not blindly: negations and intensifiers ("not", "very", "too") change sentiment. Use a custom list or keep them.

Follow-up 3 of 3

How do you handle emojis and repeated letters ("soooo good")?

Map emojis to tokens or words, and normalise long letter repeats ("soooo" → "soo") so they don't explode the vocabulary while keeping the emphasis signal.

#### The 30-second answer

Classic text preprocessing lowercases, removes punctuation, tokenises into words, optionally removes stop words, and normalises word forms. Stemming chops suffixes with rules, fast but crude, like ordered to order or tasted to tast; lemmatisation maps words to their dictionary form using vocabulary and part of speech, like was to be or better to good. These steps shrink the vocabulary and reduce sparsity for bag-of-words models and search, but they can destroy meaning; removing "not" flips sentiment. For Transformers you skip most of it and feed raw text to a subword tokeniser, and in all cases training and serving must use identical preprocessing.

**Go further**

#### What not to say

- "Always remove stop words and stem." It depends on the task and model.

- "BERT needs stemmed input." Pre-trained Transformers expect raw text.

**Key terms and sources**

Turning raw text into tokens a model can count: lowercasing, punctuation, word tokenisation, stop words, stemming vs lemmatisation, and when each step helps or hurts · built from Jurafsky & Martin, _Speech and Language Processing_ (3rd ed. draft), Manning, Raghavan & Schütze, _Introduction to Information Retrieval_ (2008), Porter (1980), and the NLTK and spaCy documentation · checked 29 Oct 2026

#### Sources

1. D. Jurafsky & J. Martin, _Speech and Language Processing_, 3rd ed. draft, ch. 2 (regular expressions, tokenisation, normalisation), [web.stanford.edu/~jurafsky/slp3](https://web.stanford.edu/~jurafsky/slp3/).

2. C. Manning, P. Raghavan & H. Schütze, _Introduction to Information Retrieval_, Cambridge University Press 2008, ch. 2, [nlp.stanford.edu/IR-book](https://nlp.stanford.edu/IR-book/).

3. M. Porter, "An algorithm for suffix stripping", _Program_ 14(3), 1980.

4. NLTK documentation (stemmers, WordNet lemmatiser) and spaCy documentation (tokenisation, lemmatisation).
