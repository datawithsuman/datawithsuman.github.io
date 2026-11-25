# Mixture of Experts

> How does a 47B model run at 13B cost, and what goes wrong?

- Track: Fundamentals › LLMs › Modern architecture
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/mixture-of-experts/
- Before this: Anatomy of a Modern LLM (`fundamentals/modern-llm-architecture`)
- Quiz topic: `arch`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 9a44608e79

## Intuition

### The situation

The team considers swapping the 8B dense assistant for an MoE model with similar compute per token but far more parameters. A colleague says that means the same hardware and a smarter model. The interviewer asks:

> How does a 47B model run at 13B cost, and what goes wrong?

Where this lesson sits: the feed-forward box, replaced by a router plus several expert FFNs.

Background: The Transformer Block.

**Running example:** the team considers swapping the 8B dense assistant for an MoE model with similar per-token compute but far more knowledge capacity. What does it cost, and what can go wrong?

#### More parameters, same compute per token

Bigger models know more, but in a dense model every parameter is used for every token, so compute grows with size. Different tokens need different knowledge: code, Hindi, arithmetic, recipes. Conditional computation lets each token use only the part of the network it needs.

### The idea

Think of a large call centre where each call goes to only two agents. You have many agents on the payroll, but each call uses very few. If the router favours one agent, that queue overflows, and agents who get no calls never improve. You also still pay for every agent, busy or not.

[Figure: Load on 8 experts. Without balancing, expert 1 gets far more than its fair share and goes over the capacity line, while expert 8 gets almost nothing. With bias balancing, all eight are about equal and under the line.]

_1,024 tokens at capacity factor 1.25. Expert 1's 2.37× and expert 8's 0.15× are from the lab; the bars between are illustrative._

### Play

**Try to break it.** Use top-2 with no balancing, and raise the capacity factor. Then switch to bias balancing, and compare the dropped token-slots.

#### Let the router choose freely

1,024 tokens, 8 experts. Router scores = an expert preference that has drifted towards expert 1 (as happens early in training when popular experts get more updates) + per-token noise; fixed seed. Bias balancing: before routing, each expert's bias is nudged up if it's under-loaded and down if over-loaded (300 small steps); the bias affects only which experts are chosen, not the gate weights.

Without balancing, top-2 routing sends expert 1 **2.37×** its fair share while expert 8 gets only **0.15×**; at capacity factor 1.25, **22.6%** of token-slots overflow and are dropped. Raising capacity to 2.0 cuts drops to 4.6% but wastes memory and compute on padding. It gets worse over training: favoured experts improve, get chosen more, and the others starve (**expert collapse**). With **bias balancing** every expert is within about 2% of the average and nothing is dropped at 1.25.

**Now say why:** raising capacity also cuts drops, so why isn't that the fix?

## Maths

### Maths

#### In one breath

Since most parameters sit in the feed-forward layers, an MoE layer replaces the one FFN with many **experts** (separate FFNs) and a small **router** that sends each token to only the top-k of them. Total parameters grow, but compute per token only depends on the k active experts: **Mixtral 8x7B** has 47B parameters but uses about 13B per token; **DeepSeek-V3** has 671B and activates 37B. The hard part is **load balancing**: routers tend to favour a few experts, which wastes the rest and, with fixed expert **capacity**, drops tokens. Classic fixes add an auxiliary balancing loss; DeepSeek-V3 instead nudges a per-expert bias. MoE saves compute, not memory: every expert must still be loaded. What you'll be able to do after this: explain top-k routing, total vs active parameters, and how load balancing and capacity work.

#### Router and top-k gating

$$ y = \sum_{i\,\in\,{\mathrm{TopK}(}{xW_r}{,\,k)}} {g_i(x)}\;{E_i(x)} $$

Shazeer et al., "Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer", ICLR 2017; Jiang et al., "Mixtral of Experts", [arXiv:2401.04088](https://arxiv.org/abs/2401.04088).

- **router scores**: A single linear layer W_r gives one score per expert for this token.

- **keep the top k**: Only the k highest-scoring experts run (Mixtral: 2 of 8; DeepSeek-V3: 8 of 256 routed experts plus 1 shared expert). The others cost nothing for this token.

- **gate weights**: A softmax over the kept scores decides how much each chosen expert contributes.

- **expert outputs**: Each expert is an ordinary SwiGLU FFN; the layer output is their weighted sum.

- **Total vs active:** Mixtral has 8 experts per layer but attention and embeddings are shared, so it's 47B total, not 8 × 7B = 56B, and about 13B active per token. It matched or beat Llama 2 70B on most benchmarks the paper reports.

- **Capacity:** for efficient batched compute each expert gets a fixed buffer, capacity = capacity factor × (tokens × k / experts). Tokens beyond it are dropped (passed through the residual only).

## In practice

### In practice

#### Keeping experts busy

- **Auxiliary loss** (GShard, Switch Transformer): add α · E · Σ fᵢ Pᵢ, where fᵢ is the fraction of tokens sent to expert i and Pᵢ its mean router probability (Switch: α = 0.01). It works, but too strong a loss hurts quality.

- **Switch Transformer** (Fedus et al.): top-1 routing, capacity factor ~1–1.25; up to 7× faster pre-training than a dense T5-Base with the same compute per token.

- **Fine-grained and shared experts** (DeepSeekMoE): many small experts plus always-on shared experts for common knowledge.

- **Auxiliary-loss-free balancing** (DeepSeek-V3): a per-expert bias added to the routing scores only for top-k selection, updated after each step; DeepSeek-V3 also drops no tokens during training.

**Serving costs.** All experts must sit in GPU memory (Mixtral needs the memory of a 47B model to run at 13B compute), experts are spread across GPUs (expert parallelism), and routing needs all-to-all communication. MoE pays off at high throughput; for a single user on one small GPU a dense model is often simpler.

#### Decouple parameters from FLOPs

MoE lets knowledge capacity (total parameters) grow independently of compute per token (active parameters), as long as the router spreads tokens evenly enough that every expert learns and none overflows.

### The answer that sounds right

#### "MoE reduces memory"

It sounds right, since it only uses a fraction of the model per token. But every expert must sit in GPU memory, so Mixtral needs the memory of a 47B model to run at 13B compute. It reduces compute per token, and memory still follows total parameters. And experts aren't topic specialists either: Mixtral's routing followed syntax and token patterns more than domains.

## Say it

### How does a 47B model run at 13B cost, and what goes wrong?

#### The interviewer pushes further

Follow-up 1 of 3

Why isn't Mixtral 8 × 7B = 56B?

Only the FFNs are replicated; attention, norms and embeddings are shared, so the total is about 47B.

Follow-up 2 of 3

Do experts specialise by topic?

Not cleanly: Mixtral's analysis found routing followed syntax and token patterns more than domains like biology or maths.

Follow-up 3 of 3

MoE vs dense for a latency-sensitive single-GPU deployment?

Usually dense: MoE needs memory for all experts and benefits from large batches; at batch size 1 the memory reads of a big MoE can make it slower than its active-parameter count suggests.

#### The 30-second answer

A mixture-of-experts layer replaces the dense feed-forward layer with many expert FFNs and a learned router that sends each token to its top-k experts, weighting their outputs with a softmax over the selected scores. Total parameters grow but compute per token depends only on active ones: Mixtral 8x7B is 47B total and about 13B active, DeepSeek-V3 is 671B total and 37B active. The main challenge is load balancing: without it a few experts get most tokens, others collapse, and with fixed expert capacity tokens get dropped. Fixes are an auxiliary balancing loss, capacity factors, shared experts, or DeepSeek-V3's bias-based auxiliary-loss-free balancing. MoE saves FLOPs, not memory, and needs expert parallelism with all-to-all communication.

**Go further**

#### What not to say

- "MoE reduces memory." It reduces compute per token; memory follows total parameters.

- "Each expert is an expert in a topic." Specialisation is mostly at the token level.

**Key terms and sources**

How MoE layers give a model many more parameters without more compute per token: the router and top-k gating, total vs active parameters, load imbalance and expert collapse, capacity factors and dropped tokens, auxiliary losses vs DeepSeek-V3's bias-based balancing, and the serving trade-offs · built from Shazeer et al. (2017), Lepikhin et al. (GShard, 2020), Fedus et al. (Switch Transformer, JMLR 2022), Jiang et al. (Mixtral, 2024), Dai et al. (DeepSeekMoE, 2024), Wang et al. (Loss-Free Balancing, 2024) and DeepSeek-AI (DeepSeek-V3, 2024) · checked 29 Oct 2026

#### Sources

1. N. Shazeer et al., "Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer", ICLR 2017, [arXiv:1701.06538](https://arxiv.org/abs/1701.06538); D. Lepikhin et al., "GShard", 2020, [arXiv:2006.16668](https://arxiv.org/abs/2006.16668).

2. W. Fedus, B. Zoph & N. Shazeer, "Switch Transformers", JMLR 2022, [arXiv:2101.03961](https://arxiv.org/abs/2101.03961).

3. A. Jiang et al., "Mixtral of Experts", 2024, [arXiv:2401.04088](https://arxiv.org/abs/2401.04088).

4. D. Dai et al., "DeepSeekMoE", 2024, [arXiv:2401.06066](https://arxiv.org/abs/2401.06066); L. Wang et al., "Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts", 2024, [arXiv:2408.15664](https://arxiv.org/abs/2408.15664).

5. DeepSeek-AI, "DeepSeek-V3 Technical Report", 2024, [arXiv:2412.19437](https://arxiv.org/abs/2412.19437).
