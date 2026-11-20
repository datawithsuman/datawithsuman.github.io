# Logit Lens, Tuned Lens and Verbalisers

> How can you read what a model is predicting at a middle layer?

- Track: AI Engineering › AI Interpretability › Lessons
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/ai-engineering/logit-lens-and-verbalisers/
- Before this: The Residual Stream and Circuits (`ai-engineering/residual-stream-and-circuits`)

## Intuition

### The situation

Your model gets a two-step question wrong. You want to know whether it had the intermediate answer somewhere in its middle layers. The interviewer asks:

> How can you read what a model is predicting at a middle layer?

### The idea

Reading activations is like reading a draft before the author finishes. A lens peeks at the half-written sentence. A verbaliser asks the author to describe the draft in their own words.

[Figure: Three readers, from cheap to rich.]

_Every reader shows what's decodable. None proves the model uses it._

### Play

**Try it.** Step through the layers and watch the top prediction change.

#### A toy model where we know the truth

A 12-layer toy on “A B C A B → ?”. We built it so we know what’s inside: the part of each layer the output layer reads carries the current token **B** up to layer 9 and the answer **C** from layer 10; meanwhile a **hidden part** the output layer ignores has already worked out C by layer 5. The output-facing part is also stored in a slowly **rotating basis** that only lines up with the output layer at the end. The tuned lens is actually fitted, by least squares on 300 toy prompts, to match the final layer.

Toy: 8 tokens, 16-dimensional states (8 output-facing + 8 hidden), WU reads the first 8; output-facing part rotated by drift × layers remaining; noise 0.05. Each cell: top token and its probability; “·” = nothing above 20%; “+C” = C already present in the hidden part.

**Notice:** early layers predict junk under the logit lens, partly because they don't use the output layer's basis yet. The tuned lens fixes much of that with a learned translator per layer.

## How it works

### How it works

#### In one breath

The logit lens pushes a middle layer's residual stream straight through the output layer to see what the model would say if it stopped there. Middle layers don't quite speak the output layer's language, so the tuned lens learns a small translator per layer. Verbalisers go further: Patchscopes pastes an activation into another prompt and lets the model describe it, and LatentQA trains a decoder to answer questions about activations.

#### Unembed a middle layer

1. The residual stream (The Residual Stream and Circuits) carries one vector through the layers; at the end, the unembedding WU turns it into token scores.

2. The logit lens applies that same WU to an early layer’s vector: “what would the model say if it stopped here?”

3. Typical result: early layers are diffuse, then the answer firms up. In a 12-layer model on “A B C A B”, C might enter the top 20 at layer 6 and climb to first by the last layer.

4. Two catches: middle layers may be organised differently from the last one, and decoding a token doesn’t show the model uses it.

Formally, logitsℓ = WU hℓ [p. 67](https://arxiv.org/pdf/2611.08438#page=67). Because of the mismatch, decoded tokens show “at most information recoverable from the activation, rather than information used in model computation” [p. 68](https://arxiv.org/pdf/2611.08438#page=68). The original idea is nostalgebraist’s 2020 post [LessWrong](https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens).

#### Learn a translator for each layer

$$ \text{logits}^{TL}_\ell = {W_U}\big({W_\ell}\,{h_\ell} + {b_\ell}\big),\qquad \min_{W_\ell,b_\ell}\ {\mathbb{E}_x\,\mathrm{KL}\big(p_{\text{final}}(x)\,\|\,p^{TL}_\ell(x)\big)} $$

Survey §8.2 [p. 68](https://arxiv.org/pdf/2611.08438#page=68); tuned lens by Belrose et al. [arXiv 2303.08112](https://arxiv.org/abs/2303.08112).

- **the output layer**: The model’s own unembedding, unchanged.

- **learned translator**: A per-layer affine map Wℓ, bℓ that converts layer ℓ’s format into the final layer’s format.

- **middle-layer state**: The residual stream at layer ℓ.

- **trained to match the end**: The translator is trained so the lens’s distribution matches the model’s final output. That is the source of its main weakness.

It fixes the language mismatch, but it is still correlational, and because it is trained to predict the final output it answers “what will the model say?” rather than “what is this layer computing?”. It skips intermediate computation even more than the logit lens does [p. 68](https://arxiv.org/pdf/2611.08438#page=68).

#### From “what will it say” to “what is it disposed to cause”

$$ {J_\ell = \mathbb{E}_{\text{prompt},\,t,\,t'\ge t}\Big[\tfrac{\partial h^{t'}_{\text{final}}}{\partial h^{t}_{\ell}}\Big]},\qquad {p^{JL}_\ell} = \mathrm{softmax}\big(W_U\,\mathrm{norm}({J_\ell}\,{h_\ell})\big) $$

Survey §8.3 [pp. 68–69](https://arxiv.org/pdf/2611.08438#page=68) (Gurnee et al. 2026).

- **average Jacobian**: How a small change to layer ℓ at position t moves the final-layer state at every later position t′, averaged over prompts and positions.

- **the activation**: The residual stream at layer ℓ.

- **decoded disposition**: Push the activation through J, normalise, unembed: which tokens this state is disposed to promote later.

The rows of WUJℓ are **J-lens vectors**, one per token per layer; their dot product with hℓ says how strongly the state will promote that token. They can also be used as **steering vectors**, which the logit and tuned lenses can’t offer. Reported uses: multi-step reasoning and latent planning [p. 69](https://arxiv.org/pdf/2611.08438#page=69).

##### Limits

- Still token-level: if only “photo” shows, is it “photoperiodism” or something else?

- Works best in a middle band of layers, “J-space”: about 38–92% of depth in Claude Sonnet 4.5. Earlier is noisy; later collapses onto the output [p. 69](https://arxiv.org/pdf/2611.08438#page=69).

| Lens | Answers | Main catch |
|---|---|---|
| **Logit** | what it would say if stopped here | language mismatch across layers |
| **Tuned** | what it will finally say | skips intermediate steps |
| **Jacobian** | what this state pushes the output towards | token-level; best mid-depth |

##### Next · 8.2

Let the model describe its own activations in words: Patchscopes and LatentQA.

##### Sources for this tab

- Survey §8–8.3, [arXiv 2611.08438](https://arxiv.org/abs/2611.08438), pp. 66–69.

- nostalgebraist (2020). _Interpreting GPT: the logit lens._ [LessWrong](https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens).

- Belrose et al. _Eliciting Latent Predictions from Transformers with the Tuned Lens._ [arXiv 2303.08112](https://arxiv.org/abs/2303.08112).

#### Paste the thought into a “repeat after me” prompt

1. Run a source prompt and pick the activation to explain.

2. Here: the residual stream at “Kingdom”, layer ℓ.

3. Run an inspection prompt built to make the model repeat whatever is at “?”, and overwrite that position’s activation (layer ℓ*) with ours.

4. Whatever the model generates is its own reading of the activation. A different inspection prompt asks a different question, such as “what is the largest city of x?” → London.

5. The catch: the decoder is an ordinary model never trained to read pasted activations, so they can push it out of distribution.

$$ {e(h^t_\ell)} = {f_\theta}\big({p}{[h^{t^*}_{\ell^*}\leftarrow h^t_\ell]}\big) $$

Survey §8.4 [pp. 69–70](https://arxiv.org/pdf/2611.08438#page=69); Ghandeharioun et al. 2024 [arXiv 2401.06102](https://arxiv.org/abs/2401.06102). A concurrent method, SelfIE, works similarly [p. 70](https://arxiv.org/pdf/2611.08438#page=70).

- **the explanation**: Text describing the activation from layer ℓ, position t.

- **the model itself**: The same language model acts as the decoder.

- **inspection prompt**: A prompt designed to make the model verbalise whatever sits at the patched position.

- **the paste**: Replace the activation at layer ℓ*, position t* of p with our activation.

The logit and tuned lenses are special cases with a fixed (affine) translator; Patchscopes hands the translation to the model’s own text generation, which can express things an affine map can’t [pp. 69–70](https://arxiv.org/pdf/2611.08438#page=69).

#### Train a decoder to answer questions about activations

**LatentQA** (Latent Interpretation Tuning, LIT) builds a dataset of triples (h, q, a): an activation from the target model, a question and its answer, and fine-tunes a decoder to answer q from h. To make the activation carry a known attribute, it is read from a **control prompt** such as _“In your next reply, please try to evoke a brief sense of triumphant hubris.”_; then q = “In what way does the assistant craft its responses?” and a = “…a sense of self-assured victory.” A proprietary LLM generates both the control prompts and the QA pairs [p. 71](https://arxiv.org/pdf/2611.08438#page=71).

Trained on the task, the decoder no longer sees pasted activations as strange, which fixes Patchscopes’ out-of-distribution problem [p. 71](https://arxiv.org/pdf/2611.08438#page=71).

##### Two new problems

- **Memorising instead of reading**: with too little or too narrow data, the decoder learns surface pairings. Predictive Concept Decoders and Activation Oracles build more diverse data to counter this [p. 72](https://arxiv.org/pdf/2611.08438#page=72).

- **Shortcuts**: a decoder can reconstruct the original _input_ from the activation and answer from that, without analysing the representation. Recent studies find this failure “severe and prevalent”, so good verbalisation scores alone don’t show faithful reading [p. 72](https://arxiv.org/pdf/2611.08438#page=72).

A useful sanity check follows from the shortcut: if a plain text model given only the input text answers the question as well as the decoder given the activation, the decoder hasn’t shown it reads anything the input didn’t already say.

##### Next · 8.3

The oldest tool of all, probing classifiers, and the traps that make a high accuracy mean less than it seems.

##### Sources for this tab

- Survey §8.4–8.5, [arXiv 2611.08438](https://arxiv.org/abs/2611.08438), pp. 69–72.

- Ghandeharioun et al. (2024). _Patchscopes._ [arXiv 2401.06102](https://arxiv.org/abs/2401.06102).

- Pan et al. _LatentQA._ [arXiv 2412.08686](https://arxiv.org/abs/2412.08686).

## In practice

### In practice

#### Asking the model about its own activations

A related 2025 line of work tests whether models can report on their own internal states. Anthropic's introspection experiments (Lindsey, 2025) injected a concept vector into a model's activations, told it a thought might have been injected, and asked what it noticed. Claude Opus 4 and 4.1 generally did best, detecting the injection and naming the concept about 20% of the time at the right layer and strength. Other models did so less often, and results depended on post-training.

That's the same lesson as for lenses and verbalisers: a readout is a hint about what's represented. For anything you'll act on, confirm with an intervention.

### The answer that sounds right

#### "The lens shows the answer at layer 15, so the model knew it there"

It sounds direct, but a lens is a readout you chose, and a learned one can find information the model doesn't use. Decodable at layer 15 isn't the same as used by later layers. Patch or steer at that layer to test it.

## Say it

### How can you read what a model is predicting at a middle layer?

#### The interviewer pushes further

Follow-up 1 of 3

Why is the logit lens worse in early layers?

Early layers represent things in a basis the unembedding isn't tuned for, and later processing hasn't happened yet, so the direct readout is noisy.

Follow-up 2 of 3

What's the risk with LatentQA?

The decoder is a trained model, so it can answer from its own priors rather than the activation. Compare against a decoder given shuffled activations.

Follow-up 3 of 3

What did the introspection experiments find?

When concept vectors were injected, Claude Opus 4 and 4.1 sometimes noticed and named them, but only in a minority of trials, so self-reports are a weak signal.

#### The 30-second answer

The logit lens pushes a middle layer's residual stream through the final unembedding to see what the model would predict if it stopped there. It's free, but middle layers don't quite use the output basis, so it's biased early on. The tuned lens learns a small translator per layer and fits much better. For richer questions, Patchscopes pastes the activation into another prompt and lets the model describe it, and LatentQA trains a decoder to answer questions about activations. All of these show what's decodable, so I'd confirm anything important with an intervention.

**Key terms and sources**

Built from Barez et al., _Understanding AI from the Inside_ (arXiv [2611.08438](https://arxiv.org/abs/2611.08438)) and 5 more sources · checked 13 Nov 2026

#### Sources

- [Barez et al., Understanding AI from the Inside (survey, 2026)](https://arxiv.org/abs/2611.08438)

- [nostalgebraist, Interpreting GPT: the logit lens (2020)](https://www.lesswrong.com/posts/AcKRB8wDpdaN6v6ru/interpreting-gpt-the-logit-lens)

- [Belrose et al., Eliciting Latent Predictions with the Tuned Lens (2023)](https://arxiv.org/abs/2303.08112)

- [Ghandeharioun et al., Patchscopes (2024)](https://arxiv.org/abs/2401.06102)

- [Pan et al., LatentQA (2024)](https://arxiv.org/abs/2412.08686)

- [Lindsey, Emergent Introspective Awareness in Large Language Models (Anthropic, 2025)](https://arxiv.org/abs/2601.01828)

Explanations are ours, built from these sources. Chapters marked with page numbers come from the survey. Lab numbers are illustrative unless a lab says otherwise. Many recent papers are preprints.
