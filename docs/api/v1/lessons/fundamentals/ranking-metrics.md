# Ranking Metrics

> How do you score a search page, a recommendation list, or a RAG retriever?

- Track: Fundamentals › Classical ML › Evaluation metrics
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/ranking-metrics/
- Before this: Classification Metrics (`fundamentals/classification-metrics`)
- Related: Design a recommendation system (`system-design/recommendation-system`)
- Quiz topic: `metrics`

## Intuition

### The situation

Two search engines return the same 10 products in a different order. Accuracy-style metrics score them the same, but users don't see them the same. The interviewer asks:

> Which metrics would you use to evaluate a ranked list?

**Scenarios:** an e-commerce search for "wireless earbuds under ₹3,000" with graded relevance labels (3 = perfect, 2 = good, 1 = loosely related, 0 = irrelevant), and a RAG retriever that must find the one chunk containing the answer. Lists and labels are illustrative; metrics are computed live.

#### Two search engines return the same 10 products in a different order

Accuracy-style metrics see the same set and score them identically. Users don't: they look at the first few results, and a perfect match in position 1 is worth far more than one in position 9. A RAG system is even stricter: if the chunk with the answer isn't in the top 5 passed to the LLM, the answer is lost no matter what's at position 6. Ranking metrics put a number on "the right things, near the top".

### The idea

Think of a shop window. Items at the front get seen, and items at the back barely do. Ranking metrics give more credit for putting good items near the front, and they differ in how much.

[Figure: Bars for result positions 1 to 5. Each position counts for less: 1, 0.63, 0.5, 0.43 and 0.39.]

_The standard log discount used in DCG, 1 ÷ log₂(position + 1)._

### Play

**Try to break it.** Compare Engine A and Engine C at a cut-off of 10, then change the cut-off to 3. Then look at the ideal order.

#### Three engines, one query, every metric

Binary metrics count grade ≥ 2 ("good" or better) as relevant. There are 5 such items in the catalogue for this query, one of which no engine retrieved in its top 10 (so recall never reaches 100%). NDCG uses the grades (0–3) directly as gains, with the ideal order built from all labelled items.

**Now say why:** why can two engines tie on one metric and differ on another?

## Maths

### Maths

#### In one breath

Search, recommendations and RAG retrieval return an **ordered list**, and users mostly look at the top. Ranking metrics score the list, not single predictions. **Precision@k**: how much of the top k is relevant. **Recall@k**: how much of everything relevant made the top k (the key RAG retriever metric). **MRR**: how high the first relevant result is. **MAP**: precision averaged at every relevant hit. **NDCG**: graded relevance with a position discount, normalised against the ideal order, the standard for search. Offline metrics are a proxy; online behaviour (clicks, conversions) is the truth.What you'll be able to do after this: compute every metric by hand on a ranked list, choose the right one for search vs RAG vs recommendations, and explain why NDCG needs graded labels.

#### Relevance labels and the cut-off k

You need a judgement for each (query, item) pair: **binary** (relevant or not; RAG gold chunks, clicked or not) or **graded** (0–3 from human raters, or purchase > add-to-cart > click). And a **cut-off k**: how many positions matter (what fits on the first screen, how many chunks fit in the prompt). Every metric below is "@k". Choose k from the product, not habit.

#### Precision@k, Recall@k and hit rate

$$ P@k = \tfrac{\#\text{rel in top }k}{k} \qquad R@k = \tfrac{\#\text{rel in top }k}{\#\text{rel total}} \qquad HR@k = \mathbb 1[\#\text{rel in top }k \ge 1] $$

- **precision@k**: Share of the top k that is relevant. What the user sees on the first screen.

- **recall@k**: Share of all relevant items that made the top k. For RAG, the gold chunk must be in the k chunks sent to the LLM: this is the retriever's key metric.

- **hit rate@k**: 1 if at least one relevant item is in the top k, else 0, averaged over queries. Common for recommendations (“did the user's next purchase appear in our 10 suggestions?”).

Recall@k needs to know every relevant item, which is easy when there's one gold answer (RAG evaluation sets) and hard for open catalogues, where it's estimated by pooling results from several systems (the TREC approach).

#### Reciprocal rank and MRR

$$ \text{MRR} = \tfrac{1}{|Q|}\textstyle\sum_{q\in Q} \,1\,/\,\text{rank}_q $$

scikit-learn notes that with exactly one relevant label per sample, label-ranking average precision "is equivalent to the mean reciprocal rank" docs.

- **mean reciprocal rank**: Average over queries of 1 / (position of the first relevant result).

- **over queries**: |Q| queries in the evaluation set.

- **rank of the first hit**: First relevant at position 1 → 1.0; at 2 → 0.5; at 5 → 0.2; none found → 0. Steep: moving from 1st to 2nd halves the score.

RAG retriever evaluation: 8 questions, each with one gold chunk. The table shows the rank where each retriever placed it (— = not in the top 20).

Retriever X often puts the gold chunk first but sometimes misses it entirely; Y rarely ranks it first but almost always gets it into the top 5. If you pass 5 chunks to the LLM, Y's Recall@5 matters more than X's higher MRR. If you show one answer (a FAQ bot), MRR, or even Recall@1, is the metric.

#### Average precision and MAP

$$ AP@k = \tfrac{1}{\min(k,\,R)}\textstyle\sum_{i=1}^{k} P@i\cdot\text{rel}(i) $$

The standard IR definition (Manning, Raghavan & Schütze, _Introduction to Information Retrieval_, ch. 8); it's the ranking version of the area under the precision–recall curve from the ROC vs PR lesson.

- **average precision@k**: For one query: average of precision@i taken at each position i where a relevant item appears.

- **only at hits**: rel(i) is 1 at relevant positions, 0 elsewhere, so precision is sampled exactly where the user finds something useful.

- **normaliser**: Divide by the number of relevant items (capped at k in the @k version), so missing relevant items costs you. MAP is the mean of AP over queries.

#### DCG and NDCG

$$ \text{DCG}@k = \textstyle\sum_{i=1}^{k}\text{rel}_i \,/\, \log_2(i+1) \qquad \text{NDCG}@k = \text{DCG}@k \,/\, \text{IDCG}@k $$

Järvelin & Kekäläinen introduced cumulated gain, its discounted version, and normalisation against the ideal ranking ACM TOIS 2002. scikit-learn: "Use NDCG when [the ground truth] has graded relevance" docs. Log base and gain function vary between libraries: always say which you used.

- **discounted cumulative gain**: Sum of the gains of the top k items, each discounted by its position.

- **gain**: The relevance grade of the item at position i (some use 2^rel − 1 to reward top grades more strongly).

- **position discount**: Divide by log₂(i + 1): position 1 counts fully, 2 counts 63%, 3 counts 50%, 10 counts 29%.

- **normalise**: Divide by the DCG of the ideal ordering (IDCG), so NDCG is between 0 and 1 and comparable across queries with different numbers of relevant items.

## In practice

### In practice

#### Labels are a proxy; users are the truth

##### Offline (before launch)

- NDCG / MAP / Recall@k on labelled queries

- Fast, repeatable, cheap to compare 50 models

- Labels can be stale, biased toward what the old system showed, or miss new items

##### Online (after launch)

- Click-through rate, conversion, add-to-cart, dwell time, "zero-result rate", reformulation rate

- A/B test against the current system

- Clicks have **position bias** (people click the top regardless), so raw CTR flatters whatever is shown first

Beyond accuracy, recommenders also track **coverage** (how much of the catalogue ever gets recommended), **diversity** (are the top 10 all the same item in different colours?) and **novelty**. A list that maximises NDCG with ten near-duplicates is a bad product.

#### Which metric, in which situation

| Scenario | Offline metric | Why |
|---|---|---|
| E-commerce / web search | NDCG@10 (graded) | Grades and positions both matter; first screen dominates |
| RAG retriever | Recall@k (k = chunks passed to the LLM), + MRR | The answer must be in the context; order matters less once it's in |
| FAQ bot / "I'm feeling lucky" / voice assistant | MRR or Recall@1 | Only the first answer is used |
| Recommendations ("next purchase") | Hit rate@k, Recall@k, + coverage/diversity | Usually one held-out positive per user; avoid an all-bestseller list |
| Binary relevance with several relevant items (document retrieval) | MAP | Rewards finding all of them early |
| Legal / patent / medical literature search | Recall@k with large k | Missing a relevant document is the costly error |
| Feed ranking at scale | NDCG offline, CTR / dwell / retention online | Offline to iterate, online to decide |

### The answer that sounds right

#### "Use precision@10"

Precision@10 counts relevant items in the top 10, so it can't tell "perfect match first" from "perfect match tenth", and it treats a loosely related accessory like the exact product. In the Play lab, in the Intuition tab, engines A and C have the same precision@10 but very different NDCG. Position and grade both matter, which is what MRR, MAP and NDCG add.

#### What to keep

- **Average over queries, then look at the worst queries.** A great mean can hide queries that return nothing useful.

- **NDCG values aren't comparable** across different gain functions, log bases, k, or label sets.

- **Relevance labels age**: new products, new documents, new user intents. Refresh them.

- **Offline wins don't always transfer online.** Treat offline metrics as a filter for what's worth an A/B test.

## Say it

### Which metrics would you use to evaluate a ranked list?

#### The interviewer pushes further

Follow-up 1 of 4

How would you evaluate the retriever in a RAG system?

Build a set of questions with gold chunks (or answer-containing passages). Measure Recall@k at the k you actually pass to the LLM, plus MRR and latency. Then evaluate end-to-end answer quality separately, since good retrieval doesn't guarantee a good answer.

Follow-up 2 of 4

Why the log discount in NDCG?

It models declining attention down the list, smoothly: position 1 counts fully, position 10 about 29%. Normalising by the ideal DCG makes scores comparable across queries with different numbers of relevant items.

Follow-up 3 of 4

MRR vs MAP?

MRR only cares about the first relevant item, right for single-answer tasks. MAP rewards ranking all relevant items early, right when users want several.

Follow-up 4 of 4

Offline NDCG improved but online CTR didn't. Why?

Stale or biased labels, position bias in the click data the labels came from, a mismatch between label grades and what users want, diversity or latency changes, or a difference too small to show up in the test. Check per-segment results and run the test long enough.

#### The 30-second answer

Ranking metrics score an ordered list at a cut-off k. Precision@k and Recall@k ignore order within the top k; MRR looks at the position of the first relevant result; MAP averages precision at each relevant hit; NDCG uses graded relevance with a logarithmic position discount, normalised by the ideal ranking. For a RAG retriever I'd use Recall@k with k equal to the number of chunks in the prompt, plus MRR; for search, NDCG@10; for single-answer systems, MRR. Then I'd validate online with an A/B test on clicks or conversions, keeping position bias in mind.

**Go further**

#### What not to say

- "Accuracy for search." Order and position are the whole point.

- "NDCG with binary labels is the same as MAP." They weight positions differently.

- "High offline NDCG means users will be happy." Validate online.

**Key terms and sources**

Precision@k, Recall@k, Hit Rate, MRR, MAP and NDCG · built from Järvelin & Kekäläinen (2002), Manning et al.'s _Introduction to IR_ and scikit-learn's docs · checked 28 Oct 2026

#### Glossary

| Term | Meaning |
|---|---|
| **P@k / R@k** | Share of top k that's relevant / share of relevant found in top k. |
| **Hit rate@k** | At least one relevant in top k. |
| **MRR** | Mean of 1 / rank of the first relevant result. |
| **AP / MAP** | Precision averaged at each relevant position / mean over queries. |
| **DCG / NDCG** | Position-discounted graded gain / normalised by the ideal order. |
| **IDCG** | DCG of the best possible ordering. |
| **Position bias** | Users click higher results more, regardless of relevance. |

#### What this page is built from

1. K. Järvelin & J. Kekäläinen, Cumulated gain-based evaluation of IR techniques, ACM TOIS 20(4) (2002).

2. C. Manning, P. Raghavan & H. Schütze, _Introduction to Information Retrieval_, ch. 8 (evaluation: precision, recall, MAP), Cambridge University Press 2008.

3. scikit-learn, Metrics and scoring: ranking metrics (DCG/NDCG, LRAP ≈ MRR, coverage error).

4. Discounted cumulative gain (common log₂(i + 1) form).

Search results, grades and RAG ranks are illustrative.
