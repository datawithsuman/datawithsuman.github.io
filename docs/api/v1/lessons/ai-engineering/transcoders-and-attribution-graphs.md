# Transcoders and Attribution Graphs

> How do transcoders make circuits readable, and what does an attribution graph show?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/ai-engineering/transcoders-and-attribution-graphs/
- Before this: Sparse Autoencoders (`ai-engineering/sparse-autoencoders`), The Residual Stream and Circuits (`ai-engineering/residual-stream-and-circuits`)

## Intuition

### The situation

You want to explain why a model answers "Austin" to "the capital of the state containing Dallas is". Circuits made of attention heads and MLPs are hard to read. The interviewer asks:

> How do transcoders make circuits readable, and what does an attribution graph show?

### The idea

Think of rewiring a machine with labelled replacement parts. If each part does the same job as the original but has readable labels, you can trace which part feeds which, as long as you remember the replacements aren't perfect.

[Figure: A readable part, a readable model, a graph per prompt.]

_Attribution graphs are built on a replacement model, not the original._

### Play

**Try it.** Change the input, and watch which feature-to-feature connections light up.

#### Learn a wide, sparse MLP that copies the real one

$$ \mathcal{L} = \big\lVert {h_\ell^{\text{out}}} - {(W_{\text{out}}z + b_{\text{out}})}\big\rVert_2^2 + {\lambda}\lVert z\rVert_1,\quad {z = \sigma(W_{\text{in}}h_\ell^{\text{in}} + b_{\text{in}})} $$

Survey §6.6.1 [p. 41](https://arxiv.org/pdf/2611.08438#page=41).

- **the real MLP’s output**: What the model’s MLP at layer ℓ actually produced.

- **sparse rebuild**: The transcoder’s output: a few decoder directions, weighted by feature activations z.

- **sparsity**: The same L1 trade-off as an SAE.

- **features from the input**: z = σ(W_in hₗ^in + b_in): features are computed from the MLP’s input, but judged by how well they predict its output.

The only change from an SAE is the target: **the MLP’s output**, not the input itself. In tests on GPT-2 small, Pythia-410M and Pythia-1.4B, transcoders were at least as good as SAEs on sparsity, faithfulness and human interpretability [Dunefsky et al. §4](https://arxiv.org/pdf/2406.11944#page=7).

##### The payoff: wiring you can read from weights

Because a transcoder feature’s output is linear in its activation, the effect of an earlier feature _i_ on a later feature _i′_ factors into two parts [Dunefsky et al. Eq. 7](https://arxiv.org/pdf/2406.11944#page=4):

$$ \text{effect}_{i\to i'} = {z_i(x)}\cdot{\big(f^{(\ell,i)}_{\text{dec}}\cdot f^{(\ell',i')}_{\text{enc}}\big)} $$

- **input-dependent**: How active the earlier feature is on this input. The only part that changes from input to input.

- **input-invariant**: Earlier feature’s decoder vector · later feature’s encoder vector: a fixed number, computed from weights alone. It describes the wiring for every input.

##### Try it: fixed wiring, changing inputs

Three earlier transcoder features and three later ones, with a fixed table of connections (decoder · encoder). Choose the input token. Only the earlier activations change; the wiring stays the same.

Illustrative weights and labels, inspired by the Polish-surname transcoder feature in Dunefsky et al. (§3.2.4); not values from a real model.

**Notice:** the weights between features stay fixed, and only the activations change with the input. That's what makes the wiring readable straight from the weights.

## How it works

### How it works

#### In one breath

A transcoder replaces an MLP with a sparse, readable stand-in that maps the MLP's input to its output, so feature-to-feature wiring can be read from the weights. A cross-layer transcoder lets each feature write to every later layer, giving a replacement model for all the MLPs. An attribution graph uses it for one prompt: features are nodes, direct effects are edges, and the graph is pruned to what matters.

#### An SAE on each side of an MLP doesn’t tell you how the MLP connects them

Suppose you have SAE features before an MLP and after it, and want to know which input features cause which output features. The MLP sits in between, with thousands of neurons each applying its own nonlinearity. Gradient or patching attributions through it depend on the specific input, so you only learn about one example at a time, never the MLP’s general behaviour [Dunefsky et al. §3.2](https://arxiv.org/pdf/2406.11944#page=4). The survey puts it simply: SAEs “do not explain the nonlinear transformations … themselves that produce the activations” [p. 41](https://arxiv.org/pdf/2611.08438#page=41).

#### One feature, many destinations

A cross-layer transcoder (CLT) reads features from the residual stream at layer ℓ, and each feature has a separate decoder vector into the MLP output of _every_ later layer. The reconstructed MLP output at layer ℓ′ sums contributions from all earlier layers’ features [p. 42](https://arxiv.org/pdf/2611.08438#page=42):

$$ {\hat h^{\text{out}}_{\ell'}} = {\sum_{\ell=1}^{\ell'}}\sum_j {W^{\ell\to\ell'}_{\text{out},j}}\,{z^j_\ell} $$

Survey §6.6.2 [p. 42](https://arxiv.org/pdf/2611.08438#page=42).

- **rebuilt MLP output**: The CLT’s stand-in for the MLP output at layer ℓ′.

- **from every earlier layer**: Sum over all layers ℓ up to and including ℓ′: features read early can still write late.

- **layer-pair decoder**: Feature j’s own decoder vector for the jump from layer ℓ to layer ℓ′.

- **feature activation**: Feature j read at layer ℓ (a JumpReLU of the residual stream).

Why this helps: a feature doesn’t need to be re-encoded at every layer, so circuits get simpler, and with MLPs replaced the rest of the computation becomes roughly linear. That makes clean attribution possible [p. 44](https://arxiv.org/pdf/2611.08438#page=44).

1. Start from the original model: attention and MLP blocks.

2. Replace every MLP with the CLT’s features, which read the stream and write to the current and all later layers.

3. Keep attention, but freeze its patterns (and the normalisation statistics) at the values from the original forward pass. The CLT does not model attention at all.

4. Add an error term at each layer for whatever the CLT failed to rebuild. With these, the replacement exactly reproduces the original on this one prompt.

5. Remove the crutches and swap the CLT in for real, and the replacement model’s top prediction matches the original on only about 50% of prompts from the Pile, in an 18-layer model survey p. 43.

#### Encode all layers together, decode each separately

$$ {z} = \mathrm{ReLU}\Big({\sum_{\ell=1}^{L} W^{\ell}_{\text{in}}h_\ell} + b_{\text{in}}\Big),\qquad {\hat h_\ell = W^{\ell}_{\text{out}}z + b^{\ell}_{\text{out}}} $$

Survey §6.6.3 [p. 45](https://arxiv.org/pdf/2611.08438#page=45). The sparsity penalty weights each feature by the sum of its decoder norms across layers.

- **one shared code**: z, a single set of sparse feature activations for the whole stack.

- **read every layer**: Each layer’s activation hₗ gets its own encoder W_in^ℓ, and their contributions are summed before the ReLU.

- **rebuild each layer**: Each layer has its own decoder, so one feature can have a different strength, or none, at each depth.

- **Causal crosscoders** read only layers up to the current one, respecting the forward pass.

- **Acausal crosscoders** read any layer, which is useful for describing feature relationships across the whole model after the fact [p. 46](https://arxiv.org/pdf/2611.08438#page=46).

##### Try it: a feature’s footprint across depth

For each crosscoder feature you can plot how strongly it is written at each layer, i.e. its decoder norm per layer. Different shapes tell different stories.

Illustrative profiles, not measured. The same idea applied across two models instead of two layers is used for model diffing (Steering Vectors).

#### Simpler circuits, and comparing models

Because one latent can stand for a feature at every layer, crosscoders remove duplicate copies that clutter circuits. Features can “jump” across intervening layers that just pass them along, and you can see which features persist unchanged and which get actively transformed [p. 46](https://arxiv.org/pdf/2611.08438#page=46).

Train one crosscoder on two models (say a base model and its fine-tuned version), and features whose decoder strength is large in only one model are candidates for what fine-tuning added [p. 45](https://arxiv.org/pdf/2611.08438#page=45).

##### False positives

Crosscoders trained with an L1 penalty can falsely report features as unique to one model. BatchTopK helps but doesn’t eliminate it: a feature whose direction merely _rotated_ during fine-tuning can look new. Treat “model-exclusive” features as hypotheses to test [p. 79](https://arxiv.org/pdf/2611.08438#page=79).

#### A feature’s direct pull on a later feature

$$ {A_{\phi_s\to\phi_t}} = \sum_{\ell_s\le\ell<\ell_t}{z^s_{\ell_s}}\,{(v_{\text{in},\phi_t})^{\top}}\,{J_{c_s,\ell\to c_t,\ell_t}}\,{v^{\ell}_{\text{out},\phi_s}} $$

Survey §7.2, Circuit Tracer box [pp. 55–57](https://arxiv.org/pdf/2611.08438#page=56).

- **edge weight**: How much source feature s directly raises target feature t on this prompt.

- **how active s is**: The source feature’s activation: the only input-dependent factor besides the Jacobian.

- **what t reads**: The target feature’s encoder direction.

- **the path between**: The Jacobian from a write at layer ℓ, position cₛ to the MLP input at layer ℓₜ, position cₜ, through the residual stream and attention, with attention patterns and normalisation frozen.

- **what s writes**: The source feature’s decoder vector into layer ℓ. Summed over every layer it writes to.

Two differences from EAP. The **nodes** are fine-grained features with natural-language labels, not whole heads or MLPs. The **edges** are direct, input-specific influences: gradients through intermediate MLPs are stopped, so each edge counts only the direct feature-to-feature effect, and no clean/corrupted pair is needed [p. 57](https://arxiv.org/pdf/2611.08438#page=57). The graph’s nodes also include token embeddings, error nodes (what the CLT failed to rebuild) and output logits [Ameisen et al.](https://transformer-circuits.pub/2025/attribution-graphs/methods.html).

#### Keep the strong edges, lose some of the story

A toy attribution graph for “the capital of the state containing Dallas is” → Austin, with the two-hop path (Dallas → Texas → Austin) plus a crowd of weak side features. Raise the threshold to prune weak edges, then drop features that no longer connect to the output.

Illustrative graph and weights (not from a real model). Influence = sum over all paths from the tokens to the output of the product of edge weights, computed in your browser.

Real graphs have many more nodes and edges, so they must be pruned, clustered or condensed before anyone can read them [p. 57](https://arxiv.org/pdf/2611.08438#page=57). Platforms such as Neuronpedia host interactive versions.

## In practice

### In practice

#### Parameters grow with depth squared

With L layers, model width d and expansion factor e, a full CLT has L encoders and L(L+1)/2 layer-pair decoders. Ignoring biases, that is _N = (e·d²/2)(L² + 3L)_ [p. 44](https://arxiv.org/pdf/2611.08438#page=44). Training the CLTs for Gemma-2-9B took about 3,844 H100 GPU-hours [p. 44](https://arxiv.org/pdf/2611.08438#page=44).

Survey formula (§6.6.2, Fig. 8), computed in your browser. Memory assumes 2 bytes per parameter.

##### Fidelity caveats the survey lists

- Results come mainly from small models, on short sequences from the CLT’s own training data; behaviour under distribution shift isn’t well tested.

- The headline metric is top-1 agreement; softer metrics (top-5, KL divergence) may tell a different story.

- Exact matching requires frozen attention, cached normalisation and per-layer error terms.

- Fidelity is higher in middle layers, and on factual recall and syntax than on reasoning or arithmetic.

[pp. 43–44](https://arxiv.org/pdf/2611.08438#page=43)

This scarcity shows in practice: the survey counts only a handful of downstream CLT applications so far (a greater-than mechanism study, an open-source extension, multilingual analysis) [p. 44](https://arxiv.org/pdf/2611.08438#page=44). CLTs come back in Activation Patching and Circuit Discovery as the engine of attribution graphs.

#### Caveats

##### Limits

- It explains the **replacement model**. CLTs only approximate the MLPs (a full replacement matches the top-1 prediction on about 50% of prompts in an 18-layer model), so the graph may cover only part of the real mechanism [pp. 43, 57](https://arxiv.org/pdf/2611.08438#page=43).

- **Attention is frozen**: the graph shows what flows through attention, not why attention looked where it did [p. 44](https://arxiv.org/pdf/2611.08438#page=44).

- The authors report satisfying insight on only a minority of prompts tried (secondary summaries say about a quarter) [Lindsey et al. 2025](https://transformer-circuits.pub/2025/attribution-graphs/biology.html).

What it gives in return: readable, prompt-specific mechanisms such as the two-hop Dallas → Texas → Austin reasoning in Claude 3.5 Haiku (The Residual Stream and Circuits), where intervening on the intermediate “Texas” features changes the answer [Lindsey et al. 2025](https://transformer-circuits.pub/2025/attribution-graphs/biology.html).

##### Next · 6.4

Is a discovered circuit actually causal, and how much does it explain?

##### Sources for this tab

- Survey §7.2, [arXiv 2611.08438](https://arxiv.org/abs/2611.08438), pp. 55–57.

- Ameisen et al. (2025). _Circuit Tracing._ [transformer-circuits.pub](https://transformer-circuits.pub/2025/attribution-graphs/methods.html).

- Lindsey et al. (2025). _On the Biology of a Large Language Model._ [transformer-circuits.pub](https://transformer-circuits.pub/2025/attribution-graphs/biology.html).

#### Open tools anyone can use

Anthropic introduced attribution graphs with cross-layer transcoders in March 2025 and used them on Claude 3.5 Haiku. On 29 May 2025 it open-sourced the `circuit-tracer` library, which supports popular open-weights models (Anthropic used it on Gemma-2-2B and Llama-3.2-1B), with an interactive front end on Neuronpedia. By mid-June 2025, Neuronpedia reported almost 5,000 graphs generated by users.

Google DeepMind's Gemma Scope 2 (December 2025) added skip-transcoders and cross-layer transcoders for every Gemma 3 model, so you can trace multi-step computations in models up to 27B parameters.

### The answer that sounds right

#### "The attribution graph shows how the model works"

It sounds like a full explanation, but the graph describes a replacement model, not the original. Attention is frozen, error nodes hold what the transcoders miss, and it covers one prompt. Confirm the key steps by intervening on the real model, as the Dallas → Austin example did.

## Say it

### How do transcoders make circuits readable, and what does an attribution graph show?

#### The interviewer pushes further

Follow-up 1 of 3

Why are transcoder circuits easier to read than SAE circuits?

Between SAEs on two layers, the connection passes through the MLP's nonlinearity and depends on the input. Transcoder features connect through fixed weights.

Follow-up 2 of 3

What are error nodes?

The part of each MLP's output the transcoder fails to reconstruct. They keep the graph adding up, but they're unexplained computation.

Follow-up 3 of 3

What does a crosscoder add?

One dictionary across layers removes duplicate copies of a feature at every depth, and one across two models supports model diffing.

#### The 30-second answer

An SAE describes what a layer contains, but a transcoder describes what an MLP does: it maps the MLP's input to its output through sparse, readable features, so feature-to-feature wiring can be read from the weights. A cross-layer transcoder lets each feature write to every later layer, which gives a replacement model for all the MLPs. An attribution graph uses that for one prompt: nodes are features, and edges are direct effects through the frozen residual stream and attention. It's rich but approximate, so I'd prune it and check the main paths with interventions on the real model.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv [2611.08438](https://arxiv.org/abs/2611.08438)) and 7 more sources · checked 13 Nov 2026

#### Sources

- [Barez et al., Understanding AI from the Inside (survey, 2026)](https://arxiv.org/abs/2611.08438)

- [Dunefsky et al., Transcoders Find Interpretable LLM Feature Circuits (2024)](https://arxiv.org/abs/2406.11944)

- [Lindsey et al., Sparse Crosscoders (Anthropic, 2024)](https://transformer-circuits.pub/2024/crosscoders/index.html)

- [Ameisen et al., Circuit Tracing: Revealing Computational Graphs in Language Models (Anthropic, 2025)](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)

- [Lindsey et al., On the Biology of a Large Language Model (Anthropic, 2025)](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)

- [Anthropic, Open-sourcing circuit tracing tools (29 May 2025)](https://www.anthropic.com/research/open-source-circuit-tracing)

- [Neuronpedia, Circuit tracer blog post (2025)](https://www.neuronpedia.org/blog/circuit-tracer)

- [Google DeepMind, Gemma Scope 2 (19 Dec 2025)](https://deepmind.google/blog/gemma-scope-2-helping-the-ai-safety-community-deepen-understanding-of-complex-language-model-behavior/)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
