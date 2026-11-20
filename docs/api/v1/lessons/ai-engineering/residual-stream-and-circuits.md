# The Residual Stream and Circuits

> How does information flow through a transformer, and what is a circuit?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/ai-engineering/residual-stream-and-circuits/
- Before this: Features, Polysemanticity and Superposition (`ai-engineering/features-and-superposition`)

## Intuition

### The situation

Your model completes "Mr Dursley … Mr" with "Dursley", and does the same for made-up names it has never seen. A teammate says it has memorised the pattern. The interviewer asks:

> How does information flow through a transformer, and what is a circuit?

### The idea

Think of a shared whiteboard passed down a row of people. Each person reads it and adds a note, and nobody erases anything. Features are the ideas on the board, and a circuit is the group of people whose notes together produce one answer.

[Figure: Three parts. The stream, attention, MLPs.]

_Because every write adds to the stream, a prediction can be split into parts._

### Play

**Try it.** Type a sequence with a repeated token, and watch the two heads find the earlier copy and predict what followed it.

#### [A][B] … [A] → predict [B]

An induction head completes repeated patterns. If token A was followed by B earlier, and A appears again, it predicts B. It cannot do this alone. A **previous-token head** in an earlier layer first writes “the token before me was …” into every position. The induction head then searches for the position whose previous token matches the current token, attends there, and copies what it finds [survey p. 58](https://arxiv.org/pdf/2611.08438#page=58) [Olsson et al. 2022](https://arxiv.org/abs/2209.11895).

$$ {(x_i = x_j)} \;\Rightarrow\; {\hat{x}_{j+1} \approx x_{i+1}} $$

Survey §6.8 induction-head box [p. 47](https://arxiv.org/pdf/2611.08438#page=47).

- **prefix match**: Somewhere earlier, token xᵢ equals the current token xⱼ. Finding it is the QK job, made possible by the previous-token head.

- **copy**: Predict that the next token is whatever came after the earlier occurrence, xᵢ₊₁. Writing that token is the OV job.

##### Try it: run the circuit by hand

Pick a sequence (or type your own, separated by spaces). The panel runs an idealised two-head induction circuit on the last token and shows what each head does.

Try the random-token preset: it works just as well, because the rule does not depend on _what_ A and B are. That is exactly how Olsson et al. define an induction head: by its behaviour on repeated sequences of random tokens [Olsson et al. 2022](https://arxiv.org/abs/2209.11895). They report that induction heads appear in a sudden phase change early in training, at the same point the model gains most of its in-context learning ability. The evidence is causal for small attention-only models and correlational for larger ones (more in the survey's training-dynamics chapters).

**Notice:** the circuit works on tokens it has never seen together, because it copies from the context instead of recalling facts. That's why induction heads explain much of in-context learning.

## How it works

### How it works

#### In one breath

Every transformer layer reads from one shared residual stream and adds its output back, so the final state is a sum of every component's contribution. Attention moves information between tokens, and MLPs transform it within a token. A circuit is the subgraph of components or features that computes one behaviour, like the induction heads that copy repeated patterns.

#### A running total that every layer reads and adds to

Picture one vector per token flowing up through the model. Each attention module and each MLP reads the current vector, computes something, and **adds** its result back. Nothing is overwritten. The survey calls this the residual stream, “the shared communication channel through which transformer components exchange information” [p. 23](https://arxiv.org/pdf/2611.08438#page=23), following Elhage et al. (2021).

1. The stream starts as the token’s embedding.

2. Attention reads the stream, gathers information from other tokens, and adds its output back.

3. The MLP reads the updated stream, transforms it, and adds its output back.

4. Every layer repeats the pattern. Nothing is erased; each block only adds.

5. At the top, the unembedding turns the final stream into scores (logits) over the vocabulary.

#### Unroll the layers and the stream becomes a sum

Each layer applies _h′ = h + Attn(h)_ and then _h = h′ + MLP(h′)_. Unroll that recursion and you get the equation below [p. 24](https://arxiv.org/pdf/2611.08438#page=24):

$$ {h_\ell(x)} = {h_0(x)} + {\sum_{k=1}^{\ell}}\Big({\mathrm{Attn}_k(h_{k-1}(x))} + {\mathrm{MLP}_k(h'_k(x))}\Big) $$

Survey §4.4 box [p. 24](https://arxiv.org/pdf/2611.08438#page=24) · hover any symbol for its meaning.

- **the stream at layer ℓ**: hℓ(x), the residual stream after layer ℓ, for every token of input x.

- **the start**: h₀(x), the token (and position) embedding. The stream begins here.

- **add every layer**: A plain sum over layers 1 to ℓ. Nothing multiplies earlier contributions away.

- **attention’s write**: What layer k’s attention module added, computed from the stream before it.

- **MLP’s write**: What layer k’s MLP added, computed from the stream after that layer’s attention.

This is “central to mechanistic interpretability”, says the survey, because it lets us “decompose model computation into additive contributions from individual components” [p. 24](https://arxiv.org/pdf/2611.08438#page=24). The equation leaves out layer normalisation. For a fixed input, layer norm is close to an affine map plus a scalar rescaling, so most of it can be folded into neighbouring weights. That makes the clean sum an approximation, but a good one [p. 24](https://arxiv.org/pdf/2611.08438#page=24).

##### Try it: split a prediction into parts

Because the stream is a sum, a component’s effect on a logit is just its write dotted with that token’s unembedding vector. This is direct logit attribution. Switch components off to see how the “Paris vs. London” decision for _The Eiffel Tower is in_ → ? is built up.

Illustrative numbers, not measured from a real model. Real direct logit attribution must also handle the final layer norm and indirect effects through later layers.

#### Each head decides where to look, then what to copy

Attention is the only part of a transformer that moves information _across_ token positions [Wang et al. 2023, App. J](https://arxiv.org/pdf/2211.00593#page=23). The survey describes its role as routing, aggregating and composing information across positions [p. 24](https://arxiv.org/pdf/2611.08438#page=24).

$$ {A} = \mathrm{softmax}\!\Big(\frac{{Q^{\top}K}}{{\sqrt{d_{\text{head}}}}}\Big), \qquad \Delta h = {W_O\,V}\,{A^{\top}} $$

Survey §4.4 attention box [p. 24](https://arxiv.org/pdf/2611.08438#page=24); the QK / OV split is from Elhage et al. (2021), as used in [Wang et al. p. 3](https://arxiv.org/pdf/2211.00593#page=3).

- **attention pattern**: A, a T×T table: how much each token (row) looks at each earlier token (column). Each row sums to 1.

- **where to look (QK)**: Each token’s query is compared with every token’s key. A high score means “look there”. Together, W_Q and W_K form the QK circuit.

- **keep it stable**: Dividing by √d_head keeps the scores in a range where softmax doesn’t saturate.

- **what to move (OV)**: The values of the attended tokens, mixed by A, are mapped by W_O back into the stream. W_O and W_V together form the OV circuit.

The QK/OV split is worth keeping in mind for the rest of the series: **QK decides where information moves from, OV decides what gets written**. A module with several heads simply adds the heads’ writes together, which is another sum the decomposition can exploit [p. 24](https://arxiv.org/pdf/2611.08438#page=24).

#### An MLP behaves like a large table of pattern → output memories

The MLP works on each token separately: up-project, apply a nonlinearity, down-project, add to the stream. Its hidden layer is usually much wider than the stream [p. 25](https://arxiv.org/pdf/2611.08438#page=25). The survey assigns MLPs feature transformation and factual knowledge retrieval [p. 24](https://arxiv.org/pdf/2611.08438#page=24).

A useful way to read it, from Geva et al. (2021): each row of the first matrix is a **key** that detects a pattern in the input, and each column of the second is a **value** that pushes the output towards certain tokens. In a 16-layer model, lower layers’ keys caught shallow patterns (texts ending in the same word), upper layers caught semantic ones (TV shows, time ranges). Each layer’s output was usually a blend of hundreds of memories rather than one winner [Geva et al. 2021](https://arxiv.org/abs/2012.14913).

| Memory (layer) | What it does | Kind |
|---|---|---|
| key, layer 1 | fires on texts ending in “substitutes” | shallow |
| key, layer 6 | fires on military texts ending in “base(s)” | shallow + semantic |
| key, layer 16 | fires on TV-show contexts | semantic |
| value, layer 15 | after “…owing in large”, pushes “part” | output side |

Examples from Geva et al. Tables 1–2. This key–value reading is why later episodes look for facts in MLPs (knowledge editing, Steering Vectors).

#### A circuit is a subgraph that does one job

The survey uses mechanism for the organisation of activations, features and transformations that together produce a behaviour. A circuit is the usual way to write a mechanism down: for a fixed computation with graph _G_, a circuit _C_ ⊆ _G_ whose nodes are components (attention layers, MLPs) or features, and whose edges are information flowing between them [p. 25](https://arxiv.org/pdf/2611.08438#page=25).

1. The survey’s Figure 3 example: the model reads “Dallas is in” and should say “Texas”.

2. Early MLPs turn “Dallas” into features such as “Southern state”, and “in” into a “state” context.

3. An attention head combines them into “say something starting with T”.

4. A later MLP sharpens that into “say …exas”.

5. Out comes “Texas”. The highlighted nodes and edges are the circuit: a small subgraph of the full computation that carries this one job.

Figure redrawn from survey Fig. 3 [p. 26](https://arxiv.org/pdf/2611.08438#page=26); the node labels are the survey’s illustration, not a measured graph.

#### Circuits for a capability vs. circuits for one prompt

| | Capability (task-level) circuits | Query-level circuits |
|---|---|---|
| **Question** | Which minimal set of heads and MLPs reproduces a behaviour across a dataset? | How do features interact to produce _this_ prompt’s answer? |
| **Nodes** | attention heads, MLP layers | sparse features from SAEs or transcoders |
| **Success** | the circuit recovers the model’s performance on the task dataset | the attribution graph faithfully traces this prediction |
| **Examples** | indirect object identification, greater-than, in-context learning | attribution graphs (Circuit Tracer) |

Survey §4.5 [p. 26](https://arxiv.org/pdf/2611.08438#page=26). How these are actually found (patching, ACDC, attribution graphs) is Activation Patching and Circuit Discovery.

## In practice

### In practice

#### How GPT-2 small knows to say “Mary”

“When Mary and John went to the store, John gave a drink to” → **Mary**. This task is indirect object identification (IOI). Wang et al. found the circuit GPT-2 small uses: 26 attention heads in 7 classes, about 1.1% of all (head, position) pairs. The heads implement a three-step algorithm [Wang et al. p. 2–4](https://arxiv.org/pdf/2211.00593#page=2):

1. The task: of the two names, output the one that is not the subject of the last clause.

2. Step 1. Duplicate-token heads (helped by induction and previous-token heads) notice that “John” appeared twice.

3. Step 2. S-inhibition heads pass that on, steering later heads away from “John”.

4. Step 3. Name-mover heads attend to the remaining name and copy “Mary” into the output.

5. The surprise: knock out all the name movers and the circuit still works with only a 5% drop, because “backup” heads step in. Redundancy like this makes circuits hard to pin down completely.

##### How well does the circuit explain the model?

Measured as the logit difference between “Mary” and “John”, the circuit alone reaches about **87%** of the full model’s performance (it is off by 0.46 out of 3.56). It passes this **faithfulness** test, but by the authors’ own account it fails the most demanding **completeness** tests [Wang et al. p. 9](https://arxiv.org/pdf/2211.00593#page=9).

#### Dallas → Texas → Austin

Query-level methods now trace circuits of features in deployed models. Anthropic’s study of Claude 3.5 Haiku found that, for “the capital of the state containing Dallas is”, the model internally activates **Texas** features first and then combines them with “capital” to say **Austin**. The two-hop reasoning happens inside a single forward pass, and you can intervene on the intermediate step [Lindsey et al. 2025](https://transformer-circuits.pub/2025/attribution-graphs/biology.html).

##### The authors’ own caveat

These attribution graphs come from an interpretable _replacement model_ that only approximates the real one. The authors report the method gives satisfying insight on only a minority of the prompts they tried (secondary sources summarise this as about a quarter) [Lindsey et al. 2025](https://transformer-circuits.pub/2025/attribution-graphs/biology.html). The survey adds that a full CLT replacement matches the original model’s top-1 prediction on only about 50% of prompts [p. 43](https://arxiv.org/pdf/2611.08438#page=43).

#### Circuits in production-scale models

Circuits were first worked out in small models: induction heads in small attention-only transformers (Elhage et al., 2021; Olsson et al., 2022), and the 26-head indirect-object circuit in GPT-2 small (Wang et al., 2022). In March 2025 Anthropic traced circuits in Claude 3.5 Haiku using attribution graphs (_On the Biology of a Large Language Model_). Examples include two-hop reasoning, where the model represents "Texas" on the way from "Dallas" to "Austin", and poems where the model often picks a rhyming word before writing the line that ends with it.

In May 2025 Anthropic open-sourced the tools, and Neuronpedia hosts an interactive front end for open models such as Gemma-2-2B. The Transcoders and Attribution Graphs lesson explains how those graphs are built.

### The answer that sounds right

#### "It just memorised the answer"

It sounds plausible for a large model, but induction works on random tokens the model has never seen, so it can't be memorised. The model learned a general copying algorithm. Check whether a behaviour generalises to new tokens before calling it memorisation.

## Say it

### How does information flow through a transformer, and what is a circuit?

#### The interviewer pushes further

Follow-up 1 of 3

Why does an additive stream help interpretability?

Because contributions add, you can split the output logits into each component's share, for example with direct logit attribution. Layer norm makes this approximate.

Follow-up 2 of 3

What did the indirect-object identification work find?

GPT-2 small uses a circuit of 26 heads in several classes, such as duplicate-token, S-inhibition and name-mover heads, plus backup heads that take over when the main ones are removed.

Follow-up 3 of 3

What's the difference between a feature and a circuit?

A feature says what is represented. A circuit says how features and components are wired together to compute a behaviour.

#### The 30-second answer

In a transformer every layer reads from a shared residual stream and adds its output back, so the final state is the embedding plus every component's contribution. That's what lets us attribute a prediction to parts. Attention heads move information between positions, and MLPs transform it within a position. A circuit is the small subgraph of heads, MLPs or features that produces one behaviour. The classic example is induction: one head marks which token came before each token, and another finds the earlier copy of the current token and copies what followed it.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv [2611.08438](https://arxiv.org/abs/2611.08438)) and 5 more sources · checked 13 Nov 2026

#### Sources

- [Barez et al., Understanding AI from the Inside (survey, 2026)](https://arxiv.org/abs/2611.08438)

- [Elhage et al., A Mathematical Framework for Transformer Circuits (2021)](https://transformer-circuits.pub/2021/framework/index.html)

- [Olsson et al., In-context Learning and Induction Heads (2022)](https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads/index.html)

- [Wang et al., Interpretability in the Wild: the IOI circuit in GPT-2 small (2022)](https://arxiv.org/abs/2211.00593)

- [Lindsey et al., On the Biology of a Large Language Model (Anthropic, 2025)](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)

- [Anthropic, Open-sourcing circuit tracing tools (29 May 2025)](https://www.anthropic.com/research/open-source-circuit-tracing)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
