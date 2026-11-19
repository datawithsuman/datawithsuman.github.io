# The Transformer Block

> What's inside one block, and where do the parameters go?

- Track: Fundamentals › Deep Learning › Attention and Transformers
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/transformer-block/
- Before this: Multi-Head Attention (`fundamentals/multi-head-attention`), BatchNorm vs LayerNorm vs RMSNorm (`fundamentals/normalisation-layers`)
- Quiz topic: `attn`

## Intuition

### The situation

A teammate stacks attention layers and nothing else, and the model is weak. Attention only produces weighted averages. The interviewer asks:

> What's inside one block, and where do the parameters go?

**Running example:** each token of "_the biryani was cold but the naan was great_" enters as a vector. One block lets "cold" pull in "biryani" (attention), then processes the combined vector (feed-forward), and adds the result back to what it already had.

Where this lesson sits: the dashed box that repeats N times.

Full walkthrough: The Transformer, End to End.

#### Mixing across tokens isn't enough

Attention only produces weighted averages of value vectors: on its own it's nearly linear in the values, and it never transforms a token's features with a non-linearity. Stacking attention alone would be weak. We need a unit that alternates communication between tokens with computation on each token, and that can be stacked dozens of times without training falling apart.

### The idea

Think of a meeting followed by desk work. In attention, tokens share what they know. In the feed-forward layer, each works alone on what it heard. Everything gets added to one running document, so nothing is lost along the way.

[Figure: A vertical residual stream on the left. Attention and feed-forward sub-layers each add to it, and the block repeats.]

_Illustrative. The block keeps its shape, so you can stack N of them._

### Play

**Try to break it.** Compare GPT-2 small, BERT-base and LLaMA-7B, then change the number of layers. Look at attention against FFN parameters.

#### Where do the parameters go?

Attention 4d² per block (Q, K, V, O); FFN 2·d·dff (GELU) or 3·d·dff (SwiGLU); embeddings V·d (plus learned positions for GPT-2/BERT; LLaMA has untied input and output embeddings). Biases and norms are ignored (under 0.1%). Changing N shows what a deeper version of the same width would cost.

The formula reproduces the published sizes: **GPT-2 small ≈ 124M**, **BERT-base ≈ 109M** (110M with biases, token-type and pooler weights), **LLaMA-7B ≈ 6.74B**. In every block the FFN holds **twice as many** parameters as attention, so across the stack about two-thirds of the non-embedding parameters are FFN. In small models the embedding table is a big share (32% for GPT-2 small); in LLaMA-7B it's under 4%.

**Now say why:** why do most of the parameters sit in the feed-forward layers, when attention gets all the attention?

## Maths

### Maths

#### In one breath

A Transformer is the same **block** stacked N times. Each block has two sub-layers: **multi-head self-attention**, which mixes information _across tokens_, and a position-wise **feed-forward network** (an MLP applied to each token separately, usually 4× wider), which transforms information _within_ each token. Each sub-layer is wrapped as x + Sublayer(Norm(x)): a **residual connection** plus **layer normalisation**. Modern LLMs use **pre-norm** with RMSNorm and a SwiGLU FFN. Surprisingly, about **two-thirds of the parameters** sit in the FFNs, not in attention.What you'll be able to do after this: draw a Transformer block, explain each part's role, compare pre- and post-norm, and count a model's parameters.

#### Inside one block (pre-norm)

1. The residual stream: each token's vector flows straight up through the block. Everything else only adds to it.

2. Sub-layer 1: normalise a copy, run multi-head attention across all tokens, and add the result back to the stream. Here "cold" picks up "biryani".

3. Sub-layer 2: normalise again, run the feed-forward network on each token separately (expand to 4d, non-linearity, project back), and add that back too.

4. The block outputs vectors of the same shape it received, so blocks stack: attention lets tokens exchange information, the FFN processes what each token now holds.

## In practice

### In practice

#### The feed-forward network

- Original: FFN(x) = max(0, xW1 + b1)W2 + b2 with inner width 4d (2,048 for d = 512). GPT and BERT use GELU.

- Modern LLMs use **SwiGLU** (Shazeer 2020): three matrices, inner width about (8/3)d so the parameter count matches (activation functions).

- What it does: Geva et al. (EMNLP 2021) showed FFN layers act like **key–value memories**: the first matrix detects input patterns, the second writes associated outputs, often promoting likely next tokens.

- Mixture-of-Experts models replace one FFN with many expert FFNs and route each token to a few of them.

### The answer that sounds right

#### Where the norm goes matters

$$ x_{l+1} = \mathrm{Norm}\big(x_l + F(x_l)\big) \qquad\text{vs}\qquad x_{l+1} = x_l + F\big(\mathrm{Norm}(x_l)\big) $$

Details: BatchNorm vs LayerNorm vs RMSNorm and learning-rate warmup.

- **post-norm (2017)**: The original Transformer normalises after adding the residual. The norm sits on the residual path, so gradients near the input are badly scaled at initialisation; training needs a careful warmup.

- **pre-norm (GPT-2 onwards)**: Normalise only the branch input; the residual path stays a clean identity from bottom to top. Stable at depth and less dependent on warmup (Xiong et al. 2020). Standard in LLMs, usually with RMSNorm.

## Say it

### What's inside one block, and where do the parameters go?

#### The interviewer pushes further

Follow-up 1 of 3

Why does the FFN act per token?

Mixing across positions is attention's job; the FFN applies the same MLP to each position independently, so it's cheap to parallelise and its cost is linear in sequence length.

Follow-up 2 of 3

Rough FLOPs per token?

About 2 × parameters for a forward pass (one multiply-add per weight), ~6 × parameters for training (Kaplan et al. 2020), plus the attention term that grows with context length.

Follow-up 3 of 3

What is the "residual stream" view?

Treat the residual as a shared channel: every sub-layer reads from it and writes an update into it; interpretability work analyses what each layer adds.

#### The 30-second answer

A Transformer block has two sub-layers: multi-head self-attention, which moves information between tokens, and a position-wise feed-forward network, usually four times wider, which transforms each token independently. Each is wrapped in a residual connection with layer normalisation; modern models use pre-norm, x plus F of Norm x, which keeps the residual path an identity and trains stably at depth, typically with RMSNorm and a SwiGLU FFN. The block preserves shape, so you stack N of them. Per block, attention has 4 d squared parameters and the FFN 8 d squared, so about two-thirds of the parameters are in the FFNs.

**Go further**

#### What not to say

- "Most parameters are in attention." Most are in the FFNs.

- "LayerNorm normalises across the batch." Across features of each token.

**Key terms and sources**

The repeating unit of every Transformer: multi-head attention and a feed-forward network, each wrapped in a residual connection and layer normalisation; pre-norm vs post-norm; what the FFN does; and where the parameters go · built from Vaswani et al. (2017), Xiong et al. (2020), Geva et al. (EMNLP 2021), Shazeer (2020), Radford et al. (2019), Devlin et al. (2019) and Touvron et al. (2023) · checked 29 Oct 2026

#### Sources

1. A. Vaswani et al., "Attention Is All You Need", NeurIPS 2017, arXiv:1706.03762.

2. R. Xiong et al., "On Layer Normalization in the Transformer Architecture", ICML 2020, arXiv:2002.04745.

3. M. Geva, R. Schuster, J. Berant & O. Levy, "Transformer Feed-Forward Layers Are Key-Value Memories", EMNLP 2021, arXiv:2012.14913.

4. N. Shazeer, "GLU Variants Improve Transformer", arXiv:2002.05202, 2020.

5. A. Radford et al., "Language Models are Unsupervised Multitask Learners" (GPT-2), OpenAI 2019; J. Devlin et al., "BERT", NAACL 2019, arXiv:1810.04805.

6. H. Touvron et al., "LLaMA", arXiv:2302.13971, 2023; J. Kaplan et al., "Scaling Laws for Neural Language Models", arXiv:2001.08361, 2020.
