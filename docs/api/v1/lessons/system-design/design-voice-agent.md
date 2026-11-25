# Design a Voice AI Agent

> Customers call a support line, and an AI agent answers. Design it so it responds fast enough to feel natural and can still look up orders and take actions.

- Track: System Design › LLM Apps and Chatbots › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-voice-agent/
- Before this: Tool and Function Calling (`ai-engineering/tool-calling`), Serving Metrics and SLOs (`ai-engineering/serving-metrics-and-slos`)
- Quiz topic: `sdllm`
- Sources checked: 2026-11-05 · Text last changed: 2026-11-20 · Version: e4e886bdf4

## Intuition

### The situation

A retailer wants an AI agent to answer its customer support line. Callers ask about orders, returns and deliveries, and the agent must look things up and sometimes make changes. Say 20,000 calls a day. Callers hang up if the line goes quiet too long. The interviewer asks:

> Customers call a support line, and an AI agent answers. Design it so it responds fast enough to feel natural and can still look up orders and take actions.

#### Ask before designing

- **Callers and jobs:** what do people call about? Order status, returns, changing a booking? Which of these can the agent finish alone?

- **Actions:** read-only lookups, or real changes like refunds? Changes need confirmation and limits.

- **Scale:** say 20,000 calls a day, peaking at 300 at the same time, in two languages.

- **Feel:** how long can the agent stay silent before callers think it's broken? Can callers interrupt it?

- **Must never happen:** acting on a misheard number, trapping a caller who wants a person, or reading out private data to the wrong caller.

- **Success metrics:** calls resolved without a person, correct hand-offs, time to first useful audio, and caller satisfaction.

### The idea

Think of a good call-centre worker. They know when you've finished talking without waiting for an awkward pause, start checking your order while you're still explaining, and say "one moment, pulling that up" only when they really are. They never act on an order number until they've read it back.

[Figure: The caller speaks. A model decides they've finished. Lookups and checks run in parallel. Speech starts from the first sentence. Every stage is timed.]

_Silence is the enemy, but filler isn't the fix._

### Play

**Try to break it.** Start with everything off and read the breakdown. Turn on each fix. Then drag the end-of-speech wait down to 200 ms.

#### How long is the caller left in silence?

**Where the time goes**

Illustrative timings we made up for the interview, not figures from the post: lookup 450 ms, retrieval 300 ms, planning 400 ms (150 ms small), answer first sentence 350 ms, full answer 1,200 ms, speech 200 ms to first audio. Cut-offs grow as the wait drops below 500 ms.

Start with everything off and read the breakdown. Then turn on each fix. Parallel lookups and streaming help most, because they remove waits rather than speed anything up. Now drag the end-of-speech wait down: it saves time, but past a point the agent **talks over people who only paused**. That's why a better end-of-speech model, rather than a shorter timer, is worth building.

**Now say why:** why does a shorter silence timer make the agent feel worse, not better?

## Architecture

### Architecture

#### In one breath

A voice agent is judged by **silence**. Measure the time from when the caller stops speaking to when the agent says something **useful**, not just "uh-huh". Spend that budget carefully: detect the end of speech quickly, run lookups **in parallel**, use small models for small jobs, and **stream** speech as soon as the first words are ready. Keep separate speech-to-text, LLM and text-to-speech steps, so the agent can still call your systems and you can see where time goes.

#### One turn of the conversation

1. **Hear:** audio streams in, and speech-to-text transcribes it as the caller talks.

2. **Decide they've finished:** an end-of-speech model judges when the turn is over. Waiting for a fixed silence is slow; guessing too early cuts people off.

3. **Think in parallel:** the agent runs checks, retrieval and system lookups at the same time, and only waits where one step needs another's result.

4. **Speak while thinking:** text-to-speech starts on the first sentence while the rest is still being written.

5. **Listen while speaking:** if the caller talks over the agent, stop the audio and handle the new turn.

##### Why separate steps, not one voice-to-voice model?

A single speech-in, speech-out model can be quick and natural. But a support agent must call order systems, follow policies and be debuggable. Separate steps give you text you can check, log and act on, and a timing breakdown for each stage. You can still combine steps later where it's safe.

##### Small models for small jobs

Not every step needs the biggest model. Summarising the call so far or updating state can use a small fast model, and only real reasoning goes to a larger one.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Concurrent calls at peak | given | **300** |
| Turns per minute per call | about one every 10 seconds | **6** |
| LLM calls per second at peak | 300 × 6 ÷ 60 × 3 calls per turn | **about 90** |
| Audio streams to transcribe and speak | one in and one out per call | **600 live streams** |
| Minutes of calls a day | 20,000 × 4 minutes | **80,000 minutes** |

The hard part isn't raw volume, it's keeping hundreds of streams under tight, steady latency. So the tail matters: a p95 of three seconds feels broken even if the median is fine.

## In practice

### In practice

#### What every voice design gets asked

- **Tail latency:** send the same request to two model providers and use the first valid reply. It costs more, but cuts the slow outliers callers remember.

- **Filler isn't an answer:** "uh-huh" hides silence but doesn't help. Use short, specific progress messages like "Let me pull up your order" only while real work runs, and measure time to the first useful words.

- **Interruptions:** stop speaking the moment the caller talks, keep what was already said in the history, and treat the interruption as a new turn.

- **Mishearing:** read back key details, like an order number or an amount, before acting. Speech-to-text errors on numbers are common and costly.

- **Hand-off:** always let callers reach a person. Pass a summary and the call history so they don't have to repeat themselves.

- **Safety and privacy:** verify the caller before reading out account details, and confirm any change before making it.

- **Observability:** trace every turn with timing for each stage, so you can compare providers and catch slowdowns after a change.

##### Rollout

Start with one simple, high-volume call reason, like order status, with easy hand-off. Listen to recordings, add reasons one at a time, and only then allow actions that change things.

#### What the real system reported

- **The metric:** time to first audio, measured from the true end of the caller's speech, and judged on the first relevant response rather than filler.

- **End of speech:** a custom model trained for noisy, multi-speaker audio, which they say cut reaction lag by hundreds of milliseconds compared with off-the-shelf options.

- **Reasoning as a concurrent graph:** abuse checks, retrieval and API calls in parallel; prefetching likely next steps; small models for summaries and state; provider hedging, where the fastest valid reply wins; and context-aware progress messages.

- **Speech:** cached common phrases, playback from the first tokens, and sentence-by-sentence delivery for providers that don't stream.

- **Why separate steps:** enterprise work needs reliability, capability and observability, and "you still can't make an API call to a system of record with voice tokens".

From the company's post. It gives no target or measured latency, and doesn't cover interruptions or hand-off to people; those parts of this design are ours.

### The answer that sounds right

#### "Fill the silence with 'uh-huh' and it feels fast"

It sounds right, since filler stops the line going quiet. But callers notice when nothing useful follows, and a metric that counts filler as a response hides the real delay. Measure time to the first useful words, cut real waits with parallel work and streaming, and use short, specific progress messages only while real work runs.

## Say it

### Customers call a support line, and an AI agent answers. Design it so it responds fast enough to feel natural and can still look up orders and take actions.

#### The interviewer pushes further

Follow-up 1 of 3

Why not just shorten the silence timer to save time?

Because people pause mid-sentence. A short timer makes the agent talk over them, which feels worse than a small delay. A model that predicts the end of a turn from the words and the audio can respond sooner when the caller has clearly finished, and wait when they haven't.

Follow-up 2 of 3

Would you use a speech-to-speech model instead?

For casual chat, maybe. For support, I need text I can log, check against policy and use to call systems, and a timing breakdown per stage. So I'd keep separate steps, and only merge them where I can still meet those needs.

Follow-up 3 of 3

The agent mishears an order number and cancels the wrong order. How do you prevent it?

Read back the number and the action, and wait for a clear yes before any change. Check the order belongs to the verified caller. Make changes reversible where possible, and log every action with the transcript, so mistakes can be traced and undone.

#### The 30-second answer

First I'd clarify the call reasons, which actions the agent may take, the volume and how quickly it must respond. The key metric is time to the first useful audio after the caller finishes. Audio streams through speech-to-text, and an end-of-speech model decides when the turn is over, because a fixed silence timer is either slow or cuts people off. The agent then works as a graph, not a chain: lookups, retrieval and safety checks run in parallel, small models handle small jobs, and I'd prefetch the caller's recent orders at the start. Text-to-speech streams from the first sentence, common phrases are cached, and a short, specific progress message covers real waits. I'd keep separate speech, LLM and speech steps so the agent can call our systems and every stage is traced. For tail latency I'd hedge across providers. The agent reads back numbers before acting, verifies the caller before sharing data, handles interruptions, and can always hand off to a person with a summary. I'd roll out one call reason at a time.

**Key terms and sources**

Based on a customer-service AI company's published engineering post: [Sierra's "Engineering low-latency voice agents"](https://sierra.ai/blog/voice-latency) (October 2025). The post gives no latency targets or measured times, so the lab's numbers, the estimate, barge-in and hand-off come from our own knowledge. Uses tool calling, serving metrics and human-in-the-loop design. · checked 5 Nov 2026
