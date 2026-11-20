# NLP Fundamentals Practice

> 10 interview questions: TF-IDF, perplexity, BPE, BLEU, NER F1 and hybrid search.

- Track: Fundamentals › NLP Fundamentals › Tagging, retrieval and evaluation
- Type: Interview · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/nlp-practice/
- Before this: Search: BM25, Dense and Hybrid Retrieval (`fundamentals/search-and-retrieval`), NLP Evaluation: BLEU, ROUGE, EM/F1 (`fundamentals/nlp-evaluation-metrics`)
- Quiz topic: `nlp`

How to use this page

Give yourself about 5 minutes per question, as in an interview. Work each one out on paper or out loud (the numbers are small enough to do by hand), then open the answer and compare.

**The toolkit:** idf = log(N / df); bigram P(w | prev) = count(prev w) / count(prev); perplexity = exp(−average log-probability); BPE merges the most frequent adjacent pair; entity F1 needs exact span + type; RRF score = Σ 1 / (60 + rank); BLEU clips each n-gram count at its count in the reference.

Question 1 · Easy · preprocessing

### A teammate adds stop-word removal, stemming and lowercasing to a review sentiment classifier. Accuracy drops from 91% to 84%, mostly on reviews like “the food was not bad”. What went wrong, and what would you do?

Answer: **standard stop-word lists contain negations (“not”, “no”, “never”), so “not bad” became “bad” and the label flipped**

1. Look at the errors first: if they cluster on negated reviews, check the stop-word list. NLTK's and scikit-learn's English lists include “not” and “no”.

2. Fix: keep negations (custom stop list), or skip stop-word removal entirely: with TF-IDF the common words are already down-weighted, and with Transformers you don't remove anything.

3. Add bigrams (“not bad”) so the model sees the negation and the word together.

**Follow-up:** Is stemming ever harmful? Yes: it merges words with different meanings (“university” and “universe” both stem to “univers” with Porter) and produces non-words, which hurts when you need readable features.

Question 2 · Easy · TF-IDF

### You have 400 reviews. “the” appears in all 400; “paneer” appears in 4. Using idf = ln(N / df), what are their idf values, and what does that mean for search?

Answer: **idf(the) = ln(400/400) = 0; idf(paneer) = ln(400/4) = ln 100 ≈ 4.61**

1. A word in every document carries no information about which document you want, so its idf, and therefore its TF-IDF weight, is 0.

2. A rare word like “paneer” gets a high weight, so a query containing it is matched mainly to the few documents that mention it.

3. Libraries add smoothing (scikit-learn uses ln((1 + N) / (1 + df)) + 1 by default), so exact numbers differ but the ordering is the same.

**Follow-up:** Why do we L2-normalise TF-IDF vectors before cosine similarity? So long reviews don't score higher just because they repeat words more; cosine then compares the direction of the vectors.

Question 3 · Medium · perplexity

### A bigram model scores “<s> pizza cold </s>” with P(pizza | <s>) = 0.5, P(cold | pizza) = 0.25, P(</s> | cold) = 0.5. What is the perplexity over the 3 predicted tokens?

Answer: **PP = (0.5 × 0.25 × 0.5)^(−1/3) = 0.0625^(−1/3) ≈ 2.52**

1. Probability of the sequence: 0.5 × 0.25 × 0.5 = 0.0625.

2. Perplexity is the inverse probability normalised by the number of predictions N = 3: 0.0625^(−1/3) ≈ 2.52. Equivalently exp(−(ln 0.5 + ln 0.25 + ln 0.5) / 3).

3. Reading: on average the model is as uncertain as choosing among about 2.5 equally likely words at each step.

**Follow-up:** What happens if one of the bigrams was never seen and the model is unsmoothed? That factor is 0, the product is 0 and perplexity is infinite: that's why n-gram models need smoothing such as Kneser–Ney.

Question 4 · Medium · BPE

### Train BPE on the word counts hug ×10, pug ×5, pun ×12, bun ×4, hugs ×5, starting from characters. What are the first two merges, and how is “bug” tokenised afterwards?

Answer: **merge 1: u + g → “ug” (count 20); merge 2: u + n → “un” (count 16); “bug” → b + ug**

1. Count adjacent pairs weighted by word frequency: u-g appears in hug, pug, hugs = 10 + 5 + 5 = 20; p-u = 17; u-n = 16; h-u = 15. Merge u-g.

2. Recount after the merge: u-n = 12 + 4 = 16, h-ug = 15, p-u = 12. Merge u-n.

3. To tokenise “bug”, apply the merges in order: b u g → b ug. A word with an unseen character like “mug” would hit an unknown token, which byte-level BPE avoids.

**Follow-up:** How does WordPiece choose differently? It scores a pair by count(pair) / (count(first) × count(second)), preferring pairs whose parts rarely appear apart, rather than raw frequency (Hugging Face course, ch. 6).

Question 5 · Medium · BLEU

### Reference: “the cat is on the mat”. Candidate: “the the the the the the the”. What is the unigram precision, and BLEU's modified (clipped) unigram precision?

Answer: **plain precision 7/7 = 1.0; clipped precision 2/7 ≈ 0.29**

1. Every candidate word appears in the reference, so plain precision is 7/7, a perfect score for nonsense.

2. BLEU clips each word's count at the maximum number of times it appears in any reference: “the” appears twice, so only 2 of the 7 count: 2/7.

3. This is the example from the original BLEU paper (Papineni et al., 2002).

**Follow-up:** Your new summariser raises ROUGE-L from 0.41 to 0.44 but users like it less. How? ROUGE rewards word overlap, not faithfulness or readability; check for copied but irrelevant sentences, and validate with human ratings or an LLM judge checked against humans.

Question 6 · Medium · NER F1

### A sentence has 4 gold entities. Your NER model predicts 5 entities; 3 of them match a gold entity exactly (same span and type). What are entity-level precision, recall and F1?

Answer: **P = 3/5 = 0.60, R = 3/4 = 0.75, F1 = 2 × 0.60 × 0.75 / 1.35 ≈ 0.67**

1. Precision = correct predictions / all predictions = 3/5.

2. Recall = correct predictions / gold entities = 3/4.

3. F1 is their harmonic mean, 0.67. A prediction with the right type but one token off counts as both a false positive and a false negative under exact-match scoring (CoNLL).

**Follow-up:** Why not report token accuracy? Most tokens are O (outside any entity), so a model that predicts all O can still score high token accuracy while finding nothing.

Question 7 · Hard · hybrid retrieval

### Your RAG search uses dense embeddings. Users report that queries with order IDs like “ORD-48213” and dish names like “Bawarchi biryani” return the wrong documents, while paraphrased questions work well. What's happening, and how do you fix it? With reciprocal rank fusion (k = 60), document A is ranked 1st by BM25 and 10th by dense; document B is 3rd and 2nd. Which ranks higher?

Answer: **dense embeddings blur exact rare tokens; add BM25 and fuse with RRF. B wins: 1/63 + 1/62 ≈ 0.0320 vs A's 1/61 + 1/70 ≈ 0.0307**

1. Dense retrievers map text to meaning; IDs, codes and rare names are split into subword pieces and land near similar-looking strings, so exact matches are lost. BM25 matches exact terms and weights rare ones highly (high idf).

2. Run BM25 and dense retrieval in parallel and fuse the ranked lists with reciprocal rank fusion, which needs no score calibration: score(d) = Σ 1 / (k + rank).

3. A: 1/61 + 1/70 ≈ 0.0164 + 0.0143 = 0.0307. B: 1/63 + 1/62 ≈ 0.0159 + 0.0161 = 0.0320. B, ranked well by both, beats A, ranked top by only one.

4. Then measure recall@k and MRR on a labelled query set that includes both ID lookups and paraphrased questions, and optionally add a cross-encoder re-ranker on the fused top 20–50.

**Follow-up:** When would you route instead of fuse? If a query matches a strict pattern (an order ID regex), skip retrieval and do a direct database lookup: it's exact, faster and cheaper.

Question 8 · Easy · BERT masking

### A BERT training sequence has 200 tokens. About how many are chosen for masking, and what happens to them? How many positions contribute to the masked loss?

Answer: **30 chosen: about 24 become [MASK], 3 random, 3 unchanged. All 30 are scored**

1. 15% of 200 = 30.

2. 80% of 30 = 24, 10% = 3 and 10% = 3.

3. The loss is computed on all 30, including those left unchanged.

Scoring the unchanged tokens stops the model relying on [MASK] to know where to predict.

Question 9 · Medium · edit distance

### What's the edit distance between “sunday” and “saturday”, with each edit costing 1? Give the edits.

Answer: **3: insert a, insert t, substitute n with r**

1. Line them up: s + (a t) + u + n→r + d a y.

2. That's two insertions and one substitution.

3. The lengths differ by 2, so at least 2 edits are needed, and the table confirms 3 is the minimum.

Filling in the table takes O(mn) time, here 6 × 8 cells.

Question 10 · Hard · Viterbi

### Two tags, N and V. Start: P(N) = 0.6, P(V) = 0.4. Transitions: N→N 0.3, N→V 0.7, V→N 0.8, V→V 0.2. Word 1: P(w₁|N) = 0.5, P(w₁|V) = 0.1. Word 2: P(w₂|N) = 0.2, P(w₂|V) = 0.4. What's the best tag sequence?

Answer: **N, V, with a probability of 0.084**

1. Step 1: N = 0.6 × 0.5 = 0.3, and V = 0.4 × 0.1 = 0.04.

2. Step 2, N: max(0.3 × 0.3, 0.04 × 0.8) × 0.2 = 0.09 × 0.2 = 0.018.

3. Step 2, V: max(0.3 × 0.7, 0.04 × 0.2) × 0.4 = 0.21 × 0.4 = 0.084.

4. V wins, and its pointer leads back to N.

Note that V alone scores higher on word 2, while N wins on word 1. Transitions join the two.

**More practice and sources**

10 interview questions, easy to hard · answers hidden until you click · checked 29 Oct 2026

Keep practising

Built from the lessons in this track and their sources: Jurafsky & Martin, [SLP3](https://web.stanford.edu/~jurafsky/slp3/) (ch. 3, 4, 18, 11); Sennrich et al. (2016) and the [Hugging Face course](https://huggingface.co/learn/llm-course/chapter6/5) BPE example; Papineni et al. (2002) for BLEU clipping; Cormack et al. (2009) for RRF. Review: Preprocessing, TF-IDF, N-gram LMs, Tokenisation, NER, Retrieval, Evaluation.

New lessons: Edit Distance, HMMs and Viterbi and BERT.
