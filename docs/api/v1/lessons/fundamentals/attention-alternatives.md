# Attention Alternatives: Sparse, Linear and Compressed

> How do new models handle a million tokens of context, and what do they give up?

- Track: Fundamentals › LLMs › Modern architecture
- Type: Concept · 22 min
- Page: https://aimlrounds.com/tracks/fundamentals/attention-alternatives/
- Before this: Long Context: RoPE Scaling, Sliding Windows and Attention Sinks (`fundamentals/long-context`), GPUs, TPUs and Memory Bandwidth (`fundamentals/gpus-tpus-and-memory-bandwidth`)
- Quiz topic: `arch`
- Sources checked: 2026-11-07 · Text last changed: 2026-11-20 · Version: 69ac4f581b

## Intuition

### The situation

A coding agent needs to read a million tokens of context. Your 8B model already uses GQA, but one conversation would still need over 100 GB of KV cache. A teammate suggests a model that claims linear attention. The interviewer asks:

> How do new models handle a million tokens of context, and what do they give up?

#### Why it matters

GQA and MLA make each cached token smaller, but the cache still grows with every token, and FlashAttention leaves the compute quadratic. Reasoning models and coding agents now use very long contexts, and this is where architectures changed most in 2025 and 2026. Stanford's CS336 teaches it alongside mixture of experts.

### The idea

Think of revising for an exam from a huge pile of notes. You could reread everything. You could flip straight to the few useful pages, which is sparse. You could keep one running summary, which is linear. You could shrink the notes into short digests, which is compressed. Each is faster, and each can miss a detail, so good students mix them.

[Figure: Four ways to save. Read fewer entries, keep a fixed state, shrink the entries, or share them across layers.]

_Most recent models mix these with some full attention._

### Play

**Try to break it.** Compare all six methods at 1M tokens. Then slide the context down to 4k.

#### Stretch the context

Illustrative: every method uses the same 32-layer shape, in 16-bit, so these aren't real models. Standard: GQA with 8 KV heads of size 128. MLA and compressed entries: 576 numbers per token. Sparse: top 2,048, plus a cheap scan of all keys. Linear hybrid: 8 standard layers and 24 layers with a 16-head state of 128 × 128. Compressed hybrid: half the layers merge 4 tokens and read the top 512; half merge 128 tokens. Bars use a log scale.

At 1M tokens, **standard GQA** needs about 137 GB for a single conversation, more than a whole GPU. **MLA** cuts that to about 39 GB, but it still grows with every token. A **sliding window** stays at 537 MB, but has forgotten everything else. A **linear hybrid** saves 75%, because only a quarter of its layers keep a cache, which matches the “up to 75%” that Kimi Linear reports. The **compressed hybrid** needs about 5 GB. Now slide the context down to 4k: even standard GQA needs only 537 MB. These methods add complexity, so they only earn it at very long context.

**Now say why:** why do hybrids keep some layers of full attention?

## Maths

### Maths

#### In one breath

At very long context, even a small KV cache gets huge, because it grows with every token. New models attack this in four ways. **Sparse attention** reads only the most useful past tokens. **Linear attention** squeezes the past into a fixed-size state. **Compressed attention** merges many tokens into fewer entries, or works in a smaller space. **Sharing** reuses keys and values across layers. Each one loses something, usually exact recall, so most recent models are **hybrids** that keep some layers of standard attention.

#### Four ways to pay less

| Idea | How it saves | What it gives up | Example |
|---|---|---|---|
| **Sparse** | Each query reads only its top-k past tokens | Tokens it doesn't select | DeepSeek Sparse Attention |
| **Linear** | Past tokens update a fixed-size state | Exact recall of old details | Gated DeltaNet, Kimi Delta Attention |
| **Compressed** | Fewer or smaller entries to store | Fine detail in what's merged | CSA and HCA, Compressed Convolutional Attention |
| **Shared** | Later layers reuse earlier layers' keys and values | Some capacity in those layers | Cross-Layer Attention |

##### Sparse attention

DeepSeek's version uses a small, cheap **indexer** to score every past token, then runs full attention on the top-k only. This cuts the main attention from O(L²) to O(Lk). The indexer itself is still O(L²), but it has few heads and can run in FP8. The cache isn't smaller, as every token must stay available for selection.

##### Linear attention

Instead of storing every key and value, keep one matrix, and add each new token's information to it. A learned gate decides what to forget. Time per token and memory stay constant, however long the context gets. The catch is that a fixed-size state can't hold everything exactly.

##### Compressed attention

You can compress along two directions. **Along the sequence:** merge several neighbouring tokens into one entry. DeepSeek-V4's CSA merges 4 tokens and then selects sparsely, while its HCA merges 128 and attends to all of them. **Along the channels:** Compressed Convolutional Attention runs all of attention in a smaller space. Unlike MLA, which only stores a small version, this also cuts the compute, which speeds up prefill and training.

##### Why hybrids win

Kimi Linear and Qwen3-Next both use three linear layers for each full-attention layer. DeepSeek-V4 interleaves CSA and HCA, and adds a short sliding window of recent tokens. The cheap layers do most of the mixing, and the others keep access to specific earlier tokens.

##### Reported results

| Model | Reported by its authors |
|---|---|
| Kimi Linear | KV cache down by up to 75%, and up to 6× decoding speed at 1M context |
| Qwen3-Next | Beat its 32B base model on downstream tasks, at 10% of the training cost, with 10× throughput above 32K tokens |
| DeepSeek-V4-Pro | 27% of the FLOPs per token and 10% of the KV cache of DeepSeek-V3.2, at 1M context |
| Cross-Layer Attention | A further 2× smaller cache than MQA, with nearly the same accuracy |

These are the authors' own numbers, on their own hardware and tests. Kimi's paper also reports smaller speed-ups in some settings, so treat "up to" figures as best cases.

#### The maths

$$ {S_t} = {A_t}\,{S_{t-1}} + {k_t v_t^{\top}}, \qquad {o_t = S_t^{\top} q_t} $$

The general linear attention update, as written in the Kimi Linear paper (Eq. 15). Standard attention would keep every key and value, and compare the query with each one.

- **the state**: A fixed-size matrix that stands in for the whole past. Its size doesn’t depend on the context length.

- **forget**: A learned gate shrinks parts of the old state. Better gates are the main difference between methods.

- **the previous state**: Everything remembered so far.

- **write**: Add the new token’s key and value to the state.

- **read**: Multiply the state by the query, rather than comparing the query with every past token.

## In practice

### In practice

#### In practice

- **Test what you care about:** a long context only helps if the model uses it. Test retrieval and multi-step tasks at your real length, as in Long Context. Qwen3-Next's card reports 91.8 on a 1M-token RULER test, against 92.5 for its larger sibling.

- **Ask which phase you're speeding up:** GQA and MLA mostly help decoding. Channel compression also helps prefill and training. Long-context work is mostly prefill.

- **Kernels matter:** sparse and linear methods need custom kernels. A method that looks cheap in FLOPs can be slower in practice, as memory traffic decides.

- **Other models exist:** state space models such as Mamba also keep a fixed state, and report 5× throughput on their tests. Later work mostly mixes this idea with attention.

- **Evidence is young:** most numbers come from the labs that built these methods, and full ablations are rare. Treat the claims as promising.

### The answer that sounds right

#### "Linear attention is simply better, because it's constant memory"

It sounds right, as constant memory beats memory that grows. But a fixed-size state can't hold everything exactly, so a model can lose specific details. That's why Kimi Linear and Qwen3-Next both keep some full-attention layers. Test recall on your own long-context tasks.

## Say it

### How do new models handle a million tokens of context, and what do they give up?

#### The interviewer pushes further

Follow-up 1 of 3

Why does a 3:1 linear hybrid cut the cache by about 75%?

At long context the linear layers' fixed state is tiny next to the cache, so only the quarter of layers using full attention still store a cache that grows with every token.

Follow-up 2 of 3

Sparse attention reads only k tokens. Why isn't its cache small?

Any past token might be selected later, so all of them must stay available. It mostly saves compute and memory reads, unless you also compress the entries, as DeepSeek-V4 does.

Follow-up 3 of 3

Your agent needs 500k tokens of context. How do you choose a model?

Test on your own long-context tasks, rather than its advertised length. Measure retrieval from the middle of the context, prefill time and memory per conversation. Prefill usually dominates for long inputs, so check which phase the model actually speeds up.

#### The 30-second answer

GQA and MLA make each cached token smaller, but the cache still grows with context. Four newer ideas go further. Sparse attention uses a cheap indexer to read only the top-k past tokens, which cuts the main attention from L squared to L times k. Linear attention replaces the cache with a fixed-size state and a learned forget gate, so memory stays constant, but it can't recall details exactly. Compression merges tokens along the sequence, or works in a smaller space, which can also cut prefill and training cost. Sharing reuses keys and values across layers. Most models are hybrids, such as three linear layers per full-attention layer, because some layers still need exact access to earlier tokens.

**Key terms and sources**

Why full attention gets expensive, sparse attention, linear attention with a fixed-size state, compressing keys and values, cross-layer sharing, and why hybrids win. · checked 7 Nov 2026

#### Sources

- [Kimi Team, Kimi Linear](https://arxiv.org/abs/2510.26692)

- [DeepSeek-AI, DeepSeek-V3.2 (Sparse Attention)](https://arxiv.org/abs/2512.02556)

- [DeepSeek-AI, DeepSeek-V4](https://arxiv.org/abs/2606.19348)

- [Qwen3-Next model card](https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Instruct)

- [Figliolia et al., Compressed Convolutional Attention](https://arxiv.org/abs/2510.04476)

- [Brandon et al., Cross-Layer Attention](https://arxiv.org/abs/2405.12981)

- [Gu and Dao, Mamba](https://arxiv.org/abs/2312.00752)

- [Raschka, Recent Developments in LLM Architectures](https://magazine.sebastianraschka.com/p/recent-developments-in-llm-architectures)

- [Stanford CS336, attention alternatives lecture](https://cs336.stanford.edu/)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
