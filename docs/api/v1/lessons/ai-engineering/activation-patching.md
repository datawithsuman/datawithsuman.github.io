# Activation Patching and Circuit Discovery

> How do you test whether a component causes a behaviour, and how do you scale that to a whole model?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/ai-engineering/activation-patching/
- Before this: The Residual Stream and Circuits (`ai-engineering/residual-stream-and-circuits`)
- Sources checked: 2026-11-13 · Text last changed: 2026-11-20 · Version: 9fd182aaec

## Intuition

### The situation

Your team thinks a few attention heads make the model pick the right name in "When Mary and John went to the store, John gave a drink to". Zero-ablating the main head barely changes the output. The interviewer asks:

> How do you test whether a component causes a behaviour, and how do you scale that to a whole model?

### The idea

Think of finding which wire powers one light in a house. Swap one wire's signal for the one from a house where the light is off, and see if the light changes. A backup wire can hide an important one, so a small change doesn't mean the wire is useless.

[Figure: One patch, then automate it.]

_Patching is the causal test that most circuit methods are built on._

### Play

**Try it.** Patch each component of the toy circuit one at a time. Then knock out the main name mover.

#### Patch each part of a small circuit with a built-in backup

A toy circuit with the same shape as GPT-2’s name-picking circuit (The Residual Stream and Circuits): a **duplicate detector** (D) feeds an **inhibition** step (S), which drives a **name mover** (N) that writes the answer. A **backup** mover (B) only acts when N is weaker than expected, and a **negative** mover (Neg) pushes slightly the other way. Clean logit difference is 1.8, corrupted is 0.2.

Toy equations: D ∈ {1 clean, 0 corrupt}; S = D; N = 2S; B = max(0, 1.6S − 0.8N); Neg = −0.4S; output = N + B + Neg + 0.2. Effect = (clean − patched) / (clean − corrupted).

This is what Wang et al. saw in GPT-2: knocking out all the name-mover heads cost only about 5% of performance, because backup heads took over [Wang et al. §3.4](https://arxiv.org/pdf/2211.00593#page=9). The survey lists this “hydra effect” among the reasons that explaining is not the same as controlling [p. 20](https://arxiv.org/pdf/2611.08438#page=20).

**Notice:** knocking out the main head barely hurts, because a backup head takes over. Testing one component at a time can make an important one look unimportant.

## How it works

### How it works

#### In one breath

Activation patching runs a model on a clean input, swaps in one component's value from a minimally corrupted input, and measures how the output changes. Path patching does the same for one connection. The choice of corruption and metric changes the answer, and backup components can hide importance. ACDC automates patching edge by edge, and edge attribution patching estimates every edge at once with gradients.

#### Swap one part, see what breaks

1. Run the model on a clean input that shows the behaviour, and remember every activation.

2. Run it on a corrupted input with the key information changed, and remember those activations too.

3. Run the clean input again, but overwrite one component’s activation with its corrupted value. Everything downstream recomputes normally.

4. Measure the change in a scalar metric, such as the logit difference between the right and wrong answer. A big change means that component carries information the behaviour needs.

$$ {s_S(x)} = {M}\big({f_\theta(x)}\big) - {M}\big({f_\theta(x_{[S\leftarrow\tilde h_S]})}\big) $$

Survey §7.1 [p. 54](https://arxiv.org/pdf/2611.08438#page=54).

- **importance of S**: The causal effect of the component set S on input x.

- **a scalar metric**: Usually the logit difference between the correct and the wrong answer.

- **normal run**: The model’s output on the clean input.

- **patched run**: The same input, but S’s activations replaced by reference values h̃_S: from a corrupted input, the mean, or zero.

#### Patch a connection, not a whole component

Path patching replaces the activation travelling along one edge _eij_ (from component i to component j) and leaves every other route clean. That separates a component’s _direct_ effect from effects routed through other components, which is exactly what the toy above needed [p. 54](https://arxiv.org/pdf/2611.08438#page=54). It is finer, and also costlier: there are far more edges than nodes.

#### Remove an edge if it costs less than τ

1. Start with the full computational graph and a threshold τ.

2. Begin at the output. For each incoming edge, patch it with its corrupted value and measure how much the metric (KL divergence to the full model) gets worse.

3. If the damage is below τ, remove the edge for good; otherwise keep it. Here B → out goes.

4. Move to the parents of what remains and repeat, working back towards the input.

5. What’s left is the circuit. A lower τ keeps more edges.

ACDC rediscovered all 5 component types of GPT-2 small’s greater-than circuit, choosing 68 of about 32,000 edges, all of which earlier manual work had found [Conmy et al. 2023](https://arxiv.org/abs/2304.14997). The limits: it needs a forward pass per edge tested, it is sensitive to τ and to the order in which edges are tried, and because it optimises one metric it tends to miss _negative_ components (heads that push against the answer) unless τ is very small [Conmy et al. §4](https://arxiv.org/pdf/2304.14997#page=7) [survey Table 8](https://arxiv.org/pdf/2611.08438#page=56).

#### Estimate all edges at once with a first-order approximation

$$ {s_{ij}(x)} \approx {\frac{\partial M}{\partial h_{e_{ij}}}}\cdot{\big(h^{\text{clean}}_{e_{ij}} - h^{\text{corrupt}}_{e_{ij}}\big)} $$

Survey §7.1 [p. 54](https://arxiv.org/pdf/2611.08438#page=54).

- **estimated effect**: EAP’s guess at what patching edge eᵢⱼ would do.

- **local slope**: How sensitive the metric is to that edge’s activation, from one backward pass on the clean input.

- **how much it would change**: The difference between the edge’s clean and corrupted activations, from two forward passes.

Two forward passes and one backward pass score every edge, against one pass per edge for ACDC [p. 54](https://arxiv.org/pdf/2611.08438#page=54). But it assumes the metric is roughly a straight line between the clean and corrupted values.

##### Try it: when the straight-line guess fails

One edge, whose effect on the metric saturates (M = 3·tanh(h)). Its clean value is 1.5. Move the corrupted value and compare the true patching effect with EAP’s estimate and with integrated gradients (EAP-IG), which averages the slope along the path instead of using the slope at one end.

Real computation on a toy metric; IG uses 50 steps along the straight path from corrupted to clean.

That is why later work improved the estimate (EAP-IG, EAP-GP) and extended it across token positions (PEAP) [p. 54](https://arxiv.org/pdf/2611.08438#page=54).

#### Learn which edges to keep

A third family treats discovery as optimisation: learn a mask over edges (Edge Pruning) or over nodes at several scales (multi-granular node pruning) with gradient descent, so the model still behaves the same with as little of the graph as possible. These usually find sparser circuits, but the training itself adds randomness and sensitivity to settings like the learning rate [p. 55](https://arxiv.org/pdf/2611.08438#page=55).

| Method | Strength | Limit |
|---|---|---|
| **Activation patching** | simple, direct causal evidence | many runs; component-level is coarse |
| **Path patching** | finer: isolates information flow | huge number of paths |
| **ACDC** | fully automated; finds a sufficient subgraph | slow; sensitive to τ and order |
| **EAP / EAP-IG** | fast; every edge in parallel | first-order; can miss nonlinear effects |
| **Mask learning** | sparser circuits | optimisation noise, hyperparameters |

Survey Table 8 [p. 56](https://arxiv.org/pdf/2611.08438#page=56).

## In practice

### In practice

#### What to replace with, and what to measure

| Choice | Options | Recommendation |
|---|---|---|
| **Reference value** | zero · dataset mean · a corrupted input’s value | Zero and mean can push the model off-distribution; corrupted (resampled) values are usually preferred |
| **How to corrupt** | Gaussian noise on embeddings · swap key tokens for similar ones | Prefer token swaps (in-distribution); noise can break mechanisms and give misleading peaks |
| **Metric** | probability · logit difference · KL divergence | Logit difference; probability can miss components that actively hurt the answer |

Zhang & Nanda (2024) found that Gaussian noise and token swaps picked out different heads on the same IOI task, and that probability failed to detect negative name-mover heads [arXiv 2309.16042](https://arxiv.org/abs/2309.16042). Survey §7.1 notes zero and mean references are also used [p. 54](https://arxiv.org/pdf/2611.08438#page=54).

#### A circuit for a dataset, or for one prompt?

**Task-level** discovery (IOI, greater-than) averages edge scores over a dataset to describe a capability as a whole; all the methods above were developed mainly for this. **Query-level** discovery explains one prompt, which matters for open-ended questions where the computation varies a lot from input to input. EAP-IG has been extended to find sparse, faithful circuits for individual natural prompts [p. 55](https://arxiv.org/pdf/2611.08438#page=55).

##### Next · 6.3

Attribution graphs: query-level circuits built from interpretable features instead of whole heads and MLPs.

##### Sources for this tab

- Survey §7.1, Table 8, [arXiv 2611.08438](https://arxiv.org/abs/2611.08438), pp. 53–56.

- Conmy et al. (2023). _Towards Automated Circuit Discovery for Mechanistic Interpretability._ NeurIPS 2023, [arXiv 2304.14997](https://arxiv.org/abs/2304.14997).

#### Best practice, as the field settled it

Patching goes by many names: interchange intervention, causal tracing, resample ablation and causal mediation analysis (Heimersheim and Nanda, 2024). Their guide and Zhang and Nanda (2023) found that small choices change conclusions, and recommend:

- **Corrupt minimally.** Swap one token for a similar one ("Mary" for "John") rather than adding Gaussian noise or zeroing, which push activations off the model's normal range.

- **Use logit difference.** Probability saturates, so large effects look small.

- **Know which direction you patched.** Patching clean into corrupted (denoising) tests whether a component is sufficient. Patching corrupted into clean (noising) tests whether it's necessary. They can disagree.

### The answer that sounds right

#### "Ablating the head did nothing, so it doesn't matter"

It sounds like a clean negative result, but backup heads can take over when one is removed, and zero ablation pushes activations off distribution. Patch with a realistic corrupted input, test paths and groups of components, not just single nodes.

## Say it

### How do you test whether a component causes a behaviour, and how do you scale that to a whole model?

#### The interviewer pushes further

Follow-up 1 of 3

Noising versus denoising?

Denoising patches clean activations into a corrupted run and tests sufficiency. Noising patches corrupted ones into a clean run and tests necessity. They can give different answers.

Follow-up 2 of 3

Why can edge attribution patching mislead?

It's a first-order approximation. When an effect saturates, the gradient is near zero even though a full patch would change a lot, so important edges get underestimated.

Follow-up 3 of 3

Why not zero ablation?

Zero is often far from any real activation, so you measure the damage of an unnatural input, not the component's role. Mean or resample ablation keeps activations realistic.

#### The 30-second answer

I'd use activation patching: run the model on a clean prompt and a minimally corrupted one, swap one component's activation between the runs, and measure the change in logit difference. Path patching does the same for a single connection. The choices matter: corrupt with a realistic swap rather than zeros, and use logit difference, because probability saturates. Backup heads can hide importance, so I'd test groups too. To scale up, ACDC prunes edges against a threshold, and edge attribution patching estimates every edge's effect with gradients in one backward pass, and then I'd check the top edges with real patches.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv [2611.08438](https://arxiv.org/abs/2611.08438)) and 5 more sources · checked 13 Nov 2026

#### Sources

- [Barez et al., Understanding AI from the Inside (survey, 2026)](https://arxiv.org/abs/2611.08438)

- [Heimersheim and Nanda, How to Use and Interpret Activation Patching (2024)](https://arxiv.org/abs/2404.15255)

- [Zhang and Nanda, Towards Best Practices of Activation Patching (2023)](https://arxiv.org/abs/2309.16042)

- [Conmy et al., Towards Automated Circuit Discovery (ACDC, 2023)](https://arxiv.org/abs/2304.14997)

- [Syed et al., Attribution Patching Outperforms Automated Circuit Discovery (2023)](https://arxiv.org/abs/2310.10348)

- [Wang et al., Interpretability in the Wild: the IOI circuit in GPT-2 small (2022)](https://arxiv.org/abs/2211.00593)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
