# Design a Shared LLM Platform

> Dozens of teams want to use LLMs from different vendors, and customer data mustn't leak. Design a shared platform for them.

- Track: System Design › ML and LLM Platforms › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-llm-platform/
- Before this: LLMOps: What's Different (`ai-engineering/llmops`), Guardrails and Prompt Injection (`ai-engineering/guardrails-and-prompt-injection`)
- Quiz topic: `sdllm`

## Intuition

### The situation

A large company has dozens of teams building with LLMs. Each has its own vendor keys and its own way of connecting, and nobody can see the total cost or say what data is leaving the company. Say 100 million requests a month. The interviewer asks:

> Dozens of teams want to use LLMs from different vendors, and customer data mustn't leak. Design a shared platform for them.

#### Ask before designing

- **Users:** how many teams and use cases, and which languages do their services use?

- **Models:** outside vendors, your own hosted models or both? Which data may go to which of them?

- **Scale:** say 100 million requests a month, many of them streaming.

- **Must never happen:** customer data reaching a vendor without approval, one team using up everyone's quota, or the platform taking down every product at once.

- **Success metrics:** teams onboarded, time to onboard, added latency, availability, data incidents and cost per team.

### The idea

Think of a company's post room. Every team hands letters to one desk, in one format. The desk checks the sender, blacks out private details on anything leaving the building, sends it by the right courier and keeps a record of the cost. If the desk closes, though, nothing gets sent, so it needs cover.

[Figure: Teams call one API. The gateway checks access and limits, redacts personal data, then routes to a vendor or in-house model. Every request is logged for cost and audit.]

_Every team gets the same checks, without building them again._

### Play

**Try to break it.** Turn redaction off, and read what the vendor sees. Turn it back on, and swap the names. Then drag the message length up.

#### What does the vendor actually see?

**Your service sends**

**The vendor sees**

**The vendor replies**

**Your service gets**

Illustrative: a made-up message, and about 10 ms plus 1 ms per 100 characters for the redactor. The placeholder style follows the real post. The post says the delay grows with the length of the request, but we couldn't read its figures.

Turn it off, and the vendor sees all three details. Now swap the names: **the same person gets a different placeholder**, because numbers follow the order of appearance. The model also loses meaning. It can't tell a name's gender, region or language from a placeholder, which can hurt answer quality. Redaction is a trade-off, so review which use cases need it.

**Now say why:** why might an answer get worse once the names are hidden?

## Architecture

### Architecture

#### In one breath

Put a **gateway** between every team and every model. Teams call **one API**, in a format they already know, and the gateway handles sign-in, routing, logging and cost tracking. Before a request leaves for an outside vendor, it **swaps personal data for placeholders**, and restores them in the reply. Since everything depends on the gateway now, it needs **budgets per team, fallbacks and no single point of failure**.

#### The path of one request

1. **Call one API:** teams use a widely adopted format, like the OpenAI API, and name a model. Existing client libraries and frameworks then work unchanged.

2. **Sign in and check access:** identify the team, and confirm the use case was reviewed and may use this model.

3. **Check limits:** apply the team's rate limit and budget.

4. **Redact:** if the request is going outside, replace personal data with placeholders and keep the mapping.

5. **Route:** pick the vendor client or your own serving stack, and translate the request if needed.

6. **Restore and log:** put the real values back in the reply, then record the team, model, tokens, latency and cost.

##### Why one format beats your own

A custom API must be documented and kept current by you, and it can quickly fall behind a fast-moving field. Copying the most common format gives teams every tool built for it, and switching model becomes a one-word change. The cost is that other vendors' features don't always map neatly onto it.

##### Onboarding

The platform makes review easy to enforce. Each new use case goes through one standard security review of the data it handles, and only then gets access. Teams no longer each hold their own vendor keys and contracts.

##### What doesn't belong here

Keep prompts, retrieval and business logic in the teams' own services. A gateway that knows about each product's logic becomes a bottleneck for every team.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Average load | 100 million ÷ 2.6 million seconds in a month | **about 38 per second** |
| Peak load | 38 × 3 | **about 115 per second** |
| Open connections at peak | 115 × 10 seconds per streamed reply | **about 1,150** |
| Log storage per month | 100 million × 5 KB of metadata | **about 500 GB** |

The gateway does little computing itself, since the model does the hard work. What it must handle is many slow, open connections, so choose a server built for that.

## In practice

### In practice

#### What every LLM design gets asked

- **Quality and evaluation:** quality belongs to each team, since only they know what good means for their product. The platform provides the logs and a way to replay traffic against a new model, so they can compare before switching.

- **Reliability:** every product now depends on you, so run many instances in several zones, and make deploys gradual. Retry with backoff, and fall back to a second approved model when a vendor fails. Teams must opt in, because a different model can behave differently, and a fallback must never send data to a vendor it isn't approved for.

- **Scalability:** the gateway is stateless, and vendor quotas are the real limit. Share those fairly across teams, reserving capacity for critical products and giving batch jobs what's left.

- **Latency and cost:** stream replies straight through, and keep the added delay small. Attribute cost per team from logs, set budgets with alerts, and offer exact-match caching only as an opt-in, since a shared cache can leak data between users.

- **Safety and security:** keep vendor keys only in the gateway. Logs now hold sensitive text, so log metadata by default, and restrict and expire anything more. Redaction misses things, so it's one layer, alongside contracts and approved-use review.

##### The risk of a shared layer

Decide in advance what happens if a check fails. If the redactor is down, requests to outside vendors should be refused and never sent unredacted. If the logging system is down, requests can usually continue, with logs queued for later.

##### Rollout

Start with one or two willing teams and one vendor. Move others over by making the platform the easiest path, then block direct vendor access once most have moved.

#### What the real system reported

- **Why they built it:** over 60 LLM use cases across the company, with teams integrating in different ways and repeating each other's work.

- **Scale in July 2024:** close to 30 customer teams, 16 million queries a month and a peak of 25 per second.

- **Design:** a Go service that copies the OpenAI API, wraps vendor clients and sits alongside in-house serving. It includes authentication, metrics, and audit logs for cost and security.

- **Redaction:** typed placeholders numbered by position, restored in the reply. The post says this creates challenges for both latency and result quality.

The company's own figures. We couldn't read the post's later sections, so anything about how they reduced those problems isn't included.

### The answer that sounds right

#### "Add a fallback, and send everything to the next vendor"

It sounds right, since it keeps products running when a vendor is down. But each vendor has its own data approvals, and a different model can behave differently. A silent global switch could send customer data somewhere it isn't allowed, or change a product's behaviour untested. Make fallback a per-team choice, limited to approved models.

## Say it

### Dozens of teams want to use LLMs from different vendors, and customer data mustn't leak. Design a shared platform for them.

#### The interviewer pushes further

Follow-up 1 of 3

One team's batch job uses up the vendor quota, and customer chat starts failing. How do you prevent that?

Give each team its own rate limit and budget, and reserve part of the quota for critical products. Batch work goes through a queue at low priority, and uses what's left. Alerts warn teams before they reach their limits.

Follow-up 2 of 3

A vendor has an outage. Do you switch every team to another vendor automatically?

Only teams that opted in, and only to models approved for their data. A different model can change behaviour, so a team must test its fallback first. Others get a clear error they can handle. That's why fallback is a per-team setting rather than a global one.

Follow-up 3 of 3

Doesn't the redactor make answers worse? Would you remove it?

It can, because the model loses context, and placeholders can confuse it. I wouldn't remove it across the board. I'd measure quality with and without it on safe test data, then use a stricter contract or an in-house model for cases that need real values. Requests to an in-house model may not need redaction, depending on policy.

First I'd clarify the number of teams, which models they need, what data may go where and the volume. I'd build a gateway between all teams and all models. Teams call one API in a widely used format, so existing tools work and switching models is easy. For each request, the gateway signs in the team, checks that the use case was approved, applies rate limits and budgets, and redacts personal data if it's going to an outside vendor. It routes to a vendor or our own serving stack, restores the placeholders in the reply and logs team, model, tokens and cost. Vendor keys live only in the gateway. Redaction costs latency and some quality, so I'd review where it's needed, and refuse to send if the redactor fails. Because every product now depends on it, I'd run it across zones with gradual deploys, plus opt-in fallbacks that respect data rules. Vendor quotas are the real limit, so I'd share them fairly by priority. Quality stays with each team, and the platform gives them logs and replay tools.

**Key terms and sources**

Based on a ride-hailing company's published design: Uber's post on its LLM gateway. We could read only part of the post, up to the start of its section on challenges. Budgets, fallback, caching and the lab's numbers come from our own knowledge and are not from the post. Uses LLMOps, guardrails and cost and latency.
