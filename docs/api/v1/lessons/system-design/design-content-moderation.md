# Design AI Content Moderation

> A platform gets billions of chat messages and hours of voice every day. Design moderation that blocks harmful content fast, without silencing normal users, and knows when a person must decide.

- Track: System Design › Trust and Safety › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-content-moderation/
- Before this: Guardrails and Prompt Injection (`ai-engineering/guardrails-and-prompt-injection`), Classification Metrics (`fundamentals/classification-metrics`)
- Quiz topic: `sdllm`
- Sources checked: 2026-11-05 · Text last changed: 2026-11-20 · Version: 0783795d9a

## Intuition

### The situation

A social gaming platform has 100 million daily users who send a billion chat messages and hundreds of thousands of hours of voice a day, in 20 languages, many of them children. Harmful content must be stopped fast, without silencing normal players. The interviewer asks:

> A platform gets billions of chat messages and hours of voice every day. Design moderation that blocks harmful content fast, without silencing normal users, and knows when a person must decide.

#### Ask before designing

- **Content types:** text chat, voice, images, uploaded items? Each has different speed needs and options.

- **Policies:** harassment, hate, sexual content, personal information, self-harm, scams. Who defines them, and how often do they change?

- **Scale:** say 1 billion messages and 200,000 hours of voice a day, in 20 languages.

- **Speed:** block text before others see it; act on voice within seconds; handle legal reports within minutes.

- **Must never happen:** severe harm to children getting through, or large numbers of normal users silenced for harmless messages.

- **Success metrics:** precision and recall per policy, user reports per hour of use, appeal overturn rate, and time to action.

### The idea

Think of security at a huge stadium. Scanners at every gate check everyone in a second, guards watch screens for trouble that develops, and only the hard cases go to the supervisor. The rulebook is written by people who agree on what counts as a weapon.

[Figure: Every message passes fast classifiers in milliseconds. Voice is checked within seconds. Bigger models review flagged items with context, and people take the hard calls and appeals.]

_Fast models take the volume; people take the judgement calls._

### Play

**Try to break it.** Drag the threshold from 0.9 down to 0.6. Then turn review off.

#### What happens when you move the threshold?

Illustrative: 1 billion messages a day, 0.2% harmful, and made-up score curves. Real systems tune a threshold per policy, since a missed threat is worse than a missed rude word.

Drag the threshold down: fewer harmful messages get through, but far more harmless ones are blocked. Now look at the review queue: millions a day, far more than people can handle. Turn review off, and harm gets through instead. That's why real systems use **separate thresholds per policy**, lean towards fewer misses for severe harm, and keep improving the models so the uncertain band shrinks.

**Now say why:** why can't you just send every uncertain message to a person?

## Architecture

### Architecture

#### In one breath

Moderation is a **volume and latency** problem first. Text must be checked in **milliseconds**, so use **many small, specialised models**, distilled and quantized, rather than one big LLM on every message. Voice is checked within seconds and handled with warnings. Policy experts write **golden sets** that define what counts as a violation. Thresholds trade wrongly blocked users against missed harm, and **people** handle rare, nuanced cases and **appeals**, whose outcomes become new training data.

#### Tiers, by speed and severity

1. **Real-time text filter:** every message passes through specialised models, one per policy type such as personal information or harassment, before delivery. They must answer in milliseconds.

2. **Near-real-time voice:** audio clips are classified within seconds. You can't un-hear speech, so the response is an on-screen warning, then short suspensions for repeat offenders.

3. **Slower, deeper checks:** bigger models, including LLMs with conversation context, review flagged items and patterns over time, such as grooming signals across many messages.

4. **Human review:** rare, ambiguous or severe cases, investigations and appeals go to trained moderators, with the highest-risk cases first.

5. **Feedback:** appeals that are overturned and user reports become labelled training data.

##### Why not one LLM for everything?

At hundreds of thousands of requests per second, a large LLM on every message is far too slow and expensive. Small, distilled and quantized classifiers handle the volume; LLMs are used where context matters, on a much smaller stream.

##### Policy as data

Policy experts hand-pick clear examples of what should and shouldn't be caught, a golden set, which is used for training and evaluation. If moderators disagree on more than about one in five labels, the policy itself is probably unclear.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Average text load | 1 billion ÷ 86,400 seconds | **about 12,000 per second** |
| Peak text load | 12,000 × 4 × 5 models per message | **about 240,000 model calls a second** |
| Voice clips per second | 200,000 hours × 3,600 ÷ 15 s clips ÷ 86,400 | **about 560** |
| Human reviews a day | 1 billion × 0.05% sent to review | **about 500,000** |

Half a million reviews is thousands of moderators, so the human queue must be tiny compared with the stream. Every point of precision gained in the uncertain band saves real people's time.

## In practice

### In practice

#### What every moderation design gets asked

- **Latency:** distil large models into small ones, quantize them, separate tokenisation from inference, and serve on GPUs. Text must finish in milliseconds.

- **Context:** a single message can look harmless while the conversation isn't. Use conversation context in the slower tier, and detect patterns across messages and users.

- **Evasion:** users misspell, use symbols or switch languages. Use AI-assisted red teaming to generate evasion attempts, and add them to training.

- **Many languages:** train with machine-labelled data at scale plus a smaller human-labelled set, and report recall per language.

- **When to automate:** only automate a decision where the model beats people on both precision and recall at scale; keep people for nuance, investigations and appeals.

- **Appeals:** every automated action should be appealable, and overturned decisions become training examples.

- **Feedback to users:** a warning that explains the rule often changes behaviour more than a silent block.

##### Rollout

Run a new model in shadow mode, compare its decisions with the current system and with the golden set, then switch on one policy and one language at a time.

#### What the real system reported

- **Scale:** an average of 6.1 billion chat messages and 1.1 million hours of voice a day, in 28 languages; text filters handling more than 750,000 requests per second, blocking within milliseconds.

- **Models:** many purpose-built transformer models, distilled and quantized; separating tokenisation from inference quadrupled throughput for the personal-information filter.

- **Policy and labels:** golden sets hand-curated by policy experts; if moderators agree on 80% or more of labels, the policy is clear enough. Models are tuned for fewer false negatives.

- **Voice:** a classifier acting within 15 seconds, with on-screen warnings and appeals. A 2026 version grew to 320M parameters, distilled to stay real-time, reporting 61% recall at a 1% false positive rate. Abuse reports per hour of speech dropped over 50% after notifications launched in the US.

- **People:** AI only where it beats humans on precision and recall at scale; people for rare cases, investigations and appeals. Median time to action on illegal-content notices: ten minutes.

The company's own figures, from the two posts above.

### The answer that sounds right

#### "Use one big LLM to judge every message"

It sounds right, since LLMs understand context and nuance. But at hundreds of thousands of messages a second with a millisecond budget, it's far too slow and expensive. Use small specialised classifiers for the stream, and LLMs with context only on the much smaller set of flagged items.

## Say it

### A platform gets billions of chat messages and hours of voice every day. Design moderation that blocks harmful content fast, without silencing normal users, and knows when a person must decide.

#### The interviewer pushes further

Follow-up 1 of 3

Why not run a big LLM on every message?

At hundreds of thousands of requests per second with a budget of milliseconds, it's far too slow and expensive. Small specialised classifiers handle the volume; LLMs add value where context matters, on a much smaller stream of flagged items.

Follow-up 2 of 3

Recall is great in English but poor in Thai. What do you do?

Report and set targets per language, add native-speaker golden sets and human labels for that language, use machine-labelled data for scale, and red-team in that language. Until recall improves, send more Thai content to review.

Follow-up 3 of 3

Users keep finding new spellings to evade the filter. How do you keep up?

Use AI-assisted red teaming to generate variants, mine user reports and overturned appeals for new patterns, retrain regularly, and add context-aware checks that look at the conversation, not just the word.

#### The 30-second answer

First I'd clarify the content types, policies, languages, volume and speed limits. I'd tier the system by speed. Every text message passes through small specialised classifiers, one per policy, distilled and quantized so they answer in milliseconds before delivery. Voice is classified within seconds; since speech can't be un-heard, the response is a warning, then short suspensions. A slower tier with larger models and conversation context reviews flagged items and patterns across messages. People handle ambiguous and severe cases, investigations and appeals, with the riskiest first. Policy experts maintain golden sets that define each policy and are used for training and evaluation, and low moderator agreement tells me a policy is unclear. Thresholds are set per policy, leaning towards fewer misses for severe harm. Red teaming generates evasion attempts, recall is reported per language, and overturned appeals become training data. New models run in shadow mode before going live, one policy and language at a time.

**Key terms and sources**

Based on a gaming platform's published posts: [Roblox's "How Roblox Uses AI to Moderate Content on a Massive Scale"](https://about.roblox.com/newsroom/2025/07/roblox-ai-moderation-massive-scale) (July 2025) and its [voice safety classifier update](https://about.roblox.com/newsroom/2026/06/upgrading-voice-safety-classifier-22-languages-sharper-detection-capabilities) (June 2026). The lab's numbers and the estimate are ours. Uses guardrails, quantization and human-in-the-loop design. · checked 5 Nov 2026
