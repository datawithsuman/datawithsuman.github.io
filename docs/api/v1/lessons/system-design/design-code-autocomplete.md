# Design Code Autocomplete

> Design code autocomplete for hundreds of millions of requests a day, with suggestions arriving in under 200 ms.

- Track: System Design › Developer Tools › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-code-autocomplete/
- Before this: Continuous Batching and Scheduling (`ai-engineering/continuous-batching`), Scaling Inference: Parallelism, Replicas and Routing (`ai-engineering/scaling-inference`)
- Quiz topic: `sdllm`

## Intuition

### The situation

A code editor plugin suggests the next lines as developers type, for users all over the world. A suggestion that arrives late is useless. It must serve hundreds of millions of requests a day, with a mean under 200 ms. The interviewer asks:

> Design code autocomplete for hundreds of millions of requests a day, with suggestions arriving in under 200 ms.

#### Ask before designing

- **Scale:** 400 million requests a day, peaking in the overlap between the working day in Europe and the US.

- **Latency:** under 200 ms on average. A late suggestion is useless, because the person has already typed past it.

- **Users:** worldwide, so distance matters as much as model speed.

- **Clients:** an IDE plugin that people may not update for a long time, so the server must absorb changes.

- **Must never happen:** code leaking between users, or secrets in suggestions and logs.

- **Success metrics:** acceptance rate, code kept after a while, latency, error rate and cost per suggestion.

### The idea

Think of a friend finishing your sentences, on a phone call. If they're slow, you've already moved on, and what they say is wasted. Hanging up and redialling each time you talk over them would be absurd, so you stay on the line and just say "never mind".

[Figure: The IDE waits for a pause and sends a short prompt to the nearest proxy over an open connection. The proxy checks a token and forwards to a model in the same region. Cancels travel back down the same path.]

_Staying on the line is HTTP/2. "Never mind" is a cancel that reaches the model._

### Play

**Try to break it.** Start with both boxes off, and see how far you are from 200 ms. Make the round trip shorter. Then try each box.

#### Where does the time go?

Illustrative: 100 ms to run the model, 5.5 round trips for each new connection, one reconnect per cancel, and 20 ms round trip in the user's region. With cancels passed through, we assume a tenth of the cancelled work still runs.

A faster model can't fix this. At a **100 ms** round trip, the network and reconnects together take over three times as long as the model. Turn on **HTTP/2** and then the **nearby region**, and you drop from about 448 ms to 120 ms with the same model.

**Now say why:** why can't a faster model alone meet the target?

## Architecture

### Architecture

#### In one breath

The model isn't your only latency problem. **The network and wasted requests are just as big.** Most typing makes requests go stale, so the client cancels them and the cancel must reach the model. **HTTP/2 streams** let you cancel one request while keeping the connection open. A **proxy in each region, next to the model**, handles sign-in, routing and experiments, and each proxy takes itself out of service when it's unhealthy.

#### The path of one keystroke

1. **Decide when to ask:** there's no "complete" key, so the client guesses when typing has paused. It can use a timer, a small prediction model or a guess on each key, and real systems mix them.

2. **Build the context:** the code before and after the cursor, plus a few snippets from open files, trimmed to fit the budget. A short prompt means a quick prefill.

3. **Send to the nearest proxy:** DNS sends the user to their closest healthy region, over a connection that's already open.

4. **Check the token:** the client swaps its login for a token that lasts minutes. The proxy checks the signature locally, with no call to another service, and swaps in the real model key.

5. **Run the model:** the proxy forwards the request over its open connection pool to a fast model in the same region, and streams the reply back.

6. **Show or discard:** the IDE shows it if it's still relevant. If the user kept typing, it cancels.

##### Cancellation is the core of it

The real team reported that about half of requests were typed through, meaning the user kept typing before the reply arrived. With plain HTTP, the client's only way to cancel is to reset the connection, and that has two costs:

- **Wasted model work:** the server may not notice the reset until it writes the reply, so the model has already run. About 45% of requests were cancelled after inference had run.

- **Slow reconnects:** a new connection takes five or six round trips for TCP and TLS, which alone can use up the 200 ms.

**HTTP/2** fixes both. One connection carries many streams, so the client resets just one stream and the connection stays open. The proxy passes the cancel to the model, which stops work almost immediately. Every hop must speak HTTP/2, and many load balancers downgrade to HTTP/1 on the way to the backend, so check yours.

##### Regions

Put a proxy in every region that has the model. The real team rejected separate edge locations, because traffic from Japan could go through Singapore and on to a model on the US West Coast. The network round trip can take longer than running the model.

#### The numbers worth saying out loud

The first two rows use the talk's figures. The rest are assumptions for the interview.

| Question | Working | Result |
|---|---|---|
| Average load | 400 million ÷ 86,400 | **about 4,600 per second** |
| Peak load | From the talk | **about 8,000 per second** |
| Wasted without cancel | 400 million × 45% | **180 million model runs a day** |
| GPUs at peak | 8,000 ÷ 100 per GPU, × 2 for headroom | **about 160** |

Cancelling is a cost feature as well as a speed feature. Stopping nearly half the work early frees that capacity for live requests.

## In practice

### In practice

#### What every LLM design gets asked

- **Quality and evaluation:** track acceptance rate, and how much accepted code is still there later, since accepting isn't the same as keeping. Because the proxy sees all traffic, it can split traffic between model versions for A/B tests, and mirror traffic to test a new one safely.

- **Reliability:** each proxy watches its own success rate. If it drops below target, the health check starts to fail and DNS removes that instance. It returns once it recovers. A regional outage becomes a loss of some capacity.

- **Scalability:** proxies are stateless and hold long-lived connections, so spread load across a pool of connections to each model. Load shifts around the world during the day, so scale each region to its own peak.

- **Latency and cost:** use a small, fast model, keep prompts short and batch requests on the GPU. A mean hides slow users, so watch percentiles measured at the proxy.

- **Safety and security:** short-lived tokens limit the damage from a stolen one, and the real model key never reaches the client. Filter secrets from prompts and suggestions, and don't log code by default.

##### Why the proxy earns its place

Clients update slowly, so server-side fixes matter. The real team used the proxy to remove a parameter that was crashing model instances, and to change requests on the way through. All of that happens with no client release.

##### Rollout

Use the proxy to send a small share of traffic to a new model, and compare acceptance and latency. Redeploy proxies behind a load balancer that holds the client connection, so users don't get disconnected.

#### What the real system reported

- **Scale:** more than 400 million requests a day when the talk was pitched, and higher by the time it was given. About 8,000 requests a second at peak.

- **Latency:** a mean under 200 ms during that peak.

- **Waste:** about 45% of requests were cancelled after inference had run, before the fix.

- **Tokens:** they last 10 to 30 minutes, and the client refreshes a couple of minutes before expiry.

- **Load balancers:** many cloud ones and CDNs downgraded to HTTP/1 on the backend, so the team used its own, based on HAProxy.

These are the speaker's own figures, from a November 2024 talk.

### The answer that sounds right

#### "Just get a faster model and more GPUs"

It sounds right, since the model is the expensive part. But reconnecting takes five or six round trips, so distance alone can use up 200 ms. And if requests aren't cancelled, about half of those extra GPUs do work no one will see. Fix the wasted work and the network path first, then see how much model speed you still need.

## Say it

### Design code autocomplete for hundreds of millions of requests a day, with suggestions arriving in under 200 ms.

#### The interviewer pushes further

Follow-up 1 of 3

Why not make the model faster and skip all this?

You can't beat distance. If a round trip takes 100 ms and a reconnect takes five or six of them, that alone exceeds the budget however fast the model is. Without cancels, a faster model would still run about half its requests for nothing. Both a fast model and a good network path are needed.

Follow-up 2 of 3

One region's model starts returning errors. What do users see?

Proxies there see their success rate fall below target, fail their health checks and drop out of DNS. New requests go to the next closest region, so those users get slower suggestions, not errors. When the rate recovers, the proxies return. Suggestions are optional, so failing quietly is fine too.

Follow-up 3 of 3

Doesn't a proxy add a hop and slow things down?

It adds a small hop, but it's in the same region as the model, and it holds open connections, which saves far more than it costs. In return you get central sign-in, a hidden model key, routing, cancels, experiments and fixes for old clients.

#### The 30-second answer

First I'd confirm the scale, the latency target and where users are. At 400 million requests a day and about 8,000 a second at peak, under 200 ms leaves little room, and the network matters as much as the model. The client waits for a pause, builds a short prompt from the code around the cursor and sends it over a connection that's already open. About half of requests go stale as people type, so cancelling is central. I'd use HTTP/2, so the client resets one stream and keeps the connection, avoiding five or six round trips per reconnect. The proxy passes the cancel to the model, so it stops wasting GPU time. I'd put a proxy in every region with the model, and route by DNS to the closest healthy one. It checks a short-lived token locally and holds the real model key. Each proxy watches its success rate and fails its health check when it's unhealthy, so a regional outage only reduces capacity. The proxy also lets me A/B test models and fix problems without client releases. I'd measure acceptance, code kept, percentile latency and cost.

**Key terms and sources**

Based on a talk about a real system: [David Cheney on serving GitHub Copilot](https://www.infoq.com/presentations/github-copilot/) ([QCon SF 2024](https://qconsf.com/presentation/nov2024/how-github-copilot-serves-400-million-completion-requests-day)). We could read most of the transcript and only a summary of the rest. Context building, quality metrics, privacy and the lab's numbers come from our own knowledge and are not from the talk. Uses prefill and decode, continuous batching, serving metrics and scaling inference. · checked 5 Nov 2026
