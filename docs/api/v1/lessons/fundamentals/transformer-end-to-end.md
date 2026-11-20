# The Transformer, End to End

> Walk a sentence through a whole Transformer, with shapes.

- Track: Fundamentals › Deep Learning › Attention and Transformers
- Type: Concept · 30 min
- Page: https://aimlrounds.com/tracks/fundamentals/transformer-end-to-end/
- Before this: The Transformer Block (`fundamentals/transformer-block`), Positional Encodings (incl. RoPE) (`fundamentals/positional-encodings`)
- Related: Attention Is All You Need (`papers/attention-is-all-you-need`)
- Quiz topic: `attn`

## Intuition

### The situation

An interviewer hands you the marker and asks you to go through a whole Transformer on the board, from raw text to the next word. The interviewer asks:

> Walk a sentence through a whole Transformer, with shapes.

**Running example:** a GPT-2-small-sized model (d = 768, 12 layers, 12 heads, vocabulary 50,257) reads "_the biryani was cold but the naan was_" and predicts the next word. Shapes below are for one sequence of n tokens.

### The idea

Think of an assembly line. Text goes in and becomes ids, then vectors. The vectors pass through identical stations that keep their shape, and a final station turns each one into a score for every word in the vocabulary.

[Figure: A pipeline: text becomes n ids, then an n by 768 matrix, passes through 12 blocks and a norm keeping that shape, then a linear layer gives n by 50,257 logits.]

_Shapes for one sequence of n tokens, in a GPT-2-small-sized model. The last shape is the logits._

### Play

**Try to break it.** Switch between GPT-2 small and LLaMA-7B. Then raise the batch size and sequence length, and watch the logits tensor and KV cache.

#### Tensor shapes through the model

Shapes for one forward pass. KV cache = 2 × layers × B × n × d × 2 bytes (multi-head attention; LLaMA-7B has 32 layers and d = 4,096).

For one 8-token sentence in GPT-2 small, every hidden tensor is 1 × 8 × 768 and the logits are 1 × 8 × 50,257. Push n to 4,096 with a batch of 8 on LLaMA-7B: the KV cache alone is about **17 GB**, which is why serving long contexts is limited by memory (Pope et al. 2022; multi-head attention).

**Now say why:** why does the KV cache grow so fast, and where does its memory go?

## Maths

### Maths

#### In one breath

Text is split into **tokens**, each token id is looked up in an **embedding** table (n × d), **position** information is added (or applied as RoPE), and the vectors pass through **N identical blocks**: each lets tokens exchange information with **causal multi-head attention**, then processes each token with a **feed-forward network**, both as residual updates with normalisation. A final norm and a **linear layer to the vocabulary** turn each position's vector into **logits**; a **softmax** on the last position gives the next-token probabilities. Pick a token, append it, repeat, reusing cached keys and values. Every arrow in that pipeline is one of the lessons in this track. What you'll be able to do after this: walk through a Transformer forward pass with shapes, explain generation with a KV cache, and compare the decoder-only design with the 2017 encoder–decoder.

#### A decoder-only Transformer, bottom to top

1. The text is split into tokens (sub-word pieces) and mapped to integer ids: here 8 tokens. Tokenisation is covered in the LLMs track.

2. Each id selects one row of the embedding table (V × d): the sequence becomes an 8 × 768 matrix, one vector per token.

3. Position information is added (GPT-2: a learned 1,024 × 768 table) or applied inside attention as RoPE (LLaMA). Without it the model can't tell word order.

4. N = 12 identical pre-norm blocks. In each, causal multi-head attention lets every token read the earlier ones (12 heads, each with an 8 × 8 score matrix), then a 4× wider MLP processes each token; both add their output to the residual stream. Shape stays 8 × 768 throughout.

5. A final LayerNorm, then a linear layer (often the embedding matrix reused, "tied") maps each position's vector to 50,257 logits, one per vocabulary token.

6. Softmax on the last position gives the probability of each possible next token; "great" should rank high after "the naan was". In training, the cross-entropy loss is computed at every position at once.

7. Generation: sample or pick a token, append it, and run again. Keys and values of earlier tokens are cached, so each new step only computes the new token's row.

#### "Attention Is All You Need": the encoder–decoder

1. The encoder: 6 blocks of bidirectional self-attention and feed-forward over the English sentence, each followed by "add & norm" (post-norm).

2. The decoder: 6 blocks over the French words generated so far, with a causal mask so it can't peek at future words.

3. Between them, each decoder block has a cross-attention sub-layer: queries from the decoder, keys and values from the encoder's output. This is how the translation reads the source (seq2seq attention without RNNs).

4. The base model: d = 512, 8 heads, dff = 2,048, sinusoidal positions. It reached 28.4 BLEU on WMT 2014 English–German, beating previous results including ensembles, at a fraction of the training cost.

Vaswani et al., NeurIPS 2017 [arXiv:1706.03762](https://arxiv.org/abs/1706.03762). GPT kept only the decoder (dropping cross-attention); BERT kept only the encoder (encoder vs decoder).

## In practice

### In practice

#### 2017 → today

| Part | 2017 Transformer | Typical LLM today (e.g. LLaMA) | Lesson |
|---|---|---|---|
| Architecture | encoder–decoder | decoder-only | encoder vs decoder |
| Positions | sinusoidal, added | RoPE in every attention layer | positional encodings |
| Normalisation | post-norm LayerNorm | pre-norm RMSNorm | normalisation |
| FFN activation | ReLU | SwiGLU | activations |
| Attention | multi-head | grouped-query (GQA), FlashAttention kernels | multi-head attention |
| Optimiser | Adam + warmup + inverse-sqrt decay | AdamW + warmup + cosine decay, clipping | LR schedules |

To see the same design on images, read Vision Transformers.

### The answer that sounds right

#### "A Transformer is basically just attention"

It sounds right, since attention is what made it famous. But about two-thirds of a block's parameters are in the feed-forward network, and the residual connections and normalisation are what let it train at depth. In a good walkthrough, you name those parts as well.

## Say it

### Walk a sentence through a whole Transformer, with shapes.

#### The interviewer pushes further

Follow-up 1 of 3

What is the KV cache and why does it help?

At each generation step, the keys and values of earlier tokens don't change, so they're stored and reused; only the new token's Q, K, V are computed. It turns quadratic recomputation into linear work per step, at the cost of memory.

Follow-up 2 of 3

What are "tied embeddings"?

Using the same matrix for the input embedding and the output projection to logits, saving V × d parameters (GPT-2 does this; LLaMA doesn't).

Follow-up 3 of 3

Where does most compute go?

For short contexts, the matrix multiplies in the projections and FFNs (~2 × parameters FLOPs per token); for long contexts the n² attention term grows to dominate.

#### The 2-minute walkthrough

Text is tokenised into ids, each id is looked up in an embedding matrix to give an n by d matrix, and positional information is added or applied as RoPE. That passes through N identical blocks. Each block normalises, applies causal multi-head self-attention so each token can gather information from earlier tokens, and adds the result to the residual stream; then it normalises again and applies a position-wise MLP, about four times wider, and adds that too. After the last block, a final norm and a linear layer to the vocabulary give logits at every position; during training, cross-entropy against the next token is computed at all positions in parallel thanks to the causal mask. At inference, softmax on the last position gives the next-token distribution; we sample or pick a token, append it and repeat, caching keys and values so each step only processes the new token. The 2017 original was an encoder–decoder with cross-attention for translation; modern LLMs are decoder-only with RoPE, pre-norm RMSNorm, SwiGLU and grouped-query attention.

**Go further**

#### What not to say

- "The model outputs the whole answer at once." It generates one token per step.

- "Softmax is applied to every position at inference." Only the last position is needed to pick the next token.

**Key terms and sources**

One sentence followed through a whole GPT-style decoder: tokens, embeddings, positions, N blocks of attention and feed-forward with residuals and norms, the output projection, softmax and the generation loop, with tensor shapes at every step; then the original 2017 encoder–decoder · built from Vaswani et al. (2017), Radford et al. (2019), Touvron et al. (2023), Xiong et al. (2020), Pope et al. (2022) and Alammar (2018) · checked 29 Oct 2026

#### Sources

1. A. Vaswani et al., "Attention Is All You Need", NeurIPS 2017, [arXiv:1706.03762](https://arxiv.org/abs/1706.03762).

2. A. Radford et al., "Language Models are Unsupervised Multitask Learners" (GPT-2), OpenAI 2019.

3. H. Touvron et al., "LLaMA: Open and Efficient Foundation Language Models", [arXiv:2302.13971](https://arxiv.org/abs/2302.13971), 2023.

4. R. Xiong et al., "On Layer Normalization in the Transformer Architecture", ICML 2020, [arXiv:2002.04745](https://arxiv.org/abs/2002.04745).

5. R. Pope et al., "Efficiently Scaling Transformer Inference", MLSys 2023, [arXiv:2211.05102](https://arxiv.org/abs/2211.05102).

6. J. Alammar, ["The Illustrated Transformer"](https://jalammar.github.io/illustrated-transformer/), 2018.
