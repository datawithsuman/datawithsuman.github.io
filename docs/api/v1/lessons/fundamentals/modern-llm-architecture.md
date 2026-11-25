# Anatomy of a Modern LLM

> What changed since 2017, and where do an 8B model's parameters live?

- Track: Fundamentals › LLMs › Modern architecture
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/modern-llm-architecture/
- Before this: The Transformer, End to End (`fundamentals/transformer-end-to-end`)
- Quiz topic: `arch`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: e4c3d4c9ee

## Intuition

### The situation

The delivery app wants its own support assistant, an open 8B model like Llama 3 8B. A colleague says it's the 2017 Transformer made bigger, with most of the parameters in attention. The interviewer asks:

> What changed since 2017, and where do an 8B model's parameters live?

Where this lesson sits: the whole block. Each part has its own Deep Learning lesson; this one covers what modern LLMs changed.

Background: The Transformer, End to End · Encoder vs Decoder.

**Running example (whole track):** the food-delivery app wants its own support assistant, an open 8B model like Llama 3 8B, fine-tuned on customer chats. To choose, serve and train it, the team needs to know what's inside.

#### The 2017 recipe didn't scale cleanly

The original Transformer was an encoder-decoder for translation, with post-norm residual blocks, ReLU feed-forward layers and fixed sinusoidal positions. Scaling that recipe to tens of billions of parameters exposed problems: deep post-norm stacks needed careful warm-up to train, long-context generation made the **KV cache** huge, and fixed positions didn't extend past the training length. Each modern change fixes one of these.

### The idea

Think of a restaurant famous for its front counter, where orders get passed along. Everyone talks about the counter, but most of the staff are in the back kitchen. Attention is the counter, and the feed-forward layers are the kitchen.

[Figure: Where parameters live. In an 8B model: 70 percent feed-forward, 17 percent attention, 13 percent embeddings. In a 70B model: 80 percent feed-forward, 17 percent attention, 3 percent embeddings.]

_Counted in the lab, from the Llama 3 model cards._

### Play

**Try to break it.** Start at the 8B shape, then switch to 70B. Change SwiGLU to classic FFN, GQA to full MHA and a separate output head to tied embeddings. Watch the totals and shares.

#### Where do 8 billion parameters live?

The naive guess is "mostly attention", since attention is what the Transformer is famous for. Count them.

Configs from the Llama 3 model cards: 8B: d = 4,096, 32 layers, 32 query heads, 8 KV heads, FFN 14,336, vocab 128,256; 70B: d = 8,192, 80 layers, 64 heads, 8 KV heads, FFN 28,672. Attention = WQ, WK, WV, WO; norms = two RMSNorm gains per layer plus a final one.

The Llama 3 8B shape comes out at **8.03 B**: the feed-forward layers hold **70%**, attention only **17%**, and the input and output embedding tables **13%** (1.05 B, because the 128k vocabulary is large). At the 70B shape the feed-forward share rises to **80%** and embeddings fall to 3%. Switching to full MHA adds 0.8 B parameters to the 8B shape (8.84 B) and makes the KV cache 4× bigger; tying the input and output embeddings saves 0.5 B, which is why small models like Llama 3.2 1B/3B tie them. Norms are a rounding error. So when people prune, quantise or route (MoE), they mostly target the FFN.

**Now say why:** why does the embeddings share drop so much at 70B, while the feed-forward share rises?

## How it works

### How it works

#### In one breath

A modern LLM is still a stack of Transformer blocks, but **decoder-only** and with a handful of upgrades that became standard after Llama (2023): **pre-norm** with **RMSNorm** (cheaper, more stable training), a **SwiGLU** feed-forward layer (a gated FFN that trains better), **RoPE** rotary positions inside attention, **grouped-query attention** to shrink the KV cache, no bias terms, and a vocabulary of 100k+ tokens. In an 8B model about **70% of the parameters are in the feed-forward layers**, about 17% in attention and 13% in the embedding tables; at 70B the feed-forward share rises to about 80%. What you'll be able to do after this: list the modern changes and why each was made, and count an LLM's parameters from its config.

#### 2017 Transformer vs a 2024 LLM block

| Part | 2017 (Vaswani et al.) | Modern (Llama 3, Mistral, Qwen) | Why |
|---|---|---|---|
| Shape | encoder-decoder | decoder-only, causal | one stack does every text task as next-token prediction |
| Norm position | post-norm (after residual add) | **pre-norm** (before each sub-layer) | a clean residual path keeps gradients healthy in deep stacks |
| Norm type | LayerNorm | **RMSNorm** | drops mean-centring; cheaper, works as well (norm lesson) |
| Feed-forward | ReLU, d → 4d → d | **SwiGLU**, three matrices | gated FFNs gave lower loss at equal compute (Shazeer 2020) |
| Positions | sinusoidal, added to input | **RoPE**, rotates Q and K | encodes relative position; can be stretched for long context |
| Attention | multi-head (MHA) | **GQA** (e.g. 8 KV heads) | 4–8× smaller KV cache (next lesson) |
| Biases | yes | none in linear layers | no quality loss, slightly more stable |
| Vocabulary | 37k shared BPE | 128k (Llama 3), 150k+ (Qwen) | fewer tokens per text, better multilingual coverage (tokenisation) |

$$ {\mathrm{RMSNorm}(x) = \frac{x}{\sqrt{\tfrac1d\sum_i x_i^2 + \epsilon}}\odot g}, \qquad \mathrm{FFN}_{\mathrm{SwiGLU}}(x) = {\big(}{\mathrm{SiLU}(xW_1)}\odot {xW_3}{\big)W_2} $$

Zhang & Sennrich, "Root Mean Square Layer Normalization", NeurIPS 2019; Shazeer, "GLU Variants Improve Transformer", [arXiv:2002.05202](https://arxiv.org/abs/2002.05202). SiLU(z) = z·σ(z).

- **RMSNorm**: Divide each vector by its root-mean-square and multiply by a learned gain g. No mean subtraction and no bias, unlike LayerNorm.

- **gate branch**: x W₁ passes through Swish (SiLU), which decides how much of each hidden unit to let through.

- **value branch**: x W₃ is a plain linear projection; it is multiplied element by element by the gate.

- **down projection**: W₂ maps the hidden size back to d. Three matrices instead of two, so the hidden size is shrunk to about 8d/3 to keep the parameter count similar. Models adjust this: Llama 3 8B uses 14,336 for d = 4,096, which is 3.5d.

#### Counting parameters from a config file

- **Attention per layer:** 2d² for Q and O, plus 2 · d · (KV heads × head dim) for K and V.

- **SwiGLU FFN per layer:** 3 · d · dff. A classic FFN: 2 · d · 4d = 8d².

- **Embeddings:** V · d, twice if the output head isn't tied.

- Rough rule for dense models: params ≈ 12 · L · d² (attention 4d² + FFN 8d²), plus embeddings. For Llama 3 8B: 12 × 32 × 4,096² ≈ 6.4 B, close to the 6.98 B in its layers.

## In practice

### In practice

#### The open-model family resemblance

- **Llama** (Touvron et al. 2023) combined pre-norm RMSNorm, SwiGLU and RoPE, and most open models since copy that template. Llama 2 70B added GQA; Llama 3 uses GQA at every size, a 128k-token vocabulary and a RoPE base of 500,000 for longer context.

- **Mistral 7B** added sliding-window attention; **Mixtral** and **DeepSeek-V3** replace the dense FFN with a mixture of experts; DeepSeek-V2/V3 replace GQA with multi-head latent attention.

- Newer stability tweaks include QK-norm (normalising queries and keys before the dot product, used in OLMo 2 and Qwen3) and extra norms after sub-layers; see Training Instabilities.

##### What changed in 2025 and 2026

Llama 3 is still a good model to learn from, and it's our running example. Newer models keep most of its design, and change these parts:

- **Norm placement is less settled.** OLMo 2 puts norms after attention and the FFN, inside the residual. Gemma 3 uses RMSNorm both before and after its attention.

- **QK-norm has spread.** OLMo 2, Gemma 3 and Qwen3 all use it for stability.

- **Attention is changing most.** Gemma 4's smallest models reuse keys and values across layers. Kimi Linear and Qwen3-Next mix linear attention with full attention, and DeepSeek-V4 compresses its cache. See Attention Alternatives.

- **MoE keeps getting sparser.** Qwen3-Next has 80B parameters with 3B active, and DeepSeek-V4-Pro has 1.6T with 49B active.

From the models' technical reports and model cards, and Raschka's [Recent Developments in LLM Architectures](https://magazine.sebastianraschka.com/p/recent-developments-in-llm-architectures). Gemma 4's KV sharing is as Raschka describes it.

### The answer that sounds right

#### "Most parameters are in attention"

It sounds right, since attention is what the Transformer is famous for. But count them in Llama 3 8B: the feed-forward layers hold 70%, attention only 17% and the embedding tables 13%. So when people prune, quantise or route, they mostly target the FFN.

## Say it

### What changed since 2017, and where do an 8B model's parameters live?

#### The interviewer pushes further

Follow-up 1 of 3

Why pre-norm instead of post-norm?

With pre-norm the residual stream is an identity path from input to output, so gradients reach early layers undamped and training is stable without long warm-up (Xiong et al. 2020). Post-norm can reach slightly better quality but is harder to train deep.

Follow-up 2 of 3

Why is SwiGLU's hidden size 8d/3 instead of 4d?

It has three weight matrices instead of two; shrinking the hidden size by 2/3 keeps the parameter count and compute about the same as a 4d two-matrix FFN. That's a starting point: Llama 3 8B actually uses 3.5d (14,336 for d = 4,096).

Follow-up 3 of 3

Estimate the parameters of a model with d = 4,096 and 32 layers.

About 12 · L · d² ≈ 6.4 B in the blocks, plus vocabulary × d for each embedding table: around 7–8 B in total.

#### The 30-second answer

Modern LLMs are decoder-only Transformers with a few standard changes from the 2017 design: pre-norm residual blocks with RMSNorm for stable deep training, SwiGLU gated feed-forward layers, rotary position embeddings applied to queries and keys, grouped-query attention to shrink the KV cache, no biases, and large vocabularies around 128k tokens. Most parameters sit in the feed-forward layers, about 70 percent in an 8B model and about 80 percent at 70B, with attention around 17 percent; that's why MoE replaces the FFN and why quantisation and pruning focus there.

**Go further**

#### What not to say

- "Most parameters are in attention." It's the FFN.

- "LLMs use the original Transformer." They use a decoder-only variant with several changes.

**Key terms and sources**

What changed between the 2017 Transformer and today's decoder-only LLMs (Llama, Mistral, Qwen, DeepSeek): pre-norm, RMSNorm, SwiGLU feed-forward layers, RoPE, grouped-query attention, no biases, big vocabularies, and where the parameters of an 8B model actually live · built from Vaswani et al. (2017), Zhang & Sennrich (2019), Shazeer (2020), Su et al. (RoFormer, 2021), Touvron et al. (Llama, 2023), Ainslie et al. (GQA, 2023) and Meta's Llama 3 report (2024) · checked 29 Oct 2026

#### Sources

1. A. Vaswani et al., "Attention Is All You Need", NeurIPS 2017, [arXiv:1706.03762](https://arxiv.org/abs/1706.03762).

2. B. Zhang & R. Sennrich, "Root Mean Square Layer Normalization", NeurIPS 2019, [arXiv:1910.07467](https://arxiv.org/abs/1910.07467); R. Xiong et al., "On Layer Normalization in the Transformer Architecture", ICML 2020, [arXiv:2002.04745](https://arxiv.org/abs/2002.04745).

3. N. Shazeer, "GLU Variants Improve Transformer", 2020, [arXiv:2002.05202](https://arxiv.org/abs/2002.05202); J. Su et al., "RoFormer", 2021, [arXiv:2104.09864](https://arxiv.org/abs/2104.09864).

4. H. Touvron et al., "LLaMA: Open and Efficient Foundation Language Models", 2023, [arXiv:2302.13971](https://arxiv.org/abs/2302.13971).

5. Llama Team, Meta, "The Llama 3 Herd of Models", 2024, [arXiv:2407.21783](https://arxiv.org/abs/2407.21783), and the Llama 3 8B / 70B model configs on Hugging Face.
