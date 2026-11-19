# Positional Encodings (incl. RoPE)

> How does a Transformer know word order, and why RoPE?

- Track: Fundamentals › Deep Learning › Attention and Transformers
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/positional-encodings/
- Before this: Self-Attention (Q, K, V) (`fundamentals/self-attention`)
- Quiz topic: `attn`

## Intuition

### The situation

"The biryani was cold but the naan was great" and "the naan was cold but the biryani was great" use the same words, with opposite meanings for each dish. Plain self-attention can't tell them apart. The interviewer asks:

> How does a Transformer know word order, and why RoPE?

**Running example:** "_the biryani was cold but the naan was great_" vs "_the naan was cold but the biryani was great_": same words, opposite meaning for each dish. Without position, plain self-attention can't tell them apart.

Where this lesson sits: positions enter right after the token embeddings (RoPE applies them inside every attention layer).

Full walkthrough: The Transformer, End to End.

#### Attention is order-blind

Scores q·k depend only on the two tokens' contents. Permute the input and the outputs are permuted the same way: self-attention is permutation-equivariant. For a bag of words that's fine; for language, "dog bites man" ≠ "man bites dog". RNNs got order for free by reading in sequence; Transformers have to be told.

**One exception worth knowing:** a GPT-style decoder uses a causal mask, so each token sees only itself and earlier tokens. That already leaks some order: the token at position 2 sees 3 tokens, the one at position 7 sees 8. Explicit position information is still added because the mask alone doesn't directly say "one word back" vs "ten words back". Section 6 shows models that lean on this anyway.

### The idea

Think of giving each word a clock hand, turned according to its position. Any two words a fixed distance apart have the same angle between their hands, wherever they sit. That's RoPE: attention sees how far apart words are, not just where they are.

[Figure: Two clock faces. On each, two hands sit the same angle apart, even though their absolute positions differ, because the gap between the words is the same.]

_Illustrative. Each pair sits the same angle apart, because each pair's gap is the same._

### Play

**Try to break it.** Move the query and key positions together, keeping the gap between them the same. Then change the gap.

#### RoPE: rotate queries and keys by position

$$ \big(R_{m\theta}\, q\big)^{\!\top}\big(R_{n\theta}\, k\big) = q^{\top} R_{(n-m)\theta}\, k $$

Su et al., "RoFormer: Enhanced Transformer with Rotary Position Embedding", 2021 arXiv:2104.09864: RoPE encodes absolute position with a rotation matrix and makes the attention score depend on relative position. Used in LLaMA (Touvron et al. 2023), PaLM, Mistral, Qwen and most open LLMs.

- **rotation by position**: Split the query (and key) into 2-D pairs; rotate pair i by angle m·θ_i for a token at position m, with θ_i = 10000^(−2i/d) as in the sinusoids.

- **rotated query and key**: Applied inside every attention layer, to Q and K only (not V), instead of adding anything to the embeddings.

- **only the offset matters**: Rotations compose: rotating q by m and k by n gives the same dot product as rotating q by m − n alone. The score depends on the relative position.

A fixed 8-dimensional query and key (4 rotating pairs, θi = 10000−2i/8). The circle shows pair 1 of the rotated query (teal) and key (orange); the score uses all 4 pairs.

Shift both positions by 40 and the score is identical: only m − n matters. Change the gap instead (move n) and the score changes. That's why RoPE models generalise across positions within the trained range: "the adjective two words before the noun" looks the same at the start or the end of a document.

**Now say why:** why does the score depend on the gap, and not on the absolute positions?

## Maths

### Maths

#### In one breath

Attention compares every token with every other but has no idea of **order**: shuffle the words and each token gets the same weights. So position must be injected. The original Transformer **added** fixed **sinusoidal** vectors to the embeddings; BERT and GPT-2 **learned** one vector per position. Most modern LLMs use **RoPE**: rotate each pair of query and key dimensions by an angle proportional to the token's position. Then the attention score depends only on the **relative distance** between two tokens, which is what language mostly cares about. Extending a model to longer contexts usually means adjusting these position schemes. Newer models also rotate only part of each head, skip RoPE in some layers, or add a learned distance bias instead.What you'll be able to do after this: explain why position is needed, compare absolute, learned, relative, RoPE and ALiBi, and show why RoPE gives relative positions, and say what recent models use instead of full RoPE.

#### Sinusoidal positional encoding

$$ PE_{(pos,\,2i)} = \sin\!\Big(\frac{pos}{10000^{2i/d}}\Big),\qquad PE_{(pos,\,2i+1)} = \cos\!\Big(\frac{pos}{10000^{2i/d}}\Big) $$

Vaswani et al. (2017), §3.5: chosen because PE(pos + k) is a linear function (a rotation) of PE(pos), which may let the model attend by relative position; learned embeddings performed nearly identically in their tests. A small detail: the paper also multiplies the token embeddings by √dmodel before adding the encoding, most likely so the two are on a similar scale and position doesn't swamp meaning.

- **position**: The token’s index in the sequence: 0, 1, 2, …

- **frequency per dimension pair**: Each pair of dimensions uses a different wavelength, from 2π up to about 10000·2π: fast waves tell nearby positions apart, slow waves encode coarse position.

- **sine and cosine**: Even dimensions use sine, odd use cosine. The vector is added to the token embedding.

Top: the encoding for positions 0–63 (rows) × 64 dimensions (columns), orange = +1, blue = −1. Bottom: cosine similarity between PE(p) and PE(p + k) for k = 0…100. d = 64.

Neighbouring positions get similar vectors and similarity falls with distance. Move p from 20 to 150: the similarity values for +1, +10 and +50 stay the same (0.97, 0.66 and 0.49 for d = 64), because sinusoidal similarity depends only on the offset, not on where you are in the sentence.

## In practice

### In practice

#### ALiBi and context extension

- **ALiBi** (Press et al., ICLR 2022): no position vectors at all; subtract a penalty proportional to distance from each attention score. Trained on short sequences, it extrapolated to longer ones at test time.

- **Position interpolation** (Chen et al. 2023): to run a RoPE model on 4× longer inputs, squeeze the positions (divide them by 4) so the angles stay in the trained range, then fine-tune briefly; later methods (NTK-aware scaling, YaRN) rescale the frequencies instead.

- Long-context models combine these with attention optimisations; position handling is usually the first thing to change when extending context.

#### Partial RoPE, NoPE layers and learned bias

RoPE in every attention layer is still the most common choice in open-weight LLMs. But recent models increasingly change it in three ways.

- **Partial RoPE: rotate only some dimensions.** MiniMax-M3 rotates 64 of the 128 dimensions in each head and leaves the rest unchanged. That halves the precomputed sine and cosine tables; the KV cache doesn't shrink, because keys are stored in full. Khan et al. (2026) found that rotating about 10% of the dimensions in 1B–8B models gave training loss close to full RoPE, though full RoPE was better on some evaluations.

- **NoPE layers: no explicit position at all.** Because of the causal mask, a token that spreads its attention evenly gives the first token a weight of 1/3 at position 2, 1/4 at position 3, and so on. That fraction is a position signal a later layer can read. Kazemnejad et al. (NeurIPS 2023) found that small decoders without any position encoding handled longer-than-trained inputs better than RoPE on most of their synthetic tasks. In practice models mix the two: SmolLM3 drops RoPE from every 4th layer, which its authors report helped long context without hurting short context.

- **Learned relative bias, again.** Inkling (Thinking Machines Lab, 2026) uses no RoPE. It adds a learned bias to each attention score, chosen by the distance between the two tokens and the query, which is T5's 2019 idea brought back.

In Raschka's count of open-weight architectures (Nov 2026), the share using full RoPE in every layer fell from 2025 to 2026, and among RoPE models partial RoPE went from a minority to a majority. The groups are small, so read this as a direction, not a rule.

Even a layer that skips RoPE isn't position-blind: its inputs come from earlier layers that did use position.

### The answer that sounds right

#### Learned absolute positions don't extrapolate

BERT and GPT-2 learn one vector per position (512 and 1,024 positions). Simple and effective, but a model has never seen position 1,025 and has no vector for it, and absolute position is often less useful than "how far apart are these two words?". Relative schemes (Shaw et al. 2018; T5's relative biases) add a learned term to each attention score that depends on the distance i − j.

The table also gets expensive. In GPT-2 Medium, 1,024 position vectors are about 0.3% of the weights. Stretch the table to about 100,000 positions and it would be more than 22% of the model (Raschka, 2026), and every one of those vectors has to be trained.

## Say it

### How does a Transformer know word order, and why RoPE?

#### The interviewer pushes further

Follow-up 1 of 7

Why is RoPE applied to Q and K but not V?

Position should affect _who attends to whom_ (the scores), not the content that is passed along.

Follow-up 2 of 7

Added vs multiplied position information?

Sinusoidal and learned encodings are added once to the input; RoPE multiplies (rotates) inside every attention layer, so relative position is present at every layer.

Follow-up 3 of 7

Why multiple frequencies?

Fast-rotating pairs distinguish nearby positions; slow ones cover long ranges without repeating, like the hands of a clock.

Follow-up 4 of 7

Can a decoder learn position with no positional encoding?

Partly. The causal mask means each token sees a different number of earlier tokens, and attention can turn that count into a position signal. This is NoPE. It extrapolates well in small studies, and models like SmolLM3 skip RoPE in some layers, but most models still keep RoPE in most layers.

Follow-up 5 of 7

What is partial RoPE, and why use it?

Rotate only some of each head's dimensions (MiniMax-M3 rotates 64 of 128) and leave the rest untouched. It halves the sine and cosine tables and leaves some dimensions for pure content matching. The KV cache stays the same size.

Follow-up 6 of 7

Two RoPE codebases pair dimensions differently. Which is right?

Both. The RoFormer paper and original LLaMA pair neighbouring dimensions (1,2), (3,4); most code now pairs the first half with the second half, (1,5), (2,6), because it's simpler to vectorise. Reorder the features and the scores are identical. But you can't load weights trained with one convention into code using the other.

Follow-up 7 of 7

Are the RoPE sine and cosine tables learned or stored?

Neither: they're computed once from the positions and frequencies and shared by every head, query and key. They're cheap enough that nobody saves them with the weights.

#### The 30-second answer

Self-attention is permutation-equivariant, so without position information a Transformer can't reliably tell word order (a decoder's causal mask leaks only a little). The original paper added fixed sinusoidal encodings at different frequencies to the embeddings; BERT and GPT-2 learned absolute position embeddings, which can't go beyond the trained length. Most modern LLMs use RoPE: rotate each 2-D pair of query and key dimensions by an angle proportional to position, so the dot product depends only on the relative offset. ALiBi instead adds a distance penalty to the scores. To extend context, people interpolate or rescale RoPE frequencies and fine-tune. Recent models also use partial RoPE, skip RoPE in some layers, or use a learned distance bias.

**Go further**

#### What not to say

- "Transformers know order from the input sequence." An encoder like BERT doesn't at all; a decoder gets only a weak signal from its causal mask.

- "Every modern LLM uses RoPE in every layer." Many now use partial RoPE, skip it in some layers, or use a learned distance bias.

- "RoPE lets any model handle unlimited length." It still degrades beyond the trained range unless rescaled.

**Key terms and sources**

Why attention needs position information, sinusoidal encodings, learned absolute positions, relative schemes, rotary position embeddings (RoPE) used in most modern LLMs, ALiBi, and stretching the context window · built from Vaswani et al. (2017), Devlin et al. (2019), Shaw et al. (2018), Su et al. (RoFormer, 2021), Press et al. (ALiBi, ICLR 2022), Chen et al. (2023), Touvron et al. (2023), Kazemnejad et al. (NoPE, NeurIPS 2023), the SmolLM3 report (2025), Khan et al. (partial RoPE, 2026) and Raschka's "Understanding Positional Embeddings in Modern LLMs" (Nov 2026) · checked 16 Nov 2026

#### Sources

1. A. Vaswani et al., "Attention Is All You Need", NeurIPS 2017, arXiv:1706.03762.

2. P. Shaw, J. Uszkoreit & A. Vaswani, "Self-Attention with Relative Position Representations", NAACL 2018, arXiv:1803.02155.

3. J. Su et al., "RoFormer: Enhanced Transformer with Rotary Position Embedding", arXiv:2104.09864, 2021.

4. O. Press, N. Smith & M. Lewis, "Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation" (ALiBi), ICLR 2022, arXiv:2108.12409.

5. S. Chen, S. Wong, L. Chen & Y. Tian, "Extending Context Window of Large Language Models via Positional Interpolation", arXiv:2306.15595, 2023.

6. H. Touvron et al., "LLaMA: Open and Efficient Foundation Language Models", arXiv:2302.13971, 2023.

7. C. Raffel et al., "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer" (T5), JMLR 2020, arXiv:1910.10683.

8. A. Kazemnejad et al., "The Impact of Positional Encoding on Length Generalization in Transformers" (NoPE), NeurIPS 2023, arXiv:2305.19466.

9. Hugging Face, "SmolLM3: smol, multilingual, long-context reasoner", 2025, huggingface.co/blog/smollm3.

10. M. A. Khan, K. P. Gummadi, M. Gupta & A. Ravichander, "Fractional Rotation, Full Potential? Investigating Performance and Convergence of Partial RoPE", EMNLP 2026, arXiv:2603.11611.

11. Hugging Face Transformers, "MiniMax-M3-VL" model docs (rotary_dim = 64 of head_dim 128), huggingface.co.

12. S. Raschka, "Inkling Architecture and Benchmark Notes", 2026, sebastianraschka.com.

13. S. Raschka, "Understanding Positional Embeddings in Modern LLMs", Ahead of AI, Nov 2026, magazine.sebastianraschka.com.
