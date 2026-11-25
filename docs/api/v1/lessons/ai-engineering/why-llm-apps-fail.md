# Why LLM Apps Fail: The Three Gulfs

> Your email assistant worked in the demo, and real users say it's unreliable. Where do you start?

- Track: AI Engineering › Applied Evals › Lessons
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/ai-engineering/why-llm-apps-fail/
- Before this: Prompt Engineering Patterns (`ai-engineering/prompt-engineering-patterns`)
- Quiz topic: `evals`
- Sources checked: 2026-11-15 · Text last changed: 2026-11-20 · Version: 27c6d326ea

## Intuition

### The situation

Your team shipped an email assistant after a great demo. A month later, support tickets say it's "unreliable": wrong senders, odd summaries, inconsistent formats. Your manager suggests buying an evaluation tool with a hallucination score. The interviewer asks:

> Your email assistant worked in the demo, and real users say it's unreliable. Where do you start?

#### Why it matters

An airline's support chatbot told a grieving customer he could claim a bereavement fare after travelling. The policy said the opposite. A tribunal ordered the airline to pay damages in 2024, and the bot didn't survive. Nobody had checked the bot's answers on common policy questions before customers relied on them. Interviewers ask "how would you know your LLM app works?" because most teams can't answer it. This part of the site is the answer, done the applied way: on your app, your data and your failures.

### The idea

Think of a new assistant who keeps getting your errands wrong. Sometimes they never saw the shop (they didn't know the data). Sometimes your note just said "get milk" (you didn't say which). And sometimes the note was clear and they still forgot. Only the last one needs you to start keeping score.

[Figure: Three gulfs. Know your data. Say what you want. Then measure what still fails.]

_Evals are for what survives a clear prompt._

### Play

**Try to break it.** Pick each failure and diagnose it. Which ones need an eval?

#### Which gulf is it?

A failure from the email assistant

Your diagnosis

Only one of the four failures needs an eval. Two disappear once someone reads real emails, and one disappears with a sentence in the prompt. The celebrity-name failure is the one that survives a clear prompt, so it's the one worth measuring. Teams that build evals for everything spend weeks measuring problems a prompt edit would have fixed.

**Now say why:** why build an eval for only one of the four?

## How it works

### How it works

#### In one breath

Every LLM app fails in three ways. You haven't looked at enough real inputs and outputs (**comprehension**). Your prompt doesn't say what you actually want (**specification**). Or the prompt is clear and the model still slips on some inputs (**generalization**). Fix specification problems by editing the prompt; build evals for generalization problems, because they never fully go away. The work runs as a loop: **analyze** real traces, **measure** the failures that matter, **improve**, and repeat.

#### The three gulfs

The framework comes from Shankar and colleagues, and runs through the book this part follows. Take an assistant that reads incoming emails, pulls out the sender, summarises the requests and picks a category.

| Gulf | Between | What it looks like | First fix |
|---|---|---|---|
| **Comprehension** | you and your data | You tested on clean emails. Real ones have forwarded threads, signatures in three languages and text pasted from PDFs, so the bot summarises the quoted thread. | Read real inputs and outputs. |
| **Specification** | what you want and what you wrote | "Summarise the key requests." Bullets or a paragraph? Display name or email address? Implicit requests too? The model guesses, differently each run. | Make the requirement explicit in the prompt. |
| **Generalization** | your prompt and the model's behaviour | The prompt clearly says "the sender is in the header", yet when the body mentions a famous person, the model sometimes returns that name. | Measure how often, then improve. |

##### Fix ambiguity first, then measure

The order matters. A specification failure is cheap: one sentence in the prompt fixes it, so building an automated eval for it wastes effort. Evals are for failures that remain once the prompt is clear. That's why you look before you measure.

##### The loop

1. **Analyze:** read real traces (a trace is everything that happened for one request: the input, every model and tool step, the output) and write down how the app fails.

2. **Measure:** for the failures that matter, build checks (code or an LLM judge) and get a rate you can trust.

3. **Improve:** fix the cheapest way first, then run the loop again, because every fix changes what fails next.

How much rigour you need depends on the stakes. A coding assistant's users read and test the code, so they catch many failures themselves. A personal stylist's users can't tell a bad winter-wedding suggestion from a good one, so the app must catch them.

## In practice

### In practice

#### In practice

- **Look first:** before writing any metric, read 50–100 real traces. Most teams find specification gaps in the first hour.

- **Name the gulf in reviews:** "is this a spec failure or a generalization failure?" settles arguments about whether the model is "bad".

- **Save evals for what remains:** once the prompt is clear, measure the failures that still happen.

- **Match rigour to stakes:** more checks where users can't spot mistakes themselves, or where mistakes cost money or trust.

- **Keep the loop running:** each fix shifts the failure mix, so read traces again after every real change.

### The answer that sounds right

#### "Let's buy a tool with a hallucination score"

It sounds efficient, but a generic score doesn't know your app's failures, and many of them are specification gaps a prompt edit would fix. Read your traces first, then build checks for the failures that remain.

## Say it

### Your email assistant worked in the demo, and real users say it's unreliable. Where do you start?

#### The interviewer pushes further

Follow-up 1 of 3

The model ignores an instruction 5% of the time. Spec or generalization?

First check the instruction is really unambiguous and not contradicted elsewhere in the prompt. If it is clear, it's generalization: measure the 5% with a check, and improve with examples, decomposition or a different model.

Follow-up 2 of 3

Why not build a metric for every failure you find?

Many disappear with a one-line prompt edit. An eval costs time to build, validate and maintain, so it should target failures that persist after the prompt is clear.

Follow-up 3 of 3

Which apps need the most rigorous evals?

Ones where users can't easily spot mistakes, like medical, legal or financial answers, and ones where a mistake is costly or irreversible.

#### The 30-second answer

I'd split failures into three kinds. Comprehension: we haven't looked at enough real inputs and outputs. Specification: the prompt doesn't say what we want, so the model guesses. Generalization: the prompt is clear and the model still fails on some inputs. I'd fix specification problems by editing the prompt, and build evals only for what remains, since those never fully go away. The work is a loop: analyze real traces, measure the failures that matter, improve the cheapest way, and repeat, because every fix changes what fails next.

**Key terms and sources**

The three places LLM apps break: not knowing your data, not saying what you want, and the model applying clear instructions inconsistently. How to tell them apart, and the Analyze-Measure-Improve loop that the rest of Applied Evals follows. · checked 15 Nov 2026

#### Sources

- H. Husain and S. Shankar, _Evals for AI Engineers_ (O'Reilly): the Analyze-Measure-Improve lifecycle, error analysis, judges, CI and review

- [S. Shankar et al., Steering semantic data processing with DocWrangler (the three gulfs), UIST 2025](https://arxiv.org/abs/2504.14764)

- [Moffatt v. Air Canada, 2024 BCCRT 149](https://www.canlii.org/en/bc/bccrt/doc/2024/2024bccrt149/2024bccrt149.html)

- [Anthropic, Demystifying evals for AI agents, Jan 2026](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

Explanations and examples are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and benchmark scores change quickly.
