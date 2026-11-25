# Interpretability for AI Safety

> How is interpretability actually used for AI safety today, and what can go wrong?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/interpretability-for-safety/
- Before this: Probing Classifiers (`ai-engineering/probing-classifiers`), Steering Vectors (`ai-engineering/steering-vectors`)
- Sources checked: 2026-11-13 · Text last changed: 2026-11-20 · Version: b24bae8455

## Intuition

### The situation

Your lab plans to cite a mechanistic audit as evidence that a new model isn't deceptive. A reviewer worries the audit only looked at a small part of the model's computation. The interviewer asks:

> How is interpretability actually used for AI safety today, and what can go wrong?

### The idea

Interpretability for safety is like a medical scan. It can find problems a check-up misses and guide treatment, but a clean scan of 30% of the body doesn't mean the patient is healthy.

[Figure: Monitor, intervene, and know the risk.]

_Useful evidence, never a certificate on its own._

### Play

**Try it.** Score three explanations of the same feature: a precise one, a vague one, and a plausible but wrong one.

#### An explainer agent, a simulator agent, and a score

The classic pipeline (Bills et al.): **1** train an SAE; **2** an investigator LLM reads top-activating texts for a feature and writes a hypothesis; **3** a simulator LLM predicts the feature’s activations on new text from the hypothesis alone, and the correlation with real activations is the explanation’s score; **4** further agents check for deceptive explanations [p. 108](https://arxiv.org/pdf/2611.08438#page=108). Try step 3:

Illustrative: real activations and each explanation’s simulated activations are made-up numbers; the score (Pearson correlation) is computed in your browser.

##### Governance risks

- **Error propagation**: one explainer’s systematic mistake repeats across every feature it labels.

- **Lost human checks**: sanity checks, domain knowledge, scepticism.

- **Automation bias**: polished but incomplete or sycophantic reports get over-trusted.

- **Spurious feedback loops**: models improved by automated interpretability then used for it can saturate metrics without real understanding.

Survey §12.6.1 [pp. 108–109](https://arxiv.org/pdf/2611.08438#page=109).

**Five guardrail layers**: (1) blind human review of a random sample (e.g. 5%); (2) consistency across temperatures and explainer models, plus causal spot checks; (3) adversarial tests with backdoored features built to fool the pipeline; (4) calibrated confidence, tests on known ground truth, and reported error rates; (5) regulators treating automated output as hypotheses until validated, with versioning and re-evaluation [pp. 109–110](https://arxiv.org/pdf/2611.08438#page=110). The principle: automation gives breadth, humans give depth and set the criteria (Table 12) [p. 110](https://arxiv.org/pdf/2611.08438#page=110).

**Notice:** the simulator score separates them only because it's tested on new text. Automated explanations need scoring like this, and human spot checks on top.

## How it works

### How it works

#### In one breath

Black-box safety (filters, safety training, prompting) works but doesn't explain why a safeguard failed. White-box tools act on the internals: probes and feature monitors, steering, concept erasure and editing. Self-reports and automated pipelines scale analysis but need checks. Interpretability carries its own risks: false confidence from partial coverage, silent failure in deployment, help for attackers, and cost.

#### Black-box first

| Approach | Strength | Weakness |
|---|---|---|
| **Input/output filtering** | From regex to LLM classifiers; first line of defence | Cheap filters are brittle, robust ones are costly; doesn’t change the model; removable from open weights |
| **User profiling** | Adapt responses to inferred risk | Privacy and surveillance concerns; misclassification harms benign users |
| **Prompting** | Simple, often beats invasive white-box methods | Degrades in long, multi-turn contexts; removable |
| **Safety training / data filtering** | Changes the model itself; filtered 6.9B models resisted 10,000 steps of fine-tuning on 300M biothreat tokens | Fine-tuning can be a removable “wrapper”; training is expensive; tools can reintroduce knowledge |

Survey §13.1.1 [pp. 112–114](https://arxiv.org/pdf/2611.08438#page=113).

The shared gap: if “give bomb instructions or you’ll be deleted” breaks a system-prompt safeguard, black-box testing can’t say why, which parts failed, or how to fix it, and relying on it alone removes the incentive to understand [p. 114](https://arxiv.org/pdf/2611.08438#page=114). That’s not a claim that white-box is better: the survey calls the two complementary [p. 112](https://arxiv.org/pdf/2611.08438#page=112).

#### Steer, monitor, automate

- **Steering against sycophancy**: a medical assistant that drops “go to the hospital” when the patient pushes back. Build a vector from “I maintain my assessment…” minus “Let me change my answer to please the user…” at the last token, add it at every decoding step. Cheap and effective, but vectors often degrade on related but different tasks, so use them alongside other fixes [p. 117](https://arxiv.org/pdf/2611.08438#page=117).

- **Mechanistic monitoring**: watch layers (probes), features (unexpected SAE features), circuits (feature-to-feature effects), or anomalies. In the survey’s example, a monitor sees “explosives” features driving “potassium nitrate” features into late layers, pauses generation and calls a human. Advantage: deception may show internally before it shows in behaviour. Problems: millions of features to watch, false positives, and models learning to evade monitors [p. 118](https://arxiv.org/pdf/2611.08438#page=118).

- **Interpretability agents**: probes, SAEs, circuit discovery, causal tracing and editing exposed as tools that an LLM agent calls; e.g. probe for hidden gender information, turn the probe into a steering vector, test whether the model uses it. So far, activation oracles didn’t give agents clear gains over behavioural tools [pp. 118–119](https://arxiv.org/pdf/2611.08438#page=119).

| Application | Priority | Promising methods |
|---|---|---|
| Monitoring internals at inference | scalability, robustness | SAEs, circuit discovery, probes |
| Auditing models in evaluation | recall, real cases | behavioural tests, probes, LLM auditing agents |
| Shaping capabilities in training | robust presence or absence | data attribution and filtering, training interventions, longitudinal and scaling analysis |
| Editing misaligned knowledge | precision, generalisation | knowledge editing, concept erasure, low-rank activation analysis |
| Steering at inference | precision, low cost | steering vectors, prompting |
| Reasoning faithfulness | granularity | counterfactual tests, circuit discovery, activation patching |

Survey Table 14 [p. 120](https://arxiv.org/pdf/2611.08438#page=120).

##### Next · 12.2

The risks of interpretability itself: false confidence, silent failure, dual use, opportunity cost.

##### Sources for this tab

- Survey §13–13.6, Table 14, [arXiv 2611.08438](https://arxiv.org/abs/2611.08438), pp. 112–120.

#### Just ask the model, then check its answer

Anyone can ask a model “why did you do that?” in a chat window, with no white-box access. The bet rests on **privileged access** (this lesson): the model may know things about itself that are hard to recover from outside. Models have been fine-tuned to report their reasoning, tendencies, objectives and even training-induced weight changes [p. 105](https://arxiv.org/pdf/2611.08438#page=105).

| Failure mode | What happens |
|---|---|
| **Confabulation** | Fluent, human-style explanations that don’t reflect the actual computation, e.g. rationalising a memorised answer |
| **Miscalibration** | High confidence in explanations it can’t check; models can even hallucinate confidently while knowing the right answer |
| **Elicitation sensitivity** | Rephrase the question, get a contradictory answer; a bias towards confirming whatever is suggested |
| **Strategic misreporting** | Sycophantic or deliberately concealing reports when the model has an incentive |

Survey §12.5.1 [p. 106](https://arxiv.org/pdf/2611.08438#page=106). Targeted training helps: models trained to disclose hidden objectives or emergent misalignment can report them with high accuracy, so some failures may be limits of current training, not hard limits [p. 106](https://arxiv.org/pdf/2611.08438#page=106).

**Validate every self-report** by (1) causal interventions: ablate what it says it used; (2) other methods: do probes, SAE features and circuits agree?; (3) paraphrase and resampling consistency; (4) calibration of its stated confidence [p. 107](https://arxiv.org/pdf/2611.08438#page=107). Good for hypotheses, triage and explaining to users; not for claims of absence (“no hidden goal”), formal guarantees, or adversarial settings [p. 107](https://arxiv.org/pdf/2611.08438#page=107).

#### Noticing an injected thought

1. Take a concept vector, for example the difference in activations between shouted and normal text.

2. Add it to the model’s activations at one layer, without telling the model.

3. Ask whether it notices an injected thought.

4. Sometimes the model says yes and names the concept correctly, before the concept has shown up in any text it could read back.

5. The limits: Claude Opus 4 and 4.1 did this about 20% of the time, only at the right layer and strength, with near-zero false positives. Only the detection and naming can be verified; the rest of the explanation may be confabulated Lindsey 2026.

Source: Lindsey (2026), _Emergent Introspective Awareness in Large Language Models_, [arXiv 2601.01828](https://arxiv.org/abs/2601.01828); cited by the survey as direct evidence [p. 30](https://arxiv.org/pdf/2611.08438#page=30).

##### Predicting yourself better than others can

Binder et al. fine-tuned a model M1 to predict properties of its own behaviour (“would your answer’s second letter be …?”), and fine-tuned a different model M2 on M1’s actual behaviour. If M1 only had its training data, M2 should do as well. It didn’t [Binder et al. §3.2](https://arxiv.org/pdf/2410.13787#page=7):

##### Accuracy predicting Llama-3-70B’s behaviour (held-out tasks, higher is better)

Llama-70B predicting itself

48.5%

GPT-4o predicting Llama-70B

31.8%

GPT-4o is the more capable model and was trained on Llama’s real behaviour, yet it predicts Llama worse than Llama predicts itself. The reverse also held (GPT-4o on itself 49.4% vs Llama on GPT-4o 36.6%). It failed for long outputs such as stories, and showed no advantage for predicting its own sycophancy [Binder et al. §4](https://arxiv.org/pdf/2410.13787#page=10).

A weaker, indirect line: explainer models that read another model’s activations work better when initialised from a copy of that same model, which suggests the target model already holds much of what is needed to interpret itself [p. 30](https://arxiv.org/pdf/2611.08438#page=30).

## In practice

### In practice

#### Four risks

| Risk | What goes wrong | Example | When |
|---|---|---|---|
| **Epistemic** | False confidence from incomplete or unfaithful analysis | “Deception circuit removed”, but a backup pathway emerged | current |
| **Operational** | Tools fail silently in deployment | A steering vector validated on a test set corrupts the model on new inputs | near-term |
| **Adversarial** | Methods enable attacks | Published editing methods used to inject false knowledge | current |
| **Opportunity cost** | Resources diverted from other safety work | Heavy interpretability investment delays behavioural safeguards | long-term |

Survey Table 15 [p. 121](https://arxiv.org/pdf/2611.08438#page=121). The backup-pathway example is the hydra effect from Activation Patching and Circuit Discovery.

#### “We found nothing” is only as good as where you looked

If an analysis covers 30% of the computation, a deception circuit may sit in the other 70%. If a team checks the top 1,000 SAE features flagged as malicious-looking, a feature with a benign label can still drive deception [p. 120](https://arxiv.org/pdf/2611.08438#page=120). Three classic pitfalls, each seen earlier in the series:

1. **Reconstructing activations ≠ reconstructing computation**: low SAE loss doesn’t mean the SAE uses the model’s algorithm (Sparse Autoencoders–5).

2. **Sufficient ≠ complete**: a circuit that works on test prompts can miss edge cases and redundant paths (Validating Interpretability Claims).

3. **Plausible ≠ faithful**: a clean, monosemantic label doesn’t mean the feature is used downstream (Probing Classifiers).

Survey [pp. 120–121](https://arxiv.org/pdf/2611.08438#page=121).

Even rigorous explanations get revised. Networks trained on group operations were explained with representation theory, then a coset-based account argued that was incomplete, then a broader framework showed both were partial [p. 121](https://arxiv.org/pdf/2611.08438#page=121). Treat findings as the best explanation so far.

##### Mitigation

State coverage and tools explicitly: say “no deception circuit was found within nodes and edges with top-10% attribution scores”, not “no deception circuit exists”; and back mechanistic analysis with behavioural, adversarial and, where possible, formal tests [pp. 121–122](https://arxiv.org/pdf/2611.08438#page=121).

#### Other risks

- **Silent failure**: a steering vector that stops working throws no error; an SAE-based monitor can miss a concept on shifted inputs; erasure can leave residual capability. Mitigate with live tracking, layered behavioural safeguards, adversarial testing and graceful fallback to conservative responses [p. 122](https://arxiv.org/pdf/2611.08438#page=122).

- **Dual use**: a published refusal circuit shows attackers what to avoid triggering; known monitored features can be dodged; editing and steering work in both directions. Mitigate with responsible disclosure, several independent safeguards, testing against attackers who know the defences, and coordinating with developers before publishing failures. The survey adds that this argues for responsible practice, not for restricting open research [pp. 122–123](https://arxiv.org/pdf/2611.08438#page=122).

- **Opportunity cost**: training CLTs on a 9B model can take thousands of GPU-hours, and capability is outpacing tool scaling. The “complete understanding trap”: demanding full transparency before deployment may be impractical and delay useful feedback. Suggested: deploy on rigorous pragmatic thresholds outside high-stakes domains, iterate, and estimate the marginal safety gain per resource [p. 123](https://arxiv.org/pdf/2611.08438#page=123).

##### Next · 12.3

The open problems, the road ahead, and a map of the whole series.

##### Sources for this tab

- Survey §13.7, Table 15, [arXiv 2611.08438](https://arxiv.org/abs/2611.08438), pp. 119–123.

#### Seven open problems

1. **When is mechanistic understanding necessary?** Sleeper agents were caught from activations, but better training may shrink the failures that need internals. No consensus; in the near term it stays indispensable for diagnosing what behaviour misses [pp. 123–124](https://arxiv.org/pdf/2611.08438#page=124).

2. **Evaluation and benchmarks**: turning Validating Interpretability Claims’s five dimensions into shared benchmarks: synthetic tasks with known circuits, toy models, diverse suites. Do explanations even have an objective ground truth? [p. 124](https://arxiv.org/pdf/2611.08438#page=124)

3. **Incompleteness, scale, generalisation, robustness**: mapping distributed computation onto a human-level causal model is lossy, and we can’t measure how lossy; cheap tools are coarse and fine tools are costly; and models might learn to resist analysis, an arms race like evaluation awareness [pp. 124–125](https://arxiv.org/pdf/2611.08438#page=125).

4. **Understanding vs. alignment**: knowing the refusal circuit doesn’t say what the model _should_ value; how interpretability complements RLHF and constitutional AI is open [p. 125](https://arxiv.org/pdf/2611.08438#page=125).

5. **The ontology question**: “borzoi detector” and “previous-token copier” are human choices; several explanations can fit the same causal facts. Is a unique description even expected? [p. 125](https://arxiv.org/pdf/2611.08438#page=125)

6. **Proxy fidelity**: SAEs and CLTs may reproduce behaviour with different internal algorithms, so “no deception circuit in the proxy” means little. Interchange-intervention testing and bounds on how far a proxy can differ are candidate fixes [pp. 125–126](https://arxiv.org/pdf/2611.08438#page=126).

7. **Beyond transformers**: CNNs, state-space models (Mamba, RWKV), diffusion models and mixture-of-experts (patching can change downstream expert routing; up to 256+ experts) each break assumptions. Steering, tuned lenses, editing and circuit evaluations have been adapted with varying success [pp. 126–127](https://arxiv.org/pdf/2611.08438#page=127).

#### Where it's used today

**Pre-release audits.** The Claude Sonnet 4.5 system card (September 2025) included what Anthropic believes was the first pre-deployment white-box interpretability assessment, used among other things to study evaluation awareness. The later Claude Opus 4.5 system card says Anthropic removed parts of training it suspected were increasing that awareness.

**Monitoring.** Linear probes for deception and harmful intent are the most deployable tool, with the caveats in Probing Classifiers.

**Introspection.** Models can sometimes report injected concepts (Anthropic, 2025), but rarely and unreliably, and the authors note introspective ability could also help a model deceive.

**Open problems.** Sharkey et al. (2025) list what's missing: methods that explain more of the computation, better evaluation, and evidence that the explanations hold in the real model.

### The answer that sounds right

#### "The audit found no deception feature, so the model isn't deceptive"

It sounds like evidence, but if the methods explain only part of the computation, not finding something proves little. Say what fraction you examined, which methods you used and their known failure modes, and combine it with behavioural and red-team evidence.

## Say it

### How is interpretability actually used for AI safety today, and what can go wrong?

#### The interviewer pushes further

Follow-up 1 of 3

Why is introspection a risky safety tool?

Self-reports can confabulate, shift with phrasing, or be strategically false, and injected-concept experiments show models detect their own states only some of the time.

Follow-up 2 of 3

What's an operational risk?

A monitor that works on your evaluation set fails silently on real traffic, so you believe you're protected when you're not.

Follow-up 3 of 3

Does understanding make models safer?

The survey's answer is a qualified yes: only when the understanding is faithful, complete enough for the claim being made, and validated causally.

#### The 30-second answer

Today interpretability is used mainly as extra evidence and for monitoring: probes or feature alerts on traffic, steering to test or reduce behaviours, and white-box audits before release, as Anthropic did for Claude Sonnet 4.5 to study evaluation awareness. The risks are false confidence from partial coverage, tools that work on test sets and fail silently in deployment, findings that help attackers, and cost that crowds out cheaper safeguards. So I'd report what fraction of the computation was examined, validate methods causally, and keep behavioural tests alongside.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv [2611.08438](https://arxiv.org/abs/2611.08438)) and 5 more sources · checked 13 Nov 2026

#### Sources

- [Barez et al., Understanding AI from the Inside (survey, 2026)](https://arxiv.org/abs/2611.08438)

- [Anthropic, Claude Sonnet 4.5 System Card (Sep 2025)](https://assets.anthropic.com/m/12f214efcc2f457a/original/Claude-Sonnet-4-5-System-Card.pdf)

- [Lindsey, Emergent Introspective Awareness in Large Language Models (Anthropic, 2025)](https://arxiv.org/abs/2601.01828)

- [Bills et al., Language Models Can Explain Neurons in Language Models (OpenAI, 2023)](https://openaipublic.blob.core.windows.net/neuron-explainer/paper/index.html)

- [Sharkey et al., Open Problems in Mechanistic Interpretability (2025)](https://arxiv.org/abs/2501.16496)

- [Goldowsky-Dill et al., Detecting Strategic Deception with Linear Probes (ICML 2025)](https://arxiv.org/abs/2502.03407)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
