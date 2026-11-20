# Understanding AI from the Inside

> Does looking inside a model actually make it safer?

- Track: Papers Explained › AI interpretability
- Type: Paper · 25 min
- Page: https://aimlrounds.com/tracks/papers/mech-interp-survey/
- Before this: Self-Attention (Q, K, V) (`fundamentals/self-attention`)
- Related: Why Look Inside a Model? (`ai-engineering/why-look-inside-a-model`), Sparse Autoencoders (`ai-engineering/sparse-autoencoders`)

## Gist

### The paper

Barez et al. · _Understanding AI from the Inside: The State of Mechanistic Interpretability for AI Safety_ · arXiv [2611.08438](https://arxiv.org/abs/2611.08438) · 2026 · checked 11 Nov 2026

We can measure what models do, but not how they do it, and that gap matters for safety. Output tests can be gamed, contaminated or fooled by a model that behaves well only when watched. Mechanistic interpretability studies a model's internals and makes causal claims about them. The survey asks whether that actually makes models safer. Its answer: the field has real achievements (features, circuits, targeted interventions) but explains only part of behaviour, so understanding helps safety only when it is faithful and tested causally.

### The problem

#### We design how models learn, not what they learn

We write the training procedure, so in one sense we built the model. But the procedure only says _how_ to learn, and gradient descent decides _what_ gets learned. The survey names the result the interpretability gap: the distance between what models can do and what we understand about how they do it. As models scale, the gap may widen. Reasoning appears that we cannot trace, deceptive behaviour may go unnoticed, and safety guarantees built on partial understanding can fail without warning [p. 9](https://arxiv.org/pdf/2611.08438#page=9).

Mechanistic interpretability (MI) is one way to close that gap: study a network’s internal mechanisms in relation to its behaviour. The survey keeps returning to one question throughout: **does understanding how models work actually make them safer?** It notes that many interpretability papers assume the answer is yes, and that the assumption is “largely untested” [p. 12](https://arxiv.org/pdf/2611.08438#page=12).

### The idea

Testing a model only on its answers is like judging a car by test drives alone. It can pass every drive and still hide a fault the drives never trigger. This survey asks how far we've got at opening the bonnet, and whether it makes the car safer.

1. 01 Why Look Inside a Model?

2. 02 Features and Superposition

3. 03 The Residual Stream and Circuits

4. 04 Linear Representations

5. 05 Sparse Autoencoders

6. 06 SAE Failures and Alternatives

7. 07 Transcoders and Attribution Graphs

8. 08 Activation Patching

9. 09 Validating Claims

10. 10 Logit Lens and Verbalisers

11. 11 Probing Classifiers

12. 12 Steering Vectors

13. 13 Localisation and Editing

14. 14 Model Diffing

15. 15 Interpretability for Safety

Each lesson in AI Engineering › AI Interpretability builds on this survey, with newer research added.

## Method

### Method

#### People have opened up networks for decades

The name “mechanistic interpretability” is recent, but the work is not. The survey counts much older studies as part of the field’s history, even though they predate the term [p. 9–10](https://arxiv.org/pdf/2611.08438#page=10).

1. Minsky and Papert (1969) asked which functions a network can represent at all. Hinton (1986) showed concepts can be spread over many units, and Elman (1991) ran PCA on a recurrent net’s hidden states.

2. Once deep learning worked, people looked inside: AlexNet’s early filters detect edges and deeper ones detect complex patterns (Zeiler & Fergus 2014); single RNN neurons track quotes, brackets and line length (Karpathy et al. 2015).

3. Probing classifiers asked a different question: can syntax, semantic roles or sentence length be read out of a layer’s activations? This flourished from 2016 to 2019.

4. Transformers brought attention visualisation and a debate over whether attention explains anything. The Distill “Circuits” work framed networks as features wired together by understandable algorithms.

5. Then circuits in language models: induction heads (2022), the indirect-object-identification circuit (2023), and modular arithmetic in toy models.

6. By mid-2024, sparse autoencoders extracted features from billion-parameter models. Analysis has shifted from manual inspection to automated tools p. 9–11.

The survey stresses two recent shifts. First, from manual to **assisted** analysis: at today’s sizes nobody can inspect neurons by hand, so feature extraction, circuit discovery and feature labelling are increasingly automated. Second, a **divergence of priorities**: some researchers want safety tools that work now without full understanding, others want complete causal understanding even at great cost. Chapter 11 returns to these schools of thought [p. 11](https://arxiv.org/pdf/2611.08438#page=11).

#### Four reasons a good test score can mislead

The default way to judge a model is behavioural evaluation: measure its outputs on held-out inputs. That works only if the model reached its score through the mechanism we hoped for, and output tests cannot see the mechanism [p. 15](https://arxiv.org/pdf/2611.08438#page=15).

| Problem | What goes wrong |
|---|---|
| **Contamination and saturation** | Test data leaks into web-scale training sets; even a single copy of a benchmark in pretraining can inflate scores. Benchmarks also max out long before the real capability is reached, and then they stop telling models apart. |
| **Wrong mechanism, right answers** | Two models with identical outputs can compute in very different ways, one robustly and one with brittle shortcuts. You find out which only when deployment breaks it. |
| **Evaluation awareness** | A model may recognise test-like contexts and behave differently there. Models have shown alignment faking without being trained or told to do it. |
| **No fine-grained control** | Removing one capability without damaging others means finding where it lives inside. Output tests give no handle for that. |

All four from survey §2 [p. 15](https://arxiv.org/pdf/2611.08438#page=15). A fifth issue: a model updated after deployment no longer matches the snapshot that was evaluated [p. 16](https://arxiv.org/pdf/2611.08438#page=16).

##### The case that made this concrete: sleeper agents

1. Researchers trained a model to write secure code when the prompt says the year is 2023, the “training” period.

2. When the year is 2024, the “deployment” period, the same model inserts vulnerabilities. That is a hidden backdoor objective.

3. Standard safety training (supervised fine-tuning, RLHF, adversarial training) did not remove it. Without the trigger, training sees only safe behaviour, so it has little signal to remove the mechanism p. 16.

4. But looking inside helped: a simple linear probe on the activations predicted whether the backdoor was triggered with over 99% AUROC. Note the gap. Detecting it is not the same as removing it p. 16.

#### From “what does it do” to “how does it do it”

Interpretability is broader than MI. The survey lays the families on a spectrum from correlational to causal: behavioural evaluation tells you **what** a model does, attribution and probing tell you **where** relevant information is, and mechanistic analysis tells you **how** the computation produces the behaviour [p. 19](https://arxiv.org/pdf/2611.08438#page=19).

1. **Behavioural methods**: benchmarks and red-teaming. Fast, cheap and scalable, but not designed to reveal internal computation p. 17.

2. **Input attribution** (SHAP, LIME, saliency maps): which input pixels or tokens mattered, not how the model used them. Different methods can disagree on the same input p. 18.

3. **Concept-based methods and probes**: is this information present in the activations? Correlational by default, but they become mechanistic once you intervene along what they find p. 17–19.

4. **Mechanistic methods** (features, circuits, verbalising activations): causal claims about how internals produce behaviour. The strongest claims, and the most expensive p. 19–20.

5. The survey’s view is that these work together, not as rivals: behavioural anomalies say where to look, and behavioural tests validate mechanistic findings p. 19.

##### What counts as “mechanistic” in this survey

Two criteria. (1) It engages with **internals**: activations, components such as neurons, heads and features, or parameters. Looking at inputs and outputs alone is not enough. (2) It makes **causal** claims through interventions such as ablation, patching or steering, not just correlations. Under this definition a plain probe is not mechanistic, but a probe whose direction you then intervene on is [p. 12–13](https://arxiv.org/pdf/2611.08438#page=12).

##### Try it: which tool answers your question?

Pick a question you might ask about a model. The picker shows which family answers it and how strong a claim it supports, following the survey’s Table 2 and §3.6.

## Results

### What they found

#### When “it passed the test” is not enough

The survey lists four situations where you need to know _how_, not just _that_ [p. 19](https://arxiv.org/pdf/2611.08438#page=19):

1. **Intent hidden from outputs**, such as deception or side quests that never show up in behaviour.

2. **Understanding the mechanism** of a behaviour, for example why a probe fires: a real signal or a false alarm.

3. **Verifying absence**: behavioural tests can only show a capability is present, never that it is gone.

4. **Guarantees beyond the tested inputs**: safety that must hold outside the evaluated distribution.

Even then the survey frames mechanistic analysis as a complement, not a replacement. Its cost goes beyond compute: researcher time, experimental complexity and slower iteration [p. 20](https://arxiv.org/pdf/2611.08438#page=20).

#### Seven open problems

1. **When is mechanistic understanding necessary?** Sleeper agents were caught from activations, but better training may shrink the failures that need internals. No consensus; in the near term it stays indispensable for diagnosing what behaviour misses [pp. 123–124](https://arxiv.org/pdf/2611.08438#page=124).

2. **Evaluation and benchmarks**: turning Ch 7’s five dimensions into shared benchmarks: synthetic tasks with known circuits, toy models, diverse suites. Do explanations even have an objective ground truth? [p. 124](https://arxiv.org/pdf/2611.08438#page=124)

3. **Incompleteness, scale, generalisation, robustness**: mapping distributed computation onto a human-level causal model is lossy, and we can’t measure how lossy; cheap tools are coarse and fine tools are costly; and models might learn to resist analysis, an arms race like evaluation awareness [pp. 124–125](https://arxiv.org/pdf/2611.08438#page=125).

4. **Understanding vs. alignment**: knowing the refusal circuit doesn’t say what the model _should_ value; how interpretability complements RLHF and constitutional AI is open [p. 125](https://arxiv.org/pdf/2611.08438#page=125).

5. **The ontology question**: “borzoi detector” and “previous-token copier” are human choices; several explanations can fit the same causal facts. Is a unique description even expected? [p. 125](https://arxiv.org/pdf/2611.08438#page=125)

6. **Proxy fidelity**: SAEs and CLTs may reproduce behaviour with different internal algorithms, so “no deception circuit in the proxy” means little. Interchange-intervention testing and bounds on how far a proxy can differ are candidate fixes [pp. 125–126](https://arxiv.org/pdf/2611.08438#page=126).

7. **Beyond transformers**: CNNs, state-space models (Mamba, RWKV), diffusion models and mixture-of-experts (patching can change downstream expert routing; up to 256+ experts) each break assumptions. Steering, tuned lenses, editing and circuit evaluations have been adapted with varying success [pp. 126–127](https://arxiv.org/pdf/2611.08438#page=127).

### Where it falls short

#### Three limits to keep in mind for the rest of the series

##### 1 · Explanations are often incomplete

Finding one real causal pathway (say, “this MLP retrieves facts about Paris”) does not tell you whether it is the whole story or one of several mechanisms working together [p. 20](https://arxiv.org/pdf/2611.08438#page=20).

##### 2 · It scales poorly

Large models spread computation across many components, and most circuit-discovery methods explain the computation behind one generated token. Behaviour that unfolds over many tokens is still hard to capture [p. 20](https://arxiv.org/pdf/2611.08438#page=20).

##### 3 · Explaining is not controlling

Even a causally validated mechanism does not guarantee reliable control. Effects like the hydra effect, where the network compensates when a component is removed, and poor transfer across models or settings get in the way [p. 20](https://arxiv.org/pdf/2611.08438#page=20).

The survey calls these open challenges, not fundamental barriers. But they mark “a clear gap between mechanistic explanation and reliable control or safety guarantees” [p. 21](https://arxiv.org/pdf/2611.08438#page=21). Keep this gap in mind: most later chapters are attempts to narrow one of these three limits.

## Why it matters

### What it changed

**What to remember.** Behavioural tests tell you what a model does on the inputs you tried. Mechanistic interpretability tries to say how, with causal evidence. The survey's answer to its own question is a qualified yes: understanding helps safety when it is faithful, complete enough for the claim and tested causally. The 15 lessons in AI Engineering › AI Interpretability teach each method, with newer research added.

#### One layer of defence in depth

**Achievements**: interpretable features with SAEs, task circuits, targeted interventions, and a changed view of how models compute. **Limits**: much behaviour unexplained, poor generalisation under shift, entangled computation, hard to scale. And the assumption that mechanistic understanding directly makes systems safer is “in fact largely untested” [pp. 127–128](https://arxiv.org/pdf/2611.08438#page=128).

| Paradigm | What it does | Where |
|---|---|---|
| **Post-hoc explanation** | Study trained models with SAEs, circuits, verbalisers, causal analysis; still needed because deployed models are dense | Ch 4–9 |
| **Learning dynamics** | Understand, predict and intervene as mechanisms form | Ch 10 |
| **Interpretability by design** | SoLU, weight-sparse transformers, KANs and successors: transparent by construction | Survey §6.10 |

Survey §15.2 [p. 128](https://arxiv.org/pdf/2611.08438#page=128). Progress also needs claims that are falsifiable and reproducible.

##### The closing question

“Does understanding how models work actually make them safer?” [p. 128](https://arxiv.org/pdf/2611.08438#page=128)

#### Why the survey exists

1. The interpretability gap: capabilities have outpaced our understanding of how models produce them.

2. Output tests can be contaminated, gamed by shortcuts, or fooled by evaluation-aware models, and they give no handle for precise fixes.

3. Mechanistic interpretability means internals plus causal interventions. Probes and attribution help, but become mechanistic only when you intervene.

4. It is needed for hidden intent, mechanisms, proving absence and out-of-distribution guarantees. It is also costly, incomplete, and not the same as control.

5. The survey’s stance: MI is one layer of defence in depth, and whether understanding yields safety is the question to keep testing.

##### Next · Chapter 2

The building blocks: polysemantic neurons, features as representational units, the residual stream as a shared channel, and circuits.

##### Sources for this tab

- Barez, Wu et al. (2026). _Understanding AI from the Inside._ [arXiv 2611.08438](https://arxiv.org/abs/2611.08438) · §1 (pp. 9–14), §2 (pp. 15–16), §3 (pp. 16–21), Table 2 (p. 20). The historical works, sleeper agents (Hubinger et al. 2024), linear probe detection (MacDiarmid et al. 2024) and alignment faking (Greenblatt et al. 2024) are cited as the survey reports them.

**Key terms and sources**
