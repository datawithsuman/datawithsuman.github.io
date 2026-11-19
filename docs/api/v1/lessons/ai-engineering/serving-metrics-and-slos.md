# Serving Metrics and SLOs

> TTFT, TPOT, p99 and goodput: why latency explodes near capacity.

- Track: AI Engineering › LLM inference and serving › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/serving-metrics-and-slos/
- Before this: Continuous Batching and Scheduling (`ai-engineering/continuous-batching`)
- Quiz topic: `infer`

## Intuition

### The situation

The assistant's SLO is TTFT under 1 s and TPOT under 50 ms. A colleague load-tests one GPU, gets 1,100 tokens per second, and calls that its capacity. The interviewer asks:

> How do you measure LLM serving, and why does latency explode near capacity?

**Running example:** the support assistant's SLO is **TTFT ≤ 1 s** and **TPOT ≤ 50 ms** (about 20 tokens/s, faster than people read). Requests arrive randomly; each has a 1,000-token prompt and a 200-token answer. How much traffic can one GPU take?

#### "Our server does 1,100 tokens/s" isn't an answer

A throughput number measured with a huge batch says nothing about whether users wait 100 ms or 30 s for the first word. A mean latency hides the 1% of users who time out. LLM serving needs metrics for each phase, at tail percentiles, under realistic load.

### The idea

Think of a motorway. More cars means more people moving, up to a point. Near capacity, one small burst becomes a long jam, even though the road is at its busiest. Maximum flow and a pleasant drive are different things.

[Figure: One GPU under load. At 4 requests a second: 804 tokens a second, 188 milliseconds p99 TTFT, 100 percent goodput. At 5: 1,004 tokens, 1.23 seconds, 89 percent. At 6: 1,142 tokens, over 10 seconds, 0 percent.]

_From the lab's simulation of one GPU. Illustrative numbers, not a specific GPU._

### Play

**Try to break it.** Set the arrival rate to 4 requests per second, then 5, then 6. Watch throughput, TTFT p50, TTFT p99 and goodput.

#### Push for maximum throughput

Discrete-event simulation of one GPU: Poisson arrivals; continuous batching up to 64 sequences; each new request's prefill takes 60 ms and stalls that step (no chunking); a decode step takes 10 ms + 0.4 ms per running sequence. 10 simulated minutes, first minute discarded; fixed seed. Illustrative numbers, not a specific GPU.

Up to **4 requests/s** everything is comfortable: p99 TTFT **188 ms**, TPOT 25 ms, goodput 100%, and throughput grows with load (804 tokens/s). At **5 requests/s** throughput is 1,004 tokens/s, but random bursts now queue: median TTFT is still 81 ms, yet p99 is **1.23 s** and 11% of requests miss the SLO. At **6 requests/s** the server is past its capacity (about 5.8 requests/s here): throughput peaks at 1,142 tokens/s, the queue grows without limit, TTFT exceeds 10 s, and goodput is **0%**. Maximum throughput and acceptable service are different operating points; queueing theory says latency grows sharply as utilisation approaches 100%, so production systems run with headroom.

**Now say why:** at 6 requests per second, throughput is at its highest and goodput is zero. How can both be true?

## How it works

### How it works

#### In one breath

Users feel two latencies: **TTFT** (time to first token: how long before anything appears) and **TPOT / ITL** (time per output token: how smoothly it streams). End-to-end latency ≈ TTFT + TPOT × (output tokens − 1). Operators care about **throughput** (tokens or requests per second per GPU). These pull in opposite directions: more load means bigger batches and more throughput, but each step gets slower and requests start **queueing**, and close to capacity the queue, and the **p99** TTFT, explode. So the metric that matters is **goodput**: requests per second that meet the SLO (e.g. TTFT ≤ 1 s and TPOT ≤ 50 ms), measured at percentiles, not averages. Capacity planning means finding the highest load where goodput stays near 100%, then leaving headroom.What you'll be able to do after this: define the metrics, read a load test, set SLOs and explain why p99 explodes near capacity.

#### The metrics

| Metric | Definition | Driven by |
|---|---|---|
| **TTFT** | request arrival → first output token | queueing + prefill (+ cache hits) |
| **TPOT / ITL** | average (TPOT) or per-gap (ITL) time between output tokens | decode step time: batch size, KV reads, prefill interference |
| **E2E latency** | arrival → last token ≈ TTFT + TPOT × (n − 1) | both, plus output length |
| **Throughput** | output tokens/s (or requests/s) per GPU or per dollar | batch size, utilisation |
| **Goodput** | requests/s that meet all SLOs (DistServe) | everything above, at the tail |

Report p50, p90 and p99, not means. Little's law (L = λ · W) links them: concurrent requests in the system = arrival rate × time each spends there; when W grows, so does memory pressure.

## In practice

### In practice

#### Load testing and setting SLOs

- **Benchmark with realistic traffic:** real prompt/output length distributions, Poisson or replayed arrivals, streaming on. Tools: vLLM's `benchmark_serving`, NVIDIA GenAI-Perf, LLMPerf. Sweep request rate and plot p99 TTFT / TPOT against throughput.

- **Pick SLOs per product:** chat needs fast TTFT and smooth streaming; batch summarisation cares about cost and E2E; agents chaining many calls care about E2E per step.

- **Tune for the SLO:** chunked prefill and smaller token budgets protect TPOT; prefix caching and more replicas protect TTFT; disaggregation lets you tune each phase separately (DistServe reported up to 7.4× more requests within SLO).

- **Operate:** alert on p99 TTFT and queue length, autoscale on queue depth or KV-cache usage (not GPU utilisation, which looks "busy" even when idle-waiting on memory), and shed or queue low-priority traffic under overload.

#### Optimise goodput, not throughput

Serve as much traffic as possible _while_ meeting TTFT and TPOT targets at the tail; past capacity, throughput barely rises while latency explodes.

### The answer that sounds right

#### "Maximum throughput is our capacity"

It sounds right, since throughput is the number you can measure most easily. But in the lab, peak throughput comes with 0% goodput. Capacity is the load at which SLOs still hold. Averages hide this as well: at 5 requests per second, median TTFT is still 81 ms while p99 is 1.23 s. And GPU utilisation won't warn you, because decode keeps the GPU "busy" reading memory.

## Say it

### How do you measure LLM serving, and why does latency explode near capacity?

#### The interviewer pushes further

Follow-up 1 of 3

TTFT p99 spiked but TPOT is fine. Likely causes?

Queueing from a traffic burst or capacity loss, long prompts (prefill), lost prefix-cache hits (e.g. a prompt change), or KV memory pressure delaying admission.

Follow-up 2 of 3

Why is GPU utilisation a poor autoscaling signal for LLMs?

Decode keeps the GPU "busy" reading memory even at low useful load; queue length, TTFT and KV-cache usage reflect saturation better.

Follow-up 3 of 3

Estimate E2E latency for 300 output tokens at TTFT 400 ms and TPOT 30 ms.

0.4 + 0.03 × 299 ≈ 9.4 s; streaming makes it feel much faster than that.

#### The 30-second answer

For LLM serving I track time to first token, driven by queueing and prefill; time per output token or inter-token latency, driven by decode batch size; end-to-end latency, roughly TTFT plus TPOT times output length; and throughput per GPU. They trade off: more load gives bigger batches and more throughput but slower steps and queueing, and near capacity tail latency explodes. So I define SLOs on p99 TTFT and TPOT and optimise goodput, the request rate that meets them, find it with a load test using realistic length distributions and arrival patterns, and run with headroom and autoscaling on queue depth.

**Go further**

#### What not to say

- "Average latency is 200 ms, so we're fine." Look at p99.

- "Maximum throughput is our capacity." Capacity is the load at which SLOs still hold.

**Key terms and sources**

What to measure and promise when serving an LLM: time to first token, time per output token / inter-token latency, end-to-end latency, throughput, tail percentiles, and goodput (requests served within the SLO); why throughput and latency trade off as load rises; how queues blow up near capacity; and how to load-test and set SLOs · built from Zhong et al. (DistServe, OSDI 2024), Agrawal et al. (Sarathi-Serve / Etalon metrics, 2024), the vLLM benchmarking docs, NVIDIA GenAI-Perf docs and Little (1961) · checked 29 Oct 2026

#### Sources

1. Y. Zhong et al., "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving", OSDI 2024, arXiv:2401.09670.

2. A. Agrawal et al., "Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve", OSDI 2024, arXiv:2403.02310; A. Agrawal et al., "Etalon: Holistic Performance Evaluation Framework for LLM Inference Systems", 2024, arXiv:2407.07000.

3. vLLM documentation, benchmarking (`benchmark_serving`); NVIDIA GenAI-Perf documentation.

4. J. Little, "A Proof for the Queuing Formula: L = λW", _Operations Research_ 9(3), 1961.
