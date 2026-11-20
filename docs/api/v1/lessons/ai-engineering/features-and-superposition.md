# Features, Polysemanticity and Superposition

> Why do single neurons respond to unrelated things, and what is superposition?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/ai-engineering/features-and-superposition/
- Before this: Why Look Inside a Model? (`ai-engineering/why-look-inside-a-model`)

## Intuition

### The situation

You open up a model and find a neuron that fires on academic citations, Korean text and HTTP requests. A teammate says the neuron is just noise. The interviewer asks:

> Why do single neurons respond to unrelated things, and what is superposition?

### The idea

Think of a small storage room with more boxes than shelves. You stack boxes at angles so each is still reachable, and accept some bumping, as long as you rarely need two neighbouring boxes at once.

[Figure: Three ideas. Neurons mix concepts. Features are directions. Superposition packs in more.]

_The toy model behind this lesson: five features stored in two neurons._

### Play

**Try it.** Turn on one feature and read it back. Then turn on two neighbouring features at once.

#### Squeeze five numbers into two, spread them back out, clip the small stuff

The toy model is a single equation. The input **x** holds five feature strengths (most are zero at any moment). A 2×5 matrix **W** squeezes them into two neuron activations. Its transpose spreads them back out to five numbers. A bias and a ReLU clean the result [TMS p. 10](https://arxiv.org/pdf/2209.10652#page=10).

##### The equation, piece by piece

$$ {x'} = {\mathrm{ReLU}}\big({W^{\top}}\,{W}\,{x} + {b}\big) $$

TMS “ReLU output model” [p. 10](https://arxiv.org/pdf/2209.10652#page=10) · hover any symbol for its meaning.

- **the readout**: x′, the model’s guess for all five feature strengths. Training pushes it to equal the input x.

- **the input**: x, five feature strengths. For “only cat”, x = (1, 0, 0, 0, 0).

- **compress**: W maps five features to two neurons. Column i is feature i’s direction: cat’s column is (0.95, 0.31). So Wx is the activation point h.

- **expand**: Wᵀ reads h back along every feature’s direction: five dot products. This is the projection from section 2, done for all features at once.

- **threshold**: b, a bias. A negative value like −0.4 subtracts a little from every readout, so small leaks fall below zero.

- **clip**: ReLU sets every negative number to zero. Leaks below the threshold vanish. Without this nonlinearity superposition does not happen at all (TMS p. 12–13).

##### Where the leak comes from

Write out the readout for one feature _i_ before the ReLU. It splits into the feature itself plus everyone else’s contribution:

$$ {(W^{\top}Wx)_i} = {\lVert W_i\rVert^2\,x_i} + {\sum_{j\neq i} (W_i\cdot W_j)\,x_j} $$

Decomposition behind TMS’s “feature benefit vs interference” discussion [p. 13](https://arxiv.org/pdf/2209.10652#page=13). ReLU makes negative interference free; a negative bias turns small positive interference into negative [p. 13](https://arxiv.org/pdf/2209.10652#page=13).

- **readout of i**: What the model reports for feature i, before the threshold.

- **feature benefit**: Feature i’s own strength times its squared length. With unit-length directions this is just xᵢ: the signal.

- **interference**: Every other active feature j leaks in, scaled by how aligned its direction is with i’s (the dot product). In the pentagon, neighbours leak +0.31 and the far pair −0.81.

##### Try it: the pentagon playground

Toggle which features are active and watch the activation point, the five readouts and the threshold. Start with only cat, then add French.

##### What the lab should show you

With one feature active, the bias of −0.4 removes the +0.31 leaks and cat comes out alone. Turn the bias up to 0 and code and sports appear as false positives. That is interference with no filter.

**Notice:** one feature reads back cleanly, but two at once leak into the others. Superposition works only while features are rarely active together.

## How it works

### How it works

#### In one breath

Neurons in language models often fire for several unrelated concepts, so the unit of analysis is a feature: a direction in activation space. Models store more features than they have neurons by giving each a direction that overlaps slightly with the others, and a ReLU threshold filters out the crosstalk. That works only while features are rarely active together.

#### Many neurons answer to several unrelated things

A neuron is polysemantic if it fires strongly for two distinct concepts on different inputs, and intervening on it affects behaviour tied to both [p. 22](https://arxiv.org/pdf/2611.08438#page=22). The classic example comes from the vision model InceptionV1: neuron 4e:55 seemed to respond to cat faces, the fronts of cars and cat legs [Olah et al. 2020](https://distill.pub/2020/circuits/zoom-in/).

1. Show the network cat faces: the neuron fires.

2. Show it the fronts of cars: it fires too.

3. Cat legs: it fires again.

4. A neuron-level label is now misleading. This is why polysemanticity breaks the plan of reading a model one neuron at a time.

##### Update · my check (11 Nov 2026)

Even this textbook example is being re-argued. One of the original authors has since suggested 4e:55 may respond to a shared “V” shape rather than to cats and cars as concepts (reported in blog coverage, not a peer-reviewed paper; [summary](https://www.implicator.ai/goodfire-cammarata-ai-neurons-easier-to-read/)). That is the survey’s point about concepts in miniature: what counts as “one concept” can depend on whose vocabulary you use.

Why would neurons end up mixed? The survey points to representational limits and superposition: the model stores more concepts than it has neurons [p. 22](https://arxiv.org/pdf/2611.08438#page=22). That gets a full episode of its own (3.2).

#### Stop asking “which neuron?” and ask “which direction?”

The survey’s definition: a feature for a concept _c_ is a geometric structure φ in the model’s activation space whose activation is **predictive of** and **causally relevant to** _c_ [p. 23](https://arxiv.org/pdf/2611.08438#page=23). A single neuron is just the special case where φ happens to line up with one axis. Most often in practice, φ is a direction, but the definition deliberately leaves room for other shapes.

##### Try it: one neuron vs. one direction

Two neurons, two concepts. Each dot is an input: teal dots are cat inputs, amber dots are car inputs. Rotate the readout direction and count how often it “fires” (projection above 0.5) for each concept. Angle 0° is just reading neuron 1.

Illustrative data: 40 cat inputs scattered around 35°, 40 car inputs around −30°, strengths 0.6–1.1 (fixed seed). Computed in your browser.

That is the whole move in one picture. Both concepts push neuron 1 up, so neuron 1 is polysemantic. But there is a direction that responds to cats and ignores cars. The concept is clean; it just isn’t aligned with any neuron. That is why the field analyses the activation space as a whole, not neurons one at a time [p. 22](https://arxiv.org/pdf/2611.08438#page=22).

#### One neuron, two unrelated jobs

Open up a trained network and you would hope each neuron means one thing: a “cat” neuron, a “code” neuron. Often it doesn’t. The survey calls a neuron polysemantic when it fires strongly for two distinct concepts, and nudging it changes behaviour tied to both [survey p. 22](https://arxiv.org/pdf/2611.08438#page=22). That breaks the simplest plan for understanding a model, which is to read it one neuron at a time.

This episode follows one feature, **cat**, through a toy model with just **two neurons** that must hold **five features**: cat, code, French, math and sports. By the end you will see why neuron 1 ends up firing for both cat and sports, even though nothing in the data links them.

1. Feed the model a sentence about a cat. Neuron 1 fires.

2. Feed it a sentence about sports. Neuron 1 fires again.

3. So what does neuron 1 represent? Neither concept cleanly. It is polysemantic.

4. These are the real weights from the toy model we build in this episode. By section 8 you will see exactly why both are positive.

#### Store features as nearly perpendicular directions, then filter the leaks

Packing many signals into fewer dimensions is an old idea (compressed sensing, distributed codes); Elhage et al. (2022) demonstrated it cleanly in tiny ReLU networks where the true features are known [TMS p. 2](https://arxiv.org/pdf/2209.10652#page=2). Everything below uses their toy model.

The survey’s definition: hidden states encode more features than they have dimensions, _m_ ≫ _d_. Then the features cannot all be perpendicular, only nearly orthogonal, and neurons must be shared, which makes them polysemantic [p. 28](https://arxiv.org/pdf/2611.08438#page=28).

Think of a compass. It has two axes, north–south and east–west, yet you can name many headings: north-east, south-west and so on. Here is how the parts line up:

| Compass | Superposition |
|---|---|
| the two axes | the two neurons |
| a named heading | a feature (a direction) |
| how far you walk | how strongly the feature is active |
| ignoring tiny wobbles | the ReLU threshold (a negative bias) |

Where the analogy stops: compass headings are perfectly distinct, but feature directions leak into each other. It does predict the failure in section 6, though: walk north-east and north-west at once and you have gone north, a heading you never walked.

1. The same two neurons.

2. Cat gets a direction, at 18°.

3. The other four spread evenly around it: a regular pentagon. This is the shape the toy model actually learns for five equal features in two dimensions (TMS p. 22).

4. Neighbours sit 72° apart, not 90°. Reading one feature picks up a little of its neighbours.

5. The bet that makes it worthwhile: features are rarely active at the same time, so a threshold can remove the small leaks.

#### Two features at once can create a ghost

In the playground, turn on cat and French together, which are not neighbours. Their −0.81 leaks cancel each other: cat reads 0.19 and French 0.19, both below the threshold. Meanwhile both leak +0.31 into code, the direction between them, so code reads 0.62 and fires at 0.22. The model reports a feature that was never there and loses the two that were.

So superposition is a bet on sparsity. The toy-model paper finds that sparsity is necessary for superposition and that the switch between strategies is sharp: each feature is either dropped, superposed or given its own dimension, and the boundaries behave like a first-order phase change [TMS p. 14–15](https://arxiv.org/pdf/2209.10652#page=14).

##### Try it: when does sharing pay?

Each of the five features is active with probability _p_, with a random strength between 0 and 1. The lab compares two strategies by their average reconstruction error: **pentagon** (all five superposed, best bias and scale) against **dedicated** (code and math get clean neurons; the other three output their average).

My own simulation of the toy setup, not a figure from either paper: 2,000 random inputs per point (fixed seed), bias searched from −0.8 to 0.3 in steps of 0.1, scale from {0.8, 1, 1.1}. It reproduces the qualitative result in TMS §“Superposition as a phase change”, not its exact boundary.

##### The shapes superposition takes (3D)

With many equal features, the toy model does not pack them arbitrarily. Features snap into regular shapes, and each shape gives every feature a fixed fraction of a dimension: about ¾ for a tetrahedron, ⅔ for a triangle, ½ for an antipodal pair, ⅖ for a pentagon, ⅜ for a square antiprism [TMS p. 19](https://arxiv.org/pdf/2209.10652#page=19). Drag to rotate.

#### In thousands of dimensions, almost every pair of directions is nearly perpendicular

Two dimensions is a cramped place to share: the pentagon’s neighbours leak 0.31 into each other. Real layers have thousands of neurons, and there the geometry is far kinder. Pick random directions in a high-dimensional space and almost every pair lands close to 90° apart, so far more than _d_ features can coexist with only small leaks. This is the intuition behind “nearly orthogonal” in the survey’s definition [p. 28](https://arxiv.org/pdf/2611.08438#page=28).

120 random directions per setting (fixed seed), all 7,140 pairs. Measured in your browser.

**Go deeper: why the angles concentrate**

For two random unit vectors in _d_ dimensions, the cosine of their angle has mean 0 and standard deviation about 1/√d. At d = 1000 that is about 0.03, roughly ±2° around 90°. The number of directions you can fit while keeping every pair within a fixed angle of 90° grows exponentially with d (the Johnson–Lindenstrauss intuition used in popular explanations such as [3Blue1Brown’s](https://3blue1brown.com/lessons/mlp)). Small leaks still add up when many features are active at once, which is why sparsity still matters.

#### Look at the weights row by row and the neurons stop meaning one thing

Our pentagon’s weight matrix has two rows, one per neuron. Each row lists how strongly every feature pushes that neuron. A row with several large entries is a polysemantic neuron. The toy-model paper shows exactly this shift: as features get sparser, neurons move from monosemantic to holding a few features, then more [TMS p. 32–34](https://arxiv.org/pdf/2209.10652#page=34).

1. The 2×5 weight matrix of the pentagon. Teal means positive, red negative, darker means smaller.

2. Neuron 1’s strongest weight is cat, +0.95.

3. But sports also pushes neuron 1 at +0.59. Nothing about cats and sports is related; they just happen to point the same way along this axis.

4. So neuron 1 fires for cat and for sports. Superposition forces the sharing, and polysemanticity is what we see when we read neuron by neuron.

##### Superposition and polysemanticity are not the same thing

Superposition is about directions: more features than dimensions. Polysemanticity is about neurons: one neuron, many concepts. Superposition implies polysemanticity in a privileged basis, but the reverse does not hold. Section 10 shows polysemanticity arising without superposition [survey p. 29](https://arxiv.org/pdf/2611.08438#page=29).

## In practice

### In practice

#### Strong in toy models, suggestive in real ones

##### Toy models: dimensions per feature at the geometric “sticky points” (TMS p. 19)

dedicated neuron

1

tetrahedron

3/4

triangle

2/3

antipodal pair

1/2

pentagon

2/5

square antiprism

3/8

Fraction of a dimension each feature gets (lower = more packing). Uniform importance and sparsity, n = 400 features, m = 30 dimensions; the curve is “sticky” at 1 and ½ [TMS p. 17–19](https://arxiv.org/pdf/2209.10652#page=17).

**Real networks.** Dictionary-learning methods such as sparse autoencoders recover millions of distinct features from shared activation spaces, many more monosemantic than individual neurons, and some causally influence behaviour [survey p. 28–29](https://arxiv.org/pdf/2611.08438#page=29). In the first large demonstration, a one-layer transformer with a 512-neuron MLP was decomposed by autoencoders up to 256× wider (about 131,000 features), and blinded raters scored the features as more interpretable than the neurons [Bricken et al. 2023](https://transformer-circuits.pub/2023/monosemantic-features/).

The toy-model paper also shows networks can _compute_ while superposed: a small model learned absolute value for more features than it had neuron pairs, which is why the authors suggest real networks may be “noisily simulating larger, highly sparse networks” [TMS p. 2, 34–37](https://arxiv.org/pdf/2209.10652#page=36).

##### Read the evidence carefully · my check (11 Nov 2026)

Finding many interpretable features with an autoencoder is consistent with superposition but does not prove it: the survey notes dictionary learning can recover interpretable features even without superposition [p. 29](https://arxiv.org/pdf/2611.08438#page=29). The geometric shapes may also be partly specific to the toy model; its authors say so themselves [TMS p. 16](https://arxiv.org/pdf/2209.10652#page=16).

#### What the survey actually commits to

**Still a hypothesis.** The survey is explicit: in large language models, superposition “remains a hypothesis, not an established fact”. Polysemantic neurons alone do not show that superposition caused them [p. 29](https://arxiv.org/pdf/2611.08438#page=29).

##### A second origin story: incidental polysemanticity

Lecomte et al. (2024) show polysemanticity can appear even with _more_ neurons than features. Random initialisation makes two features slightly favour the same neuron by chance, and sparsity pressure (L1 regularisation or certain kinds of noise) amplifies the overlap until that neuron wins both. They predict about n²/(4m) polysemantic neurons for n features and m neurons, and confirm the trend for n ≈ 256, m from 256 to 4,096 [2312.03096 p. 2, 5](https://arxiv.org/pdf/2312.03096#page=5). Adding neurons would not remove this kind.

**Superposition is a design consequence, not a law.** The survey frames it as the result of “architectural permissiveness”: nothing stops gradient descent from packing features. Two responses follow [p. 29–30](https://arxiv.org/pdf/2611.08438#page=29):

- **Sparsity constraints** on weights or activations, limiting how many neurons can support any feature (for example weight-sparse transformers).

- **Different computational primitives**, analysing learned transformations instead of static features (MOLT, KANs).

These are not free. An early attempt, the SoLU activation, made more neurons monosemantic, but layer normalisation re-amplified the suppressed neurons and “smuggled” superposition back in [p. 50–51](https://arxiv.org/pdf/2611.08438#page=51). The lesson is that the pressure to compress is strong. Block it in one place and the network finds another.

##### Takeaways

1. More features than neurons forces features to be directions, and those directions cannot all be perpendicular.

2. The leaks between directions are interference. A ReLU with a negative bias filters them, but only while few features are active at once.

3. Whether a model superposes, and in what shape, changes sharply with sparsity and importance: a phase change.

4. Read neuron by neuron, superposition shows up as polysemantic neurons. That is why the field moved to feature directions and sparse autoencoders.

5. In real LLMs it is the leading explanation, not a proven fact, and polysemanticity has at least one other cause.

##### Next

Interpretability for AI Safety access (can a model read its own internals?) and Linear Representations and Universality. Sparse autoencoders, the tool built to undo superposition, are Sparse Autoencoders.

#### From toy models to real ones

The picture in this lesson comes from _Toy Models of Superposition_ (Anthropic, 2022), where small networks visibly packed five features into two dimensions. Two years later, Anthropic trained sparse autoencoders with up to 34 million features on Claude 3 Sonnet and found many interpretable ones, including safety-relevant features for security vulnerabilities in code and for lying and deception (_Scaling Monosemanticity_, 2024). That's strong evidence that real models store features in superposition.

It isn't the whole story. Some features are not single directions: circular features for days of the week and months were found in GPT-2 and Mistral 7B (Engels et al., 2024). Treat "a feature is a direction" as a good default, not a law.

### The answer that sounds right

#### "Just find the neuron for X"

It sounds natural, and early vision work did find some clean neurons. But in language models most neurons mix several concepts, because the model stores more features than it has neurons. Look for directions with probes or sparse autoencoders, and confirm them by intervening.

## Say it

### Why do single neurons respond to unrelated things, and what is superposition?

#### The interviewer pushes further

Follow-up 1 of 3

Why does sparsity matter?

If features rarely occur together, the crosstalk between overlapping directions is rarely triggered. When features are dense, the toy models go back to giving the important ones their own dimensions.

Follow-up 2 of 3

How many nearly perpendicular directions fit in d dimensions?

Far more than d. In high dimensions random directions are almost perpendicular, and the number with small pairwise overlap grows exponentially with d.

Follow-up 3 of 3

Is every feature a direction?

No. Some concepts, like days of the week, sit on a circle, and others need several dimensions. The linear picture is a default, not a rule.

#### The 30-second answer

A neuron can respond to unrelated things because the model needs more features than it has neurons. So it stores each feature as a direction spread across many neurons, and the directions overlap slightly. That's superposition. It works because most features are rarely active together, so interference is rare, and a ReLU threshold filters what's left. The cost is polysemantic neurons, which is why we analyse directions, with probes or sparse autoencoders, rather than single neurons.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv [2611.08438](https://arxiv.org/abs/2611.08438)) and 3 more sources · checked 13 Nov 2026

#### Sources

- [Barez et al., Understanding AI from the Inside (survey, 2026)](https://arxiv.org/abs/2611.08438)

- [Elhage et al., Toy Models of Superposition (2022)](https://transformer-circuits.pub/2022/toy_model/index.html)

- [Templeton et al., Scaling Monosemanticity (2024)](https://transformer-circuits.pub/2024/scaling-monosemanticity/)

- [Engels et al., Not All Language Model Features Are One-Dimensionally Linear (2024)](https://arxiv.org/abs/2405.14860)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
