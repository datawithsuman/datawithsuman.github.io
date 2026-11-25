# LLM API Reliability: Rate Limits, Retries and Fallbacks

> Your provider starts returning overload errors at peak time, and your retries make it worse. How do you design calls to an LLM API so they fail gracefully?

- Track: AI Engineering › LLMOps › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/llm-api-reliability/
- Before this: Cost and Latency: Routing, Caching and Batching (`ai-engineering/cost-and-latency`)
- Quiz topic: `llmops`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: 4f8b7b29a5

## Intuition

### The situation

At peak time, your LLM provider starts returning overload errors. Your app retries in the SDK, in your wrapper and in the browser. Within minutes, your traffic to the provider triples, and nearly everything fails. The interviewer asks:

> Your provider starts returning overload errors at peak time, and your retries make it worse. How do you design calls to an LLM API so they fail gracefully?

#### Why it matters

An LLM call is a network call to a shared service with limits. At launch or peak, you'll meet rate limits and overload errors, and a long streaming answer can stall halfway. Retry logic that seems harmless in one function can multiply load across a system. Interviewers ask this in design rounds for chatbots and agents, where one user action can mean many model calls.

### The idea

Think of a crowd outside a full restaurant. If everyone knocks again every few seconds, and asks their friends to knock too, nobody gets in faster and the staff can't work. Wait your turn, knock once in a while, or go somewhere else you've tried before.

[Figure: Three rules. Retry the right errors, at one layer. Cap retries with a budget. Fall back to something tested.]

_Retries help with blips, and hurt in outages._

### Play

**Try to break it.** Use 3 layers and 3 retries in an outage. Then retry at one layer only.

#### Retry storms

Exact arithmetic, assuming each call fails independently with the chosen probability. Real outages are correlated, which makes retries help even less.

With 3 retries at each of 3 layers, an outage turns each user action into 64 calls to the provider, and every one still fails. Retry at **one layer only**, and it's 4 calls, with the same outcome for users. When half of calls fail independently, retries do help: 3 retries at one layer cut failures from 50% to 6.25%, for about 1.9 calls per action. That's why retries need a budget: they help with scattered errors, and harm during real overload, when backing off and falling back is better.

**Now say why:** why do retries multiply instead of add?

## How it works

### How it works

#### In one breath

LLM APIs fail in ordinary ways: rate limits, overload, timeouts. Retrying helps with brief errors, but retries at every layer multiply. With 3 retries at each of 3 layers, one user action can become 64 calls to an already struggling provider. So retry only **retryable** errors, only at **one layer**, with **exponential backoff and jitter**, honour the **retry-after** header, and cap retries with a **budget**. Give every call a **deadline**, fall back to another model only if you've tested it, make tool calls safe to repeat, and never hide a failure behind a plausible answer.

#### How calls fail, and what to do

| Error | Meaning | Retry? |
|---|---|---|
| **429** rate limit | You exceeded requests or tokens per minute. Anthropic also returns it for a spend cap. | Yes, after the retry-after time. Not for a spend cap, which keeps failing. |
| **529 / 503** overloaded | The provider is busy across all users. | Yes, with backoff, a limited number of times. |
| **500** server error | Something broke on their side. | Yes, with backoff. |
| **400** bad request | Your request is wrong: too long, an invalid parameter, a retired model. | No. Fix it, and alert. |
| **Timeout** | No first token, or the stream stalled. | Yes, if there's time left before the deadline. |

##### Rate limits

Providers limit requests and tokens per minute, often separately for input and output. Anthropic uses a token bucket, so capacity refills continuously rather than resetting each minute, and a limit of 60 requests a minute may be enforced as one a second. OpenAI notes that failed requests still count toward your limit, so resending immediately doesn't work.

##### Retrying without making things worse

- **Backoff with jitter:** wait longer after each failure, with a random part, so many clients don't retry at the same moment. OpenAI advises waiting at least the retry-after time, plus a small random delay.

- **Retry at one layer:** Google's SRE book says to retry only at the layer just above the one that failed. If the backend, frontend and browser each make 4 attempts, one user action can create 4 × 4 × 4 = 64 attempts.

- **Retry budgets:** Google limits each request to 3 attempts, and each client to retries under 10% of its requests, which keeps the extra load near 1.1× instead of 3×.

- **Deadlines:** give each request a total time limit and pass the remaining time downstream, so no one keeps working on a request the user has abandoned.

##### Fallbacks and safety

- **Fallback models:** a second model or provider keeps the product up, but behaves differently. Test it on your evaluation set, and log when it's used.

- **Idempotent tools:** if a call that issued a refund is retried, the refund mustn't happen twice. Use an idempotency key.

- **Queue what can wait:** move non-urgent work to batch APIs or a queue with its own rate.

- **Fail loudly:** a 2026 study of a production agent found that errors passed into an LLM's context were turned into fluent, false output. Show an honest error, and alert.

#### The maths

$$ {\text{attempts}} = ({r} + 1)^{{L}} $$

The worst case, when every attempt fails, as in an outage. It's exactly when the provider can least afford the extra load.

- **worst-case attempts**: Calls reaching the provider for one user action when everything fails.

- **retries per layer**: Each failed attempt is retried r times.

- **layers that retry**: Browser, backend, model client: each one multiplies.

## In practice

### In practice

#### In practice

- **Classify errors:** retry 429, overload, 5xx and timeouts. Don't retry 400s or spend caps.

- **One retry layer, with a budget:** a few attempts per request, and a cap on the share of traffic that's retries.

- **Two timeouts for streams:** one for the first token, and one for gaps between tokens.

- **Tested fallbacks:** a second model or provider that has passed your evaluation set, with alerts when it's in use.

- **Protect your own limits:** per-tenant quotas, a queue for bursts, and batch APIs for offline jobs.

- **Watch it:** error rates by type, retry rate, fallback rate, and latency by percentile.

### The answer that sounds right

#### "Add more retries so users don't see errors"

It sounds kind to users, but retries at several layers multiply: 3 at each of 3 layers is 64 calls during an outage. Retry at one layer with a budget, back off, and fall back to a tested model instead.

## Say it

### Your provider starts returning overload errors at peak time, and your retries make it worse. How do you design calls to an LLM API so they fail gracefully?

#### The interviewer pushes further

Follow-up 1 of 3

Your provider is overloaded. Should you retry harder?

No. Back off with jitter, cut retries to the budget, shed or queue non-urgent traffic, and fall back to a tested model. More retries only add load.

Follow-up 2 of 3

Why does a refund tool need an idempotency key?

A timeout doesn't mean the call failed. If you retry, the refund may happen twice. With a key, the second request is recognised and ignored.

Follow-up 3 of 3

Your fallback model kicked in last night. Is that fine?

Only if it passed your evaluation set for this task. Log every fallback, alert on its rate, and check the quality of answers it gave.

#### The 30-second answer

I'd split errors into retryable ones, like rate limits, overload, server errors and timeouts, and ones I fix, like bad requests or a spend cap. I'd retry at one layer only, with exponential backoff and jitter, honouring retry-after, and cap retries with a budget, because 3 retries at 3 layers turns one action into 64 calls during an outage. Every call gets a deadline, and streams get first-token and stall timeouts. I'd fall back to a second model only if it passed our evaluations, make tool calls idempotent, queue non-urgent work, and show an honest error rather than a made-up answer.

**Key terms and sources**

Rate limits and error types, which errors to retry, exponential backoff with jitter, retry budgets and amplification across layers, timeouts and deadlines for streaming calls, fallbacks to other models, idempotent tool calls, and failing loudly. · checked 7 Nov 2026

#### Sources

- [Anthropic, API errors and rate limits documentation (checked 7 Nov 2026)](https://platform.claude.com/docs/en/api/rate-limits)

- [OpenAI, Rate limits guide (checked 7 Nov 2026)](https://developers.openai.com/api/docs/guides/rate-limits)

- [Google SRE book, Handling Overload](https://sre.google/sre-book/handling-overload/)

- [Google SRE book, Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/)

- [Wu, When Errors Become Narratives: silent failures in a production LLM agent runtime](https://arxiv.org/abs/2606.14589)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and provider policies change.
