# Linear Representations and Universality

> What does it mean that concepts are linear inside a model, and when does that break?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/linear-representations/
- Before this: Features, Polysemanticity and Superposition (`ai-engineering/features-and-superposition`)

## Intuition

### The situation

A teammate found a "sentiment" direction with a probe and wants to add it during generation to make replies more positive. Another says directions inside a neural network don't mean anything. The interviewer asks:

> What does it mean that concepts are linear inside a model, and when does that break?

### The idea

Think of a mixing desk. Each slider is a direction: its position tells you how much of that sound is in the mix, and moving it changes the mix. Most concepts behave like sliders, but a few are dials that wrap around.

[Figure: Read, push, and know where it breaks.]

_One direction, used both to read a concept and to change it._

### Play

**Try it.** Start at "king" and push along the gender direction. Then push along royalty.

#### Subspace, measurement, intervention

Park et al. (2024) point out that “linear representation” is used in three different senses, and prove how they connect [Park et al. 2024, §1–2](https://arxiv.org/abs/2311.03658):

| Meaning | Claim | Tool it justifies |
|---|---|---|
| **Subspace** | All pairs that differ only in the concept differ along one shared direction: queen − king ∥ woman − man. | word-vector arithmetic |
| **Measurement** | The probability of the concept is logit-linear in the activation. | linear probes |
| **Intervention** | Adding a vector changes the concept and leaves other concepts alone. | steering vectors |

Their result: the subspace direction in the _output_ (unembedding) space acts as an ideal probe, and the matching direction in the _input_ space acts as a clean steering vector. In LLaMA-2, adding the male⇒female direction to “The prince matured and eventually became the” moves the top prediction from “king” to “queen”, without changing whether the next word is capitalised [Park et al. Fig. 5, Table 5](https://arxiv.org/pdf/2311.03658#page=7).

##### Try it: steer along one direction (3D)

A toy activation space with three concept directions: **male ⇒ female**, royalty, and capitalisation. The point starts at the context for “king”. Slide α to add the male ⇒ female direction and watch which word is closest. Drag the plot to rotate it.

Illustrative geometry with orthogonal concept directions, not a real model. Park et al. show the real directions are orthogonal only under the right inner product (section 3).

**Notice:** the same direction works for several words. That's the linear bet: one direction per concept, usable for both reading and editing.

## How it works

### How it works

#### In one breath

Many concepts behave like directions: project onto one to measure the concept, add along it to change it. That's the bet behind probes, steering and sparse autoencoders. It doesn't hold everywhere: some concepts are circles or need several directions, and which directions count as independent depends on the geometry you choose. Different models often learn similar structures, but similarity scores are fragile.

#### A concept is a direction you can read and push

The survey’s statement: a concept can be represented by a linear direction φ in activation space. Adding or subtracting (a multiple of) φ changes the related behaviour, and the projection φ⊤h(x) approximately measures how strongly the concept is present [p. 27](https://arxiv.org/pdf/2611.08438#page=27).

- **Strong version:** _every_ concept is best represented this way, so activations are approximately a sum of features: _h(x) ≈ Σ αi φi_.

- **Weak version:** only _some_ concepts are linear [p. 27](https://arxiv.org/pdf/2611.08438#page=27).

Why the field cares: if concepts are directions, the toolkit is just linear algebra. You can find them, measure them, scale them and add them back. Probes, steering vectors and sparse autoencoders all assume this [p. 27](https://arxiv.org/pdf/2611.08438#page=27).

#### “Orthogonal” depends on which inner product you use

Cosine similarity and projection need an inner product, and nothing in training picks one out. Any invertible linear change to the representation (with the inverse applied on the other side) leaves the model’s outputs unchanged, so the plain Euclidean dot product has no special claim to be meaningful [Park et al. §3](https://arxiv.org/pdf/2311.03658#page=4).

Park et al. propose a causal inner product under which concepts that can vary independently (language and gender, say) come out orthogonal. In practice it is estimated from the covariance of the unembedding vectors. In LLaMA-2 the ordinary Euclidean product happened to work reasonably well; in Gemma-2B it did not, while the causal one still did [Park et al. App. D.2](https://arxiv.org/pdf/2311.03658#page=17). When a paper reports a cosine between two feature directions, ask which inner product it used.

#### Only an element-wise operation makes the axes special

Inside an MLP, the nonlinearity (ReLU, GELU) acts on each neuron _separately_, so the coordinate axes are computationally meaningful: a privileged basis. In the residual stream, nothing acts on coordinates one at a time. Rotate the axes, apply the opposite rotation to the reading and writing weights, and the model computes exactly the same thing: a non-privileged basis [p. 27–28, Fig. 4](https://arxiv.org/pdf/2611.08438#page=28).

Consequence: in a privileged basis a single neuron _can_ be a meaningful feature. In a non-privileged one, features can point anywhere and need methods that look for directions [p. 27](https://arxiv.org/pdf/2611.08438#page=27).

##### Try it: rotate the basis and see what changes

An activation vector passes through a layer. We rotate the coordinate system by θ, apply the layer, and rotate back. If the axes don’t matter, the output shouldn’t change.

#### Same algorithm, or same representation?

The survey: models trained independently on similar tasks tend to develop similar representations or algorithms, often approximating a canonical form set by the task. How much depends on size, architecture and data [p. 31](https://arxiv.org/pdf/2611.08438#page=31).

| | Weak universality | Strong universality |
|---|---|---|
| **Claim** | Models converge on the same algorithms and computational patterns, possibly encoded differently | The representations themselves converge to a shared canonical form |
| **Evidence** | Recurring attention patterns, features and circuits across models and scales (induction heads, curve detectors, arithmetic circuits) | Representational similarity metrics; recent studies find these results fragile |
| **Status** | reasonably supported | less supported |

Survey §5.4 [p. 31](https://arxiv.org/pdf/2611.08438#page=31). Divergence can come from differences in architecture, data or the optimisation path.

#### Compare geometry, not neurons

You cannot just match neuron 7 in model A with neuron 7 in model B: there is no reason their axes line up, and in a non-privileged space (this lesson) the axes mean nothing anyway. So similarity metrics compare **geometry**, meaning how each model arranges the same inputs relative to each other. Examples are CKA (centred kernel alignment), SVCCA, and mutual nearest neighbours [Huh et al. §2](https://arxiv.org/pdf/2405.07987#page=2).

##### Try it: one model, rotated and noisy

Model B is model A’s representation of the same 30 inputs, rotated, with some noise added. Three ways of measuring similarity are shown. Watch them disagree.

30 points in 3 clusters (fixed seed), shown in their first two coordinates. Neuron matching = average correlation of neuron i in A with neuron i in B. CKA = linear centred kernel alignment. Mutual k-NN = share of each point’s 3 nearest neighbours that are the same in both models. All computed in your browser.

That is the fragility the survey points to: “are these models the same?” depends on which metric you use [p. 31](https://arxiv.org/pdf/2611.08438#page=31). Even the authors of the Platonic representation paper report that CKA showed only a very weak trend in their data, which is partly why they used nearest neighbours instead [Huh et al. App. A](https://arxiv.org/pdf/2405.07987#page=18).

## In practice

### In practice

#### Evidence for the weak version, not the strong one

##### Support

Linear probes work across many models and concepts; steering along single directions changes behaviour; sparse autoencoders recover linearly accessible, steerable features at scale [p. 27](https://arxiv.org/pdf/2611.08438#page=27).

##### Counterexamples

Nonlinear feature interactions; algorithms that rely on nonlinear transformations (the clock-like modular-addition circuits); features spread across several interacting subspaces; circles such as days of the week (Features, Polysemanticity and Superposition) [p. 27](https://arxiv.org/pdf/2611.08438#page=27) [Engels et al.](https://arxiv.org/abs/2405.14860). Some argue features may not exist as explicit objects at all, but emerge from circuit dynamics [p. 27–28](https://arxiv.org/pdf/2611.08438#page=28).

The survey’s verdict: the hypothesis is “best viewed as a useful approximation that holds in some settings, rather than as a universal law” [p. 28](https://arxiv.org/pdf/2611.08438#page=28).

#### Does what we learn about one model transfer?

If strong universality holds, fine-grained mechanistic findings and the tools built on them transfer between models. If only weak universality holds, findings may stay tied to a model family or task. Then even a _complete_ mechanistic understanding of one model might not carry over to the next [p. 31](https://arxiv.org/pdf/2611.08438#page=31). That makes universality a quiet assumption behind every research orientation in Why Look Inside a Model?: it decides whether interpretability can keep up with new models or has to start again for each one.

#### Single directions that control behaviour

The strongest recent evidence for the linear picture is behavioural. Arditi et al. (NeurIPS 2024) found that refusal is mediated by one direction in the residual stream across 13 open chat models up to 72B parameters: remove it and the model stops refusing harmful requests, add it and the model refuses harmless ones. Anthropic's persona vectors (August 2025) find directions for traits such as sycophancy and use them to monitor and steer models.

The counter-evidence is also real: some features are multi-dimensional, like the circles for days and months (Engels et al., 2024). So a direction is a good first hypothesis, and an intervention is how you check it.

### The answer that sounds right

#### "The probe found a direction, so adding it will steer"

It sounds like the same thing, but a probe finds whatever direction best separates the labels, which can be a correlated feature the model never uses. Steering needs the direction the model reads. Test it: if adding the direction doesn't change behaviour, it's a readout, not a control.

## Say it

### What does it mean that concepts are linear inside a model, and when does that break?

#### The interviewer pushes further

Follow-up 1 of 3

What is a privileged basis?

Where an elementwise operation like ReLU acts, the neuron axes become special, so single neurons can mean something. The residual stream has no such operation, so its axes are arbitrary.

Follow-up 2 of 3

What's weak versus strong universality?

Weak: different models learn similar algorithms. Strong: they learn the same representations. Recurring circuits support the weak version; the strong one rests on similarity metrics that depend on how you measure.

Follow-up 3 of 3

Why does the inner product matter?

Two directions can look orthogonal under the plain dot product but not under the geometry the model uses for its outputs, so whether two concepts are independent depends on that choice.

#### The 30-second answer

The linear representation hypothesis says many concepts are directions in activation space. Projecting onto the direction measures the concept, and adding along it changes it, which is what probes, steering and sparse autoencoders rely on. There's good evidence, for example a single refusal direction in many chat models. But it isn't universal: days of the week sit on a circle, some concepts need a subspace, and a direction that separates labels isn't always the one the model uses. So I'd validate any direction with an intervention.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv [2611.08438](https://arxiv.org/abs/2611.08438)) and 5 more sources · checked 13 Nov 2026

#### Sources

- [Barez et al., Understanding AI from the Inside (survey, 2026)](https://arxiv.org/abs/2611.08438)

- [Park et al., The Linear Representation Hypothesis and the Geometry of LLMs (2023)](https://arxiv.org/abs/2311.03658)

- [Arditi et al., Refusal in Language Models Is Mediated by a Single Direction (NeurIPS 2024)](https://arxiv.org/abs/2406.11717)

- [Chen et al., Persona Vectors: Monitoring and Controlling Character Traits (Anthropic, 2025)](https://arxiv.org/abs/2507.21509)

- [Engels et al., Not All Language Model Features Are One-Dimensionally Linear (2024)](https://arxiv.org/abs/2405.14860)

- [Huh et al., The Platonic Representation Hypothesis (2024)](https://arxiv.org/abs/2405.07987)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
