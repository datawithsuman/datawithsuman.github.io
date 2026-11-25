# Speculative Decoding

> How does a small draft make a big model faster with identical outputs?

- Track: AI Engineering › LLM inference and serving › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/speculative-decoding/
- Before this: Prefill vs Decode (`ai-engineering/prefill-vs-decode`)
- Quiz topic: `infer`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: f46efc7401

## Intuition

### The situation

The 70B model behind the premium tier streams too slowly for chat, while its GPU compute sits mostly idle during decode. A colleague says that a smaller draft model will make it faster, but only by lowering quality. The interviewer asks:

> How does a small draft make a big model faster with identical outputs?

**Running example:** the 70B model behind the premium support tier streams too slowly for chat. GPU compute is mostly idle during decode; can it be used to produce several tokens per step without changing the answers?

#### One token per pass, compute sitting idle

At small batch sizes, a decode step's time is set by reading tens of gigabytes of weights; the arithmetic for one token is tiny. Verifying 5 tokens in one pass costs almost the same as generating 1. If we could guess future tokens well, we could confirm several per pass.

### The idea

Think of a junior who drafts the next few words, while a senior checks them at a glance. Reading five words costs the senior barely more than writing one. At the first wrong word, the senior corrects it and throws the rest away. The final text reads as if the senior wrote it alone.

[Figure: The draft proposes five tokens. The target accepts the first three in one pass, rejects the fourth and replaces it with its own token, and the last draft token is discarded.]

_Illustrative. Several tokens can be confirmed in one target pass._

### Play

**Try to break it.** At a small batch, start at α = 0.8 and γ = 4, then change each. Then switch to a large batch, and drop α to 0.6.

#### More draft tokens is always better?

Draft step cost c = 0.05 of a target step. Large batch: verifying each extra draft token adds 30% of a step's cost, because the GPU is no longer idle. Dashed line: no speedup.

At small batch, α = 0.8 and γ = 4 give **3.36** tokens per target pass and a **2.80×** speedup; drafting further helps a little (best γ = 8, 3.09×) because rejections waste only cheap draft work. A weaker draft (α = 0.6) gives 1.92×; an excellent one (α = 0.9) gives 3.41× at γ = 4 and over 4× with longer drafts. Switch to a **large batch**: verifying extra tokens now competes for compute, so the same α = 0.8, γ = 4 gives only **1.40×**, and with α = 0.6 it's **slower than not speculating (0.96×)**. That's why engines tune or disable speculation as load rises.

**Now say why:** why can speculation be slower than plain decoding at a large batch?

## Maths

### Maths

#### In one breath

Decode is memory-bound: each step reads all the weights to produce one token per sequence, leaving the GPU's compute mostly idle. **Speculative decoding** uses that idle compute: a small, fast **draft** guesses the next γ tokens, and the big **target** model checks all of them in a single forward pass (as cheap as producing one token when memory-bound). Tokens are accepted left to right with a rejection-sampling rule that guarantees the output follows **exactly** the target model's distribution; at the first rejection the target supplies a corrected token, so every step yields at least one token. With acceptance rate α, the expected tokens per step is (1 − αγ+1) / (1 − α): at α = 0.8 and γ = 4, about 3.4. Typical speedups are 2–3× at small batch; EAGLE-3 reports up to 6.5×, but at large batches the GPU is no longer idle and gains shrink. What you'll be able to do after this: explain why speculative decoding is lossless, compute expected speedup, and say when it helps.

#### Draft, verify, accept

1. The draft proposes γ tokens autoregressively (cheap).

2. The target runs once over the context plus all γ draft tokens, giving its own probabilities at every position.

3. Each draft token x is accepted with probability min(1, ptarget(x) / pdraft(x)), left to right. At the first rejection, a token is sampled from the normalised difference max(0, ptarget − pdraft), and the rest are discarded. If all are accepted, the target's next-position prediction gives a bonus token.

$$ {\text{speedup}} = \frac{{(1-\alpha^{\gamma+1})/(1-\alpha)}}{{\gamma c + 1}} $$

Leviathan, Kalman & Matias, "Fast Inference from Transformers via Speculative Decoding", ICML 2023, [arXiv:2211.17192](https://arxiv.org/abs/2211.17192); Chen et al. (DeepMind), "Accelerating Large Language Model Decoding with Speculative Sampling", 2023, [arXiv:2302.01318](https://arxiv.org/abs/2302.01318).

- **expected tokens per target pass**: With per-token acceptance rate α and γ draft tokens, the accepted run length is geometric; this sum includes the corrected or bonus token, so it is always at least 1.

- **cost of one step**: γ draft steps, each costing c relative to a target step, plus one target pass.

- **speedup**: Tokens per step divided by cost per step (Leviathan et al., Theorem 3.8). High α and cheap drafts make it large.

## In practice

### In practice

#### Where drafts come from

| Draft | How | Trade-off |
|---|---|---|
| **Separate small model** | e.g. a 1B model from the same family as the 70B target | easy, needs the same tokeniser; extra memory; α depends on how similar they are |
| **Medusa** (Cai et al. 2024) | extra decoding heads on the target predict tokens t+2, t+3, …; tree of candidates verified at once | no second model; Medusa-1 about 2.2× without quality change |
| **EAGLE-3** (Li et al. 2025) | a light head drafts from the target's own hidden features (several layers), trained with "training-time test" | up to 6.5× reported; 1.38× throughput at batch 64 in SGLang; supported in vLLM and SGLang |
| **N-gram / prompt lookup** | copy candidate continuations from the prompt itself | free; great for editing, code refactors and RAG answers that quote the context |

Measure on your own traffic: acceptance depends on the task (code and quoting accept more than creative writing) and on temperature.

**Drafts built into the model.** Some models are trained to predict more than one token ahead. DeepSeek-V3 reported that its multi-token prediction head's second token was accepted 85 to 90% of the time, giving about 1.8× more tokens per second. Engines now use such heads as the draft, with no separate model to load.

#### Guess cheaply, verify in parallel, never change the answer

Speculative decoding turns idle compute during memory-bound decoding into extra tokens per step, and its rejection-sampling rule keeps the output distribution identical to the big model's.

### The answer that sounds right

#### "It's an approximation that slightly lowers quality"

It sounds right, since a weaker model is writing part of the answer. But it's lossless: the rejection rule keeps the output distribution identical, and with greedy decoding the tokens are identical, up to floating-point differences. It doesn't always give 2–3× either: it depends on acceptance and batch size, and at α = 0.6 on a large batch the lab is slower than not speculating.

## Say it

### How does a small draft make a big model faster with identical outputs?

#### The interviewer pushes further

Follow-up 1 of 3

Is the output exactly the same as without speculation?

The distribution is identical with the rejection-sampling rule; with greedy decoding the tokens are identical (up to floating-point differences).

Follow-up 2 of 3

When would you turn it off?

At high batch sizes where decode becomes compute-bound, or when acceptance is low (creative, high-temperature output); measure accepted tokens per step.

Follow-up 3 of 3

What limits the draft model's size?

Its cost per step (c): a draft too big eats the gain; it must also share the target's tokeniser.

#### The 30-second answer

Decoding is memory-bound, so verifying several tokens in one forward pass costs about the same as generating one. Speculative decoding has a cheap draft, a small model, Medusa heads or an EAGLE head, propose gamma tokens; the target model scores them all in one pass and accepts each with probability min of one and target over draft probability, resampling from the residual at the first rejection, which provably preserves the target's distribution. Expected tokens per pass are one minus alpha to the gamma plus one, over one minus alpha, so with 80 percent acceptance and four draft tokens about 3.4. Speedups are typically 2 to 3 times at low batch, but shrink at high batch where compute is no longer idle.

**Go further**

#### What not to say

- "It's an approximation that slightly lowers quality." It's lossless.

- "It always gives 2–3×." It depends on acceptance and batch size.

**Key terms and sources**

How a cheap draft proposes several tokens that the big model verifies in one forward pass, why the output distribution is exactly unchanged, how acceptance rate and draft length set the speedup, the main draft designs (separate draft model, Medusa heads, EAGLE-3, n-gram / prompt lookup), and why gains shrink at large batch sizes · built from Leviathan et al. (ICML 2023), Chen et al. (DeepMind, 2023), Cai et al. (Medusa, ICML 2024), Li et al. (EAGLE-3, NeurIPS 2025) and the vLLM and SGLang speculative decoding docs · checked 29 Oct 2026

#### Sources

1. Y. Leviathan, M. Kalman & Y. Matias, "Fast Inference from Transformers via Speculative Decoding", ICML 2023, [arXiv:2211.17192](https://arxiv.org/abs/2211.17192).

2. C. Chen et al., "Accelerating Large Language Model Decoding with Speculative Sampling", 2023, [arXiv:2302.01318](https://arxiv.org/abs/2302.01318).

3. T. Cai et al., "Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads", ICML 2024, [arXiv:2401.10774](https://arxiv.org/abs/2401.10774).

4. Y. Li et al., "EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test", NeurIPS 2025, [arXiv:2503.01840](https://arxiv.org/abs/2503.01840).

5. DeepSeek-AI, "DeepSeek-V3 Technical Report", 2024, [arXiv:2412.19437](https://arxiv.org/abs/2412.19437) (§5.4.3, multi-token prediction for speculative decoding).
