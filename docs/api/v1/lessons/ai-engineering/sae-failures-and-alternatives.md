# SAE Failures and Alternatives

> When do sparse autoencoders fail, and when should you use something simpler?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/sae-failures-and-alternatives/
- Before this: Sparse Autoencoders (`ai-engineering/sparse-autoencoders`)

## Intuition

### The situation

Your team trained an SAE and uses its "harmful request" latent as a classifier. On a new style of prompt it misses many cases, while a plain linear probe an intern trained catches them. The interviewer asks:

> When do sparse autoencoders fail, and when should you use something simpler?

### The idea

An SAE is like a filing system made by a new clerk with no instructions. It's great for discovering what's in the archive, but the clerk may file one topic under two names, or bury a general folder inside a specific one. If you already know you need the invoices, just search for invoices.

[Figure: Know the failure modes, and when to skip the SAE.]

_SAE features are one useful approximation, not the model's true parts._

### Play

**Try it.** Grow the dictionary, then change the random seed.

#### Latents that never fire, and features learned twice

Dead features never (or almost never) activate. In a poorly tuned SAE they can be 10–50% of the dictionary. Causes: bad initialisation, a sparsity penalty that is too strong too early, or common patterns being claimed first so the rest find no role. Fixes include resampling dead latents and warming up λ p. 37. At scale, Gao et al. saw up to 90% dead latents without mitigations; with an encoder initialised as the decoder transpose and an auxiliary loss, their 16M-latent SAE had only 7% dead Gao et al. §2.4.

Duplication: several latents encode the same concept. You can spot it by high cosine similarity between decoder columns, plus latents that fire together p. 37–38.

##### Try it: too big a dictionary, and a different seed

The same 5-feature data again. Make the dictionary bigger than needed and train two SAEs that differ only in the random seed. Dead latents, duplicates and seed-dependence all show up.

Real training (λ = 0.3, run A seed 1). “Shared” = live latents of run A with a live latent in run B at cosine above 0.95. Dashed amber: true features.

**Notice:** a bigger dictionary wastes latents and repeats features, and a new seed gives a different set. Treat SAE features as an approximation, and test the ones you rely on.

## How it works

### How it works

#### In one breath

SAEs can waste latents that never fire, learn the same feature twice, let a specific feature quietly take over a general one's job (absorption), and give different answers with a new random seed. When you already know the concept and have labels, a supervised direction such as a linear probe or a difference of means usually works better. SAEs earn their place in open-ended discovery.

#### When a specific feature steals a general one’s job

1. In Gemma Scope, a latent seems to track “starts with S”: it fires on snake, soccer, steam.

2. But it silently fails on “short”.

3. Instead, a token-specific “short” latent fires and carries a small piece of the “starts with S” direction. It has absorbed the general feature.

4. Why: “short” always comes with “starts with S”. Firing one latent instead of two is sparser and rebuilds the same thing, so the sparsity penalty rewards absorption.

Example and mechanism from Chanin et al. (NeurIPS 2025), arXiv 2409.14507: absorption appeared in every LLM SAE they tested, and was worse for wider and sparser SAEs. The survey describes how to detect it: compare the latent with a linear probe for the same concept p. 39.

Feature splitting is the related, sometimes harmless case: as the dictionary grows, one feature splits into finer ones. Helpful when “bank” splits into “investment bank” and “river bank”; less useful when the result is just a lexical “the token bank” detector p. 39.

##### Why absorption matters for safety

A latent that looks like a clean “deception” or “bias” detector can have arbitrary holes in its recall. Never use a single SAE latent as a monitor without measuring its recall against a probe or labelled data.

#### Different seeds, different dictionaries

SAEs with the same architecture and data but different random seeds can learn substantially different dictionaries. Frequent, clear features tend to be stable; rare or context-specific ones vary. Often **fewer than 50%** of features are shared across seeds. So report seed stability alongside reconstruction p. 39 Paulo & Belrose.

The deeper issue is identifiability. If activations really are _h = D*z* + ε_, does training recover the true D* (up to reordering and rescaling)? Classical theory says yes when dictionary elements are close to orthogonal (low coherence). In language models, high coherence is likely unavoidable, so several different sparse decompositions can fit equally well p. 40. One proposed fix is to fine-tune the model together with an SAE whose decoder is forced to be orthogonal, which imposes low coherence by construction p. 40.

##### Three tests before trusting an SAE feature (survey)

- **Necessity:** ablate it; does the concept disappear from the output?

- **Sufficiency:** activate only it; does the concept appear?

- **Specificity:** does its effect match only its concept?

p. 40

#### PCA finds orthogonal directions of high variance, and superposition isn’t that

PCA finds an orthonormal basis ordered by explained variance. It is fast and stable, but its assumptions clash with superposition: it can only return as many directions as there are dimensions, they must be perpendicular, and variance is not the same as meaning p. 49.

Same data as Sparse Autoencoders. PCA via the 2×2 covariance matrix; a PCA direction counts as matching a feature at |cosine| above 0.95. Computed in your browser.

That matches large-scale results: on the AxBench benchmark, PCA came last among representation methods for detecting concepts (mean AUROC 0.65) Wu et al. Table 1. The survey notes PCA can still beat SAEs in some localisation settings p. 49.

#### The alternatives

| Method | Assumes | Good at | Weak at |
|---|---|---|---|
| **SAE** | sparse, linear features | open-ended discovery; fast inference | hyperparameters; identifiability |
| **NMF / semi-NMF** | non-negative, additive parts | parts-based reading; uniqueness guarantees | activations can be negative; little sparsity |
| **PCA** | variance = features | closed form; a baseline | orthogonal, at most d directions |
| **ICA** | independent sources, as many as dimensions | guarantees when assumptions hold | overcomplete case; dependent features |
| **Supervised (probe, DAS, SMDS)** | labelled concepts | targeted concepts | needs labels; discovers nothing new |
| **K-SVD** | sparse, linear features | solves sparse coding directly; a baseline | slow; no encoder |

Survey Table 6 p. 48. Recent updates: semi-NMF matched SAEs on small-scale evaluations; ICA reached SAE-level performance once implemented for this scale (Liu & Han 2026), so whether ICA is just a baseline is now open p. 49. Classical dictionary learning can still produce better dictionaries; the SAE’s main advantage is speed p. 50.

## In practice

### In practice

#### A difference of means can beat a 16k-latent SAE

AxBench compared methods on 500 concepts in Gemma-2 models Wu et al. 2025:

##### Concept detection, mean AUROC (higher is better)

difference of means

0.942

linear probe

0.940

prompting an LLM judge

0.929

SAE (feature chosen with labels)

0.917

SAE (feature by its label)

0.695

PCA

0.652

Average over Gemma-2-2B and 9B, two layers each Table 1. For _steering_, prompting beat every representation method, and difference of means beat SAEs Table 2.

The survey draws the same line: when labelled data exists, supervised directions often outperform SAEs at detection and steering, and they don’t need a dictionary size or sparsity penalty. But they need labels for every concept and cannot find anything you didn’t already name p. 50.

#### Recommendations

1. **Report failure metrics**: dead-feature percentage, duplication rate, stability across seeds, not just reconstruction.

2. **Validate causally**: necessity, sufficiency, specificity via ablation or steering.

3. **Compare with baselines**, especially for safety-critical use.

4. **Try several variants**: findings that hold across Gated, Top-k and JumpReLU are stronger evidence.

5. **Acknowledge identifiability limits**: call SAE features “one valid approximate decomposition”, not “the true features”.

6. **For known concepts, consider supervised methods** (probes, DAS), which can be more reliable (this lesson).

pp. 40–41

##### Next · 4.4

Alternatives to SAEs, and when a simple supervised direction beats them.

##### Sources for this tab

- Survey §6.5, arXiv 2611.08438, pp. 37–41.

- Chanin et al. (2025). _A is for Absorption._ NeurIPS 2025, arXiv 2409.14507.

- Gao et al. (2025). arXiv 2406.04093 (dead latents).

- Paulo & Belrose. _Sparse Autoencoders Trained on the Same Data Learn Different Features._ arXiv 2501.16615.

#### Negative results, and where SAEs still help

Two 2025 results changed how practitioners use SAEs. Kantamneni et al. (February 2025) found that, averaged over 113 datasets, probes built on SAE latents did not beat logistic-regression-based baselines in any of the four hard settings they tested, though they occasionally won on individual datasets. In March 2025 Google DeepMind's interpretability team reported that SAE-based probes lagged linear probes at detecting harmful intent when the test prompts differed from the training ones, and deprioritised basic SAE research.

SAEs remain useful for discovery, when you don't know what to look for. OpenAI used SAE-based model diffing in June 2025 to find a "misaligned persona" feature that explained why narrow fine-tuning made GPT-4o misbehave broadly (see Model Diffing).

### The answer that sounds right

#### "The SAE has a 'harmful' latent, so use it as the detector"

It sounds efficient, but absorption can leave holes: some harmful cases fire a more specific latent instead. When you know the concept and have labels, a linear probe is cheaper and, in 2025 tests, generalised better. Use the SAE to discover candidates, then build the detector with supervision.

## Say it

### When do sparse autoencoders fail, and when should you use something simpler?

#### The interviewer pushes further

Follow-up 1 of 3

How do you detect absorption?

Take a general feature, like "starts with S", and check its recall on tokens where a specific feature, like "snake", fires. If the general one goes silent there, it was absorbed.

Follow-up 2 of 3

When would you pick PCA over an SAE?

When you want the main directions of variance quickly and deterministically, for example to visualise or remove a dominant direction. PCA won't separate features in superposition.

Follow-up 3 of 3

Why did DeepMind deprioritise SAE research?

In their tests, SAE-based probes did worse than plain linear probes at detecting harmful intent on unfamiliar prompts, the downstream task they cared about.

SAEs fail in known ways: latents that never fire, duplicate features, absorption where a specific latent takes a general one's job, and different results from different seeds, partly because overlapping features can be decomposed many ways. So I'd treat SAE features as an approximation and test the ones I rely on. If I know the concept and have labels, I'd use a linear probe or a difference-of-means direction, which in recent tests beat SAE-based probes on unfamiliar data. SAEs are best for discovering what I didn't know to look for.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv 2611.08438) and 4 more sources · checked 13 Nov 2026

#### Sources

- Barez et al., Understanding AI from the Inside (survey, 2026)

- Chanin et al., A is for Absorption (2024)

- Kantamneni et al., Are Sparse Autoencoders Useful? A Case Study in Sparse Probing (2025)

- Smith, Rajamanoharan, Nanda et al. (Google DeepMind), Negative Results for SAEs on Downstream Tasks and Deprioritising SAE Research (Mar 2025)

- Wang et al., Persona Features Control Emergent Misalignment (OpenAI, 2025)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
