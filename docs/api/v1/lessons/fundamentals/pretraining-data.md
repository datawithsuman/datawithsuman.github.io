# Pretraining Data: Deduplication, Filtering and Mixtures

> How do trillions of web tokens become training data?

- Track: Fundamentals › LLMs › Pretraining
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/pretraining-data/
- Before this: The Next-Token Objective (`fundamentals/next-token-prediction`)
- Quiz topic: `pre`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 5e9338aa6f

## Intuition

### The situation

While crawling the web for food-related text, the team finds thousands of near-identical restaurant pages from one template. A colleague says to keep them, because more data is always better. The interviewer asks:

> How do trillions of web tokens become training data?

**Running example:** while crawling the web for food-related text to pre-train (or continue pre-training) the assistant, the team finds thousands of near-identical restaurant landing pages generated from one template.

#### The web is big, repetitive and mostly not useful text

Common Crawl adds billions of pages per snapshot, but much of it is navigation menus, cookie banners, SEO spam, machine-generated pages and copies of the same content. Training on duplicates wastes compute and makes models **memorise and regurgitate** text: Lee et al. (2022) found that deduplicating C4 reduced how often models emitted memorised training text by about 10× and needed fewer training steps for the same accuracy.

### The idea

Think of cleaning raw grain before an expensive mill. Milling time is fixed, so every stone, husk and repeated sack wastes it. You sieve first, then keep and mix the best grain. MinHash is the quick test that spots two sacks from the same batch without checking each grain.

[Figure: A pipeline that narrows at each step: crawled web pages, extract main text, URL, language and quality filters, remove near-duplicates, then remove PII and benchmarks.]

_Illustrative widths. A typical pipeline, as in FineWeb, which ended with 15 trillion tokens from 96 snapshots._

### Play

**Try to break it.** Switch between 16, 112 and 256 hash functions. Compare pages A and B with pages A and C, and watch the flagged pairs and the largest estimate error.

#### MinHash on four pages

Exact hashing only catches identical pages; one changed word defeats it. Comparing every pair of documents exactly is impossible at billions of pages. MinHash estimates the **Jaccard similarity** of two documents' sets of word 5-grams: for each of k hash functions, keep the smallest hash value over the document's 5-grams. The fraction of positions where two signatures match is an unbiased estimate of their Jaccard similarity, and locality-sensitive hashing (the buckets) finds candidate pairs without comparing everything.

**A**: "Order chicken biryani online from Paradise Biryani House in Hyderabad. Fast delivery in 30 minutes. Fresh ingredients, authentic spices and secure payment. Track your order live and get 20% off your first order today." **B**: the same page ending in "tonight". **C**: the same template for paneer tikka from Punjab Grill in Delhi. **D**: a customer review. Word 5-grams, lower-cased; hash family fixed by seed.

A and B differ by one word, so 29 of their 31 distinct 5-grams are shared: Jaccard **0.94**, estimated as 0.91 with 112 hashes, and flagged; one copy is dropped. A and C come from the same template but describe different restaurants: Jaccard **0.51**, below 0.75, so both are kept. That's the threshold's trade-off: lower it and you also delete legitimate pages that share boilerplate; raise it and lightly edited copies survive. With only 16 hashes the estimates are noisier (A–B estimated at 1.00); more hashes cost more compute but estimate more precisely.

**Now say why:** A and C come from the same template, so why does the pipeline keep both?

## How it works

### How it works

#### In one breath

The data matters as much as the architecture. Raw web crawls are mostly boilerplate, spam, duplicates and non-text, so a pipeline **extracts** the main text, keeps the right **languages**, applies **heuristic quality filters** (length, symbol ratios, repeated lines), removes **near-duplicates**, and increasingly scores pages with a **model-based quality classifier**. Near-duplicates are found with **MinHash**: compare documents by the overlap of their word n-grams (Jaccard similarity), estimated cheaply from a short signature of minimum hash values, so billions of pages can be compared. Then the team chooses the **mixture**: Llama 3 used about 50% general knowledge, 25% maths and reasoning, 17% code and 8% multilingual tokens. Better data gives better models at the same compute: FineWeb-Edu's classifier filtering raised MMLU from 33% to 37% at equal training tokens. What you'll be able to do after this: describe a pretraining data pipeline, explain how MinHash deduplication works, and discuss data mixtures and contamination.

#### A typical pipeline (FineWeb)

1. **Text extraction** from raw HTML (FineWeb uses trafilatura on WARC files), which beat using Common Crawl's own extracted text.

2. **URL filtering and language ID** (e.g. fastText; keep English above a confidence threshold).

3. **Heuristic quality filters:** Gopher and C4 rules (word count, mean word length, symbol-to-word ratio, fraction of lines ending in punctuation, repeated lines and n-grams) plus custom ones.

4. **Near-duplicate removal** with MinHash on word 5-grams (112 hash functions in 14 buckets of 8, targeting about 75% similarity), done per crawl snapshot.

5. **PII redaction** (emails, IP addresses) and, for evaluation hygiene, **decontamination**: removing documents that contain benchmark questions.

The result, FineWeb, has 15 trillion tokens from 96 Common Crawl snapshots (Penedo et al. 2024, [arXiv:2406.17557](https://arxiv.org/abs/2406.17557)). A surprise from the paper: deduplicating globally across all snapshots did _worse_ than deduplicating within each snapshot, because it removed many good older pages and kept low-quality ones.

## In practice

### In practice

#### Model-based filtering and mixtures

- **Quality classifiers:** FineWeb-Edu had Llama-3-70B-Instruct rate hundreds of thousands of pages for educational value (0–5), trained a small classifier on those labels, and kept pages scoring ≥ 3: 1.3T tokens. At the same training budget (350B tokens) it raised MMLU from 33% to 37% and ARC from 46% to 57% compared with FineWeb. DCLM and Llama 3 also use model-based filters.

- **Mixtures:** Llama 3's final pre-training mix was roughly 50% general knowledge, 25% maths and reasoning, 17% code and 8% multilingual tokens, chosen with small-scale experiments and scaling-law predictions; high-quality data is up-weighted again at the end of training (annealing).

- **Running out of data:** Muennighoff et al. (2023) found that repeating data for up to about 4 epochs is almost as good as fresh data, after which returns fall quickly; synthetic data and other languages fill the gap (see below).

**Contamination.** If benchmark questions leak into pre-training data, scores measure memorisation. Labs filter n-gram overlaps with evaluation sets and report contamination analyses; see the evaluation lessons in this track.

##### Synthetic data

When good text runs short, you can have a strong model write more. Stanford's CS336 now teaches this as a standard part of data work.

- **For instructions:** Self-Instruct had GPT-3 write its own instructions, inputs and outputs, filtered out invalid or similar ones, then fine-tuned on the result. It gained 33% on one instruction benchmark, on par with InstructGPT-001.

- **For pre-training:** phi-1 used 6B tokens of filtered web data, plus 1B tokens of textbooks and exercises written by GPT-3.5. That 1.3B model reached 50.6% on HumanEval.

- **The risks:** errors and biases carry over from the model that wrote it, the variety can be narrow, and benchmarks can look better than real-world use. Check licences too, as many models forbid training on their outputs. This is close to sequence-level distillation.

#### Every token should earn its compute

Pre-training compute is fixed, so data work is about making each token count: remove what teaches nothing (boilerplate, spam), what teaches the wrong thing (memorised duplicates, test sets), and up-weight what teaches the most (educational, code, maths).

### The answer that sounds right

#### "More data is always better"

It sounds right, until you remember pre-training compute is fixed. Filtered, deduplicated data beats bigger raw data at equal compute. Lee et al. found that deduplicating C4 cut memorised output by about 10×, and needed fewer steps for the same accuracy. And exact hashing isn't enough: change one word and it misses the copy.

## Say it

### How do trillions of web tokens become training data?

#### The interviewer pushes further

Follow-up 1 of 3

Why deduplicate?

Duplicates waste compute, over-weight some content and increase memorisation and regurgitation of training text; deduplicated data trains as well or better with fewer steps (Lee et al. 2022).

Follow-up 2 of 3

How would you pick the data mixture?

Train small proxy models on candidate mixtures, measure downstream metrics, extrapolate with scaling laws, and up-weight high-quality sources during a final annealing phase.

Follow-up 3 of 3

What's the risk of an LLM-based quality filter?

It encodes the rater's biases (e.g. "educational" favours certain styles and topics), can reduce diversity, and can remove dialects or domains you need.

#### The 30-second answer

A pretraining data pipeline extracts main text from crawled HTML, filters by URL and language, applies heuristic quality rules like those from Gopher and C4, removes near-duplicates with MinHash over word n-grams, redacts PII and decontaminates benchmarks, and increasingly uses a model-based quality classifier, as in FineWeb-Edu, which improved MMLU from 33 to 37 percent at the same token budget. MinHash estimates Jaccard similarity between n-gram sets from short signatures of minimum hash values, and LSH buckets make it scale to billions of pages. Finally you choose a mixture, for example Llama 3's roughly half general text, a quarter maths and reasoning, 17 percent code and 8 percent multilingual, tuned with small proxy runs.

**Go further**

#### What not to say

- "More data is always better." Filtered, deduplicated data beats bigger raw data at equal compute.

- "Exact hashing is enough for deduplication." It misses near-duplicates.

**Key terms and sources**

How trillions of tokens of web text become training data: text extraction, language and heuristic quality filters, near-duplicate removal with MinHash, model-based quality classifiers, decontamination, and choosing the mix of web, code, maths and multilingual data · built from Penedo et al. (FineWeb, NeurIPS 2024 Datasets & Benchmarks), Broder (MinHash, 1997), Lee et al. (Deduplicating Training Data, ACL 2022), Rae et al. (Gopher, 2021), Raffel et al. (C4, 2020), Muennighoff et al. (Data-Constrained Scaling, NeurIPS 2023) and Meta's Llama 3 report (2024) · checked 29 Oct 2026

#### Sources

1. G. Penedo et al., "The FineWeb Datasets: Decanting the Web for the Finest Text Data at Scale", NeurIPS 2024 Datasets & Benchmarks, [arXiv:2406.17557](https://arxiv.org/abs/2406.17557).

2. A. Broder, "On the Resemblance and Containment of Documents", 1997; K. Lee et al., "Deduplicating Training Data Makes Language Models Better", ACL 2022, [arXiv:2107.06499](https://arxiv.org/abs/2107.06499).

3. J. Rae et al., "Scaling Language Models: Methods, Analysis & Insights from Training Gopher", 2021, [arXiv:2112.11446](https://arxiv.org/abs/2112.11446); C. Raffel et al. (T5 / C4), JMLR 2020, [arXiv:1910.10683](https://arxiv.org/abs/1910.10683).

4. N. Muennighoff et al., "Scaling Data-Constrained Language Models", NeurIPS 2023, [arXiv:2305.16264](https://arxiv.org/abs/2305.16264).

5. Llama Team, Meta, "The Llama 3 Herd of Models", 2024, [arXiv:2407.21783](https://arxiv.org/abs/2407.21783) (§3.1, data mix).

6. Y. Wang et al., "Self-Instruct", 2022, [arXiv:2212.10560](https://arxiv.org/abs/2212.10560); S. Gunasekar et al., "Textbooks Are All You Need", 2023, [arXiv:2306.11644](https://arxiv.org/abs/2306.11644).

7. Y. Wang et al., "Self-Instruct", 2022, [arXiv:2212.10560](https://arxiv.org/abs/2212.10560); S. Gunasekar et al., "Textbooks Are All You Need", 2023, [arXiv:2306.11644](https://arxiv.org/abs/2306.11644).

8. Y. Wang et al., "Self-Instruct", 2022, [arXiv:2212.10560](https://arxiv.org/abs/2212.10560); S. Gunasekar et al., "Textbooks Are All You Need", 2023, [arXiv:2306.11644](https://arxiv.org/abs/2306.11644).
