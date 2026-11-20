# Probing Classifiers

> A probe detects a property from activations with 95% accuracy. What does that tell you, and what doesn't it?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/probing-classifiers/
- Before this: Linear Representations and Universality (`ai-engineering/linear-representations`)

## Intuition

### The situation

Your probe detects "the model is lying" from layer 30 with 95% accuracy on your test set. The product team wants to ship it as a deception monitor next week. The interviewer asks:

> A probe detects a property from activations with 95% accuracy. What does that tell you, and what doesn't it?

### The idea

A probe is like a metal detector on a beach. A beep tells you there's metal, not that anyone is using it, and a detector that's sensitive enough beeps at bottle caps. Digging is the causal test.

[Figure: Decodable, selective, and actually used.]

_Three questions to ask of any probe result._

### Play

**Try it.** Make the probe more powerful, and compare its accuracy on real and random labels.

#### Selectivity = real accuracy − control accuracy

Hewitt & Liang’s idea: give every word type a **random** label, fixed per type. Nothing in the activations encodes it, so any accuracy a probe gets is pure memorisation. Below, 30 word types, each with a fixed activation vector plus per-occurrence noise; the real property is linearly encoded. Test tokens are new occurrences of the same words.

Real computation in your browser: logistic regression (gradient descent) vs. 1-nearest-neighbour, 600 training and 600 test tokens, fixed seed.

The survey: high selectivity means the probe works because the representation encodes the property; low selectivity means we can’t rule out exploitation of spurious structure [p. 74](https://arxiv.org/pdf/2611.08438#page=74) [Hewitt & Liang 2019](https://arxiv.org/abs/1909.03368).

**Notice:** a powerful probe scores well even on random labels, because it memorises. Selectivity, the gap between the two, tells you what the activations really hold.

## How it works

### How it works

#### In one breath

A probe is a small classifier trained to predict a property from activations. High accuracy means the property is decodable, nothing more: the probe may ride a correlated feature, the model may never use it, and a powerful probe can learn the task itself. Control tasks measure memorisation, and amnesic probing or patching test whether the model uses the information.

#### A classifier on top of activations

A linear probe predicts ŷ = g(Wprobe hℓ + bprobe), with g the identity (regression) or softmax (classification), trained on labelled activations. It tests whether the property is **linearly accessible**; MLP probes test whether a nonlinear map can retrieve it [p. 72](https://arxiv.org/pdf/2611.08438#page=72). In the residual-stream picture (The Residual Stream and Circuits), a linear probe is just a learned reading direction.

##### The probe causality problem (three ways accuracy misleads)

1. **Correlated features**: the probe may detect word frequency, which correlates with part of speech, instead of part of speech.

2. **Unused information**: later layers may never read the decoded property; it may be leftover from earlier processing.

3. **Probe capacity**: a sufficiently expressive probe can reach high accuracy by exploiting noise, even when the property isn’t there.

Survey [pp. 72–73](https://arxiv.org/pdf/2611.08438#page=72). For this reason, the survey says probing alone “does not, under our definition, constitute mechanistic interpretability research” [p. 73](https://arxiv.org/pdf/2611.08438#page=73).

#### “Can we extract it?” vs. “how easily?”

If only a very nonlinear probe succeeds, is the property encoded in a complex form, or is the probe computing it from other features? In the worst case a complex enough mapping can turn even a _randomly initialised_ network into the causal model you hoped for (Sutter et al. 2025) [p. 74](https://arxiv.org/pdf/2611.08438#page=74).

**Minimum description length (MDL) probes** (Voita & Titov 2020) score how efficiently a probe extracts the property, counting both accuracy and complexity: a property is “more encoded” if a simpler probe gets it [p. 74](https://arxiv.org/pdf/2611.08438#page=74).

##### Practical guidance (survey)

Prefer simple probes; compare against probes on random representations; consider MDL; and if a linear probe fails but an MLP probe succeeds, validate cautiously [p. 74](https://arxiv.org/pdf/2611.08438#page=74).

##### Next · 8.4

Making probes causal: erase what the probe found (amnesic probing) or patch it in, and when probing is the right tool.

##### Sources for this tab

- Survey §8.6.1–8.6.3, [arXiv 2611.08438](https://arxiv.org/abs/2611.08438), pp. 72–74.

- Hewitt & Liang (2019). _Designing and Interpreting Probes with Control Tasks._ [arXiv 1909.03368](https://arxiv.org/abs/1909.03368).

#### Erase the probe direction, see what breaks

$$ {\tilde h} = {h} - {\frac{h^\top w}{\|w\|^2}\,w} $$

Survey §8.6.4 [p. 75](https://arxiv.org/pdf/2611.08438#page=75). Elazar et al. (2021) used iterative nullspace projection (INLP) to remove a property more thoroughly [arXiv 2006.00995](https://arxiv.org/abs/2006.00995).

- **the edited activation**: What’s left after removing the property.

- **original activation**: The model’s activation.

- **its shadow on w**: The part of h lying along the probe direction w. Subtracting it makes the probe blind; then run the model on h̃ and measure the task.

Toy: 12-dimensional activations of 400 inputs with sentiment (used by the output) and word length (not used), plus noise. Probe directions = difference of class means. The “model” reads sentiment with a fixed readout; the backup variant also reads a nonlinear copy (stored in how far the activation sits along a second direction, not which way).

That last case is the survey’s warning: “unchanged performance does not establish that the information is unused”, because redundant representations or other pathways can keep the behaviour going. Erasure can also leave residue or damage other concepts [p. 75](https://arxiv.org/pdf/2611.08438#page=75).

#### Copy the probe-subspace part across inputs

Take x1 with property P and x2 without. At a chosen spot (say the last token’s residual stream at a middle layer), copy the part of x1’s activation inside the probe subspace into x2’s run. If x2’s output shifts towards P, the model uses that information. Amnesic probing tests _removal_; this tests _sufficiency_. Its catch is that you must pick the layer, component and position, and that choice can confound the result [p. 75](https://arxiv.org/pdf/2611.08438#page=75). It is the same interchange intervention as in Validating Interpretability Claims, applied to a probe direction.

Pairing probes with other attribution tools doesn’t rescue them: saliency maps can highlight inputs the model ignores, attention weights correlate weakly with causal importance, and attribution methods often disagree [p. 75](https://arxiv.org/pdf/2611.08438#page=75).

## In practice

### In practice

#### When to probe

| Appropriate | Inappropriate |
|---|---|
| Showing information is present (“P is encoded”) | Claiming the model uses P |
| Comparing encoding strength across layers | Concluding P is absent from low probe accuracy |
| Auditing for encoded sensitive information | Claiming mechanistic understanding from probes alone |
| Generating hypotheses for causal tests | Using probe results as evidence for causal hypotheses |
| Early detection or triage | Judging alignment or safety from probe results |

Survey Table 11 [p. 76](https://arxiv.org/pdf/2611.08438#page=76). Standards: report control tasks; use minimal probes; test causality; show layer-wise trends, not just the peak; separate encoding from use; report stability across seeds and splits [p. 76](https://arxiv.org/pdf/2611.08438#page=76).

#### Catching a sleeper agent with one direction

A sleeper-agent model behaves normally when the year is 2023 but switches to a hidden harmful policy when it sees 2024. MacDiarmid et al. built a detector from a _difference of means_ over contrast pairs that don’t even mention the trigger (“Are you doing something dangerous? … yes” vs. “… no”): uℓ = E[hℓ | true] − E[hℓ | false]. Projecting new activations onto uℓ flagged triggered inputs with **AUROC above 99%** [pp. 76–77](https://arxiv.org/pdf/2611.08438#page=77).

Why so easy: triggered and normal activations form two clusters far apart, so they separate along many directions. And the goal is detection, not mechanism, which is exactly a use Table 11 allows [p. 77](https://arxiv.org/pdf/2611.08438#page=77).

##### this lesson recap

1. Lenses decode a layer into tokens: logit (raw), tuned (trained to the end), Jacobian (what it pushes towards) (8.1).

2. Patchscopes and LatentQA let a model verbalise activations, with out-of-distribution and shortcut risks (8.2).

3. Probes show decodability; use control tasks and simple probes (8.3).

4. Intervene to test use; probe for detection and hypotheses (8.4).

All of these reveal what _can be decoded_, not whether the model uses it [p. 77](https://arxiv.org/pdf/2611.08438#page=77).

##### Next · Steering Vectors

Comparing models (diffing), locating knowledge, and steering behaviour with representations.

##### Sources for this tab

- Survey §8.6.4–8.6.7, [arXiv 2611.08438](https://arxiv.org/abs/2611.08438), pp. 74–77.

- Elazar et al. (2021). _Amnesic Probing._ [arXiv 2006.00995](https://arxiv.org/abs/2006.00995).

- MacDiarmid et al. (2024). _Simple probes can catch sleeper agents._ [Anthropic](https://www.anthropic.com/research/probes-catch-sleeper-agents).

#### Deception probes, 2024–2025

**Planted backdoors.** Anthropic's "defection probes" (April 2024) detected when its own sleeper-agent models were about to act on a hidden goal with AUROC above 99%, using generic contrast pairs that didn't mention the trigger. These were backdoors Anthropic planted, so they may be unusually easy to spot.

**More realistic deception.** Apollo Research (ICML 2025) trained probes on Llama-3.3-70B and tested them on scenarios like hiding insider trading. They reached AUROC 0.96–0.999 and caught 95–99% of deceptive responses at a 1% false-positive rate on ordinary chat. But the probes were partly sensitive to whether the scenario was _about_ deception, they performed roughly on par with a black-box GPT-4o baseline, and the authors judged them not yet robust enough as a defence.

**Simple wins.** Google DeepMind found plain linear probes beat SAE-based probes at detecting harmful intent on unfamiliar prompts (2025).

### The answer that sounds right

#### "95% accuracy, ship it as a monitor"

It sounds strong, but a probe can track a correlate, like whether the text talks about lying, rather than lying itself. Apollo's deception probes scored highly yet partly tracked the topic. Test on realistic, unfamiliar cases at the false-positive rate you can afford, and against a black-box baseline.

## Say it

### A probe detects a property from activations with 95% accuracy. What does that tell you, and what doesn't it?

#### The interviewer pushes further

Follow-up 1 of 3

What's a control task?

The same probe trained on random but consistent labels for the same inputs. High control accuracy means the probe can memorise, so real accuracy alone overstates what the representation holds.

Follow-up 2 of 3

What does amnesic probing do?

It removes the probe's direction from the activations and checks whether the model's task performance drops. If it doesn't, the model wasn't using that information, or has other copies.

Follow-up 3 of 3

Why did simple probes catch sleeper agents so well?

The planted backdoor creates a very distinct internal state, so even generic contrast pairs separate it. Deception that arises naturally may be far subtler.

#### The 30-second answer

High probe accuracy means the property is linearly decodable from the activations, nothing more. The probe may be riding a correlated feature, the model may never use it, and a powerful probe can learn the task itself. So I'd keep the probe linear, compare it with a control task to get selectivity, and test whether the model uses the direction with amnesic probing or patching. For a deception monitor, I'd test on realistic out-of-distribution cases at a fixed low false-positive rate and against a black-box baseline, because published deception probes look strong in-distribution but partly track the topic of deception.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv [2611.08438](https://arxiv.org/abs/2611.08438)) and 5 more sources · checked 13 Nov 2026

#### Sources

- [Barez et al., Understanding AI from the Inside (survey, 2026)](https://arxiv.org/abs/2611.08438)

- [Hewitt and Liang, Designing and Interpreting Probes with Control Tasks (2019)](https://arxiv.org/abs/1909.03368)

- [Elazar et al., Amnesic Probing (2021)](https://arxiv.org/abs/2006.00995)

- [Anthropic, Simple probes can catch sleeper agents (23 Apr 2024)](https://www.anthropic.com/research/probes-catch-sleeper-agents)

- [Goldowsky-Dill et al., Detecting Strategic Deception with Linear Probes (ICML 2025)](https://arxiv.org/abs/2502.03407)

- [Kantamneni et al., Are Sparse Autoencoders Useful? A Case Study in Sparse Probing (2025)](https://arxiv.org/abs/2502.16681)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
