# AI Interpretability Practice

> 10 questions: superposition, probes, patching, SAEs, steering, lenses, circuits, editing, diffing.

- Track: AI Engineering › AI Interpretability › Scenarios
- Type: Interview · 30 min
- Page: https://aimlrounds.com/tracks/ai-engineering/interpretability-practice/
- Before this: Validating Interpretability Claims (`ai-engineering/validating-interpretability-claims`)
- Sources checked: not stated · Text last changed: 2026-11-19 · Version: 9fa45b5e9f

How to use this page

Say your answer out loud first, in about a minute, then open the answer and compare.

Question 1 · Easy · superposition

### A layer has 512 neurons, but an SAE finds thousands of interpretable features in it. How is that possible?

Answer: **Superposition: features are stored as nearly perpendicular directions, and sparsity keeps interference rare**

1. In high dimensions, far more than 512 directions can be nearly perpendicular.

2. Most features are inactive on any given input, so overlapping directions rarely collide.

3. A ReLU threshold filters the small crosstalk that's left.

The cost: single neurons become polysemantic.

Question 2 · Easy · probes

### Your probe gets 92% accuracy on real labels and 85% on a control task with random labels. What does that tell you?

Answer: **Selectivity is only 7 points, so most of the accuracy comes from the probe memorising**

1. Selectivity = real accuracy − control accuracy.

2. A low gap means the probe is powerful enough to fit almost anything.

3. Use a simpler, linear probe, and check selectivity again.

High accuracy alone never shows the representation holds the property.

Question 3 · Medium · patching

### Zero-ablating an attention head changes the logit difference by only 2%. Your colleague concludes the head doesn't matter. Do you agree?

Answer: **No: check for backup heads and use a realistic corruption first**

1. Zero ablation pushes activations off distribution.

2. Backup heads can take over when one is removed, as in the IOI circuit.

3. Patch with a minimally corrupted input, and test the head together with likely backups.

Path patching shows whether its output still reaches later heads.

Question 4 · Medium · SAE training

### 30% of your SAE's latents never fire. What would you try?

Answer: **Treat it as a training problem: resample dead latents, adjust sparsity, or switch to a variant**

1. Dead latents waste dictionary capacity.

2. Re-initialise them on inputs the SAE reconstructs badly, or add an auxiliary loss.

3. Lower the sparsity penalty, or use Top-k with an auxiliary loss for dead latents.

4. Check whether the dictionary is simply too wide for the data.

Track the dead fraction during training, not only at the end.

Question 5 · Medium · steering

### A formality steering vector works at α = 4, but at α = 12 outputs become incoherent. Why?

Answer: **Large α pushes activations far off the model's normal range**

1. The vector adds along one direction; too much makes activations unlike anything seen in training.

2. Later layers then misread them, and fluency collapses.

3. Choose α on held-out data and check general quality, not only formality.

Persona-vector work found inference-time steering can degrade general capabilities.

Question 6 · Medium · lenses

### The logit lens shows the correct answer at layer 20 of 32. Can you say the model "knew" it there?

Answer: **Only that it's decodable there; test whether later layers use it**

1. A lens is a readout you chose.

2. Patch or steer at layer 20 and see if the final answer changes.

3. Compare with the tuned lens, which is less biased in earlier layers.

Decodable ≠ used is the core caution for every readout method.

Question 7 · Hard · circuits

### A circuit recovers 115% of the full model's logit difference. Is that a great result?

Answer: **Not by itself: it means the circuit drops components that were working against the behaviour**

1. Some heads push the other way; removing them inflates the score.

2. Report necessity as well as sufficiency.

3. Name which negative components were excluded, and check across prompts.

Recovery above 100% is common and usually a sign to look closer.

Question 8 · Hard · attribution graphs

### In your attribution graph, error nodes carry 40% of the effect on the answer. How do you interpret the graph?

Answer: **The replacement model misses a large part of the computation, so the graph is a partial story**

1. Error nodes are what the transcoders failed to reconstruct.

2. Any path through them is unexplained.

3. Validate the readable paths with interventions on the real model, and say how much was unexplained.

Larger transcoders or other layers may reduce the error.

Question 9 · Hard · editing

### A ROME edit fixes "The CEO of X is …" but the model still gives the old answer to "Who runs X?". Why, and what next?

Answer: **The paraphrase routes around the edited key, or the fact is stored in more than one place**

1. ROME edits the association for one subject representation at one layer.

2. Other phrasings or layers can still recall the old fact.

3. Test edits on paraphrases, try MEMIT across layers, or use retrieval for facts that change.

Localisation doesn't predict the best edit layer (Hase et al.).

Question 10 · Hard · diffing

### A crosscoder finds 200 features specific to your fine-tuned model. How do you check which are really new?

Answer: **Compare each with the base model's features and confirm with steering**

1. Rotated old features can look model-specific.

2. Check cosine similarity with the base model's dictionary.

3. Steer the base model with each candidate; a truly new feature shouldn't have a close counterpart.

4. Prioritise features linked to the behaviour change you care about.

This is how OpenAI tied emergent misalignment to a persona feature.

**More practice and sources**

10 interview questions · answers hidden until you click · updated 13 Nov 2026

### Keep practising

Each question links back to a lesson in this part: Why Look Inside a Model?, Features, Polysemanticity and Superposition, The Residual Stream and Circuits, Linear Representations and Universality, Sparse Autoencoders, SAE Failures and Alternatives, Transcoders and Attribution Graphs, Activation Patching and Circuit Discovery, Validating Interpretability Claims, Logit Lens, Tuned Lens and Verbalisers, Probing Classifiers, Steering Vectors, Knowledge Localisation and Editing, Model Diffing, Interpretability for AI Safety.
