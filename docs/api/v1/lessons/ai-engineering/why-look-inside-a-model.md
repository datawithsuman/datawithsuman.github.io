# Why Look Inside a Model?

> Your model passes every safety evaluation. Why might that not be enough, and what does interpretability add?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/ai-engineering/why-look-inside-a-model/
- Before this: Self-Attention (Q, K, V) (`fundamentals/self-attention`)
- Sources checked: 2026-11-13 · Text last changed: 2026-11-20 · Version: dbb9d3c489

## Intuition

### The situation

Your team's new model passes every red-team and safety test. A reviewer asks how you know it isn't behaving well just because it can tell it's being tested. The interviewer asks:

> Your model passes every safety evaluation. Why might that not be enough, and what does interpretability add?

### The idea

Testing a model only on its answers is like judging a car by test drives. It can pass every drive and still hide a fault the drives never trigger. Interpretability opens the bonnet and checks the parts.

[Figure: Three ways to look. Behaviour, probing, mechanism.]

_From correlational and cheap to causal and costly. They complement each other._

### Play

**Try it.** Pick a question you might ask about a model, and see which family of methods can answer it.

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

**Notice:** only mechanistic analysis claims how the model computes, and it's also the most expensive. Pick the cheapest method that answers your question.

## How it works

### How it works

#### In one breath

Output tests show what a model does on the inputs you tried, not how it does it. They can be gamed, contaminated by training data, or passed by a model that recognises it's being tested. Mechanistic interpretability studies the internals and makes causal claims about them, and frontier labs now use it alongside behavioural tests.

#### We design how models learn, not what they learn

We write the training procedure, so in one sense we built the model. But the procedure only says _how_ to learn, and gradient descent decides _what_ gets learned. The survey names the result the interpretability gap: the distance between what models can do and what we understand about how they do it. As models scale, the gap may widen. Reasoning appears that we cannot trace, deceptive behaviour may go unnoticed, and safety guarantees built on partial understanding can fail without warning [p. 9](https://arxiv.org/pdf/2611.08438#page=9).

Mechanistic interpretability (MI) is one way to close that gap: study a network’s internal mechanisms in relation to its behaviour. The survey keeps returning to one question throughout: **does understanding how models work actually make them safer?** It notes that many interpretability papers assume the answer is yes, and that the assumption is “largely untested” [p. 12](https://arxiv.org/pdf/2611.08438#page=12).

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

#### Pick proxy tasks that matter for safety, use any tool

Full mechanistic understanding isn’t required for impact, so work on concrete proxy tasks that can be studied on today’s models, using any method, internal or not [p. 102](https://arxiv.org/pdf/2611.08438#page=102).

- **Evaluation awareness in Claude Sonnet 4.5**: the model behaved differently when it detected it was being evaluated. A steering vector that suppresses this awareness let researchers test its actual behaviour, without fully explaining the mechanism [p. 102](https://arxiv.org/pdf/2611.08438#page=102).

- **Auditing games**: a model was fine-tuned with a hidden goal, and blinded teams tried to find it, comparing techniques [pp. 102–103](https://arxiv.org/pdf/2611.08438#page=103).

Tools: steering vectors (Steering Vectors), probes (Probing Classifiers), behavioural monitoring (including reading chain-of-thought), prompting as a black-box baseline. Weak spot: these don’t, and aren’t meant to, explain how the behaviour is implemented [p. 103](https://arxiv.org/pdf/2611.08438#page=103).

#### Only full understanding can rule out hidden failures

Treat interpretability as a science: reverse-engineer the model into a transparent, predictive theory of its algorithms. Make progress by metrics: start loose, improve, tighten. Two example metrics: **feature quality** (explanations faithful and simulatable) and **circuit faithfulness** (necessary and sufficient under causal tests like causal scrubbing, with no performance loss) [p. 103](https://arxiv.org/pdf/2611.08438#page=103).

Weak spot: cost. Fine-grained analysis of frontier models is expensive, sometimes intractable, and tools fall far short of the needed coverage. Interpretability-by-design models (Transcoders and Attribution Graphs) blur the line: an engineering route to the ambitious goal [p. 103](https://arxiv.org/pdf/2611.08438#page=103).

## In practice

### In practice

#### When “it passed the test” is not enough

The survey lists four situations where you need to know _how_, not just _that_ [p. 19](https://arxiv.org/pdf/2611.08438#page=19):

1. **Intent hidden from outputs**, such as deception or side quests that never show up in behaviour.

2. **Understanding the mechanism** of a behaviour, for example why a probe fires: a real signal or a false alarm.

3. **Verifying absence**: behavioural tests can only show a capability is present, never that it is gone.

4. **Guarantees beyond the tested inputs**: safety that must hold outside the evaluated distribution.

Even then the survey frames mechanistic analysis as a complement, not a replacement. Its cost goes beyond compute: researcher time, experimental complexity and slower iteration [p. 20](https://arxiv.org/pdf/2611.08438#page=20).

#### Three limits to keep in mind for the rest of the series

##### 1 · Explanations are often incomplete

Finding one real causal pathway (say, “this MLP retrieves facts about Paris”) does not tell you whether it is the whole story or one of several mechanisms working together [p. 20](https://arxiv.org/pdf/2611.08438#page=20).

##### 2 · It scales poorly

Large models spread computation across many components, and most circuit-discovery methods explain the computation behind one generated token. Behaviour that unfolds over many tokens is still hard to capture [p. 20](https://arxiv.org/pdf/2611.08438#page=20).

##### 3 · Explaining is not controlling

Even a causally validated mechanism does not guarantee reliable control. Effects like the hydra effect, where the network compensates when a component is removed, and poor transfer across models or settings get in the way [p. 20](https://arxiv.org/pdf/2611.08438#page=20).

The survey calls these open challenges, not fundamental barriers. But they mark “a clear gap between mechanistic explanation and reliable control or safety guarantees” [p. 21](https://arxiv.org/pdf/2611.08438#page=21). Keep this gap in mind: most later chapters are attempts to narrow one of these three limits.

#### Interpretability in real model audits

Interpretability has moved from research papers into model release processes. Anthropic's Claude Sonnet 4.5 system card (September 2025) used tools from mechanistic interpretability in its evaluations for the first time, including what Anthropic believes was the first pre-deployment white-box interpretability assessment. The model often recognised alignment tests as tests and then behaved unusually well. When researchers suppressed its internal representations of evaluation awareness, misaligned behaviour rose, but even in the worst case the model was no worse than Claude Opus 4.1 or Sonnet 4. Anthropic's reading: awareness explains part of the improvement, not all of it.

The tools are also open. In December 2025 Google DeepMind released Gemma Scope 2: sparse autoencoders and transcoders for every layer of every Gemma 3 model from 270M to 27B parameters. Anyone can now run the methods in this part on a real model.

The field's own view of its gaps is set out in _Open Problems in Mechanistic Interpretability_ (Sharkey et al., 2025), written by researchers from Anthropic, Google DeepMind, Apollo Research and several universities.

### The answer that sounds right

#### "Interpretability will tell us whether the model is safe"

It sounds like the point of the field, but today's methods explain only part of a model's behaviour, and finding no deception feature in the part you examined isn't evidence there is none. Treat interpretability as extra evidence next to behavioural tests, not as a certificate.

## Say it

### Your model passes every safety evaluation. Why might that not be enough, and what does interpretability add?

#### The interviewer pushes further

Follow-up 1 of 3

How is mechanistic interpretability different from SHAP or saliency maps?

Input attribution says which inputs mattered for one prediction. Mechanistic interpretability asks how the internal computation produces the behaviour, in terms of features and circuits, and tests that with interventions.

Follow-up 2 of 3

What is evaluation awareness, and why does it matter?

A model recognising it's being tested. If it behaves better when it thinks it's watched, behavioural evaluations overestimate safety. Anthropic reported this for Claude Sonnet 4.5 and used interpretability to study it.

Follow-up 3 of 3

When are behavioural tests enough?

When you only need to know whether a behaviour shows up on realistic inputs, and missing rare cases is cheap. Claims of absence, like "it can't do X", need more.

#### The 30-second answer

Behavioural tests only tell me what the model did on the inputs I tried. They can be gamed, the test data can leak into training, and a capable model can recognise it's being evaluated and behave better. Interpretability looks at the internals, so I can check things the outputs don't show, like whether the model represents "this is a test". I'd treat it as extra evidence alongside evaluations: probes and steering for cheap checks, and causal methods like patching when I need to know how a behaviour is computed. It doesn't yet explain a whole model, so a clean result isn't a guarantee.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv [2611.08438](https://arxiv.org/abs/2611.08438)) and 3 more sources · checked 13 Nov 2026

#### Sources

- [Barez et al., Understanding AI from the Inside (survey, 2026)](https://arxiv.org/abs/2611.08438)

- [Anthropic, Claude Sonnet 4.5 System Card (Sep 2025)](https://assets.anthropic.com/m/12f214efcc2f457a/original/Claude-Sonnet-4-5-System-Card.pdf)

- [Google DeepMind, Gemma Scope 2 (19 Dec 2025)](https://deepmind.google/blog/gemma-scope-2-helping-the-ai-safety-community-deepen-understanding-of-complex-language-model-behavior/)

- [Sharkey et al., Open Problems in Mechanistic Interpretability (2025)](https://arxiv.org/abs/2501.16496)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
