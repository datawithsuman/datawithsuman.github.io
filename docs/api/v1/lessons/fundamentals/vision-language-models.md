# Vision-Language Models

> How does an LLM see an image, and how many tokens does one cost?

- Track: Fundamentals › LLMs › Modern architecture
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/vision-language-models/
- Before this: Anatomy of a Modern LLM (`fundamentals/modern-llm-architecture`), Vision Transformers (`fundamentals/vision-transformers`)
- Quiz topic: `arch`

## Intuition

### The situation

Customers can now send a photo of their order or receipt to the support assistant. The first tests misread amounts, and the bill for image tokens is higher than expected. Someone suggests simply sending bigger images. The interviewer asks:

> How does an LLM see an image, and how many tokens does one cost?

#### Why it matters

Multimodal questions now come up in LLM interviews, and both CS336 and CME295 cover them. It's mostly a question of ideas you already have: Vision Transformers for the encoder, contrastive learning for CLIP, and KV cache sizing for the cost. This lesson joins them up.

### The idea

Think of describing a photo to a friend over the phone by cutting it into a grid of small squares, and describing each one. More squares give more detail, but the call takes longer. A few squares are quick, but you'd never read the small print. Vision-language models make the same trade.

[Figure: Three parts. An encoder turns patches into vectors. A projector matches the LLM's size. The LLM reads them as tokens.]

_The main choice is how many tokens an image gets._

### Play

**Try to break it.** Compare all four schemes on a large image. Then try a wide screenshot.

#### Spend the token budget

Fixed sizes: 896 and 448 pixels square, as in Gemma 3 and PaliGemma. Tiles: the rule OpenAI documents for models such as GPT-4o: fit within 2,048 pixels, shrink the short side to 768, then 85 + 170 tokens per 512-pixel square. One per 28 pixels is the adaptive rule without a size cap, though real services do cap image size. The grid is only a guide, and is capped so it stays readable. Text below about 6 pixels is marked as at risk, which is our own rule of thumb.

A customer sends a 2,048 × 3,008 photo of a receipt. At a **fixed 256 tokens**, it's cheap, but 12-pixel text shrinks to 3.6 pixels, and the model may misread the amount. With **one token per 28 pixels**, the text stays sharp, but the photo costs 7,992 tokens, nearly all of an 8k context, and about 1 GB of KV cache. **Tiles** land in between, at 1,105 tokens. Now try a wide screenshot: resizing it to a square squeezes it out of shape, which adaptive methods avoid.

**Now say why:** why does doubling both sides cost four times the tokens?

## Maths

### Maths

#### In one breath

A vision-language model turns an image into a sequence of vectors, then treats them like extra tokens in the prompt. A **vision encoder** splits the image into small patches and encodes them. A small **projector** maps those vectors to the LLM's size. The LLM then reads image and text together. Everything else follows from the **token budget**. Fixed-size models resize every image to the same token count, which is cheap but can lose small details. Adaptive models keep more detail, but a large image can cost thousands of tokens.

#### From pixels to tokens

##### Step 1: learn to link images and text

**CLIP** trained an image encoder and a text encoder on 400 million image and text pairs. In a batch of N pairs, it pushes each image towards its own caption, and away from the other N − 1. This gave vision encoders a good starting point, and LLaVA later built on one.

##### Step 2: connect an encoder to an LLM

| Part | Job | Examples |
|---|---|---|
| **Encoder** | Turns image patches into vectors | CLIP ViT-L/14, SigLIP, or a ViT trained for the purpose |
| **Projector** | Maps vectors to the LLM's size | One linear layer in LLaVA and PaliGemma, a small MLP in Qwen2.5-VL |
| **LLM** | Reads the image tokens and text together | Vicuna, Gemma, Qwen |

LLaVA showed how simple this can be. It first trained only the linear layer, with the encoder and LLM frozen, then fine-tuned the LLM too. Its training data came from a text-only GPT-4, given captions and object boxes instead of images.

##### Step 3: choose the token budget

| Model | Image becomes | Tokens |
|---|---|---|
| PaliGemma | A fixed square of 224, 448 or 896 pixels | 256, 1,024 or 4,096 |
| Gemma 3 | 896 × 896, then 4 × 4 average pooling | 256 |
| Qwen2.5-VL | 14-pixel patches, with each 2 × 2 group merged | One per 28 × 28 pixels, so it varies |

Gemma 3 adds **pan and scan**, which splits an image into crops and encodes each one, for when a single 256-token view isn't enough.

##### Step 4: tell the model where things are

A flat sequence loses the image's layout. Qwen2.5-VL gives each token separate time, height and width positions, a scheme called multimodal RoPE. For video, it groups two frames at a time, and ties the time position to real seconds, so the model can tell how fast things happen.

#### The maths

$$ {\text{tokens}} = {\Big\lceil \frac{W}{p} \Big\rceil}\,{\Big\lceil \frac{H}{p} \Big\rceil}, \qquad {\text{KV cache} = \text{tokens} \times \text{cache per token}} $$

The adaptive rule. Claude’s documentation states this form, with p = 28, and Qwen2.5-VL’s design implies it. Fixed-size models resize first, so their token count doesn’t change.

- **image tokens**: How many positions the image takes up in the context.

- **across**: Width divided by p, the pixels each token covers, rounded up. For Qwen2.5-VL and Claude, p is 28.

- **down**: The same for height. Doubling both sides means four times the tokens.

- **the cost**: Image tokens are ordinary tokens. They use context, take prefill time and fill the KV cache.

## In practice

### In practice

#### Where they fail

- **Simple visual tasks:** "Vision language models are blind" gave four leading models 7 very simple tasks, such as counting overlaps, and they averaged 58.07%. The best reached 77.84%, where people would expect about 100%. Tests suggest the encoders hold the information, but the LLM fails to decode it.

- **Small, rotated or non-Latin text:** OpenAI's documentation lists all three as limits. Check the resolution first, before blaming the model.

- **Invented details:** a model can describe what's usually in such an image, rather than what's there. Test with unusual images, not only typical ones.

- **Cost surprises:** image tokens count as input. Measure tokens per image on real uploads, and resize before sending.

- **Hidden instructions:** text inside an image reaches the model like any other input. Treat it as untrusted, as with other prompt injection.

### The answer that sounds right

#### "Send the highest resolution, so the model sees everything"

It sounds right, as more pixels means more detail. But services may shrink large images first, so the extra pixels can be wasted, and on an adaptive model a big image can fill the context by itself. Work out how large the text ends up, and crop to what matters.

## Say it

### How does an LLM see an image, and how many tokens does one cost?

#### The interviewer pushes further

Follow-up 1 of 3

How many tokens is a 1,000 × 1,000 image at one token per 28 pixels?

1,000 ÷ 28 rounds up to 36, so 36 × 36 = 1,296 tokens. Doubling both sides gives about four times as many.

Follow-up 2 of 3

Why does a 4 × 4 pool give 256 tokens at 896 pixels?

With 14-pixel patches, 896 pixels gives 64 × 64 = 4,096 patches. Averaging each 4 × 4 group leaves 16 × 16 = 256.

Follow-up 3 of 3

Your model misreads amounts on receipts. What do you check first?

The resolution that reaches the model. Work out how many pixels the text has after resizing, then try crops or a higher-detail setting. Test against OCR on the same images, and check the answer against the receipt's total.

#### The 30-second answer

A vision-language model has three parts. A vision encoder, usually a ViT, turns image patches into vectors. A small projector maps them to the LLM's size. The LLM then reads those image tokens along with the text. LLaVA showed that one linear layer can connect the two. The main design choice is the token budget. Gemma 3 uses 256 tokens for every image, which is cheap but can lose small text. Qwen2.5-VL uses about one token per 28 by 28 pixels, which keeps detail but can cost thousands of tokens. Image tokens are ordinary tokens, so they use context and KV cache. I'd also test simple visual tasks, as these models can still fail at counting and spatial reasoning.

**Key terms and sources**

How images become tokens, CLIP's shared space, encoders and projectors, fixed and adaptive image tokens, positions for images and video, and where these models fail. · checked 7 Nov 2026

#### Sources

- [Radford et al., CLIP](https://arxiv.org/abs/2103.00020)

- [Liu et al., LLaVA](https://arxiv.org/abs/2304.08485)

- [Beyer et al., PaliGemma](https://arxiv.org/abs/2407.07726)

- [Gemma Team, Gemma 3](https://arxiv.org/abs/2503.19786)

- [Qwen Team, Qwen2.5-VL](https://arxiv.org/abs/2502.13923)

- [Rahmanzadehgervi et al., Vision language models are blind](https://arxiv.org/abs/2407.06581)

- [OpenAI, Images and vision](https://developers.openai.com/api/docs/guides/images-vision)

- [Anthropic, Vision](https://platform.claude.com/docs/en/build-with-claude/vision)

- [Stanford CS336, multimodality lecture](https://cs336.stanford.edu/)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
