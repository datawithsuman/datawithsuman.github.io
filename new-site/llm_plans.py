# Seven-section plans for LLM lessons. Chapter text comes from the live pages (see ml_import.py).
from maths_plans import _plan

SHARES_PICTURE = """<svg viewBox="0 0 480 104" role="img" aria-label="Where parameters live. In an 8B model: 70 percent feed-forward, 17 percent attention, 13 percent embeddings. In a 70B model: 80 percent feed-forward, 17 percent attention, 3 percent embeddings.">
  <g font-size="13" fill="var(--ink)"><rect x="44" y="4" width="12" height="12" fill="var(--a)"/><text x="62" y="15">Feed-forward</text><rect x="170" y="4" width="12" height="12" fill="var(--c)"/><text x="188" y="15">Attention</text><rect x="272" y="4" width="12" height="12" fill="var(--b)"/><text x="290" y="15">Embeddings</text></g>
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="4" y="50">8B</text><text x="4" y="92">70B</text></g>
  <rect x="44" y="28" width="295" height="32" fill="var(--a)"/><rect x="339" y="28" width="70" height="32" fill="var(--c)"/><rect x="409" y="28" width="55" height="32" fill="var(--b)"/>
  <rect x="44" y="70" width="336" height="32" fill="var(--a)"/><rect x="380" y="70" width="71" height="32" fill="var(--c)"/><rect x="451" y="70" width="13" height="32" fill="var(--b)"/>
  <g font-size="14" font-weight="600" fill="#fff" text-anchor="middle"><text x="191" y="50">70%</text><text x="374" y="50">17%</text><text x="436" y="50">13%</text><text x="212" y="92">80%</text><text x="415" y="92">17%</text></g>
</svg>"""

CACHE_PICTURE = """<svg viewBox="0 0 480 136" role="img" aria-label="Conversations that fit on one GPU at 8k context. MHA fits 16, GQA-8 fits 64, MLA fits 227 and MQA fits 512.">
  <text x="4" y="14" font-size="13" fill="var(--dim)">Conversations that fit in 64 GiB, at 8k context each</text>
  <g font-size="14" fill="var(--ink)" text-anchor="end"><text x="64" y="44">MHA</text><text x="64" y="72" font-weight="700">GQA-8</text><text x="64" y="100">MLA</text><text x="64" y="128">MQA</text></g>
  <g fill="var(--dim)"><rect x="72" y="30" width="10" height="18"/><rect x="72" y="86" width="136" height="18"/><rect x="72" y="114" width="307" height="18"/></g><rect x="72" y="58" width="38" height="18" fill="var(--a)"/>
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="90" y="44">16</text><text x="118" y="72">64</text><text x="216" y="100">227</text><text x="387" y="128">512</text></g>
</svg>"""

BYTES_PICTURE = """<svg viewBox="0 0 480 116" role="img" aria-label="On GPT-2 medium, FlashAttention does slightly more arithmetic, 75.2 against 66.6 gigaFLOPs, but moves 4.4 gigabytes of memory against 40.3, and takes 7.3 milliseconds against 41.7.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="300" y="16">Standard</text><text x="420" y="16">FlashAttention</text></g>
  <path d="M0 28H480M0 58H480M0 88H480" stroke="var(--line-strong)"/>
  <g font-size="14" fill="var(--ink)"><text x="4" y="48">Arithmetic (GFLOPs)</text><text x="4" y="78">Memory moved (HBM, GB)</text><text x="4" y="108" font-weight="700">Time (ms)</text></g>
  <g font-size="15" font-weight="700" text-anchor="middle"><text x="300" y="48" fill="var(--ok)">66.6</text><text x="420" y="48" fill="var(--bad)">75.2</text><text x="300" y="78" fill="var(--bad)">40.3</text><text x="420" y="78" fill="var(--ok)">4.4</text><text x="300" y="108" fill="var(--bad)">41.7</text><text x="420" y="108" fill="var(--ok)">7.3</text></g>
</svg>"""

STRETCH_PICTURE = """<svg viewBox="0 0 480 148" role="img" aria-label="Stretching a 4k model to 16k. No change leaves 18 pairs at unseen angles and keeps 1 radian between neighbours. Position interpolation has none unseen but only 0.25 radians. NTK-aware has 17 unseen and 1 radian. YaRN has none unseen and 1 radian.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="270" y="16">Pairs at unseen angles</text><text x="420" y="16">Neighbour angle</text></g>
  <path d="M0 28H480M0 58H480M0 88H480M0 118H480" stroke="var(--line-strong)"/>
  <g font-size="14" fill="var(--ink)"><text x="4" y="48">No change</text><text x="4" y="78">Position interpolation</text><text x="4" y="108">NTK-aware</text><text x="4" y="138" font-weight="700">YaRN</text></g>
  <g font-size="15" font-weight="700" text-anchor="middle"><text x="270" y="48" fill="var(--bad)">18 of 64</text><text x="420" y="48" fill="var(--ok)">1 rad</text><text x="270" y="78" fill="var(--ok)">0</text><text x="420" y="78" fill="var(--bad)">0.25 rad</text><text x="270" y="108" fill="var(--bad)">17 of 64</text><text x="420" y="108" fill="var(--ok)">1 rad</text><text x="270" y="138" fill="var(--ok)">0</text><text x="420" y="138" fill="var(--ok)">1 rad</text></g>
</svg>"""

ROUTER_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="Load on 8 experts. Without balancing, expert 1 gets far more than its fair share and goes over the capacity line, while expert 8 gets almost nothing. With bias balancing, all eight are about equal and under the line.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="110" y="16">No balancing</text><text x="360" y="16">Bias balancing</text></g>
  <g fill="var(--bad)"><rect x="14" y="30" width="18" height="81"/></g><g fill="var(--a)"><rect x="38" y="53" width="18" height="58"/><rect x="62" y="70" width="18" height="41"/><rect x="86" y="80" width="18" height="31"/><rect x="110" y="87" width="18" height="24"/><rect x="134" y="94" width="18" height="17"/><rect x="158" y="101" width="18" height="10"/><rect x="182" y="106" width="18" height="5"/>
  <rect x="264" y="77" width="18" height="34"/><rect x="288" y="77" width="18" height="34"/><rect x="312" y="77" width="18" height="34"/><rect x="336" y="77" width="18" height="34"/><rect x="360" y="77" width="18" height="34"/><rect x="384" y="77" width="18" height="34"/><rect x="408" y="77" width="18" height="34"/><rect x="432" y="77" width="18" height="34"/></g>
  <path d="M8 111H206M258 111H456" stroke="var(--line-strong)" stroke-width="1.5"/>
  <path d="M8 68H206M258 68H456" stroke="var(--dim)" stroke-width="1.5" stroke-dasharray="4 4"/>
  <g font-size="13" fill="var(--dim)" text-anchor="middle"><text x="110" y="127">Experts 1 to 8</text><text x="357" y="127">Experts 1 to 8</text><text x="357" y="62">Capacity</text></g>
</svg>"""

SHIFT_PICTURE = """<svg viewBox="0 0 480 90" role="img" aria-label="The sentence your biryani will arrive in 20 minutes. Each position sees the tokens so far and predicts the next token, the same sentence shifted by one, giving eight training examples.">
  <g font-size="13" font-weight="600" fill="var(--dim)"><text x="0" y="28">Sees</text><text x="0" y="74">Predicts</text></g>
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="1.5"><rect x="56" y="10" width="50" height="28" rx="4"/><rect x="109" y="10" width="50" height="28" rx="4"/><rect x="162" y="10" width="50" height="28" rx="4"/><rect x="215" y="10" width="50" height="28" rx="4"/><rect x="268" y="10" width="50" height="28" rx="4"/><rect x="321" y="10" width="50" height="28" rx="4"/><rect x="374" y="10" width="50" height="28" rx="4"/><rect x="427" y="10" width="50" height="28" rx="4"/></g>
  <g fill="var(--a)"><rect x="56" y="56" width="50" height="28" rx="4"/><rect x="109" y="56" width="50" height="28" rx="4"/><rect x="162" y="56" width="50" height="28" rx="4"/><rect x="215" y="56" width="50" height="28" rx="4"/><rect x="268" y="56" width="50" height="28" rx="4"/><rect x="321" y="56" width="50" height="28" rx="4"/><rect x="374" y="56" width="50" height="28" rx="4"/><rect x="427" y="56" width="50" height="28" rx="4"/></g>
  <g font-size="11" fill="var(--ink)" text-anchor="middle"><text x="81" y="28">&lt;s&gt;</text><text x="134" y="28">your</text><text x="187" y="28">biryani</text><text x="240" y="28">will</text><text x="293" y="28">arrive</text><text x="346" y="28">in</text><text x="399" y="28">20</text><text x="452" y="28">minutes</text></g>
  <g font-size="11" font-weight="600" fill="#fff" text-anchor="middle"><text x="81" y="74">your</text><text x="134" y="74">biryani</text><text x="187" y="74">will</text><text x="240" y="74">arrive</text><text x="293" y="74">in</text><text x="346" y="74">20</text><text x="399" y="74">minutes</text><text x="452" y="74">.</text></g>
  <path d="M81 40V54M134 40V54M187 40V54M240 40V54M293 40V54M346 40V54M399 40V54M452 40V54" stroke="var(--dim)" stroke-width="1.5"/>
</svg>"""

FUNNEL_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="A pipeline that narrows at each step: crawled web pages, extract main text, URL, language and quality filters, remove near-duplicates, then remove PII and benchmarks.">
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="2"><rect x="20" y="2" width="440" height="26" rx="5"/><rect x="50" y="32" width="380" height="26" rx="5"/><rect x="80" y="62" width="320" height="26" rx="5"/><rect x="115" y="92" width="250" height="26" rx="5"/></g><rect x="145" y="122" width="190" height="26" rx="5" fill="var(--a)"/>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="240" y="20">Crawled web pages</text><text x="240" y="50">Extract main text</text><text x="240" y="80">URL, language and quality filters</text><text x="240" y="110">Remove near-duplicates</text><text x="240" y="140" fill="#fff">PII, benchmarks out</text></g>
</svg>"""

SPLIT_PICTURE = """<svg viewBox="0 0 480 158" role="img" aria-label="Two rectangles with about the same area, meaning the same compute. Gopher is wide and flat: 280B parameters on 300B tokens, predicted loss 2.000. Chinchilla is narrow and tall: 70B parameters on 1.4 trillion tokens, predicted loss 1.974.">
  <rect x="20" y="82" width="168" height="21" fill="var(--bad)" fill-opacity=".75"/><rect x="290" y="5" width="42" height="98" fill="var(--ok)"/>
  <path d="M10 103H210M270 103H470" stroke="var(--line-strong)" stroke-width="1.5"/>
  <g font-size="14" font-weight="700" fill="var(--ink)"><text x="20" y="124">Gopher</text><text x="290" y="124">Chinchilla</text></g>
  <g font-size="13" fill="var(--dim)"><text x="20" y="141">280B parameters, 300B tokens</text><text x="290" y="141">70B parameters, 1.4T tokens</text><text x="20" y="156">Predicted loss 2.000</text><text x="290" y="156">Predicted loss 1.974</text></g>
</svg>"""

SHARD_PICTURE = """<svg viewBox="0 0 480 156" role="img" aria-label="Model state per GPU for a 70B model on 64 GPUs. Data parallel 1,120 gigabytes, ZeRO-1 293, ZeRO-2 155, and ZeRO-3 17.5, which is the only one under the 80 gigabyte GPU limit.">
  <text x="4" y="14" font-size="13" fill="var(--dim)">Model state per GPU: 70B model, 64 GPUs</text>
  <g font-size="14" fill="var(--ink)" text-anchor="end"><text x="66" y="44">DDP</text><text x="66" y="72">ZeRO-1</text><text x="66" y="100">ZeRO-2</text><text x="66" y="128" font-weight="700">ZeRO-3</text></g>
  <g fill="var(--bad)"><rect x="74" y="30" width="330" height="18"/><rect x="74" y="58" width="86" height="18"/><rect x="74" y="86" width="46" height="18"/></g><rect x="74" y="114" width="5" height="18" fill="var(--ok)"/>
  <path d="M98 24V140" stroke="var(--ink)" stroke-width="1.5" stroke-dasharray="4 4"/><text x="104" y="128" font-size="13" fill="var(--ok)" font-weight="600">17.5 GB fits</text>
  <text x="98" y="154" font-size="13" font-weight="600" fill="var(--ink)" text-anchor="middle">80 GB GPU</text>
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="412" y="44">1,120 GB</text><text x="168" y="72">293 GB</text><text x="128" y="100">155 GB</text></g>
</svg>"""

DRIFT_PICTURE = """<svg viewBox="0 0 480 116" role="img" aria-label="Cross-entropy with drifting logits. The exact loss stays at 0.4496. Computed from bf16 logits, it reads 0.4600 at drift 50, 0.5174 at drift 200 and 0.2974 at drift 300.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="240" y="16">Exact loss</text><text x="400" y="16">Loss from bf16 logits</text></g>
  <path d="M0 28H480M0 58H480M0 88H480" stroke="var(--line-strong)"/>
  <g font-size="14" fill="var(--ink)"><text x="4" y="48">Drift 50</text><text x="4" y="78">Drift 200</text><text x="4" y="108">Drift 300</text></g>
  <g font-size="15" font-weight="700" text-anchor="middle"><g fill="var(--ok)"><text x="240" y="48">0.4496</text><text x="240" y="78">0.4496</text><text x="240" y="108">0.4496</text></g><g fill="var(--bad)"><text x="400" y="48">0.4600</text><text x="400" y="78">0.5174</text><text x="400" y="108">0.2974</text></g></g>
</svg>"""

HOW = ["Intuition", "How it works", "In practice"]

LLM_PLANS = {
    "fundamentals/modern-llm-architecture": _plan(
        "The delivery app wants its own support assistant, an open 8B model like Llama 3 8B. A colleague says it's the 2017 Transformer made bigger, with most of the parameters in attention. The interviewer asks:",
        "What changed since 2017, and where do an 8B model's parameters live?",
        "Think of a restaurant famous for its front counter, where orders get passed along. Everyone talks about the counter, but most of the staff are in the back kitchen. Attention is the counter, and the feed-forward layers are the kitchen.",
        SHARES_PICTURE, "Counted in the lab, from the Llama 3 model cards.",
        ("c3", "<b>Try to break it.</b> Start at the 8B shape, then switch to 70B. Change SwiGLU to classic FFN, GQA to full MHA and a separate output head to tied embeddings. Watch the totals and shares.", "<b>Now say why:</b> why does the embeddings share drop so much at 70B, while the feed-forward share rises?"),
        ["c2", "c5"], ["c4"], [], ["src"],
        ["Modern LLMs are decoder-only Transformers.",
         "Pre-norm residual blocks with RMSNorm keep deep training stable.",
         "SwiGLU replaces the ReLU feed-forward layer.",
         "RoPE is applied to queries and keys.",
         "Grouped-query attention shrinks the KV cache.",
         "There are no biases, and vocabularies are large, around 128k tokens.",
         "Most parameters are in feed-forward: about 70% at 8B and 80% at 70B.",
         "That's why MoE replaces the FFN, and quantisation and pruning focus there."],
        tabs=HOW,
        trap_title="\"Most parameters are in attention\"",
        trap_html="<p>It sounds right, since attention is what the Transformer is famous for. But count them in Llama 3 8B: the feed-forward layers hold 70%, attention only 17% and the embedding tables 13%. So when people prune, quantise or route, they mostly target the FFN.</p>"),
    "fundamentals/attention-variants-mqa-gqa-mla": _plan(
        "Your 8B assistant runs on one 80 GB GPU, and its weights take about 16 GB. Customers chat with 8k tokens of history each. A colleague assumes the weights decide how many fit at once. The interviewer asks:",
        "How many conversations fit on one GPU, and how do GQA and MLA raise that?",
        "Think of 32 researchers who each keep a private copy of the same catalogue. Their questions differ, but the catalogues are nearly identical. Share one copy per group of four and you free up most of the shelf space, and they can still ask their own questions.",
        CACHE_PICTURE, "From the lab: the Llama 3 8B shape, with bf16 cache. GQA-8 is what Llama 3 uses.",
        ("c3", "<b>Try to break it.</b> Switch between MHA, GQA-8, MQA and MLA at 8k context. Then raise the context per conversation and the number of conversations.", "<b>Now say why:</b> if MQA has the smallest cache of all, why did GQA become the default?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["We cache keys and values for every token, layer and head.",
         "Cache size is 2 × layers × KV heads × head dimension × tokens × bytes.",
         "Decoding is memory-bandwidth bound, so the cache limits batch size and context.",
         "MQA shares one K/V head across all query heads: smallest, but it loses quality.",
         "GQA shares one K/V head per group, giving a 4× smaller cache with near-MHA quality in Llama 3.",
         "MLA caches a compressed latent and reconstructs K and V.",
         "You did the sum: 128 KiB per token, so 1 GiB for an 8k conversation."],
        trap_title="\"The smallest cache wins, so MQA is strictly better\"",
        trap_html="<p>It sounds right, since MQA fits 512 conversations where GQA-8 fits 64. But giving every query head the same keys and values costs quality and can make training less stable. That's why GQA became the default, and why MLA tries to get a small cache without the quality loss. And the weights usually aren't the limit either: at long context, the KV cache dominates.</p>"),
    "fundamentals/flashattention": _plan(
        "The team fine-tunes the assistant on chat transcripts of up to 32k tokens. Plain attention runs out of memory. FlashAttention runs, finishes faster and gives the same numbers, even though it does more arithmetic. The interviewer asks:",
        "Why is exact attention faster when it does more maths?",
        "Think of cooking with the pantry at the far end of a long hall. The slow part isn't the chopping, it's the walking. So you bring one small tray to your counter, finish it there and only then go back. You chop slightly more, and walk far less.",
        BYTES_PICTURE, "Measured in the paper on GPT-2 medium, sequence length 1,024, on an A100.",
        ("c3", "<b>Try to break it.</b> Drag the sequence length up to 32k, and compare the score matrix with the saved row statistics.", "<b>Now say why:</b> FlashAttention throws the matrix away, so how can the backward pass still work?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["Standard attention writes the N × N score and probability matrices to high-bandwidth memory and reads them back.",
         "So it's memory-bandwidth bound and uses quadratic memory.",
         "FlashAttention tiles Q, K and V into blocks that fit in on-chip SRAM.",
         "It fuses the matmuls, softmax and value multiply into one kernel.",
         "An online softmax keeps a running max and sum per row, and rescales partial results.",
         "It's exact, uses linear memory and recomputes tiles in the backward pass."],
        trap_title="\"It's faster because it does fewer FLOPs\"",
        trap_html="<p>It sounds right, since faster usually means less work. But it does slightly more: 75.2 against 66.6 GFLOPs on GPT-2 medium. It moves far fewer bytes, 4.4 GB against 40.3 GB. And compute is still quadratic. It's memory that becomes linear, so don't say FlashAttention makes attention linear.</p>"),
    "fundamentals/long-context": _plan(
        "The assistant was pre-trained on 4k-token contexts, and the team wants it to read a customer's full history of about 16k tokens. They feed it in, and perplexity explodes after position 4,096. The interviewer asks:",
        "Why does a 4k model break at 16k, and how does YaRN fix it?",
        "Think of a clock's hands in training. The second hand has gone round many times, so every angle is familiar. The hour hand has never finished a lap, so going further shows it angles it has never seen. YaRN slows only the slow hands, and leaves the fast ones alone so nearby tokens stay distinct.",
        STRETCH_PICTURE, "From the lab: stretching a 4k model to 16k, with 64 rotary pairs.",
        ("c3", "<b>Try to break it.</b> At 16k, switch between no change, position interpolation, NTK-aware and YaRN. Then push the target to 64k.", "<b>Now say why:</b> position interpolation leaves nothing unseen, so why does it still need fine-tuning?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["RoPE rotates pairs of query and key dimensions at different speeds.",
         "Beyond the training length, the slow pairs hit angles never seen in training, so quality collapses.",
         "Position interpolation rescales positions into range, but blurs local order.",
         "NTK-aware scaling raises the RoPE base instead.",
         "YaRN interpolates only the low-frequency pairs, keeps the high-frequency ones and adds an attention temperature.",
         "Sliding windows bound memory, and StreamingLLM shows you must keep a few attention-sink tokens.",
         "You'd verify usable context with RULER-style tests."],
        trap_title="\"A 128k model uses all 128k tokens equally well\"",
        trap_html="<p>It sounds right, since that's what the spec sheet says. But Liu et al. found that models use information at the start and end of a long context much better than in the middle. RULER showed many models degrading well before their advertised length on harder tasks. StreamingLLM doesn't help here either: it keeps a fixed window, and evicted text is gone. So test it.</p>"),
    "fundamentals/mixture-of-experts": _plan(
        "The team considers swapping the 8B dense assistant for an MoE model with similar compute per token but far more parameters. A colleague says that means the same hardware and a smarter model. The interviewer asks:",
        "How does a 47B model run at 13B cost, and what goes wrong?",
        "Think of a large call centre where each call goes to only two agents. You have many agents on the payroll, but each call uses very few. If the router favours one agent, that queue overflows, and agents who get no calls never improve. You also still pay for every agent, busy or not.",
        ROUTER_PICTURE, "1,024 tokens at capacity factor 1.25. Expert 1's 2.37× and expert 8's 0.15× are from the lab; the bars between are illustrative.",
        ("c3", "<b>Try to break it.</b> Use top-2 with no balancing, and raise the capacity factor. Then switch to bias balancing, and compare the dropped token-slots.", "<b>Now say why:</b> raising capacity also cuts drops, so why isn't that the fix?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["An MoE layer replaces the dense FFN with many expert FFNs and a learned router.",
         "Each token goes to its top-k experts, weighted by a softmax over the selected scores.",
         "Compute per token depends only on active parameters: Mixtral is 47B total and about 13B active.",
         "Load balancing is the main challenge: experts can collapse, and tokens get dropped at capacity.",
         "Fixes: an auxiliary loss, capacity factors, shared experts or DeepSeek-V3's bias-based balancing.",
         "It saves FLOPs, not memory, and needs expert parallelism with all-to-all communication."],
        trap_title="\"MoE reduces memory\"",
        trap_html="<p>It sounds right, since it only uses a fraction of the model per token. But every expert must sit in GPU memory, so Mixtral needs the memory of a 47B model to run at 13B compute. It reduces compute per token, and memory still follows total parameters. And experts aren't topic specialists either: Mixtral's routing followed syntax and token patterns more than domains.</p>"),
    "fundamentals/next-token-prediction": _plan(
        "The team has a huge pile of raw text and almost no labels. A new hire asks where the training labels come from when you pre-train an LLM. The interviewer asks:",
        "How does one sentence become eight training examples?",
        "Think of reading with a card that covers everything after the current word. You guess the next word, slide the card along, and check. Every word becomes its own small test, so any text is full of them. The causal mask is the card.",
        SHIFT_PICTURE, "Each position sees only the tokens so far. One forward pass gives all eight predictions.",
        ("c3", "<b>Try to break it.</b> Start with the trained model and find the most surprising token. Then try the confidently wrong model, and the one that memorised the sentence.", "<b>Now say why:</b> the memorising model scores almost zero, so why is it no good?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["By the chain rule, a text's probability is the product of each token's probability given the previous tokens.",
         "So we minimise the average cross-entropy of the true next token across all positions.",
         "A causal mask blocks future tokens, so one forward pass gives a loss at every position.",
         "Teacher forcing feeds the true previous tokens, which can cause exposure bias.",
         "Documents are packed into fixed-length sequences with end-of-text separators.",
         "The loss starts near the log of the vocabulary size.",
         "The exponential of held-out loss is perplexity."],
        edits=[('<a href="https://datawithsuman.github.io/ai/interview-prep/fundamentals/llms/">SFT</a>', '<a href="../supervised-fine-tuning/">SFT</a>'),
               ('<a href="https://datawithsuman.github.io/ai/interview-prep/fundamentals/llms/">post-training</a>', '<a href="../supervised-fine-tuning/">post-training</a>')],
        trap_title="\"Lower training loss means a better model\"",
        trap_html="<p>It sounds right, since loss is what training minimises. But a model that has memorised the lab's sentence scores 0.01, and that says nothing about new text. Watch held-out loss, and deduplicate the data. Also note that the model doesn't generate during training: that's teacher forcing in parallel, and generation is sequential.</p>"),
    "fundamentals/pretraining-data": _plan(
        "While crawling the web for food-related text, the team finds thousands of near-identical restaurant pages from one template. A colleague says to keep them, because more data is always better. The interviewer asks:",
        "How do trillions of web tokens become training data?",
        "Think of cleaning raw grain before an expensive mill. Milling time is fixed, so every stone, husk and repeated sack wastes it. You sieve first, then keep and mix the best grain. MinHash is the quick test that spots two sacks from the same batch without checking each grain.",
        FUNNEL_PICTURE, "Illustrative widths. A typical pipeline, as in FineWeb, which ended with 15 trillion tokens from 96 snapshots.",
        ("c3", "<b>Try to break it.</b> Switch between 16, 112 and 256 hash functions. Compare pages A and B with pages A and C, and watch the flagged pairs and the largest estimate error.", "<b>Now say why:</b> A and C come from the same template, so why does the pipeline keep both?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["Extract main text from crawled HTML, and filter by URL and language.",
         "Apply heuristic quality rules, like those from Gopher and C4.",
         "Remove near-duplicates with MinHash over word n-grams.",
         "MinHash estimates Jaccard similarity from short signatures, and LSH buckets make it scale.",
         "Redact PII and remove benchmark questions.",
         "Model-based quality classifiers, as in FineWeb-Edu, raised MMLU at the same token budget.",
         "Choose a mixture, tuned with small proxy runs."],
        tabs=HOW,
        trap_title="\"More data is always better\"",
        trap_html="<p>It sounds right, until you remember pre-training compute is fixed. Filtered, deduplicated data beats bigger raw data at equal compute. Lee et al. found that deduplicating C4 cut memorised output by about 10×, and needed fewer steps for the same accuracy. And exact hashing isn't enough: change one word and it misses the copy.</p>"),
    "fundamentals/scaling-laws": _plan(
        "The team has a fixed GPU budget for a home-grown model. One camp wants the biggest model it can afford, and the other wants a smaller one on more tokens. The interviewer asks:",
        "Bigger model or more tokens, and why was Llama 3 8B trained on 15T?",
        "Think of the budget as a rectangle with a fixed area. One side is model size, and the other is training tokens. Wide and flat costs the same as narrow and tall, but they don't learn equally well. The best shape is about 20 tokens per parameter.",
        SPLIT_PICTURE, "Sizes to scale, with about the same compute. Predicted loss from the fitted law, as in the lab.",
        ("c3", "<b>Try to break it.</b> Compare Gopher with Chinchilla at similar compute. Then look at Llama 3 405B and Llama 3 8B, and see how far each sits from its optimum.", "<b>Now say why:</b> the law says Llama 3 8B is far from optimal. Why would Meta do that on purpose?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["Pre-training loss follows power laws, so labs fit them on small runs to plan big ones.",
         "Training compute is about 6 × parameters × tokens.",
         "Kaplan suggested scaling model size faster than data.",
         "Chinchilla found they should scale equally, at roughly 20 tokens per parameter.",
         "A 70B model on 1.4T tokens beat the 280B Gopher at the same compute.",
         "Models are now over-trained past that, like Llama 3 8B on 15T tokens.",
         "Chinchilla minimises training cost only, and a smaller model is much cheaper at inference."],
        edits=[("That's deliberate: see below.", "That's deliberate: see the In practice tab.")],
        trap_title="\"Chinchilla-optimal is always best\"",
        trap_html="<p>It sounds right, since it gives the lowest loss for the compute. But it minimises training compute only, and a model served to millions spends far more at inference. Once inference demand is included, the best model is smaller and trained on many more tokens. Scaling laws also predict loss, not benchmark scores, and task accuracy is noisier.</p>"),
    "fundamentals/distributed-training": _plan(
        "The team wants to fully fine-tune a 70B model on a cluster of 80 GB GPUs. A colleague says just add more GPUs with data parallel until it fits. The interviewer asks:",
        "Why does a 70B model need 1.1 TB to train, and how is it split?",
        "Think of cooks who each keep their own full copy of a huge recipe library. Hiring more cooks never shrinks the library. Split it across everyone's shelves, and each cook fetches the page when needed. That saves a lot of room, in exchange for more walking.",
        SHARD_PICTURE, "From the lab: 16 bytes per parameter, before activations. Only ZeRO-3 fits on an 80 GB GPU.",
        ("c3", "<b>Try to break it.</b> At 70B and 64 GPUs, go from DDP to ZeRO-3. Then change the GPU count under DDP. In the second lab, change the pipeline stages and micro-batches.", "<b>Now say why:</b> ZeRO-3 clearly uses the least memory, so why do huge runs also need tensor and pipeline parallelism?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["Mixed-precision training with Adam needs about 16 bytes per parameter.",
         "That's bf16 weights and gradients, plus fp32 master weights and two Adam moments.",
         "Data parallelism replicates the model and all-reduces gradients.",
         "ZeRO-1, -2 and -3, or FSDP, shard optimizer state, gradients and finally weights.",
         "Tensor parallelism splits each matmul within an NVLink node.",
         "Pipeline parallelism assigns layers to GPUs, with a bubble of (p−1)/(m+p−1).",
         "Large runs like Llama 3 405B combine tensor, pipeline, context and data parallelism."],
        tabs=HOW,
        trap_title="\"Adding GPUs to DDP lets a bigger model fit\"",
        trap_html="<p>It sounds right, since more GPUs means more memory in total. But DDP keeps everything on every GPU, so a 70B model needs 1,120 GB per GPU however many you add. You need sharding or model parallelism. The weights aren't the main cost either: optimizer state is 12 of the 16 bytes.</p>"),
    "fundamentals/training-instabilities": _plan(
        "Three weeks into continued pre-training of the assistant, the loss jumps from 2.1 to 7 in a few hundred steps. Each restart costs days of compute. The interviewer asks:",
        "Your loss spikes at step 40k. What happened, and what do you do?",
        "Think of a shop calculator that keeps only a few significant digits. Add 300 to every price, and on paper the differences haven't changed. But the calculator starts rounding, and two different prices read the same. The loss can't see this drift, so nothing stops it.",
        DRIFT_PICTURE, "From the lab. The model's predictions haven't changed, but the computed loss has.",
        ("c3", "<b>Try to break it.</b> Drag the logit drift from 0 up to 300. Compare the exact loss, the loss from bf16 logits and the z-loss penalty.", "<b>Now say why:</b> if the softmax doesn't change when you shift every logit, why isn't drift harmless?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["Large runs suffer loss spikes and divergence, often from logits growing out of control.",
         "Output logits can drift because softmax is shift-invariant, which breaks bf16 precision.",
         "Attention logits can grow until attention becomes one-hot.",
         "Z-loss, a 1e-4 penalty on log Z squared, keeps the normaliser near one.",
         "QK-norm, pre-norm, warm-up, gradient clipping and data cleaning also help.",
         "When a spike happens, roll back to a checkpoint and skip the batches around it.",
         "At scale, you also need frequent checkpoints and automatic restarts for hardware failures."],
        trap_title="\"Spikes are always bad data\"",
        trap_html="<p>It sounds right, since the spike appears at a particular batch. But PaLM's authors replayed the same batches from an earlier checkpoint and the spike didn't come back. It took particular data and a particular parameter state together. \"Just lower the learning rate\" isn't the full answer either: it helps, but it slows training, so fix the cause.</p>"),
}

MASK_PICTURE = """<svg viewBox="0 0 480 76" role="img" aria-label="A training conversation. The model reads the system prompt and the customer's message with no loss on them. It is trained only on the assistant's reply, including the end token.">
  <g fill="var(--tint)" stroke="var(--line-strong)" stroke-width="1.5"><rect x="2" y="4" width="120" height="40" rx="6"/><rect x="128" y="4" width="130" height="40" rx="6"/></g><rect x="264" y="4" width="214" height="40" rx="6" fill="var(--a)"/>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="62" y="29">System prompt</text><text x="193" y="29">Customer's text</text><text x="371" y="29" fill="#fff">Reply + end token</text></g>
  <g font-size="13" text-anchor="middle"><text x="130" y="66" fill="var(--dim)">Read, but no loss</text><text x="371" y="66" font-weight="600" fill="var(--a)">Trained on</text></g>
</svg>"""

GOODHART_PICTURE = """<svg viewBox="0 0 480 116" role="img" aria-label="Best-of-N. At N of 1 the reward-model score is 0.06 and true quality is minus 0.23. At N of 16 the score is 2.58 and quality is 0.21. At N of 1,024 the score is 4.66 and quality is minus 0.44.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="250" y="16">Reward-model score</text><text x="410" y="16">True quality</text></g>
  <path d="M0 28H480M0 58H480M0 88H480" stroke="var(--line-strong)"/>
  <g font-size="14" fill="var(--ink)"><text x="4" y="48">No optimising, N = 1</text><text x="4" y="78">Best of 16</text><text x="4" y="108">Best of 1,024</text></g>
  <g font-size="15" font-weight="700" text-anchor="middle"><g fill="var(--ink)"><text x="250" y="48">0.06</text><text x="250" y="78">2.58</text><text x="250" y="108">4.66</text></g><text x="410" y="48" fill="var(--dim)">−0.23</text><text x="410" y="78" fill="var(--ok)">0.21</text><text x="410" y="108" fill="var(--bad)">−0.44</text></g>
</svg>"""

MODELS_PICTURE = """<svg viewBox="0 0 480 92" role="img" aria-label="RLHF with PPO keeps four models in memory: policy, reference, reward model and value model. DPO keeps two: policy and reference.">
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="4" y="30">RLHF (PPO)</text><text x="4" y="76">DPO</text></g>
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="2"><rect x="96" y="8" width="84" height="34" rx="6"/><rect x="186" y="8" width="84" height="34" rx="6"/><rect x="96" y="54" width="84" height="34" rx="6"/><rect x="186" y="54" width="84" height="34" rx="6"/></g>
  <g fill="var(--bad)" fill-opacity=".16" stroke="var(--bad)" stroke-width="2"><rect x="276" y="8" width="96" height="34" rx="6"/><rect x="378" y="8" width="96" height="34" rx="6"/></g>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="138" y="30">Policy</text><text x="228" y="30">Reference</text><text x="324" y="30">Reward</text><text x="426" y="30">Value</text><text x="138" y="76">Policy</text><text x="228" y="76">Reference</text></g>
</svg>"""

ADVANTAGE_PICTURE = """<svg viewBox="0 0 480 116" role="img" aria-label="Group-relative advantages for 8 samples. With 1 of 8 correct, the right answer gets plus 2.65 and each wrong one minus 0.38. With 4 of 8, plus 1 and minus 1. With 0 or 8 correct, every advantage is 0.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="270" y="16">Right answers get</text><text x="420" y="16">Wrong answers get</text></g>
  <path d="M0 28H480M0 58H480M0 88H480" stroke="var(--line-strong)"/>
  <g font-size="14" fill="var(--ink)"><text x="4" y="48">1 of 8 correct</text><text x="4" y="78">4 of 8 correct</text><text x="4" y="108">0 or 8 correct</text></g>
  <g font-size="15" font-weight="700" text-anchor="middle"><text x="270" y="48" fill="var(--ok)">+2.65</text><text x="420" y="48" fill="var(--bad)">−0.38</text><text x="270" y="78" fill="var(--ok)">+1</text><text x="420" y="78" fill="var(--bad)">−1</text><text x="270" y="108" fill="var(--dim)">0</text><text x="420" y="108" fill="var(--dim)">0</text></g>
</svg>"""

SOFT_PICTURE = """<svg viewBox="0 0 480 146" role="img" aria-label="After the biryani was. The one-hot label puts everything on delicious. The teacher gives delicious 65 percent, tasty 29 percent, cold 3.6 percent, late 1.8 percent and purple almost nothing.">
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="90" y="16">One-hot label</text><text x="290" y="16">Teacher</text></g>
  <g font-size="14" fill="var(--ink)" text-anchor="end"><text x="80" y="42">delicious</text><text x="80" y="66">tasty</text><text x="80" y="90">cold</text><text x="80" y="114">late</text><text x="80" y="138">purple</text></g>
  <rect x="90" y="30" width="150" height="16" fill="var(--dim)"/>
  <g fill="var(--a)"><rect x="290" y="30" width="98" height="16"/><rect x="290" y="54" width="44" height="16"/><rect x="290" y="78" width="5" height="16"/><rect x="290" y="102" width="3" height="16"/></g>
  <g font-size="13" font-weight="600" fill="var(--ink)"><text x="248" y="42">100%</text><text x="396" y="42">65.3%</text><text x="342" y="66">29.3%</text><text x="303" y="90">3.6%</text><text x="301" y="114">1.8%</text><text x="290" y="138">Almost 0%</text></g>
  <g font-size="13" fill="var(--dim)"><text x="90" y="66">0</text><text x="90" y="90">0</text><text x="90" y="114">0</text><text x="90" y="138">0</text></g>
</svg>"""

LORA_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="Memory for weights and optimizer with Llama 3 8B. Full fine-tuning needs 128.5 gigabytes. LoRA needs 16.7. QLoRA needs 5.1. Both fit on a 24 gigabyte GPU.">
  <g font-size="14" fill="var(--ink)" text-anchor="end"><text x="66" y="24">Full</text><text x="66" y="54">LoRA</text><text x="66" y="84" font-weight="700">QLoRA</text></g>
  <rect x="74" y="10" width="330" height="18" fill="var(--bad)"/><rect x="74" y="40" width="43" height="18" fill="var(--ok)"/><rect x="74" y="70" width="13" height="18" fill="var(--ok)"/>
  <path d="M136 4V102" stroke="var(--ink)" stroke-width="1.5" stroke-dasharray="4 4"/><text x="136" y="118" font-size="13" font-weight="600" fill="var(--ink)" text-anchor="middle">24 GB GPU</text>
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="412" y="24">128.5 GB</text><text x="144" y="54">16.7 GB</text><text x="144" y="84">5.1 GB</text></g>
</svg>"""

TAIL_PICTURE = """<svg viewBox="0 0 480 116" role="img" aria-label="At temperature 1, top-p keeps 131 tokens with 1.5 percent junk, and min-p keeps 5 with no junk. At temperature 2, top-p keeps 887 tokens with 79.7 percent junk, and min-p keeps 9 with no junk.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="240" y="16">Tokens kept</text><text x="400" y="16">Chance of junk</text></g>
  <path d="M0 28H480M0 58H480M0 88H480" stroke="var(--line-strong)"/>
  <g font-size="14" fill="var(--ink)"><text x="4" y="48">Top-p 0.9 at T = 1</text><text x="4" y="78">Top-p 0.9 at T = 2</text><text x="4" y="108" font-weight="700">Min-p 0.1 at T = 2</text></g>
  <g font-size="15" font-weight="700" text-anchor="middle"><text x="240" y="48" fill="var(--ink)">131</text><text x="400" y="48" fill="var(--ink)">1.5%</text><text x="240" y="78" fill="var(--bad)">887</text><text x="400" y="78" fill="var(--bad)">79.7%</text><text x="240" y="108" fill="var(--ok)">9</text><text x="400" y="108" fill="var(--ok)">None</text></g>
</svg>"""

COT_PICTURE = """<svg viewBox="0 0 480 134" role="img" aria-label="MultiArith accuracy. Zero-shot 17.7 percent, few-shot 33.8 percent, zero-shot chain-of-thought 78.7 percent, few-shot chain-of-thought 93 percent.">
  <text x="4" y="14" font-size="13" fill="var(--dim)">Accuracy on MultiArith</text>
  <g font-size="14" fill="var(--ink)" text-anchor="end"><text x="130" y="44">Zero-shot</text><text x="130" y="72">Few-shot</text><text x="130" y="100">Zero-shot CoT</text><text x="130" y="128">Few-shot CoT</text></g>
  <g fill="var(--dim)"><rect x="138" y="30" width="50" height="18"/><rect x="138" y="58" width="95" height="18"/></g><g fill="var(--a)"><rect x="138" y="86" width="220" height="18"/><rect x="138" y="114" width="260" height="18"/></g>
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="196" y="44">17.7%</text><text x="241" y="72">33.8%</text><text x="366" y="100">78.7%</text><text x="406" y="128">93.0%</text></g>
</svg>"""

MARKING_PICTURE = """<svg viewBox="0 0 480 116" role="img" aria-label="The same model under two gradings. With binary grading it always answers: 51.4 percent right and 48.6 percent wrong. With a penalty for wrong answers it answers only when confident: 10 percent right, 2.4 percent wrong and 87.6 percent I don't know.">
  <g font-size="13" fill="var(--ink)"><rect x="110" y="4" width="12" height="12" fill="var(--ok)"/><text x="128" y="15">Right</text><rect x="186" y="4" width="12" height="12" fill="var(--bad)"/><text x="204" y="15">Wrong</text><rect x="266" y="4" width="12" height="12" fill="var(--line-strong)"/><text x="284" y="15">"I don't know"</text></g>
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="4" y="50">No penalty</text><text x="4" y="96">Wrong = −3</text></g>
  <rect x="110" y="30" width="185" height="32" fill="var(--ok)"/><rect x="295" y="30" width="175" height="32" fill="var(--bad)"/>
  <rect x="110" y="76" width="36" height="32" fill="var(--ok)"/><rect x="146" y="76" width="9" height="32" fill="var(--bad)"/><rect x="155" y="76" width="315" height="32" fill="var(--line-strong)"/>
  <g font-size="14" font-weight="600" text-anchor="middle"><g fill="#fff"><text x="202" y="51">51.4%</text><text x="382" y="51">48.6%</text></g><text x="128" y="97" fill="#fff" font-size="12">10%</text><text x="312" y="97" fill="var(--ink)">87.6% (2.4% wrong)</text></g>
</svg>"""

MARGIN_PICTURE = """<svg viewBox="0 0 480 136" role="img" aria-label="95 percent margins at 60 percent accuracy. MMLU plus or minus 0.8 points, SWE-bench Verified 4.3, GPQA Diamond 6.8 and AIME 17.5.">
  <text x="280" y="14" font-size="13" fill="var(--dim)" text-anchor="middle">60% accuracy</text>
  <path d="M280 20V132" stroke="var(--line-strong)" stroke-width="1.5" stroke-dasharray="4 4"/>
  <g font-size="14" fill="var(--ink)"><text x="4" y="42">MMLU</text><text x="4" y="70">SWE-bench Verified</text><text x="4" y="98" font-weight="700">GPQA Diamond</text><text x="4" y="126">AIME</text></g>
  <g stroke-width="5" stroke-linecap="round"><path d="M274 37H286" stroke="var(--ok)"/><path d="M246 65H314" stroke="var(--a)"/><path d="M226 93H334" stroke="var(--b)"/><path d="M140 121H420" stroke="var(--bad)"/></g>
  <circle cx="280" cy="37" r="4" fill="var(--ink)"/><circle cx="280" cy="65" r="4" fill="var(--ink)"/><circle cx="280" cy="93" r="4" fill="var(--ink)"/><circle cx="280" cy="121" r="4" fill="var(--ink)"/>
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="296" y="42">±0.8</text><text x="324" y="70">±4.3</text><text x="344" y="98">±6.8</text><text x="430" y="126">±17.5</text></g>
</svg>"""

JUDGE_PICTURE = """<svg viewBox="0 0 480 86" role="img" aria-label="With position bias 1.0, judging once agrees with humans 66.2 percent of the time on every pair. Judging both orders and keeping consistent verdicts agrees 77.5 percent of the time on 59.7 percent of pairs.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="270" y="16">Agrees with humans</text><text x="420" y="16">Pairs kept</text></g>
  <path d="M0 28H480M0 58H480" stroke="var(--line-strong)"/>
  <g font-size="14" fill="var(--ink)"><text x="4" y="48">Judge once</text><text x="4" y="78" font-weight="700">Judge both orders</text></g>
  <g font-size="15" font-weight="700" text-anchor="middle"><text x="270" y="48" fill="var(--bad)">66.2%</text><text x="420" y="48" fill="var(--ink)">100%</text><text x="270" y="78" fill="var(--ok)">77.5%</text><text x="420" y="78" fill="var(--ink)">59.7%</text></g>
</svg>"""

LLM_PLANS.update({
    "fundamentals/supervised-fine-tuning": _plan(
        "You have a pre-trained 8B base model and 5,000 good support chats. Ask the base model a question, and it may produce more questions or a forum thread, because those are plausible continuations. The interviewer asks:",
        "How does a text-completer become an assistant, and why mask the prompt?",
        "Think of a mimic who has read the whole internet and will continue any script, including playing the customer. In rehearsal, you hand over full conversations but only correct the assistant's lines. The customer's lines are for reading, not for practising.",
        MASK_PICTURE, "With loss on every token, 72.4% of the loss in the lab's example comes from the first two parts.",
        ("c3", "<b>Try to break it.</b> Switch between loss on all tokens and loss on assistant tokens only. Watch the tokens trained on, and the share of the loss from system and user text.", "<b>Now say why:</b> what does training on the customer's text teach the model to do?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["SFT continues training with the same next-token cross-entropy, on example conversations.",
         "A chat template marks system, user and assistant turns with special tokens.",
         "The loss is masked, so only the assistant's tokens are trained.",
         "That includes the end-of-turn token, which teaches the model when to stop.",
         "Quality matters more than quantity: LIMA used 1,000 curated examples, and Llama 2 about 27k.",
         "It mainly teaches format and behaviour, on top of pre-trained knowledge.",
         "It's usually followed by preference tuning, RLHF or DPO."],
        tabs=HOW,
        trap_title="\"More SFT data is always better\"",
        trap_html="<p>It sounds right, since more data helped in pre-training. But LIMA's 1,000 curated examples were rated equal or better than GPT-4 in 43% of comparisons, and Llama 2 found 27,540 good annotations beat millions of lower-quality ones. SFT doesn't use a different loss either: it's the same cross-entropy, masked.</p>"),
    "fundamentals/rlhf-and-reward-models": _plan(
        "After SFT, the assistant's answers are acceptable, but some are curt, some over-apologise and some promise refunds that the policy doesn't allow. You ask agents to compare pairs of answers, and train a reward model. Then a colleague optimises it as hard as possible. The interviewer asks:",
        "Why does optimising a reward model too hard make answers worse?",
        "Think of a teacher who marks essays well but has a slight soft spot for long ones. Chasing that teacher's marks improves your writing at first. Push hard enough and you're padding pages: the marks keep rising while the essays get worse. So you keep the student close to how they wrote before.",
        GOODHART_PICTURE, "From the lab's simulation, where the reward model slightly over-rewards long answers.",
        ("c3", "<b>Try to break it.</b> Drag the number of answers per prompt from 1 up to 1,024. Watch the reward-model score, true quality and the KL.", "<b>Now say why:</b> the reward-model score keeps rising past N = 16, so what is the optimiser actually finding?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["RLHF starts from an SFT model and collects human comparisons between its answers.",
         "A reward model trains with a Bradley–Terry loss, so preferred answers score higher.",
         "The policy is optimised with RL, typically PPO, to maximise reward minus a KL penalty to the SFT model.",
         "InstructGPT made even a 1.3B model preferred over 175B GPT-3.",
         "The main risk is reward hacking: the reward model is a proxy, and true quality can drop.",
         "The KL penalty, early stopping, refreshed reward models and human evals guard against that."],
        trap_title="\"A higher reward-model score means a better model\"",
        trap_html="<p>It sounds right, since that's the score you're optimising. But it's a proxy. In the lab, the score climbs from 2.58 to 4.66 between N = 16 and N = 1,024, while true quality falls from 0.21 to −0.44. So pick checkpoints with human or held-out evaluations. RLHF doesn't teach new knowledge either: it mainly shapes behaviour and preferences.</p>"),
    "fundamentals/dpo": _plan(
        "The team has 20,000 comparisons from support agents, the same data RLHF would use. Chosen: \"Sorry about that! I've refunded the biryani.\" Rejected: \"Refunds aren't possible after delivery.\" They don't want to build an RL pipeline. The interviewer asks:",
        "How does DPO skip the reward model, and what can go wrong?",
        "Think of skipping the judge at a cooking contest, because you already have a list of which dish beat which. You adjust your recipes so winners become more likely than losers, compared with how you cooked before. The catch is that you only care about the gap, so both dishes can get worse.",
        MODELS_PICTURE, "RLHF with PPO keeps four models in memory, and DPO keeps two.",
        ("c3", "<b>Try to break it.</b> Set chosen to +5 and rejected to −5, and read the loss at each β. Then set chosen to −4 and rejected to −10.", "<b>Now say why:</b> in that second setting both answers became less likely, so why did the loss fall?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["DPO optimises the same KL-regularised preference objective as RLHF, without a reward model or RL.",
         "The optimal policy implies a reward: β times the log-ratio of policy to reference.",
         "Substituting that into Bradley–Terry gives a logistic loss on the chosen and rejected log-ratios.",
         "It needs only the policy and a frozen reference, and it's stable and cheap.",
         "It's offline, so it can't explore beyond the dataset.",
         "The loss can drop while both answers lose probability, and it can favour longer answers.",
         "Online DPO and variants like IPO, KTO, ORPO and SimPO address these."],
        trap_title="\"Lower DPO loss means the chosen answer got more likely\"",
        trap_html="<p>It sounds right, since that's what the pair is asking for. But only the margin is guaranteed to grow. With chosen at −4 and rejected at −10, both are less likely than before, yet the loss falls to 0.437. Real runs show this \"likelihood displacement\": probability can move to responses that appear in neither answer. And DPO does optimise a reward, just an implicit one.</p>"),
    "fundamentals/reasoning-models-grpo": _plan(
        "The assistant must compute refunds: a ₹420 order arrived 40 minutes late, and the policy refunds 10% for delays over 30 minutes. A wrong number costs real money, but the right answer can be checked. Human-written reasoning traces are scarce and expensive. The interviewer asks:",
        "How did DeepSeek-R1 learn to think from right or wrong rewards alone?",
        "Think of a student given only an answer key, with no worked solutions. Try a problem eight times, and reinforce the attempts that got it right compared with the rest. Get it right every time, or never, and you learn nothing from that problem. Over time, the student learns to check their own work.",
        ADVANTAGE_PICTURE, "From the GRPO lab in the Maths tab. Hard problems the model occasionally solves teach the most.",
        ("c4", "<b>Try to break it.</b> This lab is about inference, once the model is trained. At 40% per sample, raise the samples per question. Then drop to 20%, and compare the majority vote with pass@k.", "<b>Now say why:</b> why does voting stop helping at 20%, and why doesn't that stop a verifier?"),
        ["c2"], ["c3", "c5"], [], ["src"],
        ["Reasoning models are trained with RL on verifiable rewards, for maths or code.",
         "Sample several attempts per problem, reward the ones that check out and reinforce them.",
         "GRPO drops PPO's value model and uses the group of samples as a baseline.",
         "The advantage is reward minus the group mean, divided by the group standard deviation.",
         "DeepSeek-R1-Zero went from about 16% to 71% on AIME 2024 from a base model.",
         "Long chains of thought and self-checking emerged on their own.",
         "At inference, more compute can beat a larger model, if the model has a decent chance of being right."],
        edits=[("8 sampled answers to the refund problem above", "8 sampled answers to a refund problem, 10% of a ₹420 order,")],
        trap_title="\"Reasoning models were trained on human chain-of-thought data\"",
        trap_html="<p>It sounds right, since reasoning looks like something you'd have to demonstrate. But R1-Zero learned from outcome rewards alone, and re-checking and backtracking emerged without examples. R1 added only a small cold-start set, because R1-Zero's reasoning was hard to read and mixed languages. DeepSeek also avoided learned reward models here, because large-scale RL tends to hack them.</p>"),
    "fundamentals/distillation": _plan(
        "The post-trained 70B assistant is excellent but too expensive to serve to millions. The team wants a 3B model that behaves almost as well. Trained on the same data and labels, a 3B model ends up much weaker. The interviewer asks:",
        "Why did distilling R1 beat RL on the same 32B model?",
        "Think of the difference between an answer key and a teacher's notes. The key says \"delicious\", full stop. The teacher says delicious is likely, tasty is nearly as good, cold is possible and purple is absurd. Each example teaches the student far more.",
        SOFT_PICTURE, "The next token after \"the biryani was\", from the lab's illustrative teacher at T = 1.",
        ("c3", "<b>Try to break it.</b> Move the temperature from 1 to 4, then to 8. Watch \"tasty\" against \"purple\", and the share on other tokens.", "<b>Now say why:</b> if a higher temperature exposes more, why is T usually kept between 1 and 4?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["Distillation trains a small student to imitate a large teacher.",
         "The student matches the teacher's softened output distribution, using a temperature.",
         "The KL loss is scaled by T², and often mixed with the normal label loss.",
         "For LLMs, you can match next-token logits at every position.",
         "You can also fine-tune on teacher-generated text, as with R1-Distill.",
         "Or do on-policy distillation, where the student samples and the teacher scores each token.",
         "Distilling R1 into a 32B model beat direct RL on it: 72.6% against 47% on AIME."],
        trap_title="\"Distillation just means fine-tuning on teacher outputs\"",
        trap_html="<p>It sounds right, since that's how DeepSeek's R1-Distill models were made. But that's only one form, called sequence-level. Logit distillation matches the teacher's full distribution at every position, and needs the same tokeniser. On-policy distillation has the student generate and the teacher score. A student also rarely exceeds its teacher, and it inherits the teacher's errors.</p>"),
    "fundamentals/lora-and-qlora": _plan(
        "The team has 20,000 good support conversations and wants the 8B assistant to follow the company's tone and format, on a single 24 GB GPU if possible. Full fine-tuning needs about 128 GB. The interviewer asks:",
        "How do you fine-tune an 8B model on one 24 GB GPU?",
        "Think of sticky notes on a printed textbook. You don't reprint the book to change its tone. You freeze it and add a few small notes, which you can peel off or swap for another set. QLoRA also shrinks the book itself, by printing it more compactly.",
        LORA_PICTURE, "From the lab: weights and optimizer, with LoRA at rank 16 on all linear layers. Activations come on top.",
        ("c3", "<b>Try to break it.</b> Switch between full fine-tuning, LoRA and QLoRA. Then raise the rank to 64, and switch between attention only and all linear layers.", "<b>Now say why:</b> why does the rank barely move the memory, and what does?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["LoRA freezes the pretrained weights and learns a low-rank update, B times A, for selected matrices.",
         "It's scaled by α over r, with B initialised to zero.",
         "That's well under 1% of the parameters, so gradients and optimizer state are tiny.",
         "QLoRA stores the frozen base in 4-bit NormalFloat, with double quantization and paged optimizers.",
         "Adapters can be merged for zero overhead, or served many-per-base.",
         "It can learn a bit less than full fine-tuning on hard new skills, but it forgets less.",
         "It's for behaviour and format, not for adding knowledge."],
        trap_title="\"Fine-tune it on our docs so it knows them\"",
        trap_html="<p>It sounds right, since fine-tuning changes the model. But fine-tuning teaches behaviour well and new facts poorly, so use retrieval for knowledge. LoRA isn't always as good as full fine-tuning either: on large-scale code and maths training it underperformed. For format, tone and narrow tasks, it usually matches.</p>"),
    "fundamentals/decoding-and-sampling": _plan(
        "The assistant is writing \"Your biryani will arrive in …\", and the next token should be a number of minutes, not \"purple\". A colleague turns the temperature up to 2 for livelier replies, with top-p at 0.9, and the text derails. The interviewer asks:",
        "Why does top-p fall apart at high temperature, and is min-p really better?",
        "Think of choosing from a huge menu. Temperature is how adventurous you feel. Top-p says to keep the dishes that make up 90% of orders, and if tastes are flat, that's most of the menu. Min-p says to keep dishes at least a tenth as popular as the favourite, so the cut moves with how clear the favourite is.",
        TAIL_PICTURE, "From the lab: nine sensible tokens plus 1,000 junk tokens.",
        ("c3", "<b>Try to break it.</b> Set the temperature to 1, and switch between no truncation, greedy, top-k, top-p and min-p. Then raise it to 2 and repeat.", "<b>Now say why:</b> each junk token is negligible, so how does the tail derail the sentence?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["Decoding turns the next-token distribution into text.",
         "Greedy and beam search give repetitive, bland text for open-ended generation.",
         "Temperature divides the logits, to sharpen or flatten the distribution.",
         "The long tail adds up, so we truncate.",
         "Top-k keeps a fixed number, and top-p keeps the smallest set covering, say, 90%.",
         "Min-p keeps tokens above a fraction of the top token's probability, so junk stays out, though its overall benefit is disputed.",
         "You matched settings to tasks: near zero for extraction, moderate for chat and higher for creative work, tested on your own task."],
        trap_title="\"Top-p always cuts out bad tokens\"",
        trap_html="<p>It sounds right, since cutting the tail is its job. But on a flat distribution the nucleus can be huge. At T = 2 in the lab, top-p needs 887 tokens to reach 90%, and samples junk 79.7% of the time. Higher temperature doesn't make the model smarter or more creative either: it only flattens the distribution.</p>"),
    "fundamentals/in-context-learning-and-cot": _plan(
        "Before investing in fine-tuning, the team tries to get refund calculations right just by prompting. Asked for the answer directly, the assistant gets most of them wrong. A colleague adds examples, and it barely helps. The interviewer asks:",
        "How did \"Let's think step by step\" take maths from 18% to 79%?",
        "Think of doing long multiplication in your head, and then being handed scratch paper. Examples show you what kind of answer is wanted, but you still have to do it all in your head. Chain-of-thought is the scratch paper: each written step is something the next one can use.",
        COT_PICTURE, "From Kojima et al. (2022), with text-davinci-002, as shown in the lab.",
        ("c3", "<b>Try to break it.</b> Go through zero-shot, few-shot, zero-shot CoT and few-shot CoT. Compare MultiArith with GSM8K.", "<b>Now say why:</b> few-shot shows worked formats too, so why does adding the reasoning do so much more?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["In-context learning is doing a task from instructions and examples in the prompt, with no weight updates.",
         "Demonstrations mostly convey the format and label space.",
         "Chain-of-thought writes intermediate reasoning before the answer, which gives extra computation.",
         "\"Let's think step by step\" took MultiArith from about 18% to 79%, and few-shot CoT reached 93%.",
         "Self-consistency samples several chains and votes.",
         "Reasoning models generate this thinking themselves, so you give them goals and constraints."],
        tabs=HOW,
        trap_title="\"The chain of thought explains the model's decision\"",
        trap_html="<p>It sounds right, since you can read the reasoning right there. But it isn't guaranteed to be why the model answered that way. Studies found explanations that omit what actually influenced the answer. Treat CoT as a useful computation aid, not a reliable explanation. Few-shot prompting doesn't fine-tune the model either: its weights don't change.</p>"),
    "fundamentals/hallucination": _plan(
        "A customer asks about a refund for a cancelled festival-day order, and the assistant confidently describes a \"48-hour festival guarantee\" that doesn't exist. In a real case, Moffatt v. Air Canada, a tribunal held an airline responsible for a policy its chatbot invented. The interviewer asks:",
        "Why do models guess confidently, and how do you stop an invented refund policy?",
        "Think of an exam with no negative marking. Guessing every question is the smart move, even when you have no idea. Add negative marking, and the same student starts leaving blanks. Most mainstream benchmarks are the first kind of exam, so guessing pays.",
        MARKING_PICTURE, "The same simulated model under two gradings, from the lab. It answers only when that scores best.",
        ("c3", "<b>Try to break it.</b> Under binary grading, raise the confidence threshold and watch the score. Switch to the penalty, and find the best threshold again.", "<b>Now say why:</b> nothing about the model changed, so why did the errors fall to 2.4%?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["Hallucinations are fluent but unsupported or false outputs.",
         "Next-token training learns plausible patterns, and can't reliably store rarely seen facts.",
         "Fine-tuning can teach confident answers on unknown facts.",
         "Evaluations that give no credit for abstaining make guessing maximise scores.",
         "Ground answers in retrieved sources with citations, and use tools for computable facts.",
         "Train and prompt the model to abstain, and score abstentions above errors.",
         "Add a verification step, and measure hallucination and abstention rates on real labelled questions."],
        tabs=HOW,
        edits=[("the subject of the lab below.", "the subject of the lab in the Intuition tab.")],
        trap_title="\"It's a decoding bug, and a lower temperature will fix it\"",
        trap_html="<p>It sounds right, since the bad text appears during generation. But it comes from training objectives and incentives. Lowering the temperature removes sampling randomness, but if the most likely answer is wrong, greedy decoding states it confidently. Bigger models don't solve it either: they hallucinate less on common facts, but still on rare ones.</p>"),
    "fundamentals/benchmarks-and-contamination": _plan(
        "Two candidate models for the support assistant differ by 3 points on GPQA Diamond and 1 point on MMLU. A colleague wants to pick the one with the higher scores. The interviewer asks:",
        "Is a 3-point GPQA gap real, and did the model see the test?",
        "Think of ranking students by a very short class test. On 30 questions, one lucky guess moves your score by over 3 points, so a small gap means little. And if the paper leaked, the score only tells you who saw it. A good test needs enough questions, correct answers and questions nobody has seen.",
        MARGIN_PICTURE, "95% margin of error in points, at 60% accuracy, from the lab.",
        ("c3", "<b>Try to break it.</b> Switch between MMLU, SWE-bench Verified, GPQA Diamond and AIME 2024. Then move the model accuracy, and watch the gap needed between two models.", "<b>Now say why:</b> GPQA Diamond is a respected test, so why is a 3-point gap on it noise?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["You named benchmarks: MMLU, GPQA Diamond, AIME and SWE-bench Verified.",
         "Small test sets are noisy: GPQA Diamond's 198 questions give about ±7 points at 60%.",
         "Older benchmarks are saturated and contain label errors.",
         "Test data leaks into training, as GSM1k exposed with drops of up to 13 points.",
         "Contamination is detected with n-gram overlap, canary strings and membership-inference tests.",
         "It's avoided with private or rolling benchmarks.",
         "For a product, rely on your own held-out evaluation set."],
        tabs=HOW,
        trap_title="\"High MMLU means it'll work for our users\"",
        trap_html="<p>It sounds right, since it's a broad knowledge test. But MMLU is saturated near 90%, and about 6.5% of its questions have errors. Benchmarks can also be contaminated. And a 1-point gap needs error bars before it means anything. A held-out set of your own real tasks, such as support tickets with correct resolutions, predicts deployment quality far better than a public leaderboard.</p>"),
    "fundamentals/llm-as-a-judge": _plan(
        "The team changes the assistant's prompt, and wants to compare replies across 3,000 real conversations. Human review would take weeks, so they use a GPT judge, and the new prompt wins 62% of pairs. The interviewer asks:",
        "Can you trust a GPT judge's 62% win rate?",
        "Think of a food critic who tends to favour whichever dish arrives first. So you serve each pair twice, swapping the order, and only count the verdict if they pick the same dish both times. You lose some pairs, but the ones you keep are about the food, not the serving order.",
        JUDGE_PICTURE, "From the lab's simulation, with a position bias of 1.0.",
        ("c3", "<b>Try to break it.</b> Set the position bias to 1.0, and compare judging once with judging both orders. Then set the bias to 0.", "<b>Now say why:</b> at zero bias, the judge still agrees with humans only 68.6% of the time. Why isn't that closer to 100%?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["Chatbot Arena collects human pairwise votes and fits Bradley–Terry ratings.",
         "LLM-as-a-judge uses a strong model to compare or grade answers.",
         "Zheng et al. found GPT-4 agreed with experts over 80% of the time, similar to human–human agreement.",
         "Judges have position, verbosity and self-preference biases.",
         "So judge both orders, control for length, use a rubric and use a judge from a different family.",
         "Validate against a few hundred human labels before trusting it.",
         "Report the win rate with a confidence interval."],
        tabs=HOW,
        trap_title="\"GPT-4 as a judge is unbiased\"",
        trap_html="<p>It sounds right, since a model has no opinions of its own. But it has measurable biases. In the lab, 40.3% of verdicts flip when the answers are swapped, and Wang et al. found position sensitivity strong enough to change rankings between models. Arena rank won't settle it either: it reflects the general chat preferences of its voters, not your task.</p>"),
})
# Masked tokens faded to an unreadable contrast, so they use a dashed grey outline instead.
LLM_PLANS["fundamentals/supervised-fine-tuning"]["script_edits"] = [("border:2px solid var(--${c});color:var(--${c});opacity:${on ? 1 : .35}", "border:2px ${on ? 'solid' : 'dashed'} var(--${on ? c : 'line-strong'});color:var(--${on ? c : 'dim'})")]
