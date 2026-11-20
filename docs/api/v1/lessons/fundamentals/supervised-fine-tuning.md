# SFT and Instruction Tuning

> How does a text-completer become an assistant, and why mask the prompt?

- Track: Fundamentals › LLMs › Post-training
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/supervised-fine-tuning/
- Before this: The Next-Token Objective (`fundamentals/next-token-prediction`)
- Quiz topic: `post`

## Intuition

### The situation

You have a pre-trained 8B base model and 5,000 good support chats. Ask the base model a question, and it may produce more questions or a forum thread, because those are plausible continuations. The interviewer asks:

> How does a text-completer become an assistant, and why mask the prompt?

**Running example (post-training):** the team has a pre-trained 8B base model and 5,000 real support chats where human agents gave good answers. They want an assistant that answers like the best agents.

#### Base models complete text; they don't follow instructions

Pre-training teaches a model what text on the internet looks like. Asked a question, a base model may answer it, but it may also produce more questions, a forum thread, or a list of similar complaints, because all of those are plausible continuations. We need it to behave as one consistent assistant: answer the user, in the right tone and format, and stop.

### The idea

Think of a mimic who has read the whole internet and will continue any script, including playing the customer. In rehearsal, you hand over full conversations but only correct the assistant's lines. The customer's lines are for reading, not for practising.

[Figure: A training conversation. The model reads the system prompt and the customer's message with no loss on them. It is trained only on the assistant's reply, including the end token.]

_With loss on every token, 72.4% of the loss in the lab's example comes from the first two parts._

### Play

**Try to break it.** Switch between loss on all tokens and loss on assistant tokens only. Watch the tokens trained on, and the share of the loss from system and user text.

#### Train on everything, or only on the answer?

One training conversation, word-level for readability (real tokens are subwords). The number under each token is an illustrative per-token loss. User text is hard to predict ("biryani", "40"), the assistant's reply is easier once the complaint is known.

Training on **all tokens** spends **72.4%** of the loss on predicting the system prompt and the customer's complaint, text the model will never have to write. Worse, it teaches the model to imitate users (and to reproduce the same system prompt thousands of times). With **assistant-only** masking, all 14 trained tokens are the reply, including the end-of-turn token. Masking is the default in most SFT libraries; some recent work finds small gains from a little prompt loss when SFT data is tiny, but the reply is what you're teaching.

**Now say why:** what does training on the customer's text teach the model to do?

## How it works

### How it works

#### In one breath

A base model trained on next-token prediction will happily continue "My biryani is late" with another complaint. **Supervised fine-tuning (SFT)** trains it further, with the same cross-entropy loss, on example conversations written or curated to show the desired behaviour. Conversations are serialised with a **chat template**: special tokens mark the system, user and assistant turns, and the same template must be used at inference. The loss is usually **masked to the assistant's tokens**, so the model learns to write answers, not to imitate users. A few thousand high-quality examples go a long way (LIMA used 1,000; Llama 2's SFT stage used 27,540) because SFT mostly teaches **format and behaviour**, while knowledge comes from pre-training. SFT is the first post-training step, before preference tuning with RLHF or DPO. What you'll be able to do after this: explain what SFT does, set up a chat template and loss mask, and argue about data quality vs quantity.

#### Chat templates and the SFT loss

$$ \mathcal{L}_{SFT} = -{\frac{1}{\sum_t m_t}}\sum_t {m_t}\,{\log p_\theta(x_t \mid x_{<t})} $$

"Completion-only" or "assistant-only" loss in libraries such as Hugging Face TRL. The model still _reads_ the prompt; it just isn't trained to predict it.

- **loss mask**: m_t = 1 for tokens the assistant wrote, 0 for system and user tokens (and padding). Only masked-in tokens contribute.

- **next-token cross-entropy**: Exactly the pre-training loss: −log probability of the true next token given everything before it, including the user’s message.

- **average over trained tokens**: Divide by the number of assistant tokens, so long prompts don’t change the scale of the loss.

- **Chat template:** each model family defines special tokens, e.g. Llama 3 uses `<|start_header_id|>user<|end_header_id|>` … `<|eot_id|>`. Training and inference must use the identical template, or quality drops sharply.

- **The end token matters:** the assistant turn ends with an end-of-turn token that _is_ trained, which teaches the model when to stop.

## In practice

### In practice

#### Quality over quantity

- **InstructGPT** (Ouyang et al. 2022) fine-tuned GPT-3 on about 13k labeller-written demonstrations before RLHF. FLAN (Wei et al. 2022) showed that instruction tuning on many tasks phrased as instructions improves zero-shot performance on unseen tasks.

- **LIMA** (Zhou et al. 2023): a 65B model fine-tuned on just **1,000** carefully curated examples was rated equivalent or better than GPT-4 in 43% of comparisons. Its "superficial alignment hypothesis": knowledge comes from pre-training; alignment mostly teaches format and style. Later work argues this is an oversimplification for reasoning and factual tasks.

- **Llama 2** stopped at 27,540 high-quality SFT annotations, finding they beat millions of lower-quality third-party examples. Llama 3 mixes human data with large amounts of filtered synthetic data generated by earlier models.

- **Risks:** fine-tuning only on support chats can erode general skills (catastrophic forgetting) and safety behaviour; mix in general instruction data, keep epochs low (2–3), and use a small learning rate. Parameter-efficient methods like LoRA are covered in AI Engineering › Fine-tuning.

For what fine-tuning can do to safety, read Safety Training and Jailbreaks.

#### Show the behaviour you want, and train only on it

SFT is ordinary next-token training on demonstrations of the target behaviour, with the loss restricted to the assistant's tokens; it changes how the model uses what it already knows far more than what it knows.

### The answer that sounds right

#### "More SFT data is always better"

It sounds right, since more data helped in pre-training. But LIMA's 1,000 curated examples were rated equal or better than GPT-4 in 43% of comparisons, and Llama 2 found 27,540 good annotations beat millions of lower-quality ones. SFT doesn't use a different loss either: it's the same cross-entropy, masked.

## Say it

### How does a text-completer become an assistant, and why mask the prompt?

#### The interviewer pushes further

Follow-up 1 of 3

Why not stop after SFT?

SFT can only imitate the demonstrations; it doesn't learn which of two acceptable answers people prefer, and it can't exceed the demonstrators. Preference tuning optimises for what humans or verifiers judge better.

Follow-up 2 of 3

Your fine-tuned model rambles and never stops. Likely cause?

The end-of-turn token wasn't in the training targets (masked out or missing from the template), or inference uses a different template or stop token.

Follow-up 3 of 3

Can SFT teach the model new facts?

Somewhat, but it's inefficient and can increase hallucination: Gekhman et al. (2024) found that fine-tuning on facts the model didn't already know makes it more likely to hallucinate. Use retrieval or continued pre-training for knowledge.

#### The 30-second answer

SFT, or instruction tuning, continues training a pre-trained model with the same next-token cross-entropy on example conversations that demonstrate the desired behaviour. Conversations are formatted with a chat template using special tokens for system, user and assistant turns, and the loss is masked so only the assistant's tokens, including the end-of-turn token, are trained. Data quality matters more than quantity: LIMA got strong results from 1,000 curated examples and Llama 2 used about 27k, because SFT mainly teaches format and behaviour on top of pre-trained knowledge. It's usually followed by preference tuning, RLHF or DPO.

**Go further**

#### What not to say

- "SFT uses a different loss." It's the same cross-entropy, masked.

- "More SFT data is always better." Quality and diversity beat volume.

**Key terms and sources**

How a pre-trained base model that only continues text becomes an assistant that follows instructions: supervised fine-tuning on demonstration conversations, chat templates and special tokens, masking the loss to the assistant's tokens, how much data is enough (quality over quantity), and what SFT can and can't teach · built from Ouyang et al. (InstructGPT, NeurIPS 2022), Wei et al. (FLAN, ICLR 2022), Zhou et al. (LIMA, NeurIPS 2023), Touvron et al. (Llama 2, 2023), Hugging Face TRL docs and Meta's Llama 3 report (2024) · checked 29 Oct 2026

#### Sources

1. L. Ouyang et al., "Training language models to follow instructions with human feedback" (InstructGPT), NeurIPS 2022, [arXiv:2203.02155](https://arxiv.org/abs/2203.02155).

2. J. Wei et al., "Finetuned Language Models Are Zero-Shot Learners" (FLAN), ICLR 2022, [arXiv:2109.01652](https://arxiv.org/abs/2109.01652).

3. C. Zhou et al., "LIMA: Less Is More for Alignment", NeurIPS 2023, [arXiv:2305.11206](https://arxiv.org/abs/2305.11206).

4. H. Touvron et al., "Llama 2: Open Foundation and Fine-Tuned Chat Models", 2023, [arXiv:2307.09288](https://arxiv.org/abs/2307.09288); Llama Team, "The Llama 3 Herd of Models", 2024, [arXiv:2407.21783](https://arxiv.org/abs/2407.21783).

5. Z. Gekhman et al., "Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?", EMNLP 2024, [arXiv:2405.05904](https://arxiv.org/abs/2405.05904); Hugging Face TRL, SFTTrainer documentation.
