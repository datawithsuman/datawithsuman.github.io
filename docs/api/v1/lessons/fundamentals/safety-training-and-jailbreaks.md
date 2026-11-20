# Safety Training and Jailbreaks

> How are LLMs trained to refuse, why do jailbreaks still work, and how do you defend a model?

- Track: Fundamentals › LLMs › Post-training
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/safety-training-and-jailbreaks/
- Before this: SFT and Instruction Tuning (`fundamentals/supervised-fine-tuning`), Reward Models and RLHF (PPO) (`fundamentals/rlhf-and-reward-models`)
- Quiz topic: `post`

## Intuition

### The situation

You've fine-tuned an open model for support, and a red-team test finds it now answers things it used to decline. Meanwhile, customers complain it refuses to explain how to "kill" a running order. You've been asked to fix both. The interviewer asks:

> How are LLMs trained to refuse, why do jailbreaks still work, and how do you defend a model?

#### Why it matters

Guardrails and prompt injection covers defences in an application. This lesson covers what happens in the model itself. It matters for anyone who fine-tunes a model, because that can change how it behaves on safety, whatever the training data was about.

### The idea

Think of security at a building. A guard has been trained on a list of situations, and also told to be helpful to visitors. A smooth request can set those two against each other, and someone in an unusual disguise may not match anything on the list. A strict guard turns away real visitors too. So buildings use several checks, rather than one perfect guard.

[Figure: Three layers. Train the model. Check inputs and outputs. Limit what the system can do.]

_No single layer is enough._

### Play

**Try to break it.** Move the threshold. Then switch to disguised requests, and add the output check.

#### Set the threshold

Illustrative, exact calculation with invented bell curves. Safe scores centre on −1.2, harmful on +1.2 and disguised harmful on −0.2, each with a standard deviation of 1. The output check is a second, independent score that reads the answer, so disguising the request doesn't fool it. It uses the same threshold, plus 1, so it blocks fewer safe answers.

At a threshold of 0, 11.5% of harmful requests get through, and 11.5% of safe ones are refused. Now switch to **disguised** requests: the same threshold lets 57.9% through. To get back to 11.5% with the threshold alone, you'd have to move it to about −1.4, which refuses 57.9% of safe requests. That's the trap of relying on one score. Back at 0, add the **output check**: disguised requests fall to 24.4%, and safe refusals rise only to 12.7%. A second, different signal helps far more than moving one threshold.

**Now say why:** why does a second check beat moving the threshold?

## Maths

### Maths

#### In one breath

Safety is mostly learned behaviour, trained with the same SFT and RLHF methods as everything else. So it can fail like other learned behaviour. **Competing objectives:** the goals of being helpful and being safe can pull against each other. **Mismatched generalisation:** the model's abilities reach further than its safety training did. There's also a trade-off, as refusing more also blocks more harmless requests, known as **over-refusal**. Fine-tuning can weaken safety, even by accident. So real systems use several layers, and measure both kinds of error.

#### How safety is built, and why it breaks

##### How models learn it

| Method | What it does |
|---|---|
| **Safety data in SFT and RLHF** | Examples and preferences that show when and how to decline |
| **Constitutional AI** | The model critiques and revises its own answers against written principles, then trains on AI preferences, with no human labels for harm |
| **Red teaming** | People or other models look for failures, which become new training data and tests |

Red teaming works, though not completely. In one study of 38,961 attacks, RLHF models got harder to red team as they grew, while other model types stayed flat.

##### Why training fails

Wei et al. proposed two failure modes:

- **Competing objectives:** the model is trained to be helpful and to be safe, and a request can set the two against each other.

- **Mismatched generalisation:** the model can understand far more kinds of input than its safety training covered, so a harmful request in an unusual form may not trigger the trained behaviour.

Automated search also works. Zou et al. found text suffixes by gradient search on open models, and these sometimes carried over to other models. So fixing one prompt doesn't fix the problem.

##### Safety can be shallow

| Finding | What it showed |
|---|---|
| Fine-tuning | Safety fell after 10 adversarial examples, costing under $0.20. Ordinary, harmless datasets weakened it too, though less |
| Refusal direction | In 13 open models, refusal could be switched off or on through one direction in the activations |
| Emergent misalignment | Fine-tuning on insecure code led to broadly bad behaviour on unrelated prompts |
| Sleeper agents | A deliberately planted backdoor survived standard safety training, and adversarial training could teach the model to hide it better |

The last two come from controlled research settings. They show what's possible, not how often it occurs in deployed models.

#### The maths

$$ {\text{refused safe}} = {P(s > t \mid \text{safe})}, \qquad {\text{harmful answered}} = {P(s \le t \mid \text{harmful})} $$

A simple way to frame the trade-off, as in any classifier. Real safety behaviour isn’t a single score, but the same tension applies.

- **over-refusal**: Harmless requests the system wrongly declines.

- **the same threshold**: s is a risk score. Lowering t refuses more of everything.

- **missed harm**: Harmful requests that get through.

- **the other side of the trade**: Raising t lets more through. You can’t improve both by moving t alone. You need a better score.

## In practice

### In practice

#### Defending a model

- **Use layers:** combine model training, input and output classifiers, tool permissions and monitoring. One classifier approach, trained on synthetic data from written rules, withstood over 3,000 estimated hours of red teaming in its early form. A later version added 0.38 points to refusals and 23.7% to inference cost.

- **Measure both errors:** test harmful prompts, and also harmless ones that sound risky. XSTest has 250 safe prompts and 200 unsafe contrasts for this.

- **Re-test after every fine-tune:** run the same safety and over-refusal tests before and after, even with harmless data. Mix safety examples into the training set.

- **Limit what's at stake:** a model with no access to refunds can't be talked into issuing one. See agent safety.

- **Open weights change things:** anyone with the weights can fine-tune safety away, so provider-side filters don't apply. Plan your own safeguards.

### The answer that sounds right

#### "We passed the safety test before fine-tuning, so we're safe"

It sounds right, as the base model was tested and your data was harmless. But fine-tuning can weaken safety even on harmless data, as Qi et al. found. Treat every fine-tune as a new model: re-run the safety and over-refusal tests before release, and keep a separate output check.

## Say it

### How are LLMs trained to refuse, why do jailbreaks still work, and how do you defend a model?

#### The interviewer pushes further

Follow-up 1 of 3

You fine-tune on harmless support chats and safety scores drop. Why, and what do you do?

Safety behaviour can be fragile, and training on a narrow task can shift the model away from it. Qi et al. saw this with harmless datasets. Mix in safety examples, lower the training intensity, re-test before release, and add an output classifier as a backstop.

Follow-up 2 of 3

Your model now refuses "how do I kill a Python process?". What's wrong?

That's over-refusal: it's reacting to a word rather than the meaning. Add safe prompts that sound risky to your tests and training data, as in XSTest, and track the over-refusal rate along with safety.

Follow-up 3 of 3

Why not just block the known jailbreak prompts?

They change easily, and automated search can produce new ones. Blocking helps as a patch, but you need defences that don't depend on the wording, such as checking the output, and limiting what the system can do.

#### The 30-second answer

Safety is learned with the same methods as other behaviour: SFT, RLHF and methods like Constitutional AI, with red teaming to find failures. It fails in two main ways. Helpfulness and safety can compete, and the model's abilities can reach further than its safety training, so unusual inputs get past it. It can also be shallow, as fine-tuning on even harmless data can weaken it. There's a trade-off too, since refusing more means blocking more safe requests, so I'd always measure both harmful answers and over-refusal. In a product I'd use layers: model training, input and output classifiers, limited tool permissions and monitoring, and I'd re-run the safety tests after every fine-tune.

**Key terms and sources**

How safety is trained, red teaming, why safety training fails, over-refusal, how fine-tuning weakens safety, and layered defences. · checked 7 Nov 2026

#### Sources

- [Wei et al., Jailbroken](https://arxiv.org/abs/2307.02483)

- [Zou et al., Universal and Transferable Adversarial Attacks](https://arxiv.org/abs/2307.15043)

- [Bai et al., Constitutional AI](https://arxiv.org/abs/2212.08073)

- [Perez et al., Red Teaming Language Models with Language Models](https://arxiv.org/abs/2202.03286)

- [Ganguli et al., Red Teaming Language Models to Reduce Harms](https://arxiv.org/abs/2209.07858)

- [Qi et al., Fine-tuning Aligned Language Models Compromises Safety](https://arxiv.org/abs/2310.03693)

- [Arditi et al., Refusal Is Mediated by a Single Direction](https://arxiv.org/abs/2406.11717)

- [Betley et al., Emergent Misalignment](https://arxiv.org/abs/2502.17424)

- [Hubinger et al., Sleeper Agents](https://arxiv.org/abs/2401.05566)

- [Röttger et al., XSTest](https://arxiv.org/abs/2308.01263)

- [Sharma et al., Constitutional Classifiers](https://arxiv.org/abs/2501.18837)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
