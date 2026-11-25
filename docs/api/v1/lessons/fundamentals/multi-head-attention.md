# Multi-Head Attention

> Why several heads, and what do they cost at long context?

- Track: Fundamentals › Deep Learning › Attention and Transformers
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/multi-head-attention/
- Before this: Self-Attention (Q, K, V) (`fundamentals/self-attention`)
- Quiz topic: `attn`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: b6030bd96e

## Intuition

### The situation

With one attention head, "cold" has to split its attention between "biryani", what is cold, and "was", the verb before it. The signals blur together. The interviewer asks:

> Why several heads, and what do they cost at long context?

**Running example:** the same review, "_the biryani was cold but the naan was great_". To understand it, a word may need to know _which food it describes_ and _which word came right before it_ at the same time.

Where this lesson sits: inside the attention box of each Transformer layer.

Full walkthrough: The Transformer, End to End.

#### One head, one weighted average

A single attention head gives each token one probability distribution over the other tokens. If "cold" needs both "biryani" (what is cold?) and "was" (the verb just before it), one distribution has to split its weight and the two signals get blurred into one average. We want several independent looks.

### The idea

Think of several readers going through the same text, each with their own highlighter. One marks food, another marks grammar. Then they combine their notes, instead of one highlighter trying to do both jobs.

[Figure: The same sentence twice. One head highlights biryani for the word cold, and another highlights was, the word just before it.]

_Illustrative. Heads aren't told their jobs. Each learns its own pattern._

### Play

**Try to break it.** Switch between the two heads, and compare what "cold" and "naan" attend to in each.

#### Two heads, two different jobs

Rows: the token doing the looking (query); columns: the token looked at (key); darker = more weight. Hand-set heads that mimic patterns found in trained models (illustrative).

Head 1 ties adjectives and verbs to the food they describe: "cold" → biryani, "great" → naan. Head 2 ignores meaning and just looks one word back: a positional head. After concatenation, the next layer gets both facts for every word. Studies of BERT found exactly such heads: some attend to the previous or next token, some to delimiters, some follow syntactic relations like objects of verbs (Clark et al. 2019); and many heads can be pruned with little loss, while a few specialised ones matter most (Voita et al. 2019; Michel et al. 2019).

**Now say why:** what would be lost if both patterns had to share one set of weights?

## Maths

### Maths

#### In one breath

One attention head produces one weighted average per token, so it can only follow one kind of relationship at a time. **Multi-head attention** splits the model width d into h heads of size d/h, runs attention separately in each (with its own WQ, WK, WV), **concatenates** the results and mixes them with an output matrix WO. Different heads learn different jobs (one links adjectives to nouns, another looks at the previous word, another follows syntax), at the **same cost** as a single full-width head: the parameter count stays 4d². The expensive part at long context is the n × n score matrix per head and the cached keys and values, which is why LLMs share keys and values across heads (**MQA/GQA**). What you'll be able to do after this: write multi-head attention, explain why multiple heads help, and compute the parameters, score-matrix size and KV-cache memory.

#### Split, attend, concatenate, mix

$$ \mathrm{MHA}(X) = {\mathrm{Concat}(\mathrm{head}_1,\dots,\mathrm{head}_h)}\,{W_O}, \qquad {\mathrm{head}_i = \mathrm{Attention}(XW_Q^{(i)},\, XW_K^{(i)},\, XW_V^{(i)})} $$

Vaswani et al. (2017) used h = 8 heads of size 64 with d = 512: "multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions". In code, all heads are computed in one batched matrix multiply.

- **one head**: Ordinary scaled dot-product attention, but with its own projections into a d/h-dimensional subspace. With d = 512 and 8 heads, each head works in 64 dimensions.

- **concatenate**: Stack the h head outputs side by side: back to d dimensions.

- **output projection**: A d × d matrix W_O that mixes information across heads.

## In practice

### In practice

#### Parameters stay the same; memory grows with n²

Score matrix = n² × heads × 2 bytes (what naive attention would hold for one sequence). KV cache = 2 × n × d × 2 bytes per layer for standard multi-head attention; with grouped-query attention using 8 key/value heads it shrinks by heads ÷ 8.

For a 7B-class model (d = 4,096, 32 heads) at 8,192 tokens, the attention weights are **67 million** per layer whatever the head count, but storing the full score matrix would take **4.3 GB per layer**, which is why FlashAttention computes it in tiles without ever storing it. During generation the cached keys and values take **134 MB per layer** (4.3 GB over 32 layers) per sequence; grouped-query attention with 8 KV heads cuts that 4× to 34 MB. At 131,072 tokens the naive score matrix would need 1.1 TB per layer.

#### Sharing keys and values: MQA and GQA

- **Multi-query attention (MQA):** all heads share a single key and value projection; the KV cache shrinks by a factor of h and decoding speeds up, with a small quality cost (Shazeer 2019).

- **Grouped-query attention (GQA):** groups of query heads share one KV head (e.g. 32 query heads, 8 KV heads): close to full multi-head quality with most of MQA's speed (Ainslie et al. 2023). Used in LLaMA 2 70B, LLaMA 3 and Mistral.

- Why it matters: generating each token re-reads the whole KV cache, so its size, not the FLOPs, often limits serving speed.

### The answer that sounds right

#### "More heads means more parameters"

It sounds right, since each head has its own projections. But with d fixed, each head works in a smaller space of size d ÷ h, so the total stays at 4d². Adding heads changes how attention gets divided, not how many weights you have. The real cost at long context is the n-by-n score matrix and, during generation, the KV cache.

## Say it

### Why several heads, and what do they cost at long context?

#### The interviewer pushes further

Follow-up 1 of 3

Does adding heads add parameters?

No, if d is fixed: each head gets d/h dimensions. 8 heads of 64 cost the same as 1 head of 512.

Follow-up 2 of 3

Can you have too many heads?

Yes: with a fixed width, each head gets too small a subspace to represent useful queries and keys; very small head sizes hurt.

Follow-up 3 of 3

KV cache size for one sequence?

2 (K and V) × layers × tokens × KV heads × head size × bytes per value. GQA and MQA reduce the KV-head count.

#### The 30-second answer

Multi-head attention runs h attention operations in parallel, each with its own query, key and value projections into a subspace of size d over h, then concatenates the outputs and mixes them with an output projection. Each head gives a separate attention pattern, so different heads can track different relations, like coreference, the previous token or syntax, instead of blending them into one average. The parameter count stays 4 d squared regardless of h. The cost that grows is the n-by-n score matrix and, during generation, the KV cache, which is why modern LLMs use FlashAttention and share keys and values across heads with grouped-query or multi-query attention.

**Go further**

#### What not to say

- "Each head sees a different part of the sentence." Each head sees the whole sentence, in a different learned subspace.

- "More heads means more parameters." Not at fixed d.

**Key terms and sources**

Running several attention operations in parallel, each in its own smaller subspace, so different heads can track different relationships; the projections, concatenation and output matrix; head specialisation; and the memory cost of attention at long context, including MQA/GQA · built from Vaswani et al. (2017), Clark et al. (2019), Voita et al. (2019), Michel et al. (2019), Shazeer (2019) and Ainslie et al. (2023) · checked 29 Oct 2026

#### Sources

1. A. Vaswani et al., "Attention Is All You Need", NeurIPS 2017, [arXiv:1706.03762](https://arxiv.org/abs/1706.03762).

2. K. Clark, U. Khandelwal, O. Levy & C. Manning, "What Does BERT Look At? An Analysis of BERT's Attention", BlackboxNLP 2019, [arXiv:1906.04341](https://arxiv.org/abs/1906.04341).

3. E. Voita et al., "Analyzing Multi-Head Self-Attention: Specialized Heads Do the Heavy Lifting, the Rest Can Be Pruned", ACL 2019, [arXiv:1905.09418](https://arxiv.org/abs/1905.09418).

4. P. Michel, O. Levy & G. Neubig, "Are Sixteen Heads Really Better than One?", NeurIPS 2019, [arXiv:1905.10650](https://arxiv.org/abs/1905.10650).

5. N. Shazeer, "Fast Transformer Decoding: One Write-Head is All You Need", [arXiv:1911.02150](https://arxiv.org/abs/1911.02150), 2019.

6. J. Ainslie et al., "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints", EMNLP 2023, [arXiv:2305.13245](https://arxiv.org/abs/2305.13245).
