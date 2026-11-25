# Steering Vectors

> How can you change a model's behaviour at inference time without retraining it?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/steering-vectors/
- Before this: Linear Representations and Universality (`ai-engineering/linear-representations`)
- Sources checked: 2026-11-13 · Text last changed: 2026-11-20 · Version: 757f449860

## Intuition

### The situation

Your chatbot is too sycophantic: it agrees with users even when they're wrong. Retraining will take weeks. Someone suggests adding a vector to the activations at inference time. The interviewer asks:

> How can you change a model's behaviour at inference time without retraining it?

### The idea

Think of a mixing desk during a live show. Steering doesn't rewrite the song; it pushes one slider while it plays. Push gently and the mood shifts. Push too far and the whole mix distorts.

[Figure: Find it, add it, watch the side effects.]

_The same vector can monitor a trait, steer it, or flag training data._

### Play

**Try it.** Add the refusal direction to a harmless request. Then remove it from a harmful one.

#### Add it, remove it, and watch what else moves

Arditi et al. build rℓ from refused vs. complied prompts and measure s = ⟨h, r⟩; adding r makes harmless prompts get refused, and projecting r out makes harmful prompts get answered [p. 81](https://arxiv.org/pdf/2611.08438#page=81) [arXiv 2406.11717](https://arxiv.org/abs/2406.11717). The toy below computes r from 200 toy prompts and applies it to 200 new ones. The model also does an unrelated task whose reading direction overlaps r a little.

Toy: 16-dimensional activations; refusal = 1 when ⟨h, r̂⟩ passes a threshold; unrelated task read along a direction with cosine 0.5 to r. Directional ablation: h − (h·r̂) r̂.

Localisation and steering meet here: measuring s across layers _locates_ refusal information; intervening along r _tests_ whether it changes behaviour. That is evidence of causal influence, not the full mechanism of refusal [p. 81](https://arxiv.org/pdf/2611.08438#page=81).

**Notice:** one direction switches refusal on and off. That's why steering is both a control knob and a jailbreak risk for open-weight models.

## How it works

### How it works

#### In one breath

Take the average activation for one behaviour minus the average for its opposite, and you get a steering vector. Adding a multiple of it during inference pushes the model towards the behaviour, with no retraining. The best-known case is refusal: one direction switches it on and off in many chat models. Steering is both a control knob and a causal test, and too much of it degrades quality.

#### Two averages and a subtraction

$$ {v_{\text{steer}}} = {\mathbb{E}[h_\ell\mid\text{preferred}]} - {\mathbb{E}[h_\ell\mid\text{unpreferred}]},\qquad {\tilde h_\ell = h_\ell + \alpha\, v_{\text{steer}}} $$

Survey §9.3 [pp. 80–81](https://arxiv.org/pdf/2611.08438#page=80). A trained probe’s weight vector can also serve as the direction (Probing Classifiers).

- **steering vector**: A direction in activation space at layer ℓ.

- **average when preferred**: Mean activation over prompts showing the behaviour we want to push towards (for refusal: prompts the model refuses).

- **average when not**: Mean activation over matched prompts without it.

- **apply it**: At inference, add α times the vector to the activation; α sets the strength and the sign sets the direction.

Simple as it is, it reliably changes refusal, helpfulness and style [p. 81](https://arxiv.org/pdf/2611.08438#page=81). It is the same move as Linear Representations and Universality’s king → queen lab, now on a behaviour instead of a word.

#### Beyond linear

- **Nonlinear**: steer linearly inside a kernel-PCA space and map back, or move along a low-dimensional manifold, since some concepts live on manifolds rather than lines [p. 81](https://arxiv.org/pdf/2611.08438#page=81).

- **Optimised**: learn the vector by maximising task performance or suppressing bad outputs under intervention. More flexible, much more compute than a difference of means [p. 81](https://arxiv.org/pdf/2611.08438#page=81).

- **As a test of features**: if an SAE or CLT feature is labelled “X”, steering along it should produce X. Benchmarks RAVEL, MIB and AxBench compare SAE features, difference-in-means and DAS this way [pp. 81–82](https://arxiv.org/pdf/2611.08438#page=82).

##### Limits: brittleness and opacity

A direction found on one distribution, model or task may not transfer. And behavioural success doesn’t make the mechanism transparent: the vector may move several features at once, interact nonlinearly, or use unintended pathways. Treat steering as evidence of causal influence, not as an explanation [p. 82](https://arxiv.org/pdf/2611.08438#page=82).

##### this lesson recap

1. Diffing compares features across models; “new” features may just be rotated old ones (9.1).

2. Localisation finds where effects concentrate; it is a first step, not an explanation (9.2).

3. Steering changes behaviour and tests causality, but can be brittle and opaque (9.3).

##### Next · the survey's training-dynamics chapters

Watching models learn: how features and circuits form during training.

##### Sources for this tab

- Survey §9.3, Figure 15, [arXiv 2611.08438](https://arxiv.org/abs/2611.08438), pp. 80–82.

- Arditi et al. (2024). _Refusal in Language Models Is Mediated by a Single Direction._ [arXiv 2406.11717](https://arxiv.org/abs/2406.11717).

## In practice

### In practice

#### Steering in 2024–2025

**Refusal.** Arditi et al. (NeurIPS 2024) found a single refusal direction in 13 open chat models up to 72B parameters. Projecting it out of the weights is a rank-one edit that removes refusals, a white-box jailbreak simpler than fine-tuning. They also showed adversarial suffixes work partly by suppressing this direction.

**Persona vectors.** Anthropic (August 2025) built an automated pipeline that turns a natural-language trait description, like "sycophantic", into a direction, tested on Qwen 2.5-7B and Llama-3.1-8B. The vectors can monitor drift towards a trait, steer it at inference, and flag training data likely to induce it. Steering against a trait at inference reduced it but could degrade general capabilities. Adding the vector during fine-tuning ("preventative steering") limited trait shifts while better preserving capability.

### The answer that sounds right

#### "Steering is a free fix, just turn up α"

It sounds cheap, but large α pushes activations off distribution and degrades quality, and persona-vector work found inference-time steering can degrade general capabilities. Evaluate the steered model on your normal benchmarks, not only the target behaviour, and consider steering during fine-tuning or fixing the data instead.

## Say it

### How can you change a model's behaviour at inference time without retraining it?

#### The interviewer pushes further

Follow-up 1 of 3

How do you choose the layer?

Sweep layers on held-out data. Middle layers usually work best: early ones haven't formed the concept, and late ones are too close to the output to change behaviour broadly.

Follow-up 2 of 3

Why is the refusal direction a safety concern?

For open-weight models, projecting it out of the weights is a cheap rank-one edit that removes refusals, a white-box jailbreak simpler than fine-tuning.

Follow-up 3 of 3

What is preventative steering?

Adding the trait vector during fine-tuning, so the model doesn't have to move towards the trait to fit the data. Anthropic reported it limited trait shifts with less capability loss than steering at inference.

#### The 30-second answer

I'd build a steering vector by taking mean activations on examples with the behaviour minus examples with its opposite, at one layer, and add a multiple of it during inference. It needs no retraining, and it's also a causal test that the direction matters. The best-known case is refusal: one direction controls it across many chat models. The risks are that too much strength hurts quality and the effect can spread to other behaviours, so I'd choose the layer and strength on held-out data and check general benchmarks too. For a lasting fix, I'd look at steering during fine-tuning or fixing the training data.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv [2611.08438](https://arxiv.org/abs/2611.08438)) and 5 more sources · checked 13 Nov 2026

#### Sources

- [Barez et al., Understanding AI from the Inside (survey, 2026)](https://arxiv.org/abs/2611.08438)

- [Turner et al., Steering Language Models with Activation Engineering (2023)](https://arxiv.org/abs/2308.10248)

- [Rimsky et al., Steering Llama 2 via Contrastive Activation Addition (2023)](https://arxiv.org/abs/2312.06681)

- [Arditi et al., Refusal in Language Models Is Mediated by a Single Direction (NeurIPS 2024)](https://arxiv.org/abs/2406.11717)

- [Chen et al., Persona Vectors: Monitoring and Controlling Character Traits (Anthropic, 2025)](https://arxiv.org/abs/2507.21509)

- [Anthropic, Persona vectors (1 Aug 2025)](https://www.anthropic.com/research/persona-vectors)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
