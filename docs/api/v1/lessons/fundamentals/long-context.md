# Long Context: RoPE Scaling, Sliding Windows and Attention Sinks

> Why does a 4k model break at 16k, and how does YaRN fix it?

- Track: Fundamentals › LLMs › Modern architecture
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/long-context/
- Before this: Positional Encodings (incl. RoPE) (`fundamentals/positional-encodings`), Attention Variants: MQA, GQA and MLA (`fundamentals/attention-variants-mqa-gqa-mla`)
- Quiz topic: `arch`

## Intuition

### The situation

The assistant was pre-trained on 4k-token contexts, and the team wants it to read a customer's full history of about 16k tokens. They feed it in, and perplexity explodes after position 4,096. The interviewer asks:

> Why does a 4k model break at 16k, and how does YaRN fix it?

Where this lesson sits: the positional encoding applied inside attention, and which tokens attention can see.

Background: Positional Encodings (incl. RoPE).

**Running example:** the support assistant was pre-trained with 4k-token contexts. The team wants it to read a customer's full order history and past chats, about 16k tokens.

#### Positions the model has never seen

Feed a 4k-trained model 16k tokens and perplexity explodes after position 4,096: the attention scores depend on rotation angles that never occurred in training. Training at 16k from scratch is expensive (attention cost grows with the square of length), so we want to extend a trained model cheaply.

### The idea

Think of a clock's hands in training. The second hand has gone round many times, so every angle is familiar. The hour hand has never finished a lap, so going further shows it angles it has never seen. YaRN slows only the slow hands, and leaves the fast ones alone so nearby tokens stay distinct.

[Figure: Stretching a 4k model to 16k. No change leaves 18 pairs at unseen angles and keeps 1 radian between neighbours. Position interpolation has none unseen but only 0.25 radians. NTK-aware has 17 unseen and 1 radian. YaRN has none unseen and 1 radian.]

_From the lab: stretching a 4k model to 16k, with 64 rotary pairs._

### Play

**Try to break it.** At 16k, switch between no change, position interpolation, NTK-aware and YaRN. Then push the target to 64k.

#### Extend a 4k model to longer contexts

Head size 128 (64 rotary pairs), base 10,000, training length 4,096. A pair counts as "unseen" if it never completed a full turn in training and the new length pushes it past its largest trained angle. Dots: each pair's rotation speed relative to training (1 = unchanged); red = unseen angles. YaRN ramp α = 1, β = 32 as in the paper.

**No change**: the 18 slow pairs go past their trained angles, the failure we started with. **Position interpolation** divides every position by 4, so nothing is unseen, but the fastest pair's angle between neighbouring tokens drops from 1 rad to **0.25 rad**: nearby tokens become harder to tell apart, which is why PI needs fine-tuning. **NTK-aware** scaling raises the base: fast pairs stay sharp (1 rad), but **17** slow pairs are still only partly slowed and reach unseen angles. **YaRN** interpolates the slow pairs fully, leaves the fast ones alone, and blends in between: **0** unseen pairs and neighbour detail kept at 1 rad. It also scales attention logits by a temperature (√(1/t) = 0.1 ln s + 1) to keep attention from becoming too spread out.

**Now say why:** position interpolation leaves nothing unseen, so why does it still need fine-tuning?

## Maths

### Maths

#### In one breath

RoPE encodes position by rotating pairs of query/key dimensions, fast for some pairs and very slowly for others. Past the training length, the slow pairs reach angles the model has **never seen**, and quality collapses. **Position interpolation (PI)** squeezes positions back into the trained range, but blurs nearby tokens; **NTK-aware** scaling raises the RoPE base instead; **YaRN** interpolates only the slow pairs, keeps the fast ones untouched and adds an attention temperature, extending Llama 2 to 128k with a short fine-tune. Separately, **sliding-window attention** caps memory by attending only to recent tokens, and **attention sinks** (keeping the first few tokens) stop it from breaking. Long context is only useful if the model uses it: test with tasks harder than needle-in-a-haystack. What you'll be able to do after this: explain why models fail beyond their training length and compare PI, NTK-aware scaling, YaRN, sliding windows and attention sinks.

#### Fast pairs and slow pairs

$$ \text{angle}_i(m) = {m}\cdot{\theta_i}, \qquad {\theta_i = }{b}^{{-2i/d}} $$

Su et al., RoFormer, [arXiv:2104.09864](https://arxiv.org/abs/2104.09864). The query–key score then depends only on the difference of positions.

- **position**: Token position m multiplies the rotation speed: the angle grows linearly with position.

- **speed of pair i**: Each pair of dimensions i = 0…d/2−1 rotates at its own speed. Pair 0 turns 1 radian per token (fine detail about neighbours); the last pairs turn extremely slowly (coarse, long-range position).

- **base**: 10,000 in the original RoPE; Llama 3 uses 500,000 so even the slowest pairs vary meaningfully over long contexts.

With base 10,000, head size 128 and a 4k training length, the fast pairs complete many full turns during training, so any angle is familiar. But **18 of the 64** pairs turn so slowly that they never complete one turn within 4,096 tokens: beyond that length they produce angles the model has never seen.

## In practice

### In practice

#### Windows, sinks, and long-context training

- **Sliding-window attention:** each token attends only to the last W tokens (Mistral 7B: W = 4,096), so the KV cache stops growing; stacking layers still lets information travel further. Gemma 3 interleaves local sliding-window layers with occasional global layers.

- **Attention sinks** (StreamingLLM, Xiao et al. 2024): models put large attention on the first tokens regardless of content; evicting them breaks a sliding window. Keeping just **4** initial tokens plus the window let Llama 2, MPT, Falcon and Pythia stream over **4 million** tokens, up to 22.2× faster than re-computing a sliding window. This bounds memory; it doesn't let the model recall evicted text.

- **Practice:** frontier models pre-train at 4k–8k, then continue training on long documents with a scaled RoPE (Llama 3.1 extended to 128k this way); YaRN reported 10× fewer tokens and 2.5× fewer steps than earlier extension methods.

**Claimed vs usable context.** Liu et al. (2024) found models use information at the start and end of a long context much better than information in the middle ("lost in the middle"), and RULER (Hsieh et al. 2024) showed many models that pass simple needle-in-a-haystack tests degrade well before their advertised length on harder retrieval and multi-hop tasks.

#### Keep every angle inside what training covered

Context extension works by mapping long positions onto rotation angles the model already knows, while protecting the fast-rotating dimensions that encode local word order; memory at long context is then handled separately, by GQA/MLA, windows, sinks and cache compression.

For newer ways to cut the cost, read Attention Alternatives.

### The answer that sounds right

#### "A 128k model uses all 128k tokens equally well"

It sounds right, since that's what the spec sheet says. But Liu et al. found that models use information at the start and end of a long context much better than in the middle. RULER showed many models degrading well before their advertised length on harder tasks. StreamingLLM doesn't help here either: it keeps a fixed window, and evicted text is gone. So test it.

## Say it

### Why does a 4k model break at 16k, and how does YaRN fix it?

#### The interviewer pushes further

Follow-up 1 of 3

Why does raising the RoPE base help long context?

It slows every pair down, so angles over a longer range stay within what the model sees during training; Llama 3 uses base 500,000.

Follow-up 2 of 3

What are attention sinks?

The first tokens receive large attention because softmax must put probability somewhere; they act as a dump. Removing them from the cache shifts attention and breaks the model.

Follow-up 3 of 3

Long context or RAG?

Long context is simpler but costs quadratic prefill and linear KV memory per request, and recall in the middle can be weak; RAG is cheaper per query and easier to update. Many systems combine them.

#### The 30-second answer

RoPE rotates pairs of query and key dimensions at different speeds; beyond the training length the slowly rotating pairs hit angles never seen in training, so quality collapses. Position interpolation rescales positions into the trained range but blurs local order; NTK-aware scaling raises the RoPE base instead; YaRN interpolates only the low-frequency pairs, keeps the high-frequency ones, and adds an attention temperature, which extends context with a short fine-tune. To bound memory, sliding-window attention keeps only recent tokens, and StreamingLLM shows you must keep a few initial attention-sink tokens. And I'd verify usable context with RULER-style tests, since models often lose information in the middle.

**Go further**

#### What not to say

- "A 128k model uses all 128k tokens equally well." Test it.

- "StreamingLLM gives infinite memory." It keeps a fixed window; evicted text is gone.

**Key terms and sources**

Why a model trained on 4k or 8k tokens breaks at 32k, how position interpolation, NTK-aware scaling and YaRN stretch RoPE to longer contexts, how sliding-window attention and attention sinks bound memory, and how to tell whether a long context actually works · built from Su et al. (RoFormer, 2021), Chen et al. (Position Interpolation, 2023), Peng et al. (YaRN, ICLR 2024), Jiang et al. (Mistral 7B, 2023), Xiao et al. (StreamingLLM, ICLR 2024), Liu et al. (Lost in the Middle, TACL 2024) and Hsieh et al. (RULER, 2024) · checked 29 Oct 2026

#### Sources

1. S. Chen et al., "Extending Context Window of Large Language Models via Positional Interpolation", 2023, [arXiv:2306.15595](https://arxiv.org/abs/2306.15595).

2. B. Peng, J. Quesnelle, H. Fan & E. Shippole, "YaRN: Efficient Context Window Extension of Large Language Models", ICLR 2024, [arXiv:2309.00071](https://arxiv.org/abs/2309.00071).

3. G. Xiao et al., "Efficient Streaming Language Models with Attention Sinks", ICLR 2024, [arXiv:2309.17453](https://arxiv.org/abs/2309.17453).

4. A. Jiang et al., "Mistral 7B", 2023, [arXiv:2310.06825](https://arxiv.org/abs/2310.06825); Gemma Team, "Gemma 3 Technical Report", 2025, [arXiv:2503.19786](https://arxiv.org/abs/2503.19786).

5. N. Liu et al., "Lost in the Middle: How Language Models Use Long Contexts", TACL 2024, [arXiv:2307.03172](https://arxiv.org/abs/2307.03172); C.-P. Hsieh et al., "RULER: What's the Real Context Size of Your Long-Context Language Models?", 2024, [arXiv:2404.06654](https://arxiv.org/abs/2404.06654).
