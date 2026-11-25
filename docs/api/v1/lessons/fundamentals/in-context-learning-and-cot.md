# In-Context Learning and Chain-of-Thought

> How did 'Let's think step by step' take maths from 18% to 79%?

- Track: Fundamentals › LLMs › Generation
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/in-context-learning-and-cot/
- Before this: Decoding: Temperature, Top-k, Top-p and Min-p (`fundamentals/decoding-and-sampling`)
- Quiz topic: `llmgen`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 84c5731d80

## Intuition

### The situation

Before investing in fine-tuning, the team tries to get refund calculations right just by prompting. Asked for the answer directly, the assistant gets most of them wrong. A colleague adds examples, and it barely helps. The interviewer asks:

> How did "Let's think step by step" take maths from 18% to 79%?

**Running example:** before investing in fine-tuning, the team tries to get refund calculations right just by prompting the assistant.

#### A new task, no training budget

Fine-tuning needs labelled data, compute and a deployment for each task. Large pre-trained models can often do a task just from a description and a few examples in the prompt, which makes prototyping fast and cheap. The question is how to write that prompt, and why it works.

### The idea

Think of doing long multiplication in your head, and then being handed scratch paper. Examples show you what kind of answer is wanted, but you still have to do it all in your head. Chain-of-thought is the scratch paper: each written step is something the next one can use.

[Figure: MultiArith accuracy. Zero-shot 17.7 percent, few-shot 33.8 percent, zero-shot chain-of-thought 78.7 percent, few-shot chain-of-thought 93 percent.]

_From Kojima et al. (2022), with text-davinci-002, as shown in the lab._

### Play

**Try to break it.** Go through zero-shot, few-shot, zero-shot CoT and few-shot CoT. Compare MultiArith with GSM8K.

#### Asking for the answer directly

Prompts are shown on the running example for illustration. Accuracies are from Kojima et al. (2022), Table 2: text-davinci-002 on MultiArith and GSM8K, with Wei et al.'s 8 exemplars for the few-shot settings. Bars: MultiArith (top, orange) and GSM8K (bottom, green).

Asking for the answer straight away forces the model to compute it inside a single token: **17.7%** on MultiArith and **10.4%** on GSM8K. Eight examples help a little (**33.8%** / 15.6%) because they show the format, but still give no room to calculate. Simply adding **"Let's think step by step."** jumps to **78.7%** / 40.7%, and eight worked examples with reasoning reach **93.0%** / 48.7%. Each intermediate token is extra computation the model can condition on. Wei et al. (2022) found CoT helps mainly in large models (around 100B parameters at the time); small models wrote fluent but wrong chains.

**Now say why:** few-shot shows worked formats too, so why does adding the reasoning do so much more?

## How it works

### How it works

#### In one breath

**In-context learning (ICL)** means an LLM performs a new task from instructions and examples placed in the prompt, with **no weight updates**. GPT-3 (Brown et al. 2020) showed this improves sharply with scale. Demonstrations mainly teach the **format, label space and input distribution**: Min et al. (2022) found that even random labels in the examples cost surprisingly little. **Chain-of-thought (CoT)** prompting asks the model to write intermediate steps before the answer, which gives it room to compute: with text-davinci-002, adding "Let's think step by step" lifted MultiArith from 17.7% to 78.7% and GSM8K from 10.4% to 40.7%; eight worked examples reached 93.0% and 48.7%. Sampling several chains and voting (**self-consistency**) helps further. Reasoning models now do this internally, so prompts for them should state the goal, not the steps. What you'll be able to do after this: choose between zero-shot, few-shot and CoT prompts, explain why CoT works, and avoid common ICL pitfalls.

#### Zero-shot, few-shot, and what examples teach

- **Zero-shot:** instruction only. **Few-shot:** add k input–output examples (GPT-3 used up to ~32, limited by context). In GPT-3 the gap between zero- and few-shot grew with model size.

- **What demonstrations teach:** Min et al. (2022) replaced the gold labels in demonstrations with random ones and saw only small drops on many classification tasks; the format, the set of possible labels and the style of inputs mattered more than correct input–label mapping. (Very large models can follow flipped labels, so this varies with scale.)

- **Pitfalls:** results are sensitive to example order and choice; models favour labels that appear often or last ("majority" and "recency" bias, Zhao et al. 2021); information in the middle of long prompts is used less well (Liu et al. 2024).

## In practice

### In practice

#### Prompting in 2026

- **Self-consistency** (Wang et al. 2023): sample several chains and take the majority answer; Kojima et al. report PaLM 540B zero-shot CoT on GSM8K rising from 43.0% to 70.1% with it. See Reasoning Models for when voting helps.

- **Reasoning models** (o-series, DeepSeek-R1, Claude and Gemini thinking modes) are trained to think before answering; give them a clear goal, constraints and output format rather than step-by-step instructions or many examples.

- **For production:** keep a small set of diverse, representative examples; put instructions and key data at the start or end; ask for structured output; evaluate prompts on a labelled set like any model change.

- **When to stop prompting:** if you need consistent behaviour across thousands of examples, lower cost per call (shorter prompts) or a skill the model lacks, fine-tune instead (SFT).

**Faithfulness caveat.** A written chain of thought is not guaranteed to be the reason for the answer: studies have found models giving explanations that omit what actually influenced them (e.g. Turpin et al. 2023). Treat CoT as a useful computation aid, not a reliable explanation.

#### Give the model the format, and room to think

In-context examples tell the model what task and format you want; chain-of-thought gives it extra tokens to compute with, which is what multi-step problems need.

### The answer that sounds right

#### "The chain of thought explains the model's decision"

It sounds right, since you can read the reasoning right there. But it isn't guaranteed to be why the model answered that way. Studies found explanations that omit what actually influenced the answer. Treat CoT as a useful computation aid, not a reliable explanation. Few-shot prompting doesn't fine-tune the model either: its weights don't change.

## Say it

### How did "Let's think step by step" take maths from 18% to 79%?

#### The interviewer pushes further

Follow-up 1 of 3

Is in-context learning actually learning?

No weights change; the model infers the task from the context and conditions on it. Some theory views it as implicit Bayesian inference or as attention implementing simple learning algorithms over the examples.

Follow-up 2 of 3

Few-shot results vary a lot between runs. Why?

Sensitivity to example choice, order and label balance (majority and recency bias). Use diverse examples, balance labels, fix the order, and evaluate on a held-out set.

Follow-up 3 of 3

When does CoT not help?

Simple lookup or classification tasks, small models, and reasoning models that already think internally; it also costs extra tokens and latency.

#### The 30-second answer

In-context learning is when a model performs a task from instructions and examples in the prompt without any weight updates; it emerged strongly with scale in GPT-3. Demonstrations mostly convey the format and label space; even random labels often hurt surprisingly little. Chain-of-thought prompting has the model write intermediate reasoning before the answer, which gives it extra computation: with InstructGPT, "Let's think step by step" took MultiArith from about 18 to 79 percent, and few-shot CoT reached 93. Self-consistency samples several chains and votes. Reasoning models now generate this thinking themselves, so you prompt them with goals and constraints rather than step-by-step instructions.

**Go further**

#### What not to say

- "Few-shot prompting fine-tunes the model." Weights don't change.

- "The chain of thought explains the model's decision." It may not be faithful.

**Key terms and sources**

How LLMs learn tasks from the prompt alone: zero-shot and few-shot prompting, what demonstrations actually teach, chain-of-thought prompting (few-shot and "Let's think step by step"), self-consistency, and how reasoning models changed prompting · built from Brown et al. (GPT-3, NeurIPS 2020), Min et al. (Rethinking the Role of Demonstrations, EMNLP 2022), Wei et al. (Chain-of-Thought, NeurIPS 2022), Kojima et al. (Zero-Shot Reasoners, NeurIPS 2022), Wang et al. (Self-Consistency, ICLR 2023), Zhao et al. (Calibrate Before Use, ICML 2021) and Liu et al. (Lost in the Middle, 2024) · checked 29 Oct 2026

#### Sources

1. T. Brown et al., "Language Models are Few-Shot Learners", NeurIPS 2020, [arXiv:2005.14165](https://arxiv.org/abs/2005.14165); S. Min et al., "Rethinking the Role of Demonstrations", EMNLP 2022, [arXiv:2202.12837](https://arxiv.org/abs/2202.12837).

2. J. Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", NeurIPS 2022, [arXiv:2201.11903](https://arxiv.org/abs/2201.11903).

3. T. Kojima et al., "Large Language Models are Zero-Shot Reasoners", NeurIPS 2022, [arXiv:2205.11916](https://arxiv.org/abs/2205.11916) (Table 2).

4. X. Wang et al., "Self-Consistency", ICLR 2023, [arXiv:2203.11171](https://arxiv.org/abs/2203.11171); Z. Zhao et al., "Calibrate Before Use", ICML 2021, [arXiv:2102.09690](https://arxiv.org/abs/2102.09690).

5. M. Turpin et al., "Language Models Don't Always Say What They Think", NeurIPS 2023, [arXiv:2305.04388](https://arxiv.org/abs/2305.04388); N. Liu et al., "Lost in the Middle", TACL 2024, [arXiv:2307.03172](https://arxiv.org/abs/2307.03172).
