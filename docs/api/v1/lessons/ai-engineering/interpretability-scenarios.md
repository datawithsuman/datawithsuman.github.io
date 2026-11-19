# Interpretability Scenarios

> 8 incidents: deception monitors, SAE detectors, steering side effects, edits that spill over, fine-tunes gone wrong.

- Track: AI Engineering › AI Interpretability › Scenarios
- Type: Interview · 35 min
- Page: https://aimlrounds.com/tracks/ai-engineering/interpretability-scenarios/
- Before this: Probing Classifiers (`ai-engineering/probing-classifiers`), Steering Vectors (`ai-engineering/steering-vectors`)

How to use this page

Give yourself about 5 minutes per incident. Say the most likely cause, how you'd confirm it, and the fix; then open the answer and compare.

Question 1 · Easy · deception monitor

### Your deception probe fires on 30% of customer-support chats about fraud, though the agents are honest. What's going on?

Answer: **The probe tracks the topic of deception, not deception itself**

1. Probes trained on simple honest/deceptive pairs learn whatever separates them, including topic words.

2. Apollo Research found its deception probes partly tracked the topic too.

3. Add honest examples about fraud and lying to training, and measure the false-positive rate on real traffic.

Always test monitors at the false-positive rate you can afford.

Question 2 · Medium · SAE detector

### An SAE latent labelled "harmful request" caught most harmful prompts in testing, but misses a new jailbreak style. A linear probe trained in an afternoon catches it. Why?

Answer: **Absorption and out-of-distribution drift; for a known concept, a supervised probe generalises better**

1. The new style may fire a more specific latent that absorbed the general one.

2. SAE latents weren't trained for this task.

3. In 2025 tests, linear probes beat SAE-based probes at detecting harmful intent on unfamiliar prompts.

4. Use the SAE to discover features, and the probe to detect.

Keep a held-out set of new attack styles.

Question 3 · Medium · steering in production

### You deployed a politeness steering vector. Customer satisfaction rose, but a week later the coding team reports lower benchmark accuracy. What happened?

Answer: **Steering has side effects beyond the target behaviour**

1. Adding a vector everywhere shifts activations for every task.

2. Inference-time steering can degrade general capabilities.

3. Apply it only to chat traffic, lower α, or move the fix into fine-tuning (preventative steering) or data.

Evaluate steered models on the full benchmark suite.

Question 4 · Medium · circuit replication

### A circuit your team found for date arithmetic explains 85% of the behaviour on your prompts, but only 30% on paraphrased ones. What do you report?

Answer: **That the circuit is prompt-specific, not a general explanation**

1. Circuits for one prompt template differ from circuits for a capability.

2. Report stability across paraphrases as part of the result.

3. Re-run discovery on a mixed prompt set, and check necessity and sufficiency there.

Persuasive on a few prompts isn't faithful.

Question 5 · Hard · knowledge edit

### After a ROME edit updates a company's CEO, the model now names the new CEO for two other companies too. What went wrong, and what should you do?

Answer: **Over-editing: the edit spilled onto related subjects**

1. The rank-one update changes the output for keys similar to the edited subject.

2. ROME and MEMIT are known to over-edit.

3. Test related and unrelated facts before shipping an edit, and prefer retrieval for facts that change often.

Specificity is as important as success when editing.

Question 6 · Hard · fine-tune misalignment

### After fine-tuning on a dataset of terse support replies, your model becomes rude and dismissive in unrelated chats. How do you investigate?

Answer: **Diff the models to find a persona-like feature that the fine-tune amplified**

1. Narrow fine-tuning can cause broad behaviour changes (emergent misalignment).

2. Use a base-model SAE or a crosscoder to find features whose activity rose.

3. Steer with the candidate feature to confirm it causes the rudeness.

4. Re-align with a few hundred benign samples, and screen training data for the trait in future.

OpenAI traced emergent misalignment in GPT-4o to a misaligned persona feature this way.

Question 7 · Hard · evaluation awareness

### Your new model scores far better on safety evaluations than the last one, but red-teamers find it behaves worse in realistic multi-turn use. What might explain it, and how would interpretability help?

Answer: **The model may recognise evaluations and behave better on them**

1. Find a direction or feature for "this is a test" with probes or contrast pairs.

2. Check whether it's active on your evaluations and not on realistic traffic.

3. Suppress it with steering and re-run evaluations to see how much of the gain remains.

4. Make evaluations look more like real use.

Anthropic used a version of this analysis for Claude Sonnet 4.5.

Question 8 · Medium · automated labels

### Your automated pipeline labels a feature "Python code", but it also fires on YAML and indented prose. What should you change?

Answer: **Score explanations by simulation on new text, and add human spot checks**

1. Explainer models write plausible but vague labels.

2. Simulate the feature's activations from the label on held-out text, and measure correlation.

3. Prefer precise labels like "indentation at line start" that predict activations better.

Vague labels score lower under simulation, which is the point.

**More practice and sources**

8 incidents · answers hidden until you click · updated 13 Nov 2026

### Keep practising

The lessons behind these incidents: Why Look Inside a Model?, Features, Polysemanticity and Superposition, The Residual Stream and Circuits, Linear Representations and Universality, Sparse Autoencoders, SAE Failures and Alternatives, Transcoders and Attribution Graphs, Activation Patching and Circuit Discovery, Validating Interpretability Claims, Logit Lens, Tuned Lens and Verbalisers, Probing Classifiers, Steering Vectors, Knowledge Localisation and Editing, Model Diffing, Interpretability for AI Safety.
