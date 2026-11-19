# Scaling Laws: Kaplan vs Chinchilla

> Bigger model or more tokens, and why was Llama 3 8B trained on 15T?

- Track: Fundamentals › LLMs › Pretraining
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/scaling-laws/
- Before this: The Next-Token Objective (`fundamentals/next-token-prediction`)
- Quiz topic: `pre`

## Intuition

### The situation

The team has a fixed GPU budget for a home-grown model. One camp wants the biggest model it can afford, and the other wants a smaller one on more tokens. The interviewer asks:

> Bigger model or more tokens, and why was Llama 3 8B trained on 15T?

**Running example:** the team has a fixed GPU budget for a home-grown model. Should they train a bigger model on fewer tokens, or a smaller one on more?

#### One shot at a very expensive run

A frontier pre-training run costs tens of millions of dollars and can't be repeated with different settings. Scaling laws let teams train dozens of small models, fit how loss depends on size and data, and choose the big run's model size, token count and even data mixture in advance. Meta chose the 405B size this way for a budget of 3.8 × 1025 FLOPs.

### The idea

Think of the budget as a rectangle with a fixed area. One side is model size, and the other is training tokens. Wide and flat costs the same as narrow and tall, but they don't learn equally well. The best shape is about 20 tokens per parameter.

[Figure: Two rectangles with about the same area, meaning the same compute. Gopher is wide and flat: 280B parameters on 300B tokens, predicted loss 2.000. Chinchilla is narrow and tall: 70B parameters on 1.4 trillion tokens, predicted loss 1.974.]

_Sizes to scale, with about the same compute. Predicted loss from the fitted law, as in the lab._

### Play

**Try to break it.** Compare Gopher with Chinchilla at similar compute. Then look at Llama 3 405B and Llama 3 8B, and see how far each sits from its optimum.

#### Was each famous model compute-optimal?

Curve: predicted loss for every model size if all models got this same compute (an "IsoFLOP" curve); D = C / 6N. Loss values come from the fitted law (Chinchilla's data and tokeniser), so compare them with each other, not with other models' reported losses.

**Gopher** (280B parameters, 300B tokens, about 1 token per parameter) and **Chinchilla** (70B, 1.4T, 20 per parameter) used similar compute, about 5–6 × 1023 FLOPs. The law puts Chinchilla right at the optimum (loss 1.974) and Gopher **0.021** above it: four times the parameters, worse loss. In the paper Chinchilla beat Gopher on MMLU, 67.5% vs 60.0%. **Llama 3 405B**, at 39 tokens per parameter, is within 0.001 of its optimum, consistent with Meta's description of it as roughly compute-optimal. **Llama 3 8B** is the interesting one: at its budget the optimum is an 81B model on 1.5T tokens, and the 8B model's predicted loss is 0.054 higher. That's deliberate: see the In practice tab.

**Now say why:** the law says Llama 3 8B is far from optimal. Why would Meta do that on purpose?

## Maths

### Maths

#### In one breath

LLM loss follows smooth **power laws**: it drops predictably as you add parameters N, training tokens D and compute C, so teams fit these laws on small runs and extrapolate before spending millions. Training compute is about **C ≈ 6·N·D** FLOPs. For a fixed C, a bigger model sees fewer tokens; the question is the best split. **Kaplan et al. (2020)** said grow the model much faster than the data, which led to GPT-3's 175B parameters on 300B tokens. **Chinchilla (2022)** redid the experiments and found parameters and tokens should grow equally, about **20 tokens per parameter**: their 70B model on 1.4T tokens beat the 280B Gopher at the same compute. Today models are deliberately **over-trained** beyond that (Llama 3 8B saw 15T tokens, ~1,900 per parameter), because a smaller model is much cheaper to serve.What you'll be able to do after this: estimate training FLOPs, explain compute-optimal scaling, and argue when to train past it.

#### Compute and the Chinchilla loss law

$$ C \approx 6ND, \qquad L(N,D) = E + \frac{A}{N^{\alpha}} + \frac{B}{D^{\beta}} $$

Hoffmann et al., "Training Compute-Optimal Large Language Models", arXiv:2203.15556 (approach 3). Besiroglu et al. (2024, arXiv:2404.10102) found the published fit inconsistent with the paper's other methods and refit it: E = 1.82, A = 482, B = 2,085, α = 0.348, β = 0.366, which gives about 20 tokens per parameter, matching Chinchilla's other two approaches. The lab uses this refit.

- **training FLOPs**: About 2 FLOPs per parameter per token for the forward pass and 4 for the backward pass: 6·N·D. Llama 3 405B: 6 × 405e9 × 15.6e12 ≈ 3.8 × 10²⁵.

- **irreducible loss**: The entropy of natural text itself: no model can go below it.

- **too few parameters**: Loss from limited model capacity, shrinking as a power of N.

- **too few tokens**: Loss from limited data, shrinking as a power of D. The optimum balances these two terms for a given C.

## In practice

### In practice

#### Training past compute-optimal

- **Chinchilla-optimal minimises training compute for a given loss**, not total cost. A model served to millions of users spends far more compute at inference, which scales with N. Sardana et al. (2024) showed that once expected inference demand is included, the best model is smaller and trained on many more tokens.

- Hence Llama 3 8B on 15T tokens (~1,875 per parameter), and small models like Qwen and Gemma trained on 10T+ tokens. Meta reported that 8B and 70B kept improving log-linearly up to 15T tokens.

- **Kaplan vs Chinchilla:** Kaplan et al. fitted mostly smaller models, counted non-embedding parameters and used a learning-rate schedule that didn't match each run's length, which biased their recommendation towards big models on few tokens.

- Scaling laws predict pre-training loss well; downstream task accuracy is less smooth. Newer work also studies test-time compute scaling (reasoning models spend more compute at inference instead).

#### Balance parameters and tokens, then pay for inference

For a fixed training budget, loss is minimised by growing parameters and tokens together (about 20 tokens per parameter); if the model will be served heavily, deliberately train a smaller model on many more tokens.

### The answer that sounds right

#### "Chinchilla-optimal is always best"

It sounds right, since it gives the lowest loss for the compute. But it minimises training compute only, and a model served to millions spends far more at inference. Once inference demand is included, the best model is smaller and trained on many more tokens. Scaling laws also predict loss, not benchmark scores, and task accuracy is noisier.

## Say it

### Bigger model or more tokens, and why was Llama 3 8B trained on 15T?

#### The interviewer pushes further

Follow-up 1 of 3

Estimate the compute to train a 7B model on 2T tokens.

6 × 7e9 × 2e12 = 8.4 × 10²² FLOPs. At 40% utilisation of a 989 TFLOPS (bf16) H100, that's about 2.1 × 10⁸ GPU-seconds ≈ 59,000 GPU-hours.

Follow-up 2 of 3

What's the compute-optimal model for 10²⁴ FLOPs?

With D = 20N and C = 6ND = 120N², N = √(C/120) ≈ 91B parameters on about 1.8T tokens.

Follow-up 3 of 3

Why did Kaplan get a different answer?

Smaller models, a fixed learning-rate schedule not tuned to each run's length, and counting only non-embedding parameters; Chinchilla corrected these.

#### The 30-second answer

Pre-training loss follows power laws in parameters, data and compute, so labs fit them on small runs to plan big ones. Training compute is about 6 times parameters times tokens. Kaplan et al. in 2020 suggested scaling model size faster than data, but Chinchilla in 2022 found they should scale equally, roughly 20 tokens per parameter: a 70B model on 1.4 trillion tokens beat the 280B Gopher at the same compute. In practice models are now over-trained beyond that, like Llama 3 8B on 15 trillion tokens, because Chinchilla minimises training cost only, and a smaller model is much cheaper at inference.

**Go further**

#### What not to say

- "Chinchilla-optimal is always best." It ignores inference cost.

- "Scaling laws predict benchmark scores." They predict loss; task accuracy is noisier.

**Key terms and sources**

How loss falls predictably with model size, data and compute; the C ≈ 6ND estimate of training FLOPs; how Kaplan et al. and Chinchilla disagreed about splitting a budget between parameters and tokens; the "20 tokens per parameter" rule; and why Llama 3 8B was trained far past it on purpose · built from Kaplan et al. (2020), Hoffmann et al. (Chinchilla, NeurIPS 2022), Besiroglu et al. (Epoch AI replication, 2024), Sardana et al. (Beyond Chinchilla-Optimal, ICML 2024) and Meta's Llama 3 report (2024) · checked 29 Oct 2026

#### Sources

1. J. Kaplan et al., "Scaling Laws for Neural Language Models", 2020, arXiv:2001.08361.

2. J. Hoffmann et al., "Training Compute-Optimal Large Language Models" (Chinchilla), NeurIPS 2022, arXiv:2203.15556.

3. T. Besiroglu, E. Erdil, M. Barnett & J. You, "Chinchilla Scaling: A replication attempt", Epoch AI, 2024, arXiv:2404.10102.

4. N. Sardana et al., "Beyond Chinchilla-Optimal: Accounting for Inference in Language Model Scaling Laws", ICML 2024, arXiv:2401.00448.

5. Llama Team, Meta, "The Llama 3 Herd of Models", 2024, arXiv:2407.21783.
