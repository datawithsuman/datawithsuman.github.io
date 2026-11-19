# NLP Evaluation: BLEU, ROUGE, EM/F1

> Why can word salad beat a correct paraphrase on BLEU?

- Track: Fundamentals › NLP Fundamentals › Tagging, retrieval and evaluation
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/nlp-evaluation-metrics/
- Before this: Text Classification: Naive Bayes vs Logistic Regression (`fundamentals/text-classification`)
- Quiz topic: `nlp`

## Intuition

### The situation

The support bot summarises complaints, and you score it automatically against human summaries. A correct paraphrase gets BLEU 0.29, and a word salad gets 0.36. So does a summary saying the opposite of the complaint. The interviewer asks:

> How do you score generated text, and what do these metrics miss?

**Running example:** the support bot summarises a complaint. The human reference summary is "_the biryani arrived cold and late_". How do we score the bot's different summaries automatically?

#### Many right answers, no single label

A classifier is either right or wrong. Generated text has many valid versions: "the biryani was delivered late and cold" says the same thing as the reference in different words. Human judgement is the gold standard but slow and expensive, so we need cheap automatic scores to compare systems during development, and we must know what they miss.

### The idea

Think of a teacher marking essays by counting the words that match the answer key. Shuffle the key and you score well. Write a correct answer in your own words and you lose marks. The count measures shared words, not shared meaning.

[Figure: Sentence BLEU against the reference. The correct paraphrase scores 0.29. Word salad and the summary with the opposite meaning both score 0.36.]

_Sentence BLEU from the lab, with add-1 smoothing for 2- to 4-grams._

### Play

**Try to break it.** Go through identical, paraphrase, word salad, too short and wrong meaning. Compare BLEU, ROUGE-1 and ROUGE-L on each.

#### Five candidate summaries, one reference

Reference: "the biryani arrived cold and late". Candidates: identical; "the biryani was delivered late and cold"; "late cold and the arrived biryani"; "biryani cold"; "the biryani arrived hot and on time". Sentence BLEU with add-1 smoothing for 2- to 4-grams.

The **correct paraphrase** gets BLEU **0.29** and ROUGE-L 0.46: it uses different words in a different order. The **word salad**, the reference's words shuffled into nonsense, scores _higher_: BLEU **0.36**, and a perfect ROUGE-1 and token F1 of **1.00**, because unigram metrics ignore order. Worst of all, "the biryani arrived **hot and on time**", the _opposite_ of the complaint, scores BLEU 0.36 and ROUGE-L **0.62**, beating the correct paraphrase on both. "biryani cold" is cut down by the brevity penalty (0.14). Overlap metrics measure shared words, not shared meaning.

**Now say why:** why does word salad get a perfect ROUGE-1 and token F1?

## Maths

### Maths

#### In one breath

Classic NLP metrics compare a model's output with one or more human **references** by counting overlapping words. **BLEU** (machine translation) is a precision: what fraction of the output's 1- to 4-grams appear in the reference, clipped so repeating a word doesn't help, times a **brevity penalty** for outputs that are too short. **ROUGE** (summarisation) leans on recall: ROUGE-1/2 count unigram/bigram overlap, **ROUGE-L** uses the longest common subsequence. Extractive QA uses **exact match** and **token F1**; language models use perplexity. All overlap metrics share one weakness: they reward the **same words**, not the **same meaning**. A correct paraphrase can score lower than word salad, which is why embedding-based scores, LLM judges and human evaluation are used alongside them.What you'll be able to do after this: compute BLEU, ROUGE and token F1, pick a metric per task, and explain what overlap metrics can't measure.

#### BLEU: clipped n-gram precision with a brevity penalty

$$ \mathrm{BLEU} = \mathrm{BP}\cdot \exp\Big(\textstyle\sum_{n=1}^{4}\tfrac14 \logp_n\Big), \qquad \mathrm{BP} = \begin{cases}1 & c > r\\ e^{1-r/c} & c \le r\end{cases} $$

Papineni, Roukos, Ward & Zhu, ACL 2002. BLEU was designed for corpus-level scoring with multiple references; sentence-level scores are noisy. Use SacreBLEU for comparable, reproducible numbers (Post 2018).

- **brevity penalty**: 1 if the candidate is longer than the reference, otherwise exp(1 − r/c). Stops a model from scoring high precision by outputting two safe words.

- **clipped n-gram precisions**: For n = 1…4: matching n-grams ÷ n-grams in the candidate, where each n-gram’s count is clipped to its count in the reference.

- **geometric mean**: Average the log-precisions: if any order has zero matches, unsmoothed BLEU is 0, so sentence-level BLEU is usually smoothed.

- **ROUGE-N** (Lin 2004): n-gram overlap, usually reported as recall or F1; ROUGE-1 and ROUGE-2 are standard for summarisation.

- **ROUGE-L:** F-measure based on the longest common subsequence, which rewards words appearing in the same order without requiring them to be adjacent.

- **Exact match / token F1** (SQuAD, Rajpurkar et al. 2016): EM is 1 only for an identical normalised answer; F1 gives partial credit for overlapping tokens.

## In practice

### In practice

#### Measuring meaning

- **Embedding-based:** BERTScore matches each token to its most similar reference token using contextual embeddings, so paraphrases score well (Zhang et al., ICLR 2020).

- **LLM-as-a-judge:** a strong LLM rates outputs against a rubric or compares two outputs; it agrees with human preferences reasonably well but has position and verbosity biases (Zheng et al., NeurIPS 2023).

- **Task metrics:** for RAG, faithfulness and answer relevance; for code, unit tests pass@k; for classification-like outputs, accuracy or F1.

- **Human evaluation** remains the final check for fluency, correctness and helpfulness; Callison-Burch et al. (2006) showed BLEU improvements don't always mean better translations.

#### Which metric

| Task | Standard metric | Watch out |
|---|---|---|
| Machine translation | BLEU (SacreBLEU), chrF, COMET | corpus-level only; tokenisation changes BLEU |
| Summarisation | ROUGE-1/2/L | rewards copying; check faithfulness separately |
| Extractive QA | exact match, token F1 | normalise case, punctuation, articles first |
| Language modelling | perplexity | only comparable with the same tokeniser |
| NER / tagging | entity-level F1 (NER lesson) | not token accuracy |
| Open-ended generation | LLM-as-judge, human eval, BERTScore | judge biases; validate against humans |

### The answer that sounds right

#### "A higher BLEU means a better system"

It sounds right, since a higher score ought to mean a closer match. But in the lab, the summary with the opposite meaning beats the correct paraphrase on BLEU and ROUGE-L. And small BLEU differences often don't match human judgement. Nor does ROUGE measure factual correctness, so check faithfulness separately.

## Say it

### How do you score generated text, and what do these metrics miss?

#### The interviewer pushes further

Follow-up 1 of 3

Why is BLEU precision-based and ROUGE recall-based?

Translation should not add content that isn't in the reference (precision); a summary should cover the reference's key content (recall).

Follow-up 2 of 3

Why clip counts in BLEU?

Without clipping, "the the the the" would get perfect unigram precision against any reference containing "the".

Follow-up 3 of 3

How would you evaluate a RAG chatbot?

Retrieval recall@k, answer faithfulness to the retrieved context, answer relevance, and a small human-labelled set to validate an LLM judge.

#### The 30-second answer

BLEU, used for translation, is the geometric mean of clipped 1- to 4-gram precisions times a brevity penalty for short outputs, and is meant to be computed at corpus level. ROUGE, used for summarisation, measures n-gram recall or F1, with ROUGE-L based on the longest common subsequence. Extractive QA uses exact match and token-level F1, and language models use perplexity. All overlap metrics reward the same words rather than the same meaning, so paraphrases can score low and fluent but wrong outputs can score high; that's why we add embedding-based metrics like BERTScore, LLM-as-judge, task-specific checks like faithfulness, and human evaluation.

**Go further**

#### What not to say

- "A higher BLEU always means a better system." Small BLEU differences often don't match human judgement.

- "ROUGE measures factual correctness." A summary can share words and still be wrong.

**Key terms and sources**

How generated or extracted text is scored against references: BLEU for translation (clipped n-gram precision and the brevity penalty), ROUGE for summarisation (n-gram and longest-common-subsequence recall), exact match and token F1 for question answering, perplexity for language models, and why overlap metrics miss meaning · built from Papineni et al. (ACL 2002), Lin (2004), Rajpurkar et al. (SQuAD, EMNLP 2016), Callison-Burch et al. (2006), Zhang et al. (BERTScore, ICLR 2020), Post (2018) and Zheng et al. (2023) · checked 29 Oct 2026

#### Sources

1. K. Papineni, S. Roukos, T. Ward & W.-J. Zhu, "BLEU: a Method for Automatic Evaluation of Machine Translation", ACL 2002.

2. C.-Y. Lin, "ROUGE: A Package for Automatic Evaluation of Summaries", ACL Workshop 2004.

3. P. Rajpurkar, J. Zhang, K. Lopyrev & P. Liang, "SQuAD: 100,000+ Questions for Machine Comprehension of Text", EMNLP 2016, arXiv:1606.05250.

4. C. Callison-Burch, M. Osborne & P. Koehn, "Re-evaluating the Role of BLEU in Machine Translation Research", EACL 2006.

5. T. Zhang et al., "BERTScore: Evaluating Text Generation with BERT", ICLR 2020, arXiv:1904.09675; M. Post, "A Call for Clarity in Reporting BLEU Scores", WMT 2018, arXiv:1804.08771.

6. L. Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena", NeurIPS 2023, arXiv:2306.05685.
