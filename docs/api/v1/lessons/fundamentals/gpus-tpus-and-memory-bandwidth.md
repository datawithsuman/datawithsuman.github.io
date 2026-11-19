# GPUs, TPUs and Memory Bandwidth

> Why is decoding limited by memory, while prefill is limited by compute?

- Track: Fundamentals › LLMs › Modern architecture
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/gpus-tpus-and-memory-bandwidth/
- Before this: Anatomy of a Modern LLM (`fundamentals/modern-llm-architecture`)
- Quiz topic: `arch`

## Intuition

### The situation

Your team doubled the batch size on its 8B assistant, and tokens per second went up. Then someone suggests buying chips with twice the compute to make replies faster. You suspect that won't help much. The interviewer asks:

> Why is decoding limited by memory, while prefill is limited by compute?

#### Why it matters

Many tricks in this track exist because of this gap between maths and memory. GQA and MLA shrink what decoding must read. FlashAttention avoids sending data to main memory. Tensor parallelism stays inside fast links. Interviewers ask you to estimate speed from a chip's numbers, so it helps to know which number is the limit.

### The idea

Think of a very fast chef with a slow helper bringing ingredients from a far-off store. If each dish needs a lot of chopping, the chef's speed decides how fast you serve. If each dish needs ingredients from all over the store, the chef mostly stands and waits. A faster chef wouldn't help at all.

[Figure: Two limits. Maths time is operations over compute. Data time is bytes over bandwidth. The larger one sets the speed.]

_The slower of the two sets the step time._

### Play

**Try to break it.** Switch between decode and prefill. Then push the batch up to 128.

#### Find the limit

Best-case estimate for one chip, using the Llama 3 8B shape in 16-bit: 16 GB of weights and 128 KiB of KV cache per token. Each token costs about 2 operations per parameter. Weights are read once per step. Attention's extra work, activations and network links are left out.

With 32 conversations of 4,096 tokens, a **decode** step needs 0.52 ms of maths, but 9.9 ms just to read the weights and cache. Faster compute wouldn't help at all. Now switch to **prefill**: the same batch needs 2.12 s of maths and still about 10 ms of reads, so compute is the limit. Raise the batch while decoding, and tokens per second keep rising, because each read of the weights is shared across more conversations. At 128 conversations the cache no longer fits in the H100's 80 GB.

**Now say why:** why does a bigger batch raise tokens per second while decoding?

## Maths

### Maths

#### In one breath

An AI chip does maths very quickly, but moves data far more slowly. An H100 can do about **989 trillion** operations a second, yet reads only about **3.35 TB** of memory a second. So a job takes at least as long as the slower of two things: doing its maths, or moving its bytes. This is the **roofline model**. **Prefill** does lots of maths per byte, so compute limits it. **Decode** reads the whole model and cache to produce one token per conversation, so memory limits it. That one fact explains GQA, MLA, FlashAttention and much of LLM serving.

#### Inside the chip

##### Faster memory is smaller

A chip has several levels of memory. Each step away from the compute units holds more, but is slower.

| Level (H100) | Size | Bandwidth |
|---|---|---|
| On-chip SRAM | 228 KiB per streaming multiprocessor | 31 TB/s across the GPU |
| L2 cache | 50 MiB | 12 TB/s |
| **HBM, the main memory** | **80 GB** | **3.35 TB/s** |
| NVLink, to other GPUs | Not applicable | 900 GB/s in total |
| PCIe, to the host | Not applicable | 128 GB/s |

SRAM, L2 and HBM figures are from the FlashAttention-3 paper. HBM capacity, NVLink and PCIe are from NVIDIA's specification.

##### Not all maths is equally fast

The Tensor Cores make matrix multiplication very fast. On an H100, matmul runs at 989 TFLOPS in 16-bit, but special functions such as exponentials run at only 3.9 TFLOPS. That's why a kernel that computes softmax in the wrong place can be surprisingly slow, however few operations it does.

##### Arithmetic intensity

Arithmetic intensity is a job's operations divided by the bytes it moves. Compare it with the chip's own ratio of compute to bandwidth. For an H100, that's about 989 trillion ÷ 3.35 trillion, or about **295 operations per byte**. A job above this is limited by compute. A job below it is limited by memory.

##### GPUs and TPUs

| | H100 | TPU v5p |
|---|---|---|
| 16-bit compute per chip | 989 TFLOPS | 459 TFLOPS |
| Main memory | 80 GB | 95 GiB |
| Memory bandwidth | 3.35 TB/s | 2.77 TB/s |
| Largest connected group | A small NVLink domain, then a slower network | 8,960 chips in a 3D torus |

The main difference for LLM work is how chips connect. An H100 has fast links within a small group, then slower links beyond it. A TPU pod connects thousands of chips directly to their neighbours, in a 3D grid. Compare them on your own workload, rather than on one peak number.

#### The maths

$$ T_{\min} = \max\!\Big(\frac{\text{FLOPs}}{\text{compute}},\; \frac{\text{bytes}}{\text{bandwidth}}\Big), \qquad I = \frac{\text{FLOPs}}{\text{bytes}} $$

The roofline idea, as used in How to Scale Your Model. If the maths and the data movement can’t overlap, the two times add up, which gives an upper limit.

- **the best possible time**: The step can’t finish faster than its slowest requirement.

- **time for the maths**: Operations needed, divided by what the chip can do each second.

- **time to move the data**: Bytes moved, divided by memory or network bandwidth.

- **arithmetic intensity**: Operations per byte. Compare it with the chip’s own ratio, about 295 on an H100.

## In practice

### In practice

#### In practice

- **Check what the number means:** NVIDIA's page lists an H100 at 1,979 TFLOPS "with sparsity". The 989 figure used in research is half that. Check before you estimate.

- **Peak isn't real:** FlashAttention-2 reached only 35% of an H100's peak. FlashAttention-3 reached 740 TFLOPS, about 75%. Llama 3 405B pre-training ran at 38 to 43% utilisation.

- **Lower precision helps both limits:** FP8 doubles matmul speed on an H100, and halves the bytes to move. See LLM quantization.

- **Batching has a limit:** at large batches, the cache dominates the bytes moved. Tokens per second then level off near bandwidth ÷ cache per conversation.

- **Fit your work to the links:** memory is roughly 4 times faster than NVLink's total, and NVLink is about 7 times faster than PCIe. Chatty work belongs on the fastest link available.

### The answer that sounds right

#### "A chip with twice the FLOPs will decode twice as fast"

It sounds right, as FLOPs are the number everyone quotes. But a decode step spends most of its time reading the weights and the KV cache from memory. With 32 conversations, the maths takes about 0.5 ms of a 10 ms step. Look at memory bandwidth, or make the cache smaller.

## Say it

### Why is decoding limited by memory, while prefill is limited by compute?

#### The interviewer pushes further

Follow-up 1 of 3

Estimate the best decode speed of an 8B model on an H100, with 32 conversations of 4,096 tokens.

Weights are 16 GB and the cache is 32 × 4,096 × 128 KiB, about 17.2 GB, so 33.2 GB per step. At 3.35 TB/s that's 9.9 ms. The maths takes only 0.52 ms, so memory is the limit. 32 tokens per 9.9 ms is about 3,200 tokens a second, as a best case.

Follow-up 2 of 3

Would a chip with twice the compute but the same memory speed help decoding?

Barely, because the step is already waiting on memory. It would help prefill and training, which spend their time on maths.

Follow-up 3 of 3

Why does on-chip SRAM matter if it's so small?

It's much faster than HBM, and a kernel can keep its working data there. FlashAttention works in tiles that fit in SRAM, so the large score matrix never has to go to main memory.

A job's best time is the larger of its maths time and its data movement time. Maths time is operations over compute, and data time is bytes over bandwidth. An H100 does about 989 TFLOPS but moves about 3.35 TB/s, so its balance point is about 295 operations per byte. Prefill does a lot of maths per byte, so compute limits it. Decode reads all the weights and the KV cache to produce one token per conversation, so memory bandwidth limits it. That's why GQA and MLA speed up decoding, and why batching helps: each read of the weights is shared across more conversations.

**Key terms and sources**

What is inside an AI chip, the roofline model, arithmetic intensity, why prefill and decode hit different limits, and how GPUs and TPUs differ.

#### Sources

- Austin et al., How to Scale Your Model (roofline, TPUs, GPUs, inference)

- NVIDIA H100 specification

- Google Cloud, TPU v5p specification

- Shah et al., FlashAttention-3

- Stanford CS336, resource accounting and GPUs lectures

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
