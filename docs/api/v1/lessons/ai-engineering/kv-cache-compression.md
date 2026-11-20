# KV Cache Compression, Eviction and Offloading

> Long conversations are filling GPU memory with KV cache. How do you shrink it, drop some of it, or move it?

- Track: AI Engineering › LLM inference and serving › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/kv-cache-compression/
- Before this: KV Cache Management and PagedAttention (`ai-engineering/kv-cache-and-pagedattention`)
- Quiz topic: `infer`

## Intuition

### The situation

Your assistant now keeps whole order histories in context, often 30,000 tokens or more. GPU memory fills with KV cache, and you can only serve a fraction of the users you could before. Someone suggests dropping old tokens from the cache. The interviewer asks:

> Long conversations are filling GPU memory with KV cache. How do you shrink it, drop some of it, or move it?

#### Why it matters

PagedAttention fixed wasted space. But an 8B model with a 32,000-token conversation needs about 4.3 GB of KV cache, and long-running agents and chats keep growing it. At that point you can't fit enough users on a GPU, however well it's packed. This lesson covers what to do next. For model changes that shrink the cache, such as GQA and MLA, see Attention Variants.

### The idea

Think of a busy desk covered in notes. You can write smaller, which saves space but is harder to read. You can throw away notes you think you won't need, and hope you're right. Or you can file some in a drawer and fetch them when needed, which takes a moment but loses nothing.

[Figure: Three choices. Quantize to shrink it. Evict to drop parts. Offload to move it to cheaper memory.]

_Choose by whether you can afford any loss._

### Play

**Try to break it.** Raise the context to 1 million tokens. Then try each method, and compare the resume times.

#### Fit more conversations

Illustrative arithmetic for the Llama 3 8B shape, at 128 KiB per token in bf16. Reload assumes 64 GB/s from CPU memory and 7 GB/s from SSD. Recompute assumes 2 FLOPs per parameter per token at half of an H100's 989 TFLOP/s, and ignores attention, so long histories take longer. 2-bit ignores the small overhead for scales.

A 32,768-token conversation needs about 4.3 GB in bf16, so only 16 fit in 64 GiB. An **FP8** cache fits 32, and a **2-bit** cache 128, each with some risk to accuracy. Keeping **20% of tokens** fits 80, but whatever was dropped is gone for good. Now look at resuming a paused conversation: reloading from CPU memory takes about 67 ms, from SSD about 0.6 s, and recomputing about 1.1 s of GPU time. That's why offloading pays for agents and long chats: reloading is usually faster, and leaves the GPU free for others. Push to 1 million tokens, and even a single conversation won't fit in bf16.

**Now say why:** why is reloading usually better than recomputing for long histories?

## How it works

### How it works

#### In one breath

Paging stops the KV cache from being wasted, but it doesn't make it smaller. At long contexts and many users, the cache itself fills the GPU. You have three choices. **Quantize** it: FP8 halves it, and methods like KIVI go to 2 bits. **Evict** parts of it: keep only the tokens that attention relies on most, which saves memory but can lose information for good. **Offload** it: move idle conversations to CPU memory or SSD and bring them back later, which is exact but costs a transfer. The right choice depends on whether you can afford any loss.

#### Shrink, drop or move

| Approach | Saves | Loses | Example |
|---|---|---|---|
| **Quantize** | 2× at FP8, more at lower bits | A little accuracy, usually small at 8 bits | FP8 KV cache, KIVI at 2 bits |
| **Evict** | As much as you choose | Dropped tokens are gone for good | H2O, SnapKV, sliding windows with attention sinks |
| **Offload** | GPU memory for idle conversations | Nothing, but a transfer delay on return | CPU memory and SSD tiers, LMCache, Mooncake |

##### Quantizing the cache

An FP8 cache halves the memory, so roughly twice as many conversations fit. KIVI goes further. It found keys and values behave differently, so it quantizes keys per channel and values per token, at 2 bits. It reported almost the same quality with 2.6× less peak memory including weights, up to 4× larger batches, and 2.35 to 3.47× throughput. Errors reach every later token, so test on long tasks.

##### Evicting tokens

- **H2O:** a few "heavy hitter" tokens get most of the attention. Keeping them, plus recent tokens, kept quality with 20% of the cache, and gave up to 29× throughput over some offloading-based systems.

- **SnapKV:** each head attends to consistent parts of the prompt, which can be spotted from the last few prompt tokens. At 16K input it reported 3.6× faster generation and 8.2× better memory efficiency.

- **Sliding windows:** keep recent tokens and the first few attention sinks. Memory stays bounded, but older text is forgotten.

The risk with eviction is that a question may need exactly what was dropped. That's fine for summarising a long chat, and bad for "what was the order number I gave you earlier?"

##### Offloading to cheaper memory

Idle conversations, such as a user who hasn't replied yet, can move to CPU memory or SSD. When they return, you can either reload their cache or recompute it by running prefill again. LMCache, which shares and stores caches outside GPU memory, reported up to 15× throughput with vLLM on multi-round and document workloads. Mooncake, the system behind Kimi, built its whole service around a shared cache across CPU memory and SSD.

##### Agents change the rules

Engines usually evict from the end of cached sequences, to protect shared prefixes. A 2026 study argues that agents, which return with long histories again and again, should instead keep the shared prefix and the most recent turns, and evict from the start of the rest, because recomputing late tokens is far more expensive. It reported up to 60% lower average time to first token than SGLang with a GPU-only cache, and up to 76% with a two-tier GPU and CPU cache.

#### The maths

$$ {t_{\text{reload}}} = \frac{{\text{KV bytes}}}{{\text{link bandwidth}}}, \qquad {t_{\text{recompute}}} \approx \frac{{2PT}}{{\text{usable FLOP/s}}} $$

Simple arithmetic for the reload-or-recompute choice. Recompute also takes GPU time away from other users, which reload doesn’t.

- **time to reload**: Bring a saved cache back from CPU memory or SSD.

- **bytes to move**: Grows with the conversation length.

- **the link**: PCIe to CPU memory, or much slower SSD.

- **time to recompute**: Run prefill again over the whole history.

- **prefill maths**: About 2 FLOPs per parameter per token, ignoring attention, which only adds to it for long histories.

- **the GPU’s real speed**: Peak FLOPs times realistic utilisation.

## In practice

### In practice

#### In practice

- **Start with FP8:** it's widely supported and usually safe. Test long-context tasks before going lower.

- **Be careful with eviction in products:** users expect exact recall of what they said. Prefer offloading, or keep eviction to tasks like summarising.

- **Plan tiers:** GPU memory for active conversations, CPU memory for recently idle ones, and SSD for long pauses. SSDs wear out with heavy writes, which a 2026 study addresses.

- **Route to the cache:** send a returning conversation back to the machine that holds its cache. See Prefix Caching.

- **Measure on your traffic:** watch cache hit rate, reload time and recompute load. Each paper reports on its own workloads.

### The answer that sounds right

#### "Drop the old tokens, the model mostly looks at recent ones"

It sounds right, since attention favours some tokens. But a later question may need exactly what you dropped, like an order number given early on, and evicted tokens can't come back. For products where exact recall matters, quantize or offload instead.

## Say it

### Long conversations are filling GPU memory with KV cache. How do you shrink it, drop some of it, or move it?

#### The interviewer pushes further

Follow-up 1 of 3

Your support bot forgets an order number from early in a long chat after you enabled KV eviction. Why?

Eviction keeps tokens that got the most attention so far, and the order number may not have seemed important until the user asked about it. Dropped tokens can't come back. Use quantization or offloading instead, or retrieve key facts explicitly.

Follow-up 2 of 3

When is recomputing a cache better than reloading it?

For short histories, prefill is quick, and avoids storing and moving the cache at all. For long histories, reloading from CPU memory is usually much faster, and doesn't take GPU time from other users. SSD sits in between, depending on its speed.

Follow-up 3 of 3

Does an FP8 KV cache change the model's output?

Slightly, as rounding errors enter every later attention step. It's usually small, but test long-context tasks, and compare against bf16 on your own evaluations.

#### The 30-second answer

Paging removes waste, but at long contexts the cache itself fills the GPU, and an 8B model's 32k-token conversation is about 4 GB. I have three options. Quantize it: FP8 halves it with little risk, and KIVI's 2-bit method reported up to 4 times larger batches. Evict tokens: H2O and SnapKV keep the tokens attention relies on, which saves a lot but loses information for good, so I'd avoid it where exact recall matters. Or offload: move idle conversations to CPU memory or SSD and reload them later. Reloading 4 GB from CPU memory takes tens of milliseconds, against about a second of GPU time to recompute. For agents, I'd keep shared prefixes and recent turns, and route returning conversations to the machine holding their cache.

**Key terms and sources**

Why long contexts make the KV cache the bottleneck, quantizing it, evicting unimportant tokens, offloading to CPU memory or SSD, and when to reload or recompute. · checked 7 Nov 2026

#### Sources

- [Liu et al., KIVI: 2-bit KV cache quantization](https://arxiv.org/abs/2402.02750)

- [Zhang et al., H2O: Heavy-Hitter Oracle](https://arxiv.org/abs/2306.14048)

- [Li et al., SnapKV](https://arxiv.org/abs/2404.14469)

- [Liu et al., LMCache](https://arxiv.org/abs/2510.09665)

- [Qin et al., Mooncake](https://arxiv.org/abs/2407.00079)

- [Rethinking KV Cache Eviction for Agentic LLM Serving](https://arxiv.org/abs/2611.00391)

- [Gandalf: increasing flash lifetime for KV cache offloading](https://arxiv.org/abs/2610.30791)

- [Kwon et al., PagedAttention](https://arxiv.org/abs/2309.06180)

Explanations are ours, built from these sources. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints, and vendor results are their own.
