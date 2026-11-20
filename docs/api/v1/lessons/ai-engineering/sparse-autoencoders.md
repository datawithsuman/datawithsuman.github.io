# Sparse Autoencoders

> How does a sparse autoencoder pull features out of activations, and how do you choose a variant?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/ai-engineering/sparse-autoencoders/
- Before this: Features, Polysemanticity and Superposition (`ai-engineering/features-and-superposition`)

## Intuition

### The situation

Your team wants to find what a model represents about medical advice, without knowing in advance what to look for. Someone suggests training a sparse autoencoder on layer 20. The interviewer asks:

> How does a sparse autoencoder pull features out of activations, and how do you choose a variant?

### The idea

Think of un-mixing a smoothie. The SAE learns a long list of possible ingredients and explains each sip with only a few of them. Push too hard for few ingredients, and it under-measures the ones that are really there.

[Figure: Encode wide and sparse, decode, and pick a variant.]

_The SAE is wider than the layer, and only a few latents fire for each input._

### Play

**Try it.** Train an SAE in your browser on the five-features-in-two-neurons toy. Lower the sparsity penalty, then raise it.

#### Recover the five hidden features from two neurons

The data comes from the model in Features, Polysemanticity and Superposition: five features (cat, code, French, math, sports) packed into two neurons as a pentagon, each active about 8% of the time. The SAE sees only the two-neuron activations. Choose the dictionary size and the sparsity strength λ; it retrains (about 5,000 Adam steps) and shows what it learned.

Real training, fixed seed, computed in your browser. Dashed amber: the 5 true directions. Teal: learned decoder directions (red if dead, i.e. never active on 2,000 test inputs). “Recovered” = a live latent with cosine above 0.95 to a true direction.

##### What to notice

Reconstruction alone doesn’t pick out the true features: with λ near 0, almost any set of directions rebuilds a 2D vector, so error is tiny but the directions are arbitrary. Sparsity is what forces the SAE onto the real features. Too much sparsity, though, and error rises: the codes get shrunk (this lesson).

**Notice:** too little sparsity gives blurry mixtures, and too much kills latents and shrinks the rest. The right penalty recovers the five hidden directions.

## How it works

### How it works

#### In one breath

A sparse autoencoder (SAE) learns a dictionary much wider than the layer and rebuilds each activation from only a few of its latents, undoing superposition. Training trades reconstruction against sparsity. An L1 penalty makes active features come out too weak (shrinkage), so variants like Top-k, BatchTopK and JumpReLU separate whether a feature is on from how strong it is, and Matryoshka training gives cleaner features.

#### Neurons are mixed; we want the features back

Superposition stores more features than neurons as overlapping directions (Features, Polysemanticity and Superposition), so reading neurons gives polysemantic mush. If the activation _h_ is really a sparse sum of feature directions, _h ≈ Σ αi φi_, then the job is to find the φi and, for each input, the few αi that are on [p. 32](https://arxiv.org/pdf/2611.08438#page=32).

That job has a name and a long history: sparse dictionary learning. Neuroscientists in the 1990s decomposed natural images into sparse basis signals and found they resembled receptive fields in the visual cortex; signal processing learned overcomplete dictionaries for compression [p. 32](https://arxiv.org/pdf/2611.08438#page=32). The SAE is the version that scales to language models.

#### Find a dictionary and sparse codes

$$ {h} \approx {D}\,{z} \quad\text{and}\quad {\lVert z\rVert_0}\ \text{is small} $$

Survey Eq. 2 [p. 32](https://arxiv.org/pdf/2611.08438#page=32).

- **the activation**: h, one activation vector from the model, e.g. the residual stream at one token.

- **the dictionary**: D, a matrix whose columns are candidate feature directions. It has many more columns than h has dimensions: overcomplete.

- **the codes**: z, how much of each dictionary direction this input uses.

- **few active**: ‖z‖₀ counts the non-zero codes. We want it small: each input should use only a handful of directions.

Classical methods solve for _z_ separately for every input, which is far too slow for billions of tokens. An SAE instead trains an **encoder** to predict _z_ in one pass [p. 32](https://arxiv.org/pdf/2611.08438#page=32).

#### Encoder, decoder, and a loss with two parts

$$ {\mathcal{L}_{\text{SAE}}} = \mathbb{E}_{h_\ell}\Big[{\lVert h_\ell - D(z)\rVert_2^2} + {\lambda}\,{\lVert z\rVert_1}\Big],\quad {z = E(h_\ell)} $$

Survey §6.2 [p. 32](https://arxiv.org/pdf/2611.08438#page=32) · hover any symbol.

- **the loss**: What training minimises, averaged over many activations from the model.

- **rebuild it**: Reconstruction error: how far the SAE’s output D(z) is from the real activation hₗ.

- **how much sparsity**: λ sets how hard the SAE is pushed to use few features. Too small: mixed, dense codes. Too large: it starts dropping or shrinking real features.

- **sparsity penalty**: ‖z‖₁, the sum of code sizes. A stand-in for counting active features, because the count (L0) has no useful gradient.

- **the encoder**: z = E(hₗ) = ReLU(W_in hₗ + b_in): a wide layer, usually e× the model width (e is the expansion factor).

Two design details matter. **L1, not L0:** the count of active features has zero gradient almost everywhere, so training uses the sum of sizes instead. **Unit-norm decoder columns:** otherwise the SAE could cheat the L1 penalty by making codes tiny and decoder columns huge, which leaves the output unchanged but lowers the penalty without making anything sparser [p. 32](https://arxiv.org/pdf/2611.08438#page=32).

#### A latent is only a vector until someone labels it

An SAE outputs directions, not meanings. To label a latent, you look at the inputs that activate it most and ask what they share; automated pipelines do this with a language model, at the scale of millions of latents [p. 33](https://arxiv.org/pdf/2611.08438#page=33). In practice SAE latents fire on recurring patterns in text: semantic, functional or lexical [p. 33](https://arxiv.org/pdf/2611.08438#page=33).

Scale: the first large demonstration decomposed a 512-neuron MLP layer into tens of thousands of features, with raters finding them more interpretable than neurons [Bricken et al. 2023](https://transformer-circuits.pub/2023/monosemantic-features/). OpenAI later trained a 16-million-latent Top-k SAE on GPT-4 activations [Gao et al. 2025](https://arxiv.org/abs/2406.04093).

##### How SAEs are judged (survey)

- **Reconstruction:** how well it rebuilds activations.

- **Loss recovered:** swap the reconstruction into the model, and how much of the model’s performance survives?

- **Absorption:** how often a general feature fails to fire because a specific one stole its direction (SAE Failures and Alternatives).

[p. 33–34](https://arxiv.org/pdf/2611.08438#page=33)

#### The penalty taxes every active feature

L1 charges a cost proportional to how large each code is. So the cheapest solution under-reports strengths: a feature that is clearly present comes out weaker than it really is [p. 34](https://arxiv.org/pdf/2611.08438#page=34). Gao et al. name this directly: L1 is an imperfect approximation of L0 and “introduces a bias of shrinking all positive activations toward zero” [Gao et al. §2.3](https://arxiv.org/pdf/2406.04093#page=3).

##### Try it: measure shrinkage

Same five-feature data as this lesson. Train an L1 SAE at different λ, or a Top-k SAE, then show it one feature at a known strength and measure how much of that strength it rebuilds.

Real training in your browser (m = 8, fixed seed). Strength measured on single-feature inputs at 0.6, 0.8 and 1.0.

#### Separate “on or off” from “how much”

| Variant | How a code turns on | Fixes shrinkage? | Must tune |
|---|---|---|---|
| **L1 (standard)** | ReLU of the encoder output; L1 penalty | no | λ |
| **Gated** | a separate gate path decides on/off; another path sets magnitude | yes | λ |
| **JumpReLU** | each latent has its own learned threshold τi: below it, 0; above it, the full value | yes | λ, threshold init, estimator bandwidth |
| **Top-k** | keep the k largest codes, zero the rest; no penalty | yes | k |
| **Batch Top-k** | keep the largest B·k codes across a batch, so busy inputs get more and quiet ones fewer | yes | k |

Survey §6.3 and its trade-off table [pp. 34–35](https://arxiv.org/pdf/2611.08438#page=35). JumpReLU and Top-k are not differentiable everywhere; JumpReLU trains with straight-through estimators.

$$ {z_i} = \begin{cases}{a_i} & \text{if } {a_i} > {\tau_i}\\ 0 & \text{otherwise}\end{cases} $$

JumpReLU, survey §6.3 [p. 34](https://arxiv.org/pdf/2611.08438#page=34).

- **latent i’s value**: What latent i reports for this input.

- **pre-activation**: aᵢ, the encoder’s raw score for latent i: (W_in h + b_in)ᵢ.

- **its own threshold**: τᵢ, learned per latent. Below it the latent is off; above it, the full value passes through, so nothing is shrunk.

## In practice

### In practice

#### A rule of thumb, not a ranking

- **Tight compute, fast iteration:** Top-k. It removes λ from the search; reported k is commonly 32–150 [p. 36–37](https://arxiv.org/pdf/2611.08438#page=36).

- **Moderate tuning budget:** Gated, a better sparsity-vs-reconstruction trade-off than plain L1 [p. 37](https://arxiv.org/pdf/2611.08438#page=37).

- **Lots of tuning:** JumpReLU gave the strongest reconstruction at matched sparsity [p. 37](https://arxiv.org/pdf/2611.08438#page=37).

- **Open resources:** Gemma Scope (Gemma 2) and Gemma Scope 2 (Gemma 3) use JumpReLU; Llama Scope (Llama-3.1-8B) uses Top-k [p. 37](https://arxiv.org/pdf/2611.08438#page=37). Many can be browsed on Neuronpedia.

##### The catch

Better scores on the sparsity-vs-reconstruction trade-off “do not reliably translate into better downstream performance”. Benchmarks such as SAEBench rank variants differently depending on the metric, and seed-to-seed variation can be larger than the gap between variants [pp. 37–39, Table 5](https://arxiv.org/pdf/2611.08438#page=37).

Placement guidance from the survey’s Table 3: residual stream mid-layers are the most studied regime (expansion 4–8×); MLP outputs call for transcoders (Transcoders and Attribution Graphs); attention outputs are the least studied [p. 36](https://arxiv.org/pdf/2611.08438#page=36).

#### What the field learned in 2025

**Proxy metrics mislead.** SAEBench (ICML 2025) compared over 200 SAEs across eight architectures on eight metrics. Reconstruction and sparsity, the usual training metrics, did not reliably predict how useful the features were. Matryoshka SAEs, which train nested parts of the dictionary to work on their own, did slightly worse on those proxies but best on feature-disentanglement metrics in the usual sparsity range, and the advantage grew with scale.

**Open SAEs at scale.** Gemma Scope 2 (Google DeepMind, December 2025) released SAEs and transcoders for every layer of every Gemma 3 model, trained with the Matryoshka technique, which fixes certain flaws found in the first Gemma Scope.

**Not always the best tool.** In March 2025 the same DeepMind team reported that SAE-based probes did worse than plain linear probes at detecting harmful intent on unfamiliar prompts, and deprioritised basic SAE research. The next lesson covers when to use something else.

### The answer that sounds right

#### "Lower reconstruction error means a better SAE"

It sounds like the obvious metric, but SAEBench found reconstruction and sparsity don't reliably predict how useful the features are. An SAE can reconstruct well with features that are absorbed or split. Judge it on what you need: probing, disentanglement or how well interventions work.

## Say it

### How does a sparse autoencoder pull features out of activations, and how do you choose a variant?

#### The interviewer pushes further

Follow-up 1 of 3

Why must the SAE be wider than the layer?

Superposition means there are more features than neurons, so the dictionary needs more latents than dimensions to give each feature its own.

Follow-up 2 of 3

What's the spliced-in loss, and why check it?

Replace the activation with the SAE's reconstruction and measure the model's loss. A small reconstruction error can still hurt the model if it falls in directions the model uses.

Follow-up 3 of 3

What is a Matryoshka SAE?

An SAE trained so nested prefixes of its dictionary each reconstruct well on their own. Early latents learn general features, which reduces absorption.

#### The 30-second answer

A sparse autoencoder learns a dictionary much wider than the layer and rebuilds each activation from only a few latents, which undoes superposition. Training trades reconstruction against sparsity. With an L1 penalty, active features come out too weak, which is shrinkage, so newer variants like Top-k, BatchTopK and JumpReLU separate whether a feature is on from how strong it is, and Matryoshka training gives cleaner features. I'd check variance explained, the model's loss with the SAE spliced in, and whether the features help my actual task, because reconstruction alone doesn't predict that.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv [2611.08438](https://arxiv.org/abs/2611.08438)) and 5 more sources · checked 13 Nov 2026

#### Sources

- [Barez et al., Understanding AI from the Inside (survey, 2026)](https://arxiv.org/abs/2611.08438)

- [Bricken et al., Towards Monosemanticity (Anthropic, 2023)](https://transformer-circuits.pub/2023/monosemantic-features/index.html)

- [Gao et al., Scaling and Evaluating Sparse Autoencoders (2024)](https://arxiv.org/abs/2406.04093)

- [Rajamanoharan et al., Jumping Ahead: JumpReLU SAEs (2024)](https://arxiv.org/abs/2407.14435)

- [Karvonen et al., SAEBench (ICML 2025)](https://arxiv.org/abs/2503.09532)

- [Google DeepMind, Gemma Scope 2 (19 Dec 2025)](https://deepmind.google/blog/gemma-scope-2-helping-the-ai-safety-community-deepen-understanding-of-complex-language-model-behavior/)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
