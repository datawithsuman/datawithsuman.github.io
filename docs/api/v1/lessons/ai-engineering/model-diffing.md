# Model Diffing

> After fine-tuning, how do you find out what changed inside the model?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/ai-engineering/model-diffing/
- Before this: Sparse Autoencoders (`ai-engineering/sparse-autoencoders`)

## Intuition

### The situation

After you fine-tune your model on a narrow task, it starts giving harmful advice in unrelated conversations. Your evaluations catch the symptom, but not why it happened. The interviewer asks:

> After fine-tuning, how do you find out what changed inside the model?

### The idea

Think of comparing two versions of a document with track changes on. The diff shows what was added or strengthened, but if a paragraph was only reworded, a naive diff marks it as brand new.

[Figure: Compare base and fine-tuned, carefully.]

_Diffing can explain why a fine-tune changed behaviour, and sometimes warn before evals do._

### Play

**Try it.** Rotate the old "sports" feature further during fine-tuning, and watch which features the diff flags as new.

#### A feature that only turned looks like one that was born

A base model with four features in a 2D toy activation space. Fine-tuning adds one genuinely new feature and **rotates** one old feature (the “sports” direction) by an angle you control. We diff with the base model’s dictionary: any fine-tuned feature with no base feature within 25° is flagged “new”.

Illustrative directions; match = largest cosine with any base feature; threshold cos 25° ≈ 0.91.

##### False positives in diffing

Crosscoders trained with an L1 penalty can invent “model-exclusive” features; BatchTopK reduces this but doesn’t remove it, because current methods “cannot distinguish between features introduced via fine-tuning and those merely represented differently” p. 79. And the reverse holds too: a feature like “confessing previous faults” appearing only in the fine-tuned model shows neither that it is used, nor that the base model lacked the means to do it p. 79.

**Notice:** past about 25°, the rotated old feature is flagged as new too, and nothing in the diff output tells them apart. Check new features against the base model's features before reporting them.

## How it works

### How it works

#### In one breath

Worrying behaviours like reward hacking and sycophancy often appear during fine-tuning, so model diffing looks for the features or circuits a training step added or amplified. Options: keep an SAE trained on the base model as a fixed yardstick, train an SAE on activation differences, or train a crosscoder that maps both models into shared features. A rotated old feature can look like a new one.

#### A spot-the-difference game played in feature space

| Method | Idea | Needs |
|---|---|---|
| **Base SAE as a fixed basis** | Encode both models’ activations with the base model’s SAE; compare feature activations on a shared prompt set | same architecture |
| **SAE on the difference** | Train an SAE or transcoder on (fine-tuned − base) activations | same architecture |
| **SAE-Track** | Initialise each checkpoint’s SAE from the previous one so features stay matched along training | a run of checkpoints |
| **Crosscoder** (Transcoders and Attribution Graphs) | Model-specific encoders into one shared feature space; a feature whose decoder is large in one model only is a candidate difference | works across architectures |
| **Transcoder diff** | Learn a correction term so the base MLP reproduces the fine-tuned MLP: diffs the _computation_, not the activations | same architecture |

Survey §9.1 p. 78. Steering with latents that fire more in the fine-tuned model has identified features responsible for misaligned behaviour p. 78.

**Was it really fine-tuning?** A feature can look new because the fine-tuning _data_ is new, not the model. Fix: fine-tune the base SAE in stages, first on base model + fine-tuning data, then fine-tuned model + base data, then fine-tuned model + fine-tuning data. Only features that appear only in the last stage are likely to come from fine-tuning p. 78.

Older similarity measures (SVCCA, PWCCA, CKA from Linear Representations and Universality) ask whether two models are _alike overall_; diffing asks which concrete features or circuits changed p. 78.

#### Diffing closed models through their answers

For closed-weight models, an LLM can compare many response pairs from the two models on a shared prompt set, then extract, cluster and summarise the differences as natural-language hypotheses. Benchmarked against an SAE baseline it matches on many dimensions and surfaces more abstract, behaviour-level differences p. 79.

Applications so far: effects of fine-tuning and distillation, differences between architectures, concept evolution during pretraining, and vision-specific features added in vision-language training p. 78.

##### Next · 9.2

Where is a fact stored? Knowledge localisation and causal tracing.

##### Sources for this tab

- Survey §9–9.1, Figure 14, arXiv 2611.08438, pp. 77–79.

## In practice

### In practice

#### Emergent misalignment, explained by diffing

Betley et al. (2025) found that fine-tuning a model on a narrow bad task, writing insecure code, made it misaligned on unrelated topics. OpenAI (June 2025) used SAE-based model diffing on GPT-4o to explain this. They found a "misaligned persona" feature whose activity rose after the bad fine-tuning. Steering towards it increased misalignment and steering away reduced it, and the feature sometimes flagged a misaligned training run before behavioural evaluations did. Fine-tuning on a few hundred benign samples re-aligned the model.

A December 2025 OpenAI follow-up reported that the bad fine-tuning also suppressed features for a helpful assistant persona. Anthropic's persona vectors (August 2025) use a similar idea to flag training data likely to shift a model's traits.

### The answer that sounds right

#### "New feature in the crosscoder, so fine-tuning taught a new behaviour"

It sounds like a finding, but a small rotation of an existing feature can appear as one specific to the new model. Check its similarity with the base model's features, and confirm it by steering before reporting it as new.

## Say it

### After fine-tuning, how do you find out what changed inside the model?

#### The interviewer pushes further

Follow-up 1 of 3

What is emergent misalignment?

Fine-tuning on a narrow bad task, like writing insecure code, makes the model misaligned across unrelated topics.

Follow-up 2 of 3

How did OpenAI fix it?

Further fine-tuning on a few hundred benign samples re-aligned the model, and the persona feature tracked the recovery.

Follow-up 3 of 3

Can you diff a model you only reach through an API?

Partly: compare output distributions on many prompts, or log-probabilities if the API exposes them. You can find what changed, but not where inside the model.

I'd diff the two models' internals. The simplest version keeps an SAE trained on the base model as a fixed yardstick and checks which features change after fine-tuning. A crosscoder trained on both models gives shared features plus ones specific to each. Then I'd steer with any suspicious feature to confirm it causes the behaviour. OpenAI used this kind of SAE diffing to find a misaligned persona feature behind emergent misalignment. The trap is that a rotated old feature can look new, so I'd check its similarity to base-model features.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv 2611.08438) and 5 more sources · checked 13 Nov 2026

#### Sources

- Barez et al., Understanding AI from the Inside (survey, 2026)

- Lindsey et al., Sparse Crosscoders (Anthropic, 2024)

- Betley et al., Emergent Misalignment (2025)

- OpenAI, Toward understanding and preventing misalignment generalization (18 Jun 2025)

- Wang et al., Persona Features Control Emergent Misalignment (OpenAI, 2025)

- Chen et al., Persona Vectors: Monitoring and Controlling Character Traits (Anthropic, 2025)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
