# Seven-section plans for Deep Learning lessons. Chapter text comes from the live pages (see ml_import.py).
from maths_plans import _plan

FENCE_PICTURE = """<svg viewBox="0 0 480 160" role="img" aria-label="Left: one straight line can't separate a band of late orders. Right: several lines from hidden units together fence the band off.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="118" y="16">One neuron: one straight fence</text><text x="360" y="16">Hidden units: fences combine</text></g>
  <rect x="20" y="28" width="196" height="120" fill="none" stroke="var(--line-strong)" stroke-width="1.5"/><rect x="262" y="28" width="196" height="120" fill="none" stroke="var(--line-strong)" stroke-width="1.5"/>
  <rect x="21" y="68" width="194" height="40" fill="var(--bad)" fill-opacity=".18"/><rect x="263" y="68" width="194" height="40" fill="var(--bad)" fill-opacity=".18"/>
  <path d="M40 148 196 28" stroke="var(--b)" stroke-width="3"/>
  <path d="M262 68H458M262 108H458" stroke="var(--a)" stroke-width="3"/>
</svg>"""

ACTIVATION_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="Left: a sigmoid curve is flat at both ends, where its slope is almost zero. Right: ReLU is flat below zero and keeps a slope of one above it.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="120" y="16">Sigmoid: flat at both ends</text><text x="360" y="16">ReLU: keeps its slope above 0</text></g>
  <path d="M30 120H210M120 30V136M270 120H450M360 30V136" stroke="var(--line-strong)" stroke-width="1.5"/>
  <path d="M30 118C95 118 125 34 210 32" fill="none" stroke="var(--a)" stroke-width="3"/>
  <path d="M270 120H360L440 36" fill="none" stroke="var(--a)" stroke-width="3"/>
  <g stroke="var(--bad)" stroke-width="5" stroke-linecap="round"><path d="M34 118H66M174 33H206M274 120H354"/></g>
  <text x="120" y="146" font-size="13" fill="var(--bad)" text-anchor="middle" font-weight="600">Red: almost no gradient gets through</text>
</svg>"""

PENALTY_CE_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="Penalty against the predicted probability for an order that was late. Cross-entropy shoots up as the prediction approaches zero. Squared error levels off at one.">
  <path d="M60 14V146H440" fill="none" stroke="var(--dim)" stroke-width="1.5"/>
  <path d="M68 16C74 80 130 118 440 145" fill="none" stroke="var(--bad)" stroke-width="3"/>
  <path d="M60 104C160 112 300 140 440 145" fill="none" stroke="var(--st)" stroke-width="3"/>
  <g font-size="14" font-weight="600"><text x="90" y="40" fill="var(--bad)">Cross-entropy: no limit</text><text x="270" y="96" fill="var(--st)">Squared error: at most 1</text></g>
  <g font-size="13" fill="var(--dim)"><text x="250" y="164" text-anchor="middle">Predicted chance of late, for an order that was late</text><text x="36" y="84" text-anchor="middle" transform="rotate(-90 36 84)">Penalty</text></g>
</svg>"""

BACKPROP_PICTURE = """<svg viewBox="0 0 480 140" role="img" aria-label="Boxes for input, hidden layer, output and loss. A forward arrow along the top stores values. A backward arrow along the bottom reuses them to give every gradient.">
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="2"><rect x="10" y="48" width="86" height="44" rx="8"/><rect x="134" y="48" width="86" height="44" rx="8"/><rect x="258" y="48" width="86" height="44" rx="8"/><rect x="382" y="48" width="86" height="44" rx="8"/></g>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="53" y="75">Input</text><text x="177" y="75">Hidden</text><text x="301" y="75">Output</text><text x="425" y="75">Loss</text></g>
  <defs><marker id="arrowBP" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 10 5 0 10z" fill="context-stroke"/></marker></defs>
  <line x1="30" y1="32" x2="448" y2="32" stroke="var(--a)" stroke-width="3" marker-end="url(#arrowBP)"/><line x1="448" y1="108" x2="30" y2="108" stroke="var(--bad)" stroke-width="3" marker-end="url(#arrowBP)"/>
  <g font-size="14" font-weight="600" text-anchor="middle"><text x="240" y="22" fill="var(--a)">Forward: compute and store values</text><text x="240" y="130" fill="var(--bad)">Backward: reuse them for every gradient</text></g>
</svg>"""

INIT_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="Three signals after 20 layers. A factor of 0.8 per layer shrinks to about 0.01. A factor of 1 stays at 1. A factor of 1.2 grows to about 38.">
  <g font-size="14" font-weight="600"><text x="4" y="32" fill="var(--st)">0.8 per layer</text><text x="4" y="72" fill="var(--ok)">1.0 per layer</text><text x="4" y="112" fill="var(--bad)">1.2 per layer</text></g>
  <rect x="110" y="20" width="4" height="16" fill="var(--st)"/><rect x="110" y="60" width="36" height="16" fill="var(--ok)"/><rect x="110" y="100" width="240" height="16" fill="var(--bad)"/>
  <g font-size="14" fill="var(--ink)"><text x="122" y="33">0.01: the signal has vanished</text><text x="154" y="73">1: it arrives intact</text><text x="358" y="113" font-weight="600">38: exploded</text></g>
</svg>"""

RESIDUAL_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="Six layers in a row, with the gradient shrinking through them. A skip connection arcs over each pair of layers and carries the gradient straight through.">
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="2"><rect x="30" y="70" width="52" height="40" rx="6"/><rect x="104" y="70" width="52" height="40" rx="6"/><rect x="178" y="70" width="52" height="40" rx="6"/><rect x="252" y="70" width="52" height="40" rx="6"/><rect x="326" y="70" width="52" height="40" rx="6"/><rect x="400" y="70" width="52" height="40" rx="6"/></g>
  <path d="M82 90H104M156 90H178M230 90H252M304 90H326M378 90H400" stroke="var(--dim)" stroke-width="2"/>
  <g fill="none" stroke="var(--ok)" stroke-width="2.5"><path d="M56 70C56 30 204 30 204 70"/><path d="M204 70C204 30 352 30 352 70"/></g>
  <text x="204" y="20" font-size="14" font-weight="600" fill="var(--ok)" text-anchor="middle">Skip connections: a highway for the gradient</text>
</svg>"""

NORM_PICTURE = """<svg viewBox="0 0 480 160" role="img" aria-label="Two grids with examples as rows and features as columns. BatchNorm normalises down a column across the batch. LayerNorm normalises along a row within one example.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="120" y="16">BatchNorm: across the batch</text><text x="360" y="16">LayerNorm: within one example</text></g>
  <g fill="none" stroke="var(--line-strong)"><path d="M40 30H200V142H40ZM40 58H200M40 86H200M40 114H200M80 30V142M120 30V142M160 30V142"/><path d="M280 30H440V142H280ZM280 58H440M280 86H440M280 114H440M320 30V142M360 30V142M400 30V142"/></g>
  <rect x="80" y="30" width="40" height="112" fill="var(--a)" fill-opacity=".45" stroke="var(--a)" stroke-width="2"/>
  <rect x="280" y="58" width="160" height="28" fill="var(--b)" fill-opacity=".4" stroke="var(--b)" stroke-width="2"/>
  <g font-size="13" fill="var(--dim)" text-anchor="middle"><text x="120" y="156">Rows are examples, columns are features</text><text x="360" y="156">Same grid, different direction</text></g>
</svg>"""

SCHEDULE_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="The learning rate over training rises quickly during warmup to a peak, then falls smoothly along a cosine towards a low value.">
  <path d="M40 12V124H460" fill="none" stroke="var(--dim)" stroke-width="1.5"/>
  <path d="M40 124 96 26C190 26 300 90 450 112" fill="none" stroke="var(--a)" stroke-width="3"/>
  <path d="M96 26V124" stroke="var(--line-strong)" stroke-dasharray="5 4"/>
  <g font-size="14" font-weight="600"><text x="50" y="142" fill="var(--b)">Warmup</text><text x="240" y="50" fill="var(--a)">Decay: settle into a lower loss</text></g>
  <text x="456" y="142" font-size="13" fill="var(--dim)" text-anchor="end">Training steps</text>
</svg>"""

STEPS_PICTURE = """<svg viewBox="0 0 480 120" role="img" aria-label="With a batch of 32 there are 2,000 steps over two epochs. With a batch of 2,048 there are only 31 steps.">
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="4" y="34">Batch 32</text><text x="4" y="84">Batch 2,048</text></g>
  <rect x="100" y="18" width="290" height="24" fill="var(--a)"/><rect x="100" y="68" width="5" height="24" fill="var(--b)"/>
  <g font-size="14" font-weight="600" fill="var(--ink)"><text x="398" y="35">2,000 steps</text><text x="113" y="85">31 steps, so each must go further</text></g>
</svg>"""

DL_PLANS = {
    "fundamentals/perceptron-to-mlp": _plan(
        "Your delivery model scores orders with one weighted sum, but orders run late in two separate rush-hour bands. No single straight line can capture that. The interviewer asks:",
        "Why can't a single neuron learn XOR, and what does a hidden layer add?",
        "Think of drawing fences on a map. One neuron can only draw one straight fence. Each hidden unit draws its own fence, and the output combines them, so together they can fence off odd shapes.",
        FENCE_PICTURE, "Illustrative, based on the lesson's rush-hour bands.",
        ("c6", "<b>Try to break it.</b> Start with 0 hidden units, then try 2, 4 and 16. Watch the boundary and compare train and test accuracy.", "<b>Now say why:</b> what does each extra hidden unit add, and when does adding more stop helping?"),
        ["c2", "c4", "c5"], ["c7"], ["c3"], ["c8", "src"],
        ["A neuron is a weighted sum plus a bias, passed through a non-linear activation.",
         "One neuron is a linear classifier, so it can't solve XOR-like patterns.",
         "Hidden units each carve the space, and later layers combine them.",
         "The non-linearity is essential, because stacked linear layers collapse into one.",
         "One wide layer can approximate any continuous function.",
         "Deeper networks often need far fewer parameters, but are harder to train."]),
    "fundamentals/activation-functions": _plan(
        "Your deep network uses sigmoid in every layer, and its early layers barely learn. The interviewer asks:",
        "Why did ReLU replace sigmoid, and what do LLMs use now?",
        "Think of a volume knob that stops responding at both ends. Sigmoid behaves like that: push it far either way, and turning it further changes nothing, so no learning signal gets through. ReLU stays responsive across its whole positive side.",
        ACTIVATION_PICTURE, "Illustrative. Backprop multiplies the gradient by this slope at every layer.",
        ("c5", "<b>Try to break it.</b> Choose sigmoid and push the mean of the pre-activations far from zero. Then switch to ReLU and make the mean strongly negative.", "<b>Now say why:</b> how does each activation get stuck, and what does that do to the gradient?"),
        ["c2", "c4", "c6"], ["c7"], ["c3"], ["src"],
        ["Activations add the non-linearity, and their slope scales every gradient flowing back.",
         "Sigmoid and tanh saturate, and sigmoid's slope is at most 0.25, so gradients vanish.",
         "ReLU has slope 1 for positive inputs and is cheap, which made deep nets trainable.",
         "ReLU units can die, and leaky ReLU and GELU keep some gradient there.",
         "CNNs mostly use ReLU, transformers GELU, and modern LLMs gated units like SwiGLU.",
         "Sigmoid and softmax stay at the output, for probabilities."]),
    "fundamentals/loss-functions": _plan(
        "Your model says 2% chance of late for an order that was late, and it barely gets corrected. You're training with squared error on the probability. The interviewer asks:",
        "Why is cross-entropy the classifier loss, not MSE?",
        "Think of two teachers marking a student who was confidently wrong. One takes off a limited number of marks and moves on. The other marks it harder the more confident the student was. Cross-entropy is the second teacher, so the biggest mistakes get the strongest correction.",
        PENALTY_CE_PICTURE, "Illustrative. The two curves show the penalty for a single late order.",
        ("c4", "<b>Try to break it.</b> Drag the predicted chance of late down towards zero, and compare the gradients. Then raise the focal loss γ.", "<b>Now say why:</b> why does the MSE gradient fade just when the model is most wrong?"),
        ["c2", "c5"], ["c6", "c7"], ["c3"], ["src"],
        ["Cross-entropy is the negative log-likelihood, and it heavily penalises confident mistakes.",
         "With sigmoid or softmax, the gradient on the logits is predicted minus true, so it never saturates.",
         "MSE on probabilities has a gradient that vanishes when the model is confidently wrong.",
         "For regression, MSE estimates the mean and MAE the median, and Huber combines them.",
         "For heavy imbalance, you use class weights or focal loss."],
        edits=[("See it in the lab below.", "See it in the Play lab, in the Intuition tab.")]),
    "fundamentals/backpropagation": _plan(
        "Your model has millions of weights. Nudging each one and re-running the network to measure its effect would take one forward pass per weight. The interviewer asks:",
        "How does one backward pass get every gradient, and what does it cost?",
        "Think of a company tracing a loss back through its departments. Going forward, each one keeps notes on what it did. Going backward, each one passes the blame to whoever fed it, using those notes. One pass gives everyone their share, with no need to rerun the company once per person.",
        BACKPROP_PICTURE, "Illustrative. The stored values are why training needs so much more memory than prediction.",
        ("c5", "<b>Try to break it.</b> Move the inputs and flip the label, then compare backprop with finite differences across all 13 weights.", "<b>Now say why:</b> why do the two methods agree, and why would you never train with finite differences?"),
        ["c2", "c4"], ["c6"], ["c3"], ["c7", "src"],
        ["Backprop is reverse-mode autodiff: the chain rule from the loss backwards, reusing results.",
         "The forward pass computes and stores activations.",
         "Each layer gets an error signal, sent back through the transposed weights.",
         "The weight gradient is that signal times the layer's input.",
         "One backward pass costs about twice a forward pass, and gives every gradient.",
         "The cost is memory, which is why big models use activation checkpointing."]),
    "fundamentals/weight-initialisation": _plan(
        "You build a 20-layer network, and before any real training its signal has already died. The interviewer asks:",
        "Why does a deep network fail with the wrong initialisation, and how do Xavier and He fix it?",
        "Think of passing a message down a line of 20 people. If each speaks slightly quieter than the last, it fades to nothing. If each speaks slightly louder, it ends in shouting. Good initialisation sets everyone's volume so the message arrives at the same level.",
        INIT_PICTURE, "From the lesson: 0.8²⁰ ≈ 0.01 and 1.2²⁰ ≈ 38.",
        ("c4", "<b>Try to break it.</b> Try N(0, 0.01²) and N(0, 1) with ReLU, then He. Then switch to tanh and compare Xavier with He.", "<b>Now say why:</b> why does each activation want a different scale for its weights?"),
        ["c2", "c5"], ["c6"], ["c3"], ["src"],
        ["Weights must be random, to break symmetry.",
         "Their scale must keep variance constant across layers, forward and backward.",
         "A layer scales variance by n times the weight variance, so Var(w) should be about 1/n.",
         "Xavier uses 2 ÷ (fan-in + fan-out), which suits tanh.",
         "He uses 2 ÷ fan-in for ReLU, because ReLU zeroes half its inputs.",
         "Normalisation and residuals reduce the sensitivity, but init still matters."]),
    "fundamentals/vanishing-exploding-gradients": _plan(
        "In your 30-layer network, the early layers' weights barely change. Occasionally, on a weird batch, the loss spikes and turns into NaN. The interviewer asks:",
        "Why do early layers stop learning, and how do residual connections fix it?",
        "Think of passing a bucket down a long line, with each person spilling a fifth of it. After 30 people, almost nothing is left. A residual connection is a pipe running alongside the line, so the water can reach the far end directly.",
        RESIDUAL_PICTURE, "Illustrative. The identity path passes the gradient straight through.",
        ("c4", "<b>Try to break it.</b> Set a deep plain network with sigmoid and read the gradient at layer 1. Then switch to residual, and then raise the weight scale.", "<b>Now say why:</b> why does the gradient shrink so fast with depth, and what does the residual path change?"),
        ["c2", "c5", "c6"], ["c7"], ["c3"], ["src"],
        ["Backprop multiplies the gradient by one Jacobian per layer.",
         "Factors below 1 vanish exponentially, and factors above 1 explode.",
         "Saturating activations make vanishing much worse.",
         "Fixes are ReLU-family activations, good init, normalisation and residual connections.",
         "Residual connections pass the gradient straight through, and LSTMs do the same for RNNs.",
         "For exploding gradients, you clip the global norm."]),
    "fundamentals/normalisation-layers": _plan(
        "Your transformer works in training, then a colleague swaps in BatchNorm, and results change with the batch size. The interviewer asks:",
        "Why do transformers use LayerNorm instead of BatchNorm?",
        "Think of grading exam papers on a curve. BatchNorm grades each question against everyone in the room, so your score depends on who else showed up. LayerNorm rescales within your own paper, so the room doesn't matter.",
        NORM_PICTURE, "The same recipe applied along a different axis.",
        ("c4", "<b>Try to break it.</b> On BatchNorm, shrink the batch size and watch the spread across random batches. Then switch to LayerNorm and RMSNorm.", "<b>Now say why:</b> why does one order's output depend on its batch-mates only under BatchNorm?"),
        ["c2", "c5", "c6"], ["c7"], ["c3"], ["src"],
        ["All three standardise activations, then apply a learned scale.",
         "BatchNorm works per feature across the batch, so it depends on the batch.",
         "It needs running statistics at inference and fails with tiny batches.",
         "LayerNorm works across one example's features, so it's batch-independent.",
         "RMSNorm drops the mean, which is cheaper, and modern LLMs use it with pre-norm.",
         "Normalisation mainly helps by smoothing the loss landscape."]),
    "fundamentals/learning-rate-schedules": _plan(
        "With one constant learning rate, your training stops improving and bounces around the minimum, and a higher rate blows up at the start. The interviewer asks:",
        "Why do LLMs warm up and then decay the learning rate?",
        "Think of driving into a parking spot from a long way off. You start gently while you feel out the car, go at full speed on the open road, and slow right down as you reach the spot. Warmup and decay do the same for training.",
        SCHEDULE_PICTURE, "Illustrative. A common recipe is linear warmup, then cosine decay.",
        ("c4", "<b>Try to break it.</b> Choose the sharp start and a high peak learning rate. Compare constant with warmup + cosine, then try the others.", "<b>Now say why:</b> why does the same peak rate survive with warmup but not without it?"),
        ["c2", "c5"], ["c6"], ["c3"], ["src"],
        ["With noisy gradients, a constant rate leaves SGD bouncing around the minimum.",
         "So you decay it, with step decay or a smooth cosine, to settle lower.",
         "The loss surface is usually sharpest at the start, so a full-size step can diverge.",
         "A linear warmup reaches flatter regions before using the peak rate.",
         "LLMs typically use AdamW, linear warmup, cosine decay and gradient clipping."]),
    "fundamentals/batch-size-and-learning-rate": _plan(
        "You have more GPUs, so you make your batches 8× bigger and keep everything else the same. Your training gets worse. The interviewer asks:",
        "You make the batch 8× bigger. What should happen to the learning rate?",
        "Think of walking somewhere using directions from a poll. A bigger poll gives better directions, but you stop to ask far less often. If each stretch stays the same length, you won't get there. So you take longer strides, up to the point where they stop being safe.",
        STEPS_PICTURE, "From the lesson: 64,000 order-visits over two epochs.",
        ("c4", "<b>Try to break it.</b> Set a batch of 2,048 with fixed η, and read the final loss. Then try linear and square-root scaling.", "<b>Now say why:</b> why does a more accurate gradient give a worse result unless you change the learning rate?"),
        ["c2", "c5"], ["c7"], ["c3", "c6"], ["src"],
        ["Batch gradients average B examples, so noise falls like 1 over root B.",
         "For fixed epochs, you get B times fewer steps.",
         "For SGD, the linear scaling rule multiplies η by the same factor, with a warmup.",
         "This works up to a critical batch size, and then extra batch wastes compute.",
         "For Adam, scaling is roughly square-root.",
         "The claimed large-batch generalisation gap mostly disappears with proper tuning."]),
}

DROPOUT_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="A small network where some hidden units are switched off with a cross. A different set would be off at the next step.">
  <g stroke="var(--line-strong)" stroke-width="1.5"><path d="M60 45 200 25M60 45 200 75M60 45 200 125M60 105 200 25M60 105 200 75M60 105 200 125M200 25 340 75M200 125 340 75"/></g>
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="2"><circle cx="60" cy="45" r="15"/><circle cx="60" cy="105" r="15"/><circle cx="200" cy="25" r="15"/><circle cx="200" cy="125" r="15"/><circle cx="340" cy="75" r="15"/></g>
  <circle cx="200" cy="75" r="15" fill="var(--line-soft)" stroke="var(--line-strong)" stroke-width="2"/>
  <path d="M191 66 209 84M209 66 191 84" stroke="var(--bad)" stroke-width="3.5"/>
  <text x="372" y="70" font-size="14" font-weight="600" fill="var(--ink)">A new random</text><text x="372" y="90" font-size="14" font-weight="600" fill="var(--ink)">mask every step</text>
</svg>"""

DECAY_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="With Adam plus L2, a weight with noisy gradients barely shrinks while a quiet weight shrinks a lot. With AdamW, both shrink by the same amount.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="120" y="16">Adam + L2: uneven</text><text x="360" y="16">AdamW: the same for both</text></g>
  <g fill="var(--line-strong)"><rect x="40" y="30" width="44" height="72"/><rect x="150" y="30" width="44" height="72"/><rect x="290" y="30" width="44" height="72"/><rect x="400" y="30" width="44" height="72"/></g>
  <g fill="var(--a)"><rect x="40" y="36" width="44" height="66"/><rect x="150" y="84" width="44" height="18"/><rect x="290" y="60" width="44" height="42"/><rect x="400" y="60" width="44" height="42"/></g>
  <g font-size="13" fill="var(--dim)" text-anchor="middle"><text x="62" y="120">Noisy weight</text><text x="172" y="120">Quiet weight</text><text x="312" y="120">Noisy weight</text><text x="422" y="120">Quiet weight</text></g>
</svg>"""

MIXUP_PICTURE = """<svg viewBox="0 0 480 110" role="img" aria-label="An order labelled late blended with an order labelled on time gives a new mixed order labelled 70 percent late.">
  <g stroke-width="2"><rect x="10" y="26" width="120" height="50" rx="8" fill="var(--bad)" fill-opacity=".16" stroke="var(--bad)"/><rect x="180" y="26" width="120" height="50" rx="8" fill="var(--ok)" fill-opacity=".16" stroke="var(--ok)"/><rect x="350" y="26" width="120" height="50" rx="8" fill="var(--b)" fill-opacity=".18" stroke="var(--b)"/></g>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="70" y="56">Order A: late</text><text x="240" y="56">Order B: on time</text><text x="410" y="48">Mixed order</text><text x="410" y="66">70% late</text></g>
  <g font-size="22" font-weight="600" fill="var(--dim)" text-anchor="middle"><text x="155" y="58">+</text><text x="325" y="58">=</text></g>
  <text x="240" y="102" font-size="13" fill="var(--dim)" text-anchor="middle">Blend the inputs, and blend the labels by the same amount</text>
</svg>"""

STOP_PICTURE = """<svg viewBox="0 0 480 160" role="img" aria-label="Training loss keeps falling. Validation loss falls, reaches a low point and rises. A marker at the low point shows the checkpoint to keep.">
  <path d="M40 14V130H460" fill="none" stroke="var(--dim)" stroke-width="1.5"/>
  <path d="M42 44C120 98 260 116 450 124" fill="none" stroke="var(--a)" stroke-width="3"/>
  <path d="M42 30C100 82 140 82 185 78S340 56 450 26" fill="none" stroke="var(--bad)" stroke-width="3"/>
  <circle cx="150" cy="77" r="7" fill="var(--ok)"/><path d="M150 84V130" stroke="var(--ok)" stroke-width="2" stroke-dasharray="4 3"/>
  <g font-size="14" font-weight="600"><text x="150" y="150" fill="var(--ok)" text-anchor="middle">Keep this checkpoint</text><text x="410" y="26" fill="var(--bad)" text-anchor="end">Validation loss</text><text x="456" y="112" fill="var(--a)" text-anchor="end">Training loss</text></g>
</svg>"""

CONV_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="A small 3 by 3 filter slides over an image grid, and each position gives one value in the output map.">
  <g fill="none" stroke="var(--line-strong)"><path d="M40 20H180V140H40ZM40 40H180M40 60H180M40 80H180M40 100H180M40 120H180M60 20V140M80 20V140M100 20V140M120 20V140M140 20V140M160 20V140"/><path d="M300 40H420V120H300ZM300 60H420M300 80H420M300 100H420M320 40V120M340 40V120M360 40V120M380 40V120M400 40V120"/></g>
  <rect x="80" y="40" width="60" height="60" fill="var(--a)" fill-opacity=".3" stroke="var(--a)" stroke-width="3"/>
  <rect x="340" y="60" width="20" height="20" fill="var(--b)"/>
  <path d="M142 70 C200 50 280 50 338 68" fill="none" stroke="var(--dim)" stroke-width="2"/>
  <text x="240" y="20" font-size="13" font-weight="600" fill="var(--ink)" text-anchor="middle">One filter position</text><text x="240" y="38" font-size="13" fill="var(--dim)" text-anchor="middle">gives one output value</text>
</svg>"""

SHAPE_PICTURE = """<svg viewBox="0 0 480 120" role="img" aria-label="The output-size formula: width plus twice the padding minus the kernel, divided by the stride, plus one. For AlexNet's first layer that gives 55.">
  <text x="240" y="36" font-size="22" font-weight="700" fill="var(--ink)" text-anchor="middle">⌊(W + 2P − K) ÷ S⌋ + 1</text>
  <text x="240" y="74" font-size="15" fill="var(--ink)" text-anchor="middle">AlexNet's first layer: (227 + 0 − 11) ÷ 4 + 1 = 55</text>
  <text x="240" y="104" font-size="13" fill="var(--dim)" text-anchor="middle">W width · P padding · K kernel size · S stride</text>
</svg>"""

BLOCK_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="A residual block: the input x goes through layers to give F of x, and a shortcut carries x around them. The two are added.">
  <path d="M34 80H110M210 80H300M340 80H420" stroke="var(--dim)" stroke-width="2.5"/>
  <rect x="110" y="56" width="100" height="48" rx="8" fill="var(--tint)" stroke="var(--c)" stroke-width="2"/>
  <circle cx="320" cy="80" r="20" fill="none" stroke="var(--ink)" stroke-width="2.5"/><path d="M310 80H330M320 70V90" stroke="var(--ink)" stroke-width="2.5"/>
  <path d="M70 80C70 16 320 16 320 60" fill="none" stroke="var(--ok)" stroke-width="3"/>
  <g font-size="15" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="20" y="85">x</text><text x="160" y="85">F(x)</text><text x="452" y="85">x + F(x)</text></g>
  <text x="195" y="20" font-size="13" font-weight="600" fill="var(--ok)" text-anchor="middle">The shortcut carries x straight through</text>
</svg>"""

TRANSFER_PICTURE = """<svg viewBox="0 0 480 120" role="img" aria-label="A row of pre-trained layers shown as frozen, followed by one new head that gets trained.">
  <g fill="var(--line-soft)" stroke="var(--line-strong)" stroke-width="2"><rect x="10" y="30" width="80" height="50" rx="8"/><rect x="104" y="30" width="80" height="50" rx="8"/><rect x="198" y="30" width="80" height="50" rx="8"/></g>
  <rect x="330" y="30" width="110" height="50" rx="8" fill="var(--c)"/>
  <path d="M90 55h14M184 55h14M278 55h52" stroke="var(--dim)" stroke-width="2"/>
  <g font-size="14" font-weight="600" text-anchor="middle"><text x="144" y="20" fill="var(--dim)">Pre-trained layers: frozen first</text><text x="385" y="60" fill="#fff">New head</text></g>
  <text x="240" y="108" font-size="13" fill="var(--dim)" text-anchor="middle">With more data, unfreeze from the top with a much smaller learning rate</text>
</svg>"""

DL_PLANS.update({
    "fundamentals/dropout": _plan(
        "Your 257-parameter network, trained on just 60 orders, hits 100% training accuracy and is wildly overconfident on new ones. The interviewer asks:",
        "Why does randomly switching off neurons make a network generalise?",
        "Think of a team where anyone might call in sick on any day. Nobody can rely on one colleague to cover their mistakes, so everyone has to be useful on their own. Dropout trains a network the same way.",
        DROPOUT_PICTURE, "Illustrative. At test time, dropout is switched off and every unit is used.",
        ("c4", "<b>Try to break it.</b> Compare no dropout, 0.2 and 0.5, then try 0.8. Watch train accuracy, test accuracy and test log loss.", "<b>Now say why:</b> why does test performance improve while training accuracy falls, and why does 0.8 go too far?"),
        ["c2", "c5"], ["c6"], ["c3"], ["src"],
        ["Dropout zeros each unit with probability p during training, with a fresh mask each step.",
         "Survivors are scaled by 1 ÷ (1 − p), so the expected activation is unchanged.",
         "Units can't co-adapt, because no unit can rely on another being present.",
         "It trains many weight-sharing sub-networks, and the full network approximates their average.",
         "You switch it off at inference, with eval mode.",
         "Typical rates are 0.1 to 0.5, and too high underfits."]),
    "fundamentals/weight-decay-and-adamw": _plan(
        "You train with Adam and set a weight_decay value. The weights with noisy gradients barely shrink, while quiet ones shrink a lot. The interviewer asks:",
        "Why is Adam with L2 not the same as AdamW?",
        "Think of a tax. AdamW charges every weight the same rate. Adam with L2 puts the tax through Adam's own scaling first, so weights with big gradients get a discount, and quiet ones get overcharged.",
        DECAY_PICTURE, "Illustrative. The grey shows each weight's starting size.",
        ("c4", "<b>Try to break it.</b> Set the gradient noise to tiny, then to large, and compare the final weight under Adam + L2 and AdamW.", "<b>Now say why:</b> why does one method's shrinkage depend on the gradients, while the other's doesn't?"),
        ["c2"], ["c5"], ["c3"], ["src"],
        ["Weight decay shrinks every weight by a small factor each step.",
         "For plain SGD, that's the same as an L2 penalty.",
         "With Adam, the L2 gradient gets divided by the per-parameter RMS.",
         "So weights with large gradients are barely regularised, and small ones over-regularised.",
         "AdamW decouples the decay from the adaptive update.",
         "It's the transformer default, and isn't applied to biases and norm parameters."]),
    "fundamentals/data-augmentation-and-mixup": _plan(
        "You have only 60 labelled orders, and more labels are expensive. The interviewer asks:",
        "How do you get more training data without collecting any?",
        "Think of showing a child the same dish from different angles: it's still biryani, so they learn what really matters. Augmentation makes those new views for free. Mixup goes further, blending two examples and blending their labels too.",
        MIXUP_PICTURE, "Illustrative, with λ = 0.7. In practice, λ is drawn from a Beta distribution.",
        ("c5", "<b>Try to break it.</b> Compare no mixup with α = 0.2, 0.4 and 1. Watch train accuracy against test log loss.", "<b>Now say why:</b> why can mixed orders that never really existed make the model better on real ones?"),
        ["c2", "c4"], ["c6"], ["c3"], ["src"],
        ["Augmentation creates new examples with transformations that don't change the label.",
         "The model learns invariances, and can't memorise the exact training set.",
         "It's applied only to training data.",
         "Mixup trains on blends of pairs of examples and their labels.",
         "Small α works best, and it smooths boundaries and improves calibration.",
         "CutMix pastes patches instead of blending pixels."]),
    "fundamentals/early-stopping-and-label-smoothing": _plan(
        "Your training loss keeps falling, but somewhere along the way the model started memorising noise and getting overconfident. The interviewer asks:",
        "When should training stop, and why soften the labels?",
        "Think of revising for an exam from a practice paper with a few typos. Past a point, you're memorising the typos, so you stop and go back to your best day. And a teacher who never claims 100% certainty keeps you from being overconfident, which is what label smoothing does.",
        STOP_PICTURE, "Illustrative. Patience sets how long you wait before stopping.",
        ("c3", "<b>Try to break it.</b> Compare no early stopping with a patience of 4 and of 20. Read where the best checkpoint is, and where training stopped.", "<b>Now say why:</b> why do you restore the best checkpoint instead of keeping the last one?"),
        ["c4"], ["c2"], ["c5"], ["src"],
        ["Early stopping monitors validation loss and saves the best checkpoint.",
         "It stops after a patience number of checks without improvement, and restores the best weights.",
         "It's a free regulariser that roughly acts like L2.",
         "Label smoothing gives the true class 1 − ε and shares ε across all classes.",
         "So the best logits are finite, and the model can't become 100% confident.",
         "It helps calibration, but teachers trained with it distil worse."]),
    "fundamentals/convolution-and-receptive-field": _plan(
        "You need to tag dish photos. A dense layer of 1,000 units on one 224×224 colour photo would need 150 million weights. The interviewer asks:",
        "Why does a 3×3 filter beat a dense layer on images?",
        "Think of scanning a photo with a small stencil. You use the same stencil everywhere, so it finds an edge wherever that edge happens to be. A dense layer would have to learn a separate detector for every spot.",
        CONV_PICTURE, "Illustrative. Each filter produces one full output map.",
        ("c3", "<b>Try to break it.</b> Pick the vertical edges filter and slide it across the crop. Then switch to horizontal edges and compare the output, and the parameter count against a dense layer.", "<b>Now say why:</b> how does one small filter do a job that would take a dense layer so many weights?"),
        ["c2", "c5"], ["c4"], [], ["src"],
        ["A conv layer slides small learned filters and takes a dot product with each local patch.",
         "Each filter produces one feature map.",
         "Weights are shared across positions, and connections are local, so there are far fewer parameters.",
         "It detects a pattern wherever it appears.",
         "Early layers learn edges and colours, and deeper layers textures and parts.",
         "Stacking grows the receptive field, and downsampling grows it much faster."],
        trap_title="\"Just flatten the image and use a dense layer\"",
        trap_html="<p>It sounds simple, and a dense layer can in principle learn anything. But on a 224×224 colour photo, 1,000 units already need 150 million weights. It also has to learn \"edge at the top-left\" and \"edge at the bottom-right\" as two unrelated things, because it ignores the fact that nearby pixels belong together.</p>"),
    "fundamentals/pooling-stride-padding": _plan(
        "An interviewer gives you a conv layer's input size, kernel, stride and padding, and wants the output shape on the spot. The interviewer asks:",
        "How do you work out the output shape of a conv layer?",
        "Think of a window sliding along a strip of paper. The window's size is how much it covers, the stride is how far it jumps, and padding adds a margin so the edges count. The output width is simply how many positions fit.",
        SHAPE_PICTURE, "The worked example comes from the lesson. Output width is the number of positions that fit.",
        ("c3", "<b>Try to break it.</b> Set a stride of 2 and a width that doesn't divide evenly, and look at the pixels never covered. Then raise the padding.", "<b>Now say why:</b> why does an uneven fit drop pixels, and how does padding change that?"),
        ["c2", "c5"], ["c4"], [], ["src"],
        ["Output width is ⌊(W + 2P − K) ÷ S⌋ + 1.",
         "Same padding with stride 1 keeps the size, and valid padding shrinks it by K − 1.",
         "Stride S divides the size by roughly S, and an uneven fit drops edge pixels.",
         "Pooling downsamples with a fixed max or average, and has no parameters.",
         "A conv layer has K² × C_in × C_out + C_out parameters.",
         "Its compute scales with the output area."],
        trap_title="\"Stride 2 just halves the width\"",
        trap_html="<p>It sounds right, and it's close. But the formula rounds down: when (W + 2P − K) doesn't divide evenly by the stride, the edge pixels are simply dropped. An interviewer asking for the exact shape wants the formula, not the rule of thumb.</p>"),
    "fundamentals/resnets-and-skip-connections": _plan(
        "A deeper network can always copy a shallower one, so it should never do worse. Yet a 34-layer plain CNN had higher training error than an 18-layer one on ImageNet. The interviewer asks:",
        "Why did deeper networks train worse, and how did ResNet fix it?",
        "Think of editing a draft instead of rewriting it from memory. Each block starts from the existing text and only adds corrections. If there's nothing to change, it leaves the text alone, while a plain layer would have to retype the whole thing perfectly.",
        BLOCK_PICTURE, "The residual block. Learning F(x) = 0 is easy, so doing nothing is easy.",
        ("c3", "<b>Try to break it.</b> Compare plain and residual at 5 layers, then at 20 and 30.", "<b>Now say why:</b> why does the plain network stop training as it gets deeper, when in principle it could learn at least as well?"),
        ["c2", "c4"], ["c5"], [], ["src"],
        ["Deeper plain networks had higher training error: the degradation problem.",
         "That's an optimisation failure, not overfitting.",
         "ResNet adds an identity shortcut, so each block computes x + F(x).",
         "Doing nothing becomes easy, and the block only learns a correction.",
         "The identity gives the gradient a direct path, since the Jacobian is I + dF/dx.",
         "The same residual pattern is the backbone of transformers."],
        trap_title="\"Deeper networks do worse because they overfit\"",
        trap_html="<p>It sounds right, because overfitting is the usual reason a bigger model disappoints. But the deeper plain network had higher <b>training</b> error, not just higher test error. That makes it an optimisation problem, and regularisation wouldn't have fixed it.</p>"),
    "fundamentals/transfer-learning": _plan(
        "Your delivery app launches in a new city with only 15 labelled orders, and you already have a model trained on 1,000 orders from another city. The interviewer asks:",
        "With only 15 labelled examples, how would you reuse a pre-trained model?",
        "Think of hiring someone who already knows the food business and teaching them your city, instead of training a complete beginner. You keep what they know, and you adjust gently, so you don't wipe out what made them valuable.",
        TRANSFER_PICTURE, "Illustrative. Early layers tend to be general, and later ones specific to the task.",
        ("c3", "<b>Try to break it.</b> Start at 15 orders and compare from scratch, frozen features and fine-tuning. Then move up to 200.", "<b>Now say why:</b> why does the best choice change as you get more data?"),
        ["c2", "c4"], ["c5"], [], ["src"],
        ["Transfer learning reuses a model pre-trained on a large dataset.",
         "Early layers learn general features, and later ones more specific ones.",
         "With little data and a similar domain, you freeze the backbone and train a new head.",
         "With more data, you fine-tune from the top with a much smaller learning rate.",
         "You keep the original preprocessing.",
         "It massively reduces the data and compute you need."],
        tabs=["Intuition", "How it works", "In practice"],
        trap_title="\"Just fine-tune the whole model at your normal learning rate\"",
        trap_html="<p>It sounds right, since more training usually helps. But pre-trained weights are already near a good solution, and large steps destroy useful features. With very little data, fine-tuning everything can also overfit, so you start with the head, then unfreeze from the top with a learning rate 10 to 100 times smaller.</p>"),
})

RNN_PICTURE = """<svg viewBox="0 0 480 120" role="img" aria-label="Words pass through a chain of hidden states. The memory of the first word fades at each step.">
  <g font-size="14" fill="var(--ink)" text-anchor="middle"><text x="50" y="108">biryani</text><text x="145" y="108">was</text><text x="240" y="108">cold</text><text x="335" y="108">but</text><text x="430" y="108">naan</text></g>
  <g fill="var(--a)"><circle cx="50" cy="48" r="24" fill-opacity="1"/><circle cx="145" cy="48" r="24" fill-opacity=".6"/><circle cx="240" cy="48" r="24" fill-opacity=".36"/><circle cx="335" cy="48" r="24" fill-opacity=".2"/><circle cx="430" cy="48" r="24" fill-opacity=".1"/></g>
  <g fill="none" stroke="var(--a)" stroke-width="1.5"><circle cx="145" cy="48" r="24"/><circle cx="240" cy="48" r="24"/><circle cx="335" cy="48" r="24"/><circle cx="430" cy="48" r="24"/></g>
  <path d="M76 48h42M171 48h42M266 48h42M361 48h42" stroke="var(--dim)" stroke-width="2"/>
  <text x="240" y="16" font-size="13" font-weight="600" fill="var(--dim)" text-anchor="middle">How much of "biryani" is left in the memory</text>
</svg>"""

LSTM_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="A straight memory line runs across the top. Gates along it decide what to forget and what to add, so memory is kept by default.">
  <path d="M20 44H460" stroke="var(--a)" stroke-width="5"/>
  <g fill="var(--surface, #fff)" stroke-width="2.5"><circle cx="150" cy="44" r="16" stroke="var(--bad)"/><circle cx="320" cy="44" r="16" stroke="var(--ok)"/></g>
  <g font-size="17" font-weight="700" text-anchor="middle"><text x="150" y="50" fill="var(--bad)">×</text><text x="320" y="50" fill="var(--ok)">+</text></g>
  <path d="M150 104V62M320 104V62" stroke="var(--dim)" stroke-width="2"/>
  <g font-size="14" font-weight="600" text-anchor="middle"><text x="150" y="122" fill="var(--bad)">Forget gate: what to erase</text><text x="340" y="122" fill="var(--ok)">Input gate: what to write</text><text x="240" y="24" fill="var(--a)">Memory carries on by default</text></g>
</svg>"""

ALIGN_PICTURE = """<svg viewBox="0 0 480 140" role="img" aria-label="An English sentence on top and French underneath, with lines linking each French word to the English word it looks at. The lines for cold and biryani cross, because French puts the adjective after the noun.">
  <g font-size="15" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="60" y="24">the</text><text x="150" y="24">cold</text><text x="250" y="24">biryani</text><text x="350" y="24">arrived</text><text x="430" y="24">late</text>
    <text x="50" y="128">le</text><text x="130" y="128">biryani</text><text x="220" y="128">froid</text><text x="290" y="128">est</text><text x="365" y="128">arrivé</text><text x="440" y="128">en retard</text></g>
  <g stroke="var(--line-strong)" stroke-width="2"><path d="M60 32 50 110M350 32 290 110M350 32 365 110M430 32 440 110"/></g>
  <g stroke="var(--b)" stroke-width="3.5"><path d="M250 32 130 110M150 32 220 110"/></g>
</svg>"""

QKV_PICTURE = """<svg viewBox="0 0 480 140" role="img" aria-label="The word cold sends out a question. Biryani's key matches best, so biryani's value gets the largest share. Naan and was get smaller shares.">
  <rect x="10" y="50" width="90" height="40" rx="8" fill="var(--c)"/><text x="55" y="75" font-size="15" font-weight="600" fill="#fff" text-anchor="middle">cold</text>
  <text x="55" y="38" font-size="13" fill="var(--dim)" text-anchor="middle">Query</text>
  <g font-size="15" fill="var(--ink)"><text x="170" y="42">biryani</text><text x="170" y="80">was</text><text x="170" y="118">naan</text></g>
  <path d="M100 66 164 38M100 70H164M100 74 164 112" stroke="var(--dim)" stroke-width="2"/>
  <g fill="var(--a)"><rect x="240" y="26" width="190" height="20"/><rect x="240" y="64" width="50" height="20"/><rect x="240" y="102" width="30" height="20"/></g>
  <text x="240" y="16" font-size="13" fill="var(--dim)">Share of each value it takes</text>
</svg>"""

HEADS_PICTURE = """<svg viewBox="0 0 480 120" role="img" aria-label="The same sentence twice. One head highlights biryani for the word cold, and another highlights was, the word just before it.">
  <g font-size="15" fill="var(--ink)"><text x="100" y="42">the</text><text x="140" y="42" font-weight="700">biryani</text><text x="212" y="42">was</text><text x="256" y="42">cold</text><text x="100" y="96">the</text><text x="140" y="96">biryani</text><text x="212" y="96" font-weight="700">was</text><text x="256" y="96">cold</text></g>
  <rect x="136" y="24" width="66" height="26" rx="5" fill="var(--a)" fill-opacity=".3"/><rect x="208" y="78" width="38" height="26" rx="5" fill="var(--b)" fill-opacity=".35"/>
  <g font-size="14" font-weight="600"><text x="4" y="42" fill="var(--a)">Head 1</text><text x="4" y="96" fill="var(--b)">Head 2</text><text x="310" y="42" fill="var(--a)">Which food?</text><text x="310" y="96" fill="var(--b)">Previous word</text></g>
</svg>"""

ROPE_PICTURE = """<svg viewBox="0 0 480 140" role="img" aria-label="Two clock faces. On each, two hands sit the same angle apart, even though their absolute positions differ, because the gap between the words is the same.">
  <g fill="none" stroke="var(--line-strong)" stroke-width="2"><circle cx="120" cy="66" r="50"/><circle cx="360" cy="66" r="50"/></g>
  <g stroke-width="3.5" stroke-linecap="round"><path d="M120 66 163.3 58.4" stroke="var(--a)"/><path d="M120 66 158.1 88" stroke="var(--b)"/><path d="M360 66 316.7 58.4" stroke="var(--a)"/><path d="M360 66 331.7 32.3" stroke="var(--b)"/></g>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="120" y="134">Words 2 and 3</text><text x="360" y="134">Words 7 and 8</text></g>
</svg>"""

STACK_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="A vertical residual stream on the left. Attention and feed-forward sub-layers each add to it, and the block repeats.">
  <path d="M90 142V14" stroke="var(--a)" stroke-width="6"/>
  <rect x="140" y="88" width="240" height="40" rx="8" fill="var(--tint)" stroke="var(--c)" stroke-width="2"/><rect x="140" y="26" width="240" height="40" rx="8" fill="var(--tint)" stroke="var(--c)" stroke-width="2"/>
  <path d="M90 124H140M140 96H90M90 62H140M140 34H90" stroke="var(--dim)" stroke-width="2"/>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="260" y="113">Attention: tokens share</text><text x="260" y="51">Feed-forward: each thinks alone</text></g>
  <text x="40" y="80" font-size="13" font-weight="600" fill="var(--a)" text-anchor="middle">Stream</text>
  <text x="456" y="80" font-size="13" fill="var(--dim)" text-anchor="end">Repeat N</text>
</svg>"""

MASKS_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="Three grids showing which tokens can see which. The encoder sees everything, the decoder only earlier tokens in a triangle, and cross-attention sees all of the source.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="80" y="16">Encoder</text><text x="240" y="16">Decoder</text><text x="400" y="16">Cross-attention</text></g>
  <rect x="30" y="28" width="100" height="100" fill="var(--a)" fill-opacity=".4" stroke="var(--a)" stroke-width="2"/>
  <rect x="190" y="28" width="100" height="100" fill="none" stroke="var(--line-strong)" stroke-width="2"/><path d="M190 28 290 128H190Z" fill="var(--b)" fill-opacity=".45"/>
  <rect x="350" y="28" width="100" height="100" fill="var(--st)" fill-opacity=".35" stroke="var(--st)" stroke-width="2"/>
  <g font-size="13" fill="var(--dim)" text-anchor="middle"><text x="80" y="146">Sees every token</text><text x="240" y="146">Only earlier tokens</text><text x="400" y="146">Output reads input</text></g>
</svg>"""

PIPELINE_PICTURE = """<svg viewBox="0 0 480 130" role="img" aria-label="A pipeline: text becomes n ids, then an n by 768 matrix, passes through 12 blocks and a norm keeping that shape, then a linear layer gives n by 50,257 logits.">
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="2"><rect x="4" y="36" width="82" height="50" rx="8"/><rect x="104" y="36" width="82" height="50" rx="8"/><rect x="204" y="36" width="82" height="50" rx="8"/><rect x="304" y="36" width="82" height="50" rx="8"/></g><rect x="404" y="36" width="72" height="50" rx="8" fill="var(--c)"/>
  <path d="M86 61h18M186 61h18M286 61h18M386 61h18" stroke="var(--dim)" stroke-width="2"/>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="45" y="66">Tokens</text><text x="145" y="66">Embed</text><text x="245" y="66">12 blocks</text><text x="345" y="66">Norm</text><text x="440" y="66" fill="#fff">Linear</text></g>
  <g font-size="13" fill="var(--dim)" text-anchor="middle"><text x="45" y="106">n</text><text x="145" y="106">n × 768</text><text x="245" y="106">n × 768</text><text x="345" y="106">n × 768</text><text x="440" y="106">n × 50,257</text></g>
</svg>"""

DL_PLANS.update({
    "fundamentals/rnns-and-backprop-through-time": _plan(
        "Your model reads reviews one word at a time. By the end of a long review, it has lost track of what \"cold\" referred to. The interviewer asks:",
        "Why can't a plain RNN remember a word from 50 steps ago?",
        "Think of reading a review with a single sticky note. After each word, you rewrite the note from what's on it and the new word. Early details get fainter with every rewrite, until they're gone.",
        RNN_PICTURE, "Illustrative. The same weights are reused at every step.",
        ("c4", "<b>Try to break it.</b> Move the recurrent weight scale below 1 and read the gradient at 10 and 50 steps back. Then push it above 1, and try the linear RNN.", "<b>Now say why:</b> why does a small change in the scale make the gradient vanish or explode?"),
        ["c2", "c3"], ["c5"], [], ["src"],
        ["An RNN reads one step at a time, updating a hidden state with the same weights.",
         "Training unrolls it into a deep network and backpropagates through every step.",
         "The gradient to an early step is a product of many Jacobians.",
         "So it vanishes or explodes exponentially, and plain RNNs remember only tens of steps.",
         "You use truncated BPTT, clipping and gated cells.",
         "Transformers largely replaced RNNs, by attending directly to distant tokens."],
        trap_title="\"The hidden state carries everything forward, so an RNN can remember any length\"",
        trap_html="<p>It sounds right, since the hidden state does flow through every step. But each step multiplies it by the same weights and squashes it, so the gradient linking a late loss to an early word shrinks or explodes exponentially. In practice, a plain RNN remembers only tens of steps.</p>"),
    "fundamentals/lstm-and-gru": _plan(
        "Your review says \"the biryani was cold\", then 40 words about delivery, then \"overall I'd order again\". A plain RNN has forgotten \"cold\" by the end. The interviewer asks:",
        "How do gates let a network remember for hundreds of steps?",
        "Think of swapping the sticky note for a notebook. Nothing gets rewritten unless you choose to. One gate decides what to erase, and another decides what to add, so old notes survive by default.",
        LSTM_PICTURE, "Illustrative. The output gate, not shown, decides what to expose at each step.",
        ("c4", "<b>Try to break it.</b> Move the forget-gate bias up and down, and compare what the LSTM keeps after 50 and 200 steps with the plain RNN.", "<b>Now say why:</b> why does the LSTM keep so much more, and what happens when its forget gate is low?"),
        ["c2", "c3"], ["c5"], [], ["src"],
        ["An LSTM adds a cell state that's updated additively.",
         "Sigmoid gates decide what to forget, what to write and what to expose.",
         "The derivative along the cell is just the forget gate.",
         "So learning f near 1 keeps information and gradients for hundreds of steps.",
         "It works much like a residual connection through time.",
         "A GRU merges this into fewer gates, usually with similar accuracy."],
        trap_title="\"An LSTM remembers because it has more memory\"",
        trap_html="<p>It sounds right, since an LSTM does have more parameters. But the fix is the shape of the path, not its size. Along the cell state, the derivative is just the forget gate, with no weight matrix or tanh slope in the way. When the network learns a forget gate near 1, information and gradients pass through almost untouched.</p>"),
    "fundamentals/seq2seq-and-attention": _plan(
        "You're translating restaurant notes into French, and your encoder–decoder works on short sentences but falls apart on long ones. The interviewer asks:",
        "How did attention fix translation of long sentences?",
        "Think of a translator. The old way is to read the whole sentence, memorise it, and translate from memory. Attention lets the translator glance back at the original for every word they write.",
        ALIGN_PICTURE, "Illustrative, using the lesson's sentence. The crossed lines show the change in word order.",
        ("c5", "<b>Try to break it.</b> Step through each French word and see which English word gets the most weight. Then change the softmax temperature.", "<b>Now say why:</b> why do the weights handle the word-order change without any rule telling them to?"),
        ["c2", "c4"], ["c6"], ["c3"], ["src"],
        ["An encoder reads the input, and a decoder generates the output token by token.",
         "Originally, the decoder only got one fixed-length summary, so long sentences failed.",
         "Attention scores the decoder state against every encoder state.",
         "A softmax turns scores into weights, and the weighted average is the context vector.",
         "The weights act as a learned soft alignment.",
         "Removing the RNNs and keeping attention gave the Transformer."]),
    "fundamentals/self-attention": _plan(
        "Your review says \"the biryani was cold but the naan was great\". An RNN has to carry \"biryani\" along to reach \"cold\", and a CNN only sees nearby words. The interviewer asks:",
        "What do Q, K and V do, and why divide by √d?",
        "Think of a room where each word asks a question. The query is what a word is looking for, the key is the label every word wears, and the value is what it hands over. \"Cold\" asks what's cold, biryani's label matches, so \"cold\" takes in most of biryani.",
        QKV_PICTURE, "Illustrative. The shares come from a softmax over the query–key scores.",
        ("c3", "<b>Try to break it.</b> Click each word and see who it attends to. Compare \"cold\" with \"great\", and then look at \"was\".", "<b>Now say why:</b> how does the same formula send \"cold\" to biryani and \"great\" to naan, with no rule about food?"),
        ["c2"], ["c5"], ["c4"], ["src"],
        ["Every token builds its representation from all the tokens.",
         "Each embedding is projected into a query, a key and a value.",
         "Weights are a softmax over query–key dot products, divided by √d.",
         "The output is the weighted sum of the values.",
         "Scaling keeps score variance near one, or softmax saturates and gradients vanish.",
         "It's parallel and direct, but O(n²) and order-agnostic, so position must be added."]),
    "fundamentals/multi-head-attention": _plan(
        "With one attention head, \"cold\" has to split its attention between \"biryani\", what is cold, and \"was\", the verb before it. The signals blur together. The interviewer asks:",
        "Why several heads, and what do they cost at long context?",
        "Think of several readers going through the same text, each with their own highlighter. One marks food, another marks grammar. Then they combine their notes, instead of one highlighter trying to do both jobs.",
        HEADS_PICTURE, "Illustrative. Heads aren't told their jobs. Each learns its own pattern.",
        ("c3", "<b>Try to break it.</b> Switch between the two heads, and compare what \"cold\" and \"naan\" attend to in each.", "<b>Now say why:</b> what would be lost if both patterns had to share one set of weights?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["Multi-head attention runs h attention operations in parallel.",
         "Each has its own projections, into a subspace of size d ÷ h.",
         "Outputs are concatenated and mixed with an output projection.",
         "Different heads can track different relations, instead of one blended average.",
         "The parameter count stays 4d², whatever h is.",
         "The n² score matrix and KV cache grow, hence FlashAttention and MQA or GQA."],
        trap_title="\"More heads means more parameters\"",
        trap_html="<p>It sounds right, since each head has its own projections. But with d fixed, each head works in a smaller space of size d ÷ h, so the total stays at 4d². Adding heads changes how attention gets divided, not how many weights you have. The real cost at long context is the n-by-n score matrix and, during generation, the KV cache.</p>"),
    "fundamentals/positional-encodings": _plan(
        "\"The biryani was cold but the naan was great\" and \"the naan was cold but the biryani was great\" use the same words, with opposite meanings for each dish. Plain self-attention can't tell them apart. The interviewer asks:",
        "How does a Transformer know word order, and why RoPE?",
        "Think of giving each word a clock hand, turned according to its position. Any two words a fixed distance apart have the same angle between their hands, wherever they sit. That's RoPE: attention sees how far apart words are, not just where they are.",
        ROPE_PICTURE, "Illustrative. Each pair sits the same angle apart, because each pair's gap is the same.",
        ("c4", "<b>Try to break it.</b> Move the query and key positions together, keeping the gap between them the same. Then change the gap.", "<b>Now say why:</b> why does the score depend on the gap, and not on the absolute positions?"),
        ["c2"], ["c5"], ["c3"], ["src"],
        ["Self-attention is permutation-equivariant, so it can't tell word order alone.",
         "The original paper added fixed sinusoidal encodings to the embeddings.",
         "BERT and GPT-2 learned absolute positions, which can't go beyond the trained length.",
         "RoPE rotates query and key pairs by an angle proportional to position.",
         "So the dot product depends only on the relative offset.",
         "ALiBi adds a distance penalty, and context can be extended by rescaling RoPE."]),
    "fundamentals/transformer-block": _plan(
        "A teammate stacks attention layers and nothing else, and the model is weak. Attention only produces weighted averages. The interviewer asks:",
        "What's inside one block, and where do the parameters go?",
        "Think of a meeting followed by desk work. In attention, tokens share what they know. In the feed-forward layer, each works alone on what it heard. Everything gets added to one running document, so nothing is lost along the way.",
        STACK_PICTURE, "Illustrative. The block keeps its shape, so you can stack N of them.",
        ("c5", "<b>Try to break it.</b> Compare GPT-2 small, BERT-base and LLaMA-7B, then change the number of layers. Look at attention against FFN parameters.", "<b>Now say why:</b> why do most of the parameters sit in the feed-forward layers, when attention gets all the attention?"),
        ["c2"], ["c4"], ["c3"], ["src"],
        ["A block has multi-head self-attention, which moves information between tokens.",
         "It also has a position-wise feed-forward network, which transforms each token alone.",
         "Each is wrapped in a residual connection with normalisation.",
         "Modern models use pre-norm, which keeps the residual path an identity.",
         "The block preserves shape, so you stack N of them.",
         "Attention has 4d² parameters and the FFN 8d², so about two-thirds are in the FFNs."]),
    "fundamentals/encoder-decoder-architectures": _plan(
        "You have three jobs: classify a review, generate a reply and translate a note. A colleague asks which of BERT, GPT and T5 to use. The interviewer asks:",
        "BERT vs GPT vs T5: what's actually different?",
        "Think of reading a finished book, writing a new one, and translating. A reader can flip to any page. A writer can only see what's written so far. A translator reads the original while writing the new text. Those are the three attention masks.",
        MASKS_PICTURE, "The same attention, with different masks deciding who can see whom.",
        ("c3", "<b>Try to break it.</b> Switch between encoder, decoder and cross-attention, and select different query tokens. Watch which tokens they can see.", "<b>Now say why:</b> what would go wrong if a token could see the future during training?"),
        ["c2", "c4"], ["c5"], [], ["src"],
        ["The three families differ mainly in the attention mask.",
         "Encoders like BERT use bidirectional attention, which suits classification and embeddings.",
         "Decoders like GPT use a causal mask and train on next-token prediction.",
         "Encoder–decoders like T5 connect the two through cross-attention.",
         "Modern LLMs are decoder-only: the objective is simple, it scales, and prompting covers most tasks."],
        trap_title="\"BERT, GPT and T5 are basically the same model at different sizes\"",
        trap_html="<p>It sounds right, since they're all built from the same blocks. But the attention mask and the training objective differ, and that decides what each can do. BERT sees the whole text and predicts hidden tokens, so it isn't built to generate. GPT only sees earlier tokens and predicts the next one, so generating text is natural.</p>"),
    "fundamentals/transformer-end-to-end": _plan(
        "An interviewer hands you the marker and asks you to go through a whole Transformer on the board, from raw text to the next word. The interviewer asks:",
        "Walk a sentence through a whole Transformer, with shapes.",
        "Think of an assembly line. Text goes in and becomes ids, then vectors. The vectors pass through identical stations that keep their shape, and a final station turns each one into a score for every word in the vocabulary.",
        PIPELINE_PICTURE, "Shapes for one sequence of n tokens, in a GPT-2-small-sized model. The last shape is the logits.",
        ("c2", "<b>Try to break it.</b> Switch between GPT-2 small and LLaMA-7B. Then raise the batch size and sequence length, and watch the logits tensor and KV cache.", "<b>Now say why:</b> why does the KV cache grow so fast, and where does its memory go?"),
        ["c1", "c3"], ["c4"], [], ["src"],
        ["Text becomes token ids, and ids become an n × d matrix.",
         "Position is added, or applied as RoPE.",
         "It passes through N identical blocks of attention and feed-forward.",
         "A final norm and linear layer give logits at every position.",
         "In training, cross-entropy against the next token runs at all positions, thanks to the causal mask.",
         "At inference, softmax on the last position gives the next token."],
        trap_title="\"A Transformer is basically just attention\"",
        trap_html="<p>It sounds right, since attention is what made it famous. But about two-thirds of a block's parameters are in the feed-forward network, and the residual connections and normalisation are what let it train at depth. In a good walkthrough, you name those parts as well.</p>"),
})
DL_PLANS["fundamentals/transformer-end-to-end"]["situation_chapters"] = []
DL_PLANS["fundamentals/transformer-end-to-end"]["say_hint"] = "This one's a walkthrough, so aim for about 2 minutes. It feels different from reading it, and that's the point."

DIFFUSION_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="Two peaks at step 0 get blurrier with added noise. By step 500 they have merged into one bump, and by step 1,000 it is pure noise. Adding noise is fixed; removing it is what the model learns.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="60" y="14">t = 0</text><text x="180" y="14">t = 200</text><text x="300" y="14">t = 500</text><text x="420" y="14">t = 1,000</text></g>
  <path d="M10 84H110M130 84H230M250 84H350M370 84H470" stroke="var(--line-strong)" stroke-width="1.5"/>
  <g fill="none" stroke="var(--a)" stroke-width="3"><path d="M10.0 84.0 12.5 83.9 15.0 83.8 17.5 83.4 20.0 82.3 22.5 80.2 25.0 76.2 27.5 69.5 30.0 60.2 32.5 48.8 35.0 37.6 37.5 29.1 40.0 26.0 42.5 29.1 45.0 37.6 47.5 48.8 50.0 60.1 52.5 69.5 55.0 75.9 57.5 79.5 60.0 80.7 62.5 79.5 65.0 75.9 67.5 69.5 70.0 60.1 72.5 48.8 75.0 37.6 77.5 29.1 80.0 26.0 82.5 29.1 85.0 37.6 87.5 48.8 90.0 60.2 92.5 69.5 95.0 76.2 97.5 80.2 100.0 82.3 102.5 83.4 105.0 83.8 107.5 83.9 110.0 84.0"/><path d="M130.0 83.2 132.5 82.6 135.0 81.5 137.5 79.8 140.0 77.3 142.5 73.8 145.0 69.0 147.5 63.1 150.0 56.3 152.5 48.8 155.0 41.4 157.5 34.8 160.0 29.7 162.5 26.7 165.0 26.0 167.5 27.5 170.0 30.7 172.5 34.6 175.0 38.4 177.5 41.0 180.0 42.0 182.5 41.0 185.0 38.4 187.5 34.6 190.0 30.7 192.5 27.5 195.0 26.0 197.5 26.7 200.0 29.7 202.5 34.8 205.0 41.4 207.5 48.8 210.0 56.3 212.5 63.1 215.0 69.0 217.5 73.8 220.0 77.3 222.5 79.8 225.0 81.5 227.5 82.6 230.0 83.2"/><path d="M250.0 83.2 252.5 82.8 255.0 82.2 257.5 81.4 260.0 80.3 262.5 78.8 265.0 76.8 267.5 74.4 270.0 71.5 272.5 68.0 275.0 63.9 277.5 59.4 280.0 54.6 282.5 49.5 285.0 44.4 287.5 39.5 290.0 35.0 292.5 31.3 295.0 28.4 297.5 26.6 300.0 26.0 302.5 26.6 305.0 28.4 307.5 31.3 310.0 35.0 312.5 39.5 315.0 44.4 317.5 49.5 320.0 54.6 322.5 59.4 325.0 63.9 327.5 68.0 330.0 71.5 332.5 74.4 335.0 76.8 337.5 78.8 340.0 80.3 342.5 81.4 345.0 82.2 347.5 82.8 350.0 83.2"/><path d="M370.0 83.4 372.5 83.0 375.0 82.5 377.5 81.8 380.0 80.7 382.5 79.4 385.0 77.6 387.5 75.3 390.0 72.5 392.5 69.1 395.0 65.2 397.5 60.7 400.0 55.8 402.5 50.6 405.0 45.3 407.5 40.2 410.0 35.6 412.5 31.6 415.0 28.6 417.5 26.6 420.0 26.0 422.5 26.6 425.0 28.6 427.5 31.6 430.0 35.6 432.5 40.2 435.0 45.3 437.5 50.6 440.0 55.8 442.5 60.7 445.0 65.2 447.5 69.1 450.0 72.5 452.5 75.3 455.0 77.6 457.5 79.4 460.0 80.7 462.5 81.8 465.0 82.5 467.5 83.0 470.0 83.4"/></g>
  <path d="M10 108H462" stroke="var(--dim)" stroke-width="2"/><path d="M470 108 460 103V113Z" fill="var(--dim)"/><text x="240" y="102" font-size="13" fill="var(--dim)" text-anchor="middle">Add noise: fixed, nothing to learn</text>
  <path d="M18 130H470" stroke="var(--c)" stroke-width="2"/><path d="M10 130 20 125V135Z" fill="var(--c)"/><text x="240" y="147" font-size="13" font-weight="600" fill="var(--c)" text-anchor="middle">Remove noise: what the model learns</text>
</svg>"""

PAIRS_PICTURE = """<svg viewBox="0 0 480 166" role="img" aria-label="A grid of photos against captions. Each photo's own caption is darkest, along the diagonal. Biryani and pulao are also a little similar, so they are hard negatives.">
  <g font-size="14" fill="var(--ink)" text-anchor="middle"><text x="189" y="18">biryani</text><text x="249" y="18">pulao</text><text x="309" y="18">chai</text><text x="369" y="18">fries</text></g>
  <g font-size="14" fill="var(--ink)" text-anchor="end"><text x="150" y="47">biryani photo</text><text x="150" y="81">pulao photo</text><text x="150" y="115">chai photo</text><text x="150" y="149">fries photo</text></g>
  <rect x="160" y="26" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.85"/><rect x="220" y="26" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.3"/><rect x="280" y="26" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.06"/><rect x="340" y="26" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.06"/><rect x="160" y="60" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.3"/><rect x="220" y="60" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.85"/><rect x="280" y="60" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.06"/><rect x="340" y="60" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.06"/><rect x="160" y="94" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.06"/><rect x="220" y="94" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.06"/><rect x="280" y="94" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.85"/><rect x="340" y="94" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.06"/><rect x="160" y="128" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.06"/><rect x="220" y="128" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.06"/><rect x="280" y="128" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.06"/><rect x="340" y="128" width="58" height="32" rx="3" fill="var(--a)" fill-opacity="0.85"/>
</svg>"""

EMBED_PICTURE = """<svg viewBox="0 0 480 170" role="img" aria-label="A map of dishes. Biryani sits next to pulao, pizza near pasta and lasagne, chai near coffee, and fries near nuggets. The groups sit far apart.">
  <rect x="1" y="1" width="478" height="168" rx="6" fill="none" stroke="var(--line-strong)" stroke-width="1.5"/>
  <g fill="var(--a)" fill-opacity=".14"><ellipse cx="105" cy="50" rx="86" ry="34"/><ellipse cx="360" cy="52" rx="100" ry="42"/><ellipse cx="105" cy="128" rx="86" ry="30"/><ellipse cx="360" cy="130" rx="100" ry="30"/></g>
  <g fill="var(--a)"><circle cx="48" cy="40" r="5"/><circle cx="104" cy="60" r="5"/><circle cx="290" cy="34" r="5"/><circle cx="362" cy="46" r="5"/><circle cx="300" cy="74" r="5"/><circle cx="48" cy="120" r="5"/><circle cx="104" cy="138" r="5"/><circle cx="290" cy="122" r="5"/><circle cx="362" cy="140" r="5"/></g>
  <g font-size="14" fill="var(--ink)"><text x="58" y="45">biryani</text><text x="114" y="65">pulao</text><text x="300" y="39">pizza</text><text x="372" y="51">pasta</text><text x="310" y="79">lasagne</text><text x="58" y="125">chai</text><text x="114" y="143">coffee</text><text x="300" y="127">fries</text><text x="372" y="145">nuggets</text></g>
</svg>"""

LATENT_PICTURE = """<svg viewBox="0 0 480 176" role="img" aria-label="Left: an autoencoder's codes form separate clumps with empty space between them, so a random code decodes to garbage. Right: a VAE's codes are overlapping regions packed around the centre, so any code decodes to something plausible.">
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="120" y="16">Autoencoder: holes</text><text x="360" y="16">VAE: no holes</text></g>
  <rect x="20" y="28" width="200" height="120" fill="none" stroke="var(--line-strong)" stroke-width="1.5"/><rect x="260" y="28" width="200" height="120" fill="none" stroke="var(--line-strong)" stroke-width="1.5"/>
  <g fill="var(--a)"><circle cx="50" cy="52" r="4"/><circle cx="60" cy="60" r="4"/><circle cx="46" cy="66" r="4"/><circle cx="178" cy="50" r="4"/><circle cx="190" cy="58" r="4"/><circle cx="180" cy="66" r="4"/><circle cx="62" cy="124" r="4"/><circle cx="74" cy="132" r="4"/><circle cx="56" cy="134" r="4"/></g>
  <path d="M136 94 148 106M148 94 136 106" stroke="var(--bad)" stroke-width="3"/>
  <circle cx="360" cy="88" r="56" fill="none" stroke="var(--dim)" stroke-width="1.5" stroke-dasharray="4 4"/>
  <g fill="var(--a)" fill-opacity=".28"><circle cx="340" cy="70" r="28"/><circle cx="382" cy="72" r="28"/><circle cx="360" cy="108" r="28"/></g>
  <circle cx="362" cy="84" r="5" fill="var(--ok)"/>
  <g font-size="13" font-weight="600" text-anchor="middle"><text x="120" y="168" fill="var(--bad)">Random code: garbage</text><text x="360" y="168" fill="var(--ok)">Random code: plausible</text></g>
</svg>"""

GAME_PICTURE = """<svg viewBox="0 0 480 150" role="img" aria-label="Noise goes into the generator, which makes fakes. Fakes and real data go to the discriminator, which says real or fake. The discriminator's reaction goes back to the generator, which never sees real data directly.">
  <g fill="var(--tint)" stroke="var(--c)" stroke-width="2"><rect x="6" y="44" width="62" height="36" rx="8"/><rect x="96" y="44" width="96" height="36" rx="8"/><rect x="96" y="104" width="96" height="36" rx="8"/><rect x="244" y="72" width="118" height="40" rx="8"/></g>
  <g font-size="14" font-weight="600" fill="var(--ink)" text-anchor="middle"><text x="37" y="67">Noise</text><text x="144" y="67">Generator</text><text x="144" y="127">Real data</text><text x="303" y="97">Discriminator</text></g>
  <path d="M68 62H88M192 62H220V82H236M192 122H220V102H236M362 92H372M303 72V24H144V36" fill="none" stroke="var(--dim)" stroke-width="2"/>
  <g fill="var(--dim)"><path d="M96 62 86 57V67Z"/><path d="M244 82 234 77V87Z"/><path d="M244 102 234 97V107Z"/><path d="M144 44 139 34H149Z"/><path d="M380 92 370 87V97Z"/></g>
  <text x="384" y="97" font-size="13" fill="var(--ink)">Real or fake?</text>
  <text x="224" y="16" font-size="13" font-weight="600" fill="var(--c)" text-anchor="middle">Its reaction teaches the generator</text>
</svg>"""

DL_PLANS.update({
    "fundamentals/embeddings": _plan(
        "The delivery app wants \"more like this\" suggestions: order biryani, get pulao rather than fries. A teammate one-hot encodes the dishes, and every dish comes out equally unlike every other. The interviewer asks:",
        "What is an embedding, and where does its meaning come from?",
        "Think of a map of dishes that nobody draws by hand. Dishes that turn up in similar order notes get placed close together. Biryani lands next to pulao and far from fries, just from how the words are used.",
        EMBED_PICTURE, "Illustrative, in two dimensions. Real embeddings use hundreds.",
        ("c4", "<b>Try to break it.</b> Pick biryani at embedding size 4, and look at its neighbours. Raise the size to 8. Then try chai.", "<b>Now say why:</b> why does a small size group dishes by cuisine, while a larger one separates finer meaning?"),
        ["c2", "c3"], ["c5"], [], ["src"],
        ["An embedding maps a discrete item to a dense, low-dimensional vector.",
         "It's a lookup table, trained by gradient descent.",
         "Similar items end up close, usually measured by cosine similarity.",
         "word2vec predicts surrounding words, so words used in similar contexts get similar vectors.",
         "That's equivalent to factorising a shifted PMI co-occurrence matrix.",
         "Transformers give contextual embeddings, which change with the sentence.",
         "You named a use, like semantic search, RAG retrieval or recommendations."],
        edits=[("The lab below uses that equivalence", "The lab in the Intuition tab uses that equivalence")],
        trap_title="\"An embedding stores what the word means\"",
        trap_html="<p>It sounds right, since similar dishes do end up close. But the vector only reflects how a word is used. The lab counts which words appear near which, and nobody tells it that biryani and pulao are both rice dishes. Individual dimensions rarely mean anything by themselves. And word2vec gives \"cold\" one vector, whether it's \"cold biryani\" or \"a cold\". Telling those apart takes contextual embeddings.</p>"),
    "fundamentals/autoencoders-and-vaes": _plan(
        "The app stores 64-pixel icons of dishes. A teammate trains an autoencoder that redraws them well, then feeds it random codes to get new icons, and gets garbage. The interviewer asks:",
        "Why can't a plain autoencoder generate, and what does a VAE change?",
        "Think of describing an icon over the phone with a few numbers. A plain autoencoder only learns the codes it has seen, with empty space between them. A VAE gives each icon a small fuzzy region and packs those regions around the centre, so any point you pick means something.",
        LATENT_PICTURE, "Illustrative, in two dimensions. The dashed circle is the prior, N(0, I).",
        ("c3", "<b>Try to break it.</b> Set the bottleneck to 1, then 3, then 12. Watch the reconstructions and the share of variance lost.", "<b>Now say why:</b> at 3 numbers, why can you tell the shapes apart even though most of the variance is still lost?"),
        ["c2", "c4"], ["c5"], [], ["src"],
        ["An autoencoder compresses an input to a low-dimensional code and reconstructs it.",
         "It trains on reconstruction error only, so it needs no labels.",
         "A linear one learns the PCA subspace.",
         "A VAE's encoder outputs a Gaussian, with a mean and a variance.",
         "The reparameterisation trick, z = μ + σ·ε, lets gradients flow through the sampling.",
         "It maximises the ELBO: reconstruction minus the KL to a standard normal.",
         "The KL keeps the latent space filled, so sampling from N(0, I) and decoding generates data."],
        trap_title="\"An autoencoder is a generative model\"",
        trap_html="<p>It sounds right, since it has a decoder that produces images. But nothing makes a plain autoencoder's code space orderly, so a random code usually decodes to garbage. The VAE's KL term is what fixes that, so you can't drop it as optional regularisation. Without it, you just have a noisy autoencoder.</p>"),
    "fundamentals/gans": _plan(
        "You need realistic delivery times to load-test the app, and real ones have two peaks, at about 25 and 45 minutes. A teammate trains a GAN, and it only ever produces the 25-minute kind. The interviewer asks:",
        "How does a GAN learn, and why is it so hard to train?",
        "Think of a forger and an inspector. The inspector learns to spot fakes, and the forger learns only from the inspector's reaction, never from the real paintings. If the inspector rejects everything with total confidence, the forger learns nothing about what to change.",
        GAME_PICTURE, "After training, you keep only the generator.",
        ("c3", "<b>Try to break it.</b> Click far away, covers one peak, wide, covers both, and between the peaks. Then drag the mean yourself, and watch the JSD and its gradient.", "<b>Now say why:</b> why does the generator get almost no signal exactly when it's furthest from the data?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["A generator maps noise to samples, and a discriminator classifies real versus fake.",
         "They play a minimax game.",
         "The optimal discriminator is p_data / (p_data + p_g).",
         "With it, the generator minimises the Jensen–Shannon divergence, which is zero only when the distributions match.",
         "If the distributions don't overlap, JSD saturates and gradients vanish.",
         "The generator can also collapse onto a few modes.",
         "Fixes include the non-saturating loss, WGAN with gradient penalty and spectral normalisation.",
         "GANs sample fast in one step, but diffusion now leads on quality and diversity."],
        trap_title="\"The discriminator always tells the generator where to go\"",
        trap_html="<p>It sounds right, since that's the whole idea of the game. But with the generator far away, at a mean of 80, the JSD sits at its maximum and its gradient is essentially zero. And a generator covering only one peak scores a JSD of 0.21 while ignoring half the data, and nothing in the game forces it to find the other peak. That's how mode collapse starts.</p>"),
    "fundamentals/diffusion-models": _plan(
        "You need new delivery times with both peaks intact. GANs dropped a peak, and VAEs came out blurry. A teammate proposes diffusion. The interviewer asks:",
        "How does a diffusion model generate, and why does it need so many steps?",
        "Think of a photo buried under static. Adding static is easy, and you know exactly how. Removing it all in one go is close to impossible, but removing a little is a simple task. So you train a model on that small task and repeat it many times.",
        DIFFUSION_PICTURE, "Illustrative shapes, using the lesson's noise schedule with T = 1,000.",
        ("c4", "<b>Try to break it.</b> Sample with 1 step, then 3, 10 and 100. Watch how many samples get stranded between the peaks.", "<b>Now say why:</b> this lab uses the exact noise prediction, so why does 1 step still land everything between the peaks?"),
        ["c2", "c3"], ["c5"], [], ["src"],
        ["The forward process gradually adds Gaussian noise over T steps, and nothing in it is learned.",
         "It has a closed form: x_t = √ᾱ_t x₀ + √(1 − ᾱ_t) ε.",
         "Training picks a random step, noises the data and predicts the noise with a mean-squared-error loss.",
         "That's equivalent to learning the score.",
         "Generation starts from noise and repeatedly removes the predicted noise.",
         "It's stable and gives diverse, high-quality samples, but needs many network calls.",
         "You named ways to cut the cost: DDIM, distillation or latent space.",
         "You mentioned classifier-free guidance for steering to a prompt."],
        trap_title="\"With a good enough network, one step is enough\"",
        trap_html="<p>It sounds right, since a perfect denoiser seems like it should finish the job. But the lab uses the exact noise prediction, and one step still puts every sample between the peaks. A single step can only jump to the average of what's possible, at delivery times that rarely happen. Getting down to a few steps takes methods built for it, like distillation and consistency models.</p>"),
    "fundamentals/contrastive-learning": _plan(
        "Customers want to search dish photos by typing, and new dishes keep appearing. Labelling millions of photos is too slow, but restaurants already upload each photo with a caption. The interviewer asks:",
        "How do you learn a shared embedding space from pairs, without labels?",
        "Think of a matching game. You get a photo and a pile of captions, and you have to pick its partner. To win against a big pile, you have to notice what makes each dish distinctive. Those noticed details are the embedding.",
        PAIRS_PICTURE, "Illustrative. Training darkens the diagonal. Biryani and pulao stay a little alike, which makes them hard negatives.",
        ("c3", "<b>Try to break it.</b> Start with trained encoders at a temperature of 0.1. Raise it to 1. Then switch to untrained encoders, and compare the loss with chance.", "<b>Now say why:</b> at a temperature of 1 every match is still right, so why does the loss rise?"),
        ["c2"], ["c4", "c5"], [], ["src"],
        ["Positive pairs, like two augmentations or an image and its caption, should get high cosine similarity.",
         "The other items in the batch act as negatives.",
         "InfoNCE is softmax cross-entropy over similarities divided by a temperature.",
         "Low temperature focuses on hard negatives.",
         "More negatives, from large batches or a MoCo queue, give a tighter bound.",
         "SimCLR uses augmented image pairs, and CLIP uses image–text pairs.",
         "You named a use, like text-to-image search or zero-shot classification."],
        trap_title="\"Temperature is just a small tuning detail\"",
        trap_html="<p>It sounds right, since every photo still picks its own caption when you raise it from 0.1 to 1. But the biryani photo's share on its own caption falls from 79% to 33%, and the loss rises from 0.15 to 1.03. Temperature sets how sharp the softmax is, which strongly affects which negatives dominate the gradient. CLIP learns it as a parameter.</p>"),
})
