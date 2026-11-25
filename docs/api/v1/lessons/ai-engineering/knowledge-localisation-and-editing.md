# Knowledge Localisation and Editing

> Where does a fact live in a model, and can you edit it safely?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/knowledge-localisation-and-editing/
- Before this: Activation Patching and Circuit Discovery (`ai-engineering/activation-patching`)
- Sources checked: 2026-11-13 · Text last changed: 2026-11-20 · Version: 4d4940ca41

## Intuition

### The situation

Your model states an outdated fact: a company's CEO who left last year. Retraining is expensive. A teammate suggests using ROME to edit just that fact. The interviewer asks:

> Where does a fact live in a model, and can you edit it safely?

### The idea

Think of correcting one entry in a phone book that's been copied into many other books. Finding the page where the entry matters most doesn't mean it's the best page to fix, and a careless fix can smudge the neighbouring entries.

[Figure: Locate, edit, then check what else moved.]

_Where a fact matters and where to edit it are different questions._

### Play

**Try it.** Corrupt the subject, then restore one hidden state at a time.

#### Which hidden state brings the answer back?

1. Clean run: the model completes the fact. Save every hidden state.

2. Corrupted run: add noise to the subject’s token embeddings, so the model loses the answer.

3. Re-run the corrupted input, but copy back one clean hidden state (one layer, one token, one component type).

4. The share of the correct answer’s probability that returns is that state’s indirect effect. Repeat for every layer and token to get a map.

Illustrative map drawn to follow the qualitative pattern Meng et al. report for GPT-2 XL, not their measured values [arXiv 2202.05262](https://arxiv.org/abs/2202.05262).

Causal tracing (Meng et al. 2022) underlies editing methods ROME, MEMIT and AlphaEdit, which rewrite the MLP weights it points to [p. 80](https://arxiv.org/pdf/2611.08438#page=80). Editing itself returns in Interpretability for AI Safety.

**Notice:** restoring middle-layer MLP states at the subject's last token brings the answer back. That inspired ROME, but where a fact matters isn't always the best place to edit it.

## How it works

### How it works

#### In one breath

Causal tracing corrupts the subject of a prompt, then restores one hidden state at a time to see which brings the answer back. For facts, the effect concentrates in middle-layer MLPs at the subject's last token, which inspired ROME (a rank-one update to one MLP) and MEMIT (many edits across layers). But where a fact matters most doesn't predict where editing works best, and edits can spill over to related facts.

#### MLPs as key–value memories

Geva et al. proposed that feed-forward layers act as key–value memories (Features, Polysemanticity and Superposition’s reading of MLP neurons); Dai et al. found factual associations stored there; and Sharma et al. found those associations flow mainly through the top singular directions of late-layer MLP weights. That motivated tools for finding where a fact sits [p. 80](https://arxiv.org/pdf/2611.08438#page=80).

Localisation is the usual first step before other interventions: choosing the layer and token position for a **probe** (Probing Classifiers), for a **steering vector** (Steering Vectors; e.g. Arditi et al. searched layers and positions for the best refusal direction), or the MLP to change in **knowledge editing** [p. 80](https://arxiv.org/pdf/2611.08438#page=80).

#### PISCES: edit the vectors that write a concept

1. Use SAE features plus automated explanations to find features tied to the concept: Fc = {fi : Corr(fi, c) > τ}. Here f2 and f3.

2. Find the MLP output vectors (columns of W2) that strongly activate those features: v2 does, v1 doesn’t.

3. Pass v2 through the SAE, set the concept features’ coefficients to negative values, and decode to get the edited v̂2.

4. The concept is removed from the weights themselves, not just blocked at the output.

Survey §13.2.1, the survey’s own worked example [pp. 114–115](https://arxiv.org/pdf/2611.08438#page=115). Reported result: accuracy on the prohibited concept near chance while general ability is kept, with higher specificity than baselines [p. 115](https://arxiv.org/pdf/2611.08438#page=115).

##### ROME: rewrite one association with a rank-one update

Causal tracing (this lesson) finds the MLP layer and token where a fact is retrieved; ROME then adds a rank-one matrix ΔW to that MLP’s output projection so the fact’s _key_ now maps to a new _value_. The survey’s example removes a backdoor that leaks an admin password after a trigger token: after the edit, the model outputs end-of-sequence instead [p. 116](https://arxiv.org/pdf/2611.08438#page=116). Try a simplified version:

Simplified ROME on a toy 32-dimensional linear memory W, with ΔW = (v* − W k*) k*ᵀ for a unit key k*. Real ROME also weights the update by the inverse covariance of keys to reduce interference.

Early ROME and MEMIT did cause substantial side effects; newer methods (AlphaEdit, CrispEdit) reduce them by using low-rank structure in activation space. And editing is double-edged: the more precise it is, the easier it is to inject misinformation undetected, which is why access control and auditability matter [p. 116](https://arxiv.org/pdf/2611.08438#page=116).

## In practice

### In practice

#### Limits

##### Why localisation is only a first step

- Transformers are overparameterised; information can be stored and processed redundantly across many components, differently for different inputs. A component with a strong causal effect may be a small part of the mechanism [p. 80](https://arxiv.org/pdf/2611.08438#page=80).

- Knowing the module, layer or subspace doesn’t explain how it works; that takes finer analyses like circuit discovery (Activation Patching and Circuit Discovery) [p. 80](https://arxiv.org/pdf/2611.08438#page=80).

- Outside the survey: Hase et al. found that where causal tracing localises a fact barely predicts which layer is best to edit it [arXiv 2301.04213](https://arxiv.org/abs/2301.04213).

##### Next · 9.3

Not just finding, but changing: steering vectors and the refusal direction.

##### Sources for this tab

- Survey §9.2, [arXiv 2611.08438](https://arxiv.org/abs/2611.08438), p. 80.

- Meng et al. (2022). _Locating and Editing Factual Associations in GPT._ [arXiv 2202.05262](https://arxiv.org/abs/2202.05262).

- Hase et al. (2023). _Does Localization Inform Editing?_ [arXiv 2301.04213](https://arxiv.org/abs/2301.04213).

#### What later work found

Hase et al. (NeurIPS 2023) tested ROME, MEMIT and fine-tuning on GPT-J and found that causal tracing provides no insight into which MLP layer is best to edit. For ROME, the edited layer explained edit success far better than the tracing result did. Later work (FiNE, 2025) reported that ROME and MEMIT often over-edit, changing facts they shouldn't, and attributed it to causal tracing focusing too much on the subject.

In practice, weight editing is a research tool and a way to test hypotheses about storage. For facts that change in production, retrieval is usually the safer fix.

### The answer that sounds right

#### "Causal tracing found the layer, so edit there"

It sounds logical, but Hase et al. found tracing gave no insight into which layer is best to edit; the choice of layer mattered far more than the trace. Pick the edit layer by testing edits directly, and measure the damage to related facts.

## Say it

### Where does a fact live in a model, and can you edit it safely?

#### The interviewer pushes further

Follow-up 1 of 3

Why a rank-one update?

ROME treats the MLP as a key–value memory: the subject gives a key, and it changes the weights so that key returns the new value with the smallest possible change, which is rank one.

Follow-up 2 of 3

ROME versus MEMIT?

ROME edits one fact in one layer. MEMIT spreads many edits across several layers so thousands of facts can change at once.

Follow-up 3 of 3

Why might an edit not stick?

The model may store the fact in more than one place or recompute it through other paths, and paraphrases can route around the edited key.

#### The 30-second answer

Causal tracing corrupts the subject in a prompt, then restores one hidden state at a time to see which brings the answer back. For facts, the effect concentrates in middle-layer MLPs at the subject's last token, which inspired ROME, a rank-one update to one MLP, and MEMIT for many facts at once. But later work showed localisation doesn't predict where editing works best, and edits can over-generalise or miss paraphrases. So I'd test any edit on paraphrases, related facts and unrelated facts. For a fact that changes in production, I'd usually prefer retrieval over editing weights.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv [2611.08438](https://arxiv.org/abs/2611.08438)) and 4 more sources · checked 13 Nov 2026

#### Sources

- [Barez et al., Understanding AI from the Inside (survey, 2026)](https://arxiv.org/abs/2611.08438)

- [Meng et al., Locating and Editing Factual Associations in GPT (ROME, 2022)](https://arxiv.org/abs/2202.05262)

- [Meng et al., Mass-Editing Memory in a Transformer (MEMIT, 2022)](https://arxiv.org/abs/2210.07229)

- [Hase et al., Does Localization Inform Editing? (NeurIPS 2023)](https://arxiv.org/abs/2301.04213)

- [Pan et al., Precise Localization of Memories: FiNE (2025)](https://arxiv.org/abs/2503.01090)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
