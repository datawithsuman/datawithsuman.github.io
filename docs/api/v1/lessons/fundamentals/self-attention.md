# Self-Attention (Q, K, V)

> What do Q, K and V do, and why divide by √d?

- Track: Fundamentals › Deep Learning › Attention and Transformers
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/self-attention/
- Before this: Seq2seq and Bahdanau Attention (`fundamentals/seq2seq-and-attention`), Vectors, Dot Products & Cosine Similarity (`fundamentals/vectors-and-cosine-similarity`)
- Related: Attention Is All You Need (`papers/attention-is-all-you-need`)
- Quiz topic: `attn`

## Intuition

### The situation

Your review says "the biryani was cold but the naan was great". An RNN has to carry "biryani" along to reach "cold", and a CNN only sees nearby words. The interviewer asks:

> What do Q, K and V do, and why divide by √d?

**Running example:** the review "_the biryani was cold but the naan was great_": 9 tokens. Which food was cold, which was great? A good representation of "cold" should contain "biryani", and "great" should contain "naan".

Where this lesson sits in the Transformer: the highlighted box. Every Attention & Transformers lesson shows this map.

Full walkthrough: The Transformer, End to End.

#### Words need context from anywhere in the sentence

"Cold" means nothing until you know what was cold. An RNN has to carry "biryani" through the hidden state to reach "cold"; a CNN only sees nearby words. We want each word to look directly at every other word and decide, from the content, which ones matter: the attention idea from seq2seq, applied within one sequence.

### The idea

Think of a room where each word asks a question. The query is what a word is looking for, the key is the label every word wears, and the value is what it hands over. "Cold" asks what's cold, biryani's label matches, so "cold" takes in most of biryani.

[Figure: The word cold sends out a question. Biryani's key matches best, so biryani's value gets the largest share. Naan and was get smaller shares.]

_Illustrative. The shares come from a softmax over the query–key scores._

### Play

**Try to break it.** Click each word and see who it attends to. Compare "cold" with "great", and then look at "was".

#### Who does each word attend to?

4-dimensional hand-set keys (noun-ness, adjective-ness, verb-ness, which clause) and queries chosen to mimic a trained head: illustrative, not trained. Bars and percentages: softmax(q·k/√4) over all 9 tokens; small numbers under each word: its scaled score q·k/√4.

The query for **cold** looks for a noun in its own clause: the biggest weight goes to **biryani**, and the "naan" key, a noun in the other clause, gets much less. **Great** does the reverse and picks **naan**. The token's new vector is mostly the value of the food it describes, which is exactly the context a later layer needs. Nothing about word order was hard-coded: the clause feature stands in for what positional encodings provide in a real model.

**Now say why:** how does the same formula send "cold" to biryani and "great" to naan, with no rule about food?

## Maths

### Maths

#### In one breath

In **self-attention**, each token asks a question (its **query**), every token advertises what it contains (its **key**), and the match between a query and each key, a dot product, decides how much of each token's **value** to blend in. Scores are divided by **√d** (the key size) so they don't grow with dimension and push the softmax into near one-hot outputs with tiny gradients. The result: every token's new vector is a weighted mix of all tokens, so "cold" can pull in information from "biryani" no matter how far apart they are. All tokens are computed at once as matrix products, which is fast on GPUs, but the score matrix is **n × n**, so cost grows with the square of the sequence length. What you'll be able to do after this: compute attention by hand, explain Q, K and V, justify the √d scaling, and state attention's cost.

#### Scaled dot-product attention

$$ \mathrm{Attention}(Q,K,V) = {\mathrm{softmax}}\!\Big({\frac{{Q}\,{K}^{\top}}{\sqrt{d_k}}}\Big)\,{V}, \qquad Q = XW_Q,\; K = XW_K,\; V = XW_V $$

Vaswani et al., "Attention Is All You Need", NeurIPS 2017, Eq. 1 [arXiv:1706.03762](https://arxiv.org/abs/1706.03762). Jay Alammar's "The Illustrated Transformer" is the classic visual guide.

- **queries**: Each token’s embedding times a learned matrix W_Q: what this token is looking for. Stacked into an n × d matrix.

- **keys**: Embeddings times W_K: what each token offers to be matched on.

- **scaled scores**: Every query dotted with every key: an n × n table of relevance, divided by √d_k to keep the scale steady.

- **softmax per row**: Each row becomes weights that are positive and sum to 1: how much token i attends to each token j.

- **values**: Embeddings times W_V: the content actually passed along. The output for token i is its weighted average of values.

## In practice

### In practice

#### Parallel, direct, and quadratic

- **Direct paths:** any two tokens interact in one step, whatever their distance (an RNN needs n steps).

- **Parallel:** all n tokens are computed together with matrix multiplies, so training uses GPUs efficiently.

- **Quadratic cost:** the score matrix is n × n: 4,096 tokens → about 16.8 million scores per head per layer. Long-context models use tricks like FlashAttention (exact, memory-efficient), sparse or sliding-window attention.

- **Order-blind:** attention treats its inputs as a set; position must be added separately (positional encodings).

### The answer that sounds right

#### Without scaling, the softmax saturates

If query and key entries are roughly independent with variance 1, their dot product over d dimensions has variance d. With d = 64, raw scores have a standard deviation of 8, and the softmax turns into a near one-hot: the gradient of everything except the top score almost vanishes. Dividing by √d brings the standard deviation back to 1 (Vaswani et al., §3.2.1).

2,000 random rows: a query and 9 keys with independent standard-normal entries, fixed seed. With uniform attention the top weight would be 1/9 ≈ 11%.

With scaling, the score spread stays near **1** at every d and the top weight stays moderate (around 35%). Without it at d = 64, the spread is **8**, the average top weight is about **87%** and about a third of rows (36%) are essentially one-hot; at d = 1,024, 79% are.

## Say it

### What do Q, K and V do, and why divide by √d?

#### The interviewer pushes further

Follow-up 1 of 3

Why separate Q, K and V projections?

What a token looks for, what it is matched on and what it passes on are different roles; separate matrices let the model learn asymmetric relations (A attends to B without B attending to A).

Follow-up 2 of 3

What's the complexity?

O(n² · d) time and O(n²) memory for the score matrix per head, versus O(n · d²) for the projections.

Follow-up 3 of 3

Self-attention vs cross-attention?

Self: Q, K, V from the same sequence. Cross: queries from one sequence (decoder), keys and values from another (encoder output).

#### The 30-second answer

Self-attention lets every token build its representation from all tokens. Each token's embedding is projected into a query, a key and a value. The attention weights for token i are a softmax over the dot products of its query with every key, divided by root d_k, and its output is the weighted sum of the values. Scaling keeps the score variance near one, otherwise the softmax saturates and gradients vanish. It's computed for all tokens at once as softmax(QKᵀ/√d)V, so it's parallel and connects distant tokens directly, but it costs O(n²) in sequence length and is order-agnostic, so positional information has to be added.

**Go further**

#### What not to say

- "Divide by d." It's √d, from the variance argument.

- "Attention weights explain the model." They're one signal; they don't fully explain predictions.

**Key terms and sources**

How every token builds a new representation by looking at every other token: queries, keys and values, scaled dot-product attention, why the scores are divided by √d, and the n² cost · built from Vaswani et al. (NeurIPS 2017), Bahdanau et al. (2015), Alammar, "The Illustrated Transformer" (2018) and Goodfellow et al. · checked 29 Oct 2026

#### Sources

1. A. Vaswani et al., "Attention Is All You Need", NeurIPS 2017, [arXiv:1706.03762](https://arxiv.org/abs/1706.03762).

2. D. Bahdanau, K. Cho & Y. Bengio, "Neural Machine Translation by Jointly Learning to Align and Translate", ICLR 2015, [arXiv:1409.0473](https://arxiv.org/abs/1409.0473).

3. J. Alammar, ["The Illustrated Transformer"](https://jalammar.github.io/illustrated-transformer/), 2018.

4. T. Dao et al., "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness", NeurIPS 2022, [arXiv:2205.14135](https://arxiv.org/abs/2205.14135).
