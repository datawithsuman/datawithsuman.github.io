# Validating Interpretability Claims

> You found a circuit. How do you know it's a real explanation and not just a convincing story?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/validating-interpretability-claims/
- Before this: Activation Patching and Circuit Discovery (`ai-engineering/activation-patching`)
- Sources checked: 2026-11-13 · Text last changed: 2026-11-20 · Version: d41a2bf4a4

## Intuition

### The situation

A paper claims a 12-head circuit explains how a model does a task, and the figure looks convincing. Your manager wants to build a production monitor on it. The interviewer asks:

> You found a circuit. How do you know it's a real explanation and not just a convincing story?

### The idea

Interpretability results today are like restaurant reviews that each use a different scale. One counts stars, one counts dishes, one just says it felt nice. A shared report card lets you compare explanations fairly.

[Figure: Test it like a hypothesis.]

_A convincing figure is not a faithful explanation._

### Play

**Try it.** Knock out the circuit, then knock out everything except the circuit.

#### Remove it, or keep only it

A circuit is necessary if ablating it degrades the behaviour, and sufficient if patching everything _outside_ it with corrupted values still reproduces the behaviour. A circuit that is both is called faithful [p. 57](https://arxiv.org/pdf/2611.08438#page=57).

##### Try it: test candidate circuits

The toy circuit from Activation Patching and Circuit Discovery (duplicate detector D → inhibition S → name mover N, plus a backup B and a negative mover Neg). Choose which components make up your candidate circuit.

Necessity = (clean − ablate circuit) / (clean − corrupted). Sufficiency = (ablate everything else − corrupted) / (clean − corrupted). Ablation = corrupted value; downstream parts recompute. Same toy equations as Activation Patching and Circuit Discovery.

Each quirk in the lab has a real counterpart. Redundancy makes necessity weak; removing negative components makes sufficiency exceed 100% (recovery metrics can leave [0, 1], which is why bounded versions have been proposed [pp. 60–61](https://arxiv.org/pdf/2611.08438#page=61)); and a backup path can be sufficient on its own. The survey: in practice a circuit is rarely sparse, necessary and sufficient at once, and typically explains 60–80% of behavioural variance [p. 57](https://arxiv.org/pdf/2611.08438#page=57).

**Notice:** a circuit can recover more than 100% of the behaviour when it drops parts that were pushing the other way. Report both tests, and say exactly what you removed.

## How it works

### How it works

#### In one breath

A discovered circuit is a hypothesis. Test necessity (knock it out and the behaviour breaks) and sufficiency (keep only it and the behaviour stays). Real circuits usually explain part of a behaviour. Beyond that, score any method on five things: faithfulness of its importance scores, completeness, stability across seeds and prompts, causal validity, and whether it helps people predict or fix the model.

#### Causal scrubbing and interchange interventions

- **Causal scrubbing**: replace activations with ones from other inputs that your hypothesis says should be _equivalent_. If the hypothesis is right, behaviour is preserved.

- **Interchange interventions**: swap activations between inputs that differ in a high-level variable (say, which name is the subject), and check whether the output changes the way that variable predicts.

Both give stronger evidence than observation alone, because they test the circuit’s claimed computation, not just whether its parts matter [p. 57](https://arxiv.org/pdf/2611.08438#page=57). Benchmarks such as **MIB** now score circuit-discovery methods by faithfulness across tasks [p. 57](https://arxiv.org/pdf/2611.08438#page=57).

#### Five questions, each with its own metrics

| Dimension | Question | Example metrics |
|---|---|---|
| **1 · Attribution faithfulness** | Do importance scores reflect real causal effects? | effect agreement (correlation), effect-size error, counterfactual recovery |
| **2 · Completeness** | How much of the behaviour is accounted for? | loss recovery, behavioural coverage, unexplained variance |
| **3 · Stability** | Robust to seeds, hyperparameters, paraphrases? | cross-seed agreement, hyperparameter sensitivity, paraphrase consistency |
| **4 · Causal validity** | Necessary, sufficient and specific? | necessity, sufficiency, specificity scores |
| **5 · Human interpretability** | Can people understand and use it? | explanation utility, debugging utility, inter-rater agreement |

Survey Table 9 [p. 60](https://arxiv.org/pdf/2611.08438#page=60). All metrics build on the intervention effect s(S, x) from Activation Patching and Circuit Discovery, averaged over prompts of the behaviour [p. 59](https://arxiv.org/pdf/2611.08438#page=59).

#### Agreement and error measure different things

**Effect agreement** is the correlation (Pearson or Spearman) between a method’s scores a(S, x) and the real intervention effects s(S, x). **Effect-size error** is the average gap |a − s|. A method can rank components perfectly and still get their sizes badly wrong [p. 60](https://arxiv.org/pdf/2611.08438#page=60).

##### Try it: EAP scores vs. true patching effects

Twelve components with the saturating metric from Activation Patching and Circuit Discovery. Each component’s clean activation is spread up to a maximum; its corrupted value is 0. The method is EAP (a first-order estimate).

True effect = 3·tanh(h); EAP score = 3·(1 − tanh²h)·h; Spearman = Pearson on ranks; error = mean |score − effect|.

**Counterfactual recovery** patches S from an input showing behaviour B into one showing a reference behaviour B′ and asks what fraction of the difference moves:

$$ \text{CFRecovery} = {\mathbb{E}_{x_1,x_2}}\left[\frac{{M\big(f_\theta(x_{1,[S\leftarrow h_S(x_2)]})\big) - M\big(f_\theta(x_1)\big)}}{{M\big(f_\theta(x_2)\big) - M\big(f_\theta(x_1)\big)}}\right] $$

Survey §7.5.2 [p. 60](https://arxiv.org/pdf/2611.08438#page=60).

- **what patching moved**: Run the reference input x₁, but with S’s activations taken from x₂. How far did the metric move from x₁’s own value?

- **the full difference**: How far apart the two inputs are without any patching. If this is close to zero, the ratio explodes.

- **averaged over pairs**: Averaged over pairs of inputs, one from each behaviour. Near 1 = patching S recovers the behaviour; near 0 = little effect.

Illustrative: 12 input pairs; patching truly recovers 80% of each pair’s gap, plus a little noise (±0.1 on the metric). Gaps vary ±50% around the slider value.

The survey flags exactly this: the denominator can be near zero and patched values can overshoot, so the metric can land far above 1 or below 0; a bounded alternative has been proposed (Wu & Barez 2026) [p. 61](https://arxiv.org/pdf/2611.08438#page=61). Loss recovery for SAEs and CLTs has the same problem [p. 61](https://arxiv.org/pdf/2611.08438#page=61).

#### How much is explained, and does it survive a re-run?

- **Loss recovery** (SAEs, CLTs): of the loss lost by ablating a layer, how much does the reconstruction win back? **Unexplained variance**: the fraction of activation variance the reconstruction misses (the FVU of Sparse Autoencoders). **Behavioural coverage**: the fraction of prompts where S has an effect bigger than a threshold τ, so a mechanism that works on 3 of 40 prompts can’t pass as general [pp. 61–62](https://arxiv.org/pdf/2611.08438#page=61).

- **Cross-seed agreement**: train K times and average the pairwise match between discovered feature sets (e.g. Hungarian matching on cosine similarity, as in SAE Failures and Alternatives). **Hyperparameter sensitivity**: (max − min) / mean of a result across reasonable settings. **Paraphrase consistency**: does S’s effect stay the same when the prompt is reworded? [p. 62](https://arxiv.org/pdf/2611.08438#page=62)

The protocol asks you to report robust and fragile findings separately [p. 63](https://arxiv.org/pdf/2611.08438#page=63).

#### Is it the cause, and does it help a person?

**Causal validity** uses necessity and sufficiency as in this lesson, with two additions: compare against _random component sets of the same size_, and test **specificity**, the share of S’s effect that falls on the target behaviour rather than on control behaviours: |s(S, B)| / ΣB′ |s(S, B′)| [p. 63](https://arxiv.org/pdf/2611.08438#page=63). (The survey normalises necessity and sufficiency by the clean metric, not by the clean–corrupted gap used in this lesson; the idea is the same.) Benchmarks: **MIB** (circuits and causal variables), **AxBench** (steering), **RAVEL** (localising concepts with interchange interventions), **SAEBench** (SAEs on reconstruction plus downstream tasks) [p. 64](https://arxiv.org/pdf/2611.08438#page=64).

**Human interpretability** is measured as a difference with and without the explanation: do people predict held-out behaviour more accurately, find and fix errors more often, and do two raters agree (Cohen’s κ)? These studies are expensive, and expertise confounds them: what is clear to an interpretability researcher may be opaque to a domain expert [p. 64](https://arxiv.org/pdf/2611.08438#page=64).

## In practice

### In practice

#### Five problems

| Problem | What it looks like |
|---|---|
| **Utility ambiguity** | SAEs are scored on reconstruction and sparsity, circuits on behaviour recovery, steering vectors on behaviour change, yet all three can be used to steer a model. Without a shared goal, which is most useful? |
| **Cherry-picking** | Results shown on hand-picked examples or a narrow distribution, with no failure cases or coverage statistics. |
| **Missing baselines** | No comparison with simple alternatives: behavioural tests, random directions, single neurons. Is the method finding anything a cheap method wouldn’t? |
| **Reproducibility gaps** | Many hyperparameters, heavy training, results that change with seeds (SAE Failures and Alternatives), and reproducibility rarely reported. |
| **Faithfulness–understandability gap** | Outputs are shown to be readable, less often shown to match the model’s real mechanism, which rewards persuasive stories. |

Survey §7.5.1 [pp. 58–59](https://arxiv.org/pdf/2611.08438#page=58).

#### Cherry-picking and missing baselines in one plot

A made-up method scored on 40 prompts (score = how much of the behaviour its explanation recovers). Switch between what a paper might show and the full picture.

Illustrative scores, generated with a fixed seed in your browser.

The survey’s fix is to report coverage across a diverse input set with uncertainty, include failures, and always compare against baselines such as random directions, PCA, single neurons and supervised probes [pp. 61, 65](https://arxiv.org/pdf/2611.08438#page=65). Shared platforms for tracking and auditing claims across papers have also been proposed [p. 59](https://arxiv.org/pdf/2611.08438#page=59).

##### Next · 7.2

The survey’s answer: five dimensions every method should be scored on.

##### Sources for this tab

- Survey §7.5–7.5.1, [arXiv 2611.08438](https://arxiv.org/abs/2611.08438), pp. 58–59.

#### A five-step protocol, and what it can’t fix

1. **Define scope**: model, layers, behaviour, a test suite with success criteria.

2. **Establish baselines**: random directions, PCA, single neurons, supervised probes.

3. **Apply the method** across seeds, hyperparameters and training details.

4. **Evaluate all five dimensions.**

5. **Report everything**, including failures, unexplained behaviour and baseline comparisons.

Survey §7.5.3 [pp. 65–66](https://arxiv.org/pdf/2611.08438#page=65). Table 10 tailors the priorities: for SAEs, cross-seed feature alignment and loss recovery; for circuits, counterfactual recovery and interchange tests; for probes and steering vectors, a search for confounds in the fitting set and side-effect analysis [p. 65](https://arxiv.org/pdf/2611.08438#page=65).

##### The framework’s own limits (survey §7.5.4)

- The metrics aren’t uniquely correct, and thresholds lack theoretical grounding.

- Evaluating all five is expensive; the human dimension especially.

- Scores depend on the task: good at factual recall doesn’t mean good at reasoning.

The authors call it “a starting point for standardisation, not a final answer” [p. 66](https://arxiv.org/pdf/2611.08438#page=66).

##### Next · Probing Classifiers

Reading activations directly: describing in plain language what a hidden activation encodes, without decomposing it into features or circuits.

##### Sources for this tab

- Survey §7.5.2–7.5.4, Tables 9–10, [arXiv 2611.08438](https://arxiv.org/abs/2611.08438), pp. 59–66.

#### Toward shared standards

The field's own review, _Open Problems in Mechanistic Interpretability_ (Sharkey et al., 2025), lists evaluation as a core gap: many results are shown on a few chosen prompts, without baselines, and are rarely reproduced. Shared benchmarks are starting to appear. SAEBench (ICML 2025) scores sparse autoencoders on eight metrics instead of reconstruction alone, and its finding that the usual proxies don't predict usefulness is a good example of why one number isn't enough.

For causal claims, the strongest tests resample everything the hypothesis says doesn't matter, as in causal scrubbing, or check that the model's internal states line up with a simpler algorithm under interchange interventions (Geiger et al.).

### The answer that sounds right

#### "The figure is convincing, so the circuit is right"

It sounds reasonable, but persuasive isn't faithful. Circuits are often shown on chosen prompts with no baseline, and few are reproduced. Ask for necessity and sufficiency numbers, a random-circuit baseline, results across prompts and seeds, and how much of the behaviour is left unexplained.

## Say it

### You found a circuit. How do you know it's a real explanation and not just a convincing story?

#### The interviewer pushes further

Follow-up 1 of 3

Why can recovery exceed 100%?

Some components push against the behaviour. Removing them along with everything outside the circuit makes the circuit look better than the full model.

Follow-up 2 of 3

What is causal scrubbing?

A test that resamples every activation the hypothesis says doesn't matter and checks the behaviour is preserved, so the whole explanation is tested, not just a few components.

Follow-up 3 of 3

Faithful versus plausible?

Plausible explanations convince people. Faithful ones match what interventions on the model show. Only faithful ones are safe to build on.

#### The 30-second answer

I'd treat the circuit as a hypothesis and test it two ways: knock it out and check the behaviour breaks, which is necessity, and knock out everything else and check it still works, which is sufficiency. Real circuits usually explain only part of a behaviour, and recovery can exceed 100% if components pushing the other way are removed, so I'd report both. Then I'd check that importance scores match real interventions, that results hold across seeds and paraphrases, how it compares to a random baseline, and whether it actually helps people predict or fix the model.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv [2611.08438](https://arxiv.org/abs/2611.08438)) and 4 more sources · checked 13 Nov 2026

#### Sources

- [Barez et al., Understanding AI from the Inside (survey, 2026)](https://arxiv.org/abs/2611.08438)

- [Chan et al., Causal Scrubbing (Redwood Research, 2022)](https://www.lesswrong.com/posts/JvZhhzycHu2Yd57RN/causal-scrubbing-a-method-for-rigorously-testing)

- [Geiger et al., Causal Abstractions of Neural Networks (2021)](https://arxiv.org/abs/2106.02997)

- [Sharkey et al., Open Problems in Mechanistic Interpretability (2025)](https://arxiv.org/abs/2501.16496)

- [Karvonen et al., SAEBench (ICML 2025)](https://arxiv.org/abs/2503.09532)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
