# Text Classification: Naive Bayes vs Logistic Regression

> Why does “not good” fool a unigram model, and how do bigrams fix it?

- Track: Fundamentals › NLP Fundamentals › Text basics
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/text-classification/
- Before this: Bag-of-Words, N-grams and TF-IDF (`fundamentals/bag-of-words-and-tf-idf`), Naive Bayes (`fundamentals/naive-bayes`), Logistic Regression (`fundamentals/logistic-regression`)
- Quiz topic: `nlp`

## Intuition

### The situation

The restaurant team wants reviews tagged positive or negative to route complaints, and you have a few hundred labelled examples. Your unigram model scores about 53%, and its "most positive" words are cold, soggy and bland. The interviewer asks:

> How do you build a text classification baseline, and why does negation break it?

**Running example:** classify delivery reviews as 👍 or 👎. Our reviews are full of negations: "the biryani was _not cold_" (👍), "the pasta was _not fresh_" (👎). Exactly the case that trips up simple models.

#### Thousands of reviews, a label for each

A restaurant team wants every incoming review tagged positive or negative to route complaints quickly. We have a few hundred labelled reviews. We need a model that trains in seconds, runs on a CPU, and whose decisions we can explain ("it's negative because of 'soggy'").

### The idea

Think of judging a review from its words cut out and shaken in a bag. "Not" and "cold" are both in there, but you can't tell they were next to each other. Bigrams cut out pairs instead, so "not cold" stays in one piece.

[Figure: The review the biryani was not cold. With unigrams, not and cold are separate features and both models score about 53 percent. With bigrams, not_cold is one feature and both reach about 94 percent.]

_Test accuracy from the lab, on reviews deliberately full of negations._

### Play

**Try to break it.** Train with unigrams only, and read logistic regression's most positive and negative features. Then add bigrams and compare.

#### Unigrams vs bigrams on reviews full of negations

300 training and 300 test reviews generated from templates where three quarters of reviews contain a negation and 4% of labels are flipped (fixed seed). Features are binary word (and word-pair) presence. Both models train in your browser.

With **unigrams** both models score about **53%**, barely better than a coin flip, and logistic regression's "most positive" words come out as **cold, soggy, bland**: in this data those words mostly appear in "not cold"-style praise. With **bigrams**, features like **not_cold** and **not_fresh** carry the meaning and both models jump to **94%** (96% on the reviews that contain "not"). Real reviews are less extreme, but negation, sarcasm and contrast ("good but…") are where bag-of-words models lose most of their errors.

**Now say why:** why did Naive Bayes and logistic regression both fail, and both recover, at the same point?

## Maths

### Maths

#### In one breath

To classify text (positive or negative review, spam or not, which topic), turn each document into a bag-of-words or TF-IDF vector and train a linear model. **Multinomial Naive Bayes** counts how often each word appears in each class and multiplies the probabilities (with add-1 smoothing so unseen words don't zero everything); **logistic regression** learns one weight per word. Both are fast, interpretable and strong on topic-like tasks. Their weakness is **word order**: with unigrams, "not cold" and "cold" look alike, so negations confuse them. Adding **bigrams** ("not_cold") fixes much of this. Fine-tuned Transformers do better still, at far higher cost. What you'll be able to do after this: build NB and logistic-regression text classifiers, explain smoothing and the independence assumption, and fix negation with n-grams.

#### Multinomial Naive Bayes

$$ \hat{c} = \arg\max_c \Big[{\log P(c)} + \sum_{w\in d}{\log P(w\mid c)}\Big], \qquad {P(w\mid c) = \frac{\mathrm{count}(w,c)+1}{\sum_{w'}\mathrm{count}(w',c) + |V|}} $$

McCallum & Nigam (1998) compared event models for text; Jurafsky & Martin SLP3 Appendix B. In practice we sum log-probabilities to avoid underflow. Logistic regression (SLP3 ch. 4) instead learns weights directly by minimising log loss: no independence assumption, usually more accurate with enough data (Naive Bayes, logistic regression).

- **class prior**: How common each class is in training: P(👍).

- **word likelihoods**: For each word, how often it appears in reviews of that class. Naive Bayes multiplies them as if words were independent given the class: the naive assumption.

- **add-1 smoothing**: Add 1 to every count so a word never seen in one class doesn’t make its probability exactly 0 (which would zero the whole product).

## In practice

### In practice

#### Strong baselines, and when to go bigger

- Pang, Lee & Vaithyanathan (2002) showed Naive Bayes, maximum entropy (logistic regression) and SVMs on unigram features reach about 80% on movie-review sentiment, and that sentiment is harder than topic classification.

- Wang & Manning (ACL 2012) found NB works better on short snippets and SVM/LR on longer documents, that bigrams consistently help sentiment, and proposed NB-SVM, which combines them into a very strong baseline.

- Fine-tuned Transformers such as BERT (Devlin et al. 2019) beat these baselines, especially on negation, contrast and context, at the cost of GPU training and slower inference. Today a common path is: TF-IDF + LR as the baseline, then a small fine-tuned Transformer or an LLM if the gap justifies the cost.

For how to fine-tune one, read BERT and Masked Language Models.

#### Making a text classifier production-ready

- Fit the vectoriser (vocabulary, IDF) on training data only; use the same pipeline at serving time.

- Handle class imbalance with class weights and threshold tuning (class imbalance); report precision/recall or F1, not just accuracy.

- Inspect the top-weighted features: they reveal leakage (an "order ID" pattern) and dataset artefacts quickly.

- Calibrate probabilities if they drive decisions; Naive Bayes is famously overconfident because of its independence assumption.

### The answer that sounds right

#### "Switching to a better model will fix the negation errors"

It sounds right, since logistic regression is usually stronger than Naive Bayes. But in the lab, both score about 53% on unigrams and both reach 94% with bigrams. The features were the problem, not the model. A fine-tuned Transformer does handle negation better, but at the cost of GPU training and slower inference, so try the cheap fix first.

## Say it

### How do you build a text classification baseline, and why does negation break it?

#### The interviewer pushes further

Follow-up 1 of 3

Why is Naive Bayes "naive", and why does it still work?

It assumes word independence given the class, which is false, but classification only needs the right class to score highest, not calibrated probabilities, so it often ranks correctly anyway.

Follow-up 2 of 3

What happens without smoothing?

A word never seen in class c gets P(w|c) = 0, and any review containing it can never be classified as c.

Follow-up 3 of 3

When would you pick NB over LR?

Very small training sets, short texts, or when you need a model trained in milliseconds or updated incrementally.

#### The 30-second answer

For a text classification baseline I vectorise with bag-of-words or TF-IDF, often adding bigrams, and train multinomial Naive Bayes or logistic regression. Naive Bayes multiplies per-class word probabilities, assuming words are independent given the class, with add-one smoothing so unseen words don't zero the product; it's very fast and works well on short texts. Logistic regression learns a weight per feature without the independence assumption and is usually more accurate with enough data. Both ignore word order, so negation breaks unigram models; bigrams like "not good" fix much of it. They're interpretable and cheap baselines before moving to a fine-tuned Transformer.

**Go further**

#### What not to say

- "Remove stop words first." For sentiment, that deletes "not".

- "Accuracy is enough." Check precision, recall and the confusion matrix, especially with imbalance.

**Key terms and sources**

Classic text classifiers on bag-of-words / TF-IDF features: multinomial Naive Bayes with smoothing, logistic regression, why negation breaks unigram models, n-gram features, and how these baselines compare with fine-tuned Transformers · built from Pang, Lee & Vaithyanathan (2002), McCallum & Nigam (1998), Wang & Manning (ACL 2012), Jurafsky & Martin (SLP3, ch. 4 and Appendix B) and Devlin et al. (2019) · checked 29 Oct 2026

#### Sources

1. B. Pang, L. Lee & S. Vaithyanathan, "Thumbs up? Sentiment Classification using Machine Learning Techniques", EMNLP 2002.

2. A. McCallum & K. Nigam, "A Comparison of Event Models for Naive Bayes Text Classification", AAAI Workshop 1998.

3. S. Wang & C. Manning, "Baselines and Bigrams: Simple, Good Sentiment and Topic Classification", ACL 2012.

4. D. Jurafsky & J. Martin, _Speech and Language Processing_, 3rd ed. draft, ch. 4 and Appendix B, [web.stanford.edu/~jurafsky/slp3](https://web.stanford.edu/~jurafsky/slp3/).

5. J. Devlin, M.-W. Chang, K. Lee & K. Toutanova, "BERT", NAACL 2019, [arXiv:1810.04805](https://arxiv.org/abs/1810.04805).
