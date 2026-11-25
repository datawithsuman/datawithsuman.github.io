# Design a Custom Vision LLM

> Your onboarding flow reads ID cards and licences in four languages. API models are slow at the tail and struggle with non-Latin scripts. Design an in-house vision model, and decide when it's worth building.

- Track: System Design › Document AI › Designs
- Type: Design · 25 min
- Page: https://aimlrounds.com/tracks/system-design/design-vision-llm/
- Before this: Vision-Language Models (`fundamentals/vision-language-models`), LoRA and QLoRA: Parameter-Efficient Fine-Tuning (`fundamentals/lora-and-qlora`)
- Quiz topic: `sdllm`
- Sources checked: 2026-11-05 · Text last changed: 2026-11-20 · Version: 69bea643eb

## Intuition

### The situation

A ride-hailing and delivery company onboards drivers and merchants across Southeast Asia, reading ID cards and licences in four languages. API models are slow at the tail and make mistakes on Thai script. The team asks whether to build its own model. The interviewer asks:

> Your onboarding flow reads ID cards and licences in four languages. API models are slow at the tail and struggle with non-Latin scripts. Design an in-house vision model, and decide when it's worth building.

#### Ask before designing

- **Documents:** ID cards, licences, registration certificates, from several countries, with many templates.

- **Languages:** say Indonesian, English, Thai and Vietnamese; Thai and Vietnamese use non-Latin or heavily accented scripts.

- **Fields:** name, number, date of birth, address: exact values, not summaries.

- **Latency:** the user is waiting in an onboarding flow, so p99 matters, not just the median.

- **Must never happen:** a wrong ID number accepted, or personal data sent somewhere it shouldn't go.

- **Success metrics:** field-level accuracy per document type and language, p50 and p99 latency, cost per document.

### The idea

Think of hiring a translator. You'd first try an agency. If they're slow and weak in Thai, you hire someone who already knows the alphabet and train them on your forms. Later, you train a junior to do most of it faster, nearly as well.

[Figure: Try what exists first. If it fails on tail latency or scripts, pick a small open model, teach it your scripts with synthetic text, fine-tune on documents, then shrink it.]

_Build only for a gap that matters, and stop when it's closed._

### Play

**Try to break it.** Step through the five approaches, watching Thai accuracy and p99 latency.

#### Which approach would you ship?

**What changes**

Illustrative numbers. The post states, in its text: p99 for external APIs can be 3–4× p50; LoRA gave high accuracy on Indonesian but struggled with Thai and Vietnamese; full fine-tuning lifted Thai by about 70 points and Vietnamese by about 40 over the baseline; the custom 1B model was within about 3 points of the 2B model and faster. Exact values were in tables we couldn't read.

Step through the options. The API looks good until you check the tail. LoRA is cheap and fixes the Latin-script documents, but **a new script needs the vision side retrained**. Full fine-tuning fixes Thai, and the custom small model gives most of that back as speed. Each step costs engineering time, so stop as soon as the requirements are met.

**Now say why:** why did LoRA fix Indonesian but not Thai?

## Architecture

### Architecture

#### In one breath

Build your own only when off-the-shelf fails on something that matters: here, **tail latency** and **non-Latin scripts**. Pick a **small** open vision model whose tokenizer suits your languages and that reads images at **native resolution**. Teach the vision side to read your scripts with **synthetic text images**, then fine-tune on labelled documents. LoRA can be enough for Latin scripts; new scripts need **full fine-tuning**. Finally, assemble and train a **smaller custom model** to cut latency, accepting a small accuracy gap.

#### Build or buy, then build carefully

1. **Try what exists:** traditional OCR struggles with many templates; API models handle variety but their p99 can be several times their p50, and they can hallucinate on some scripts; open models off the shelf may not be accurate enough.

2. **Choose a base:** small enough to fully fine-tune on your GPUs, a tokenizer that handles your languages efficiently, and native-resolution image input so small text isn't distorted.

3. **Prepare data:** render text in your languages from web text into images with varied fonts and backgrounds, and auto-label real documents with an internal pipeline (detect, rotate, OCR, extract), checked by people.

4. **Train in stages:** first teach the vision encoder to read your scripts, then fine-tune the whole model on document extraction.

5. **Shrink:** combine the vision encoder with a smaller language decoder, align them, and train in stages to get a faster model close to the larger one's accuracy.

##### Why pre-processing still matters

Detecting the document and correcting its rotation before the model sees it improves extraction a lot. A model shouldn't have to learn to read upside-down cards.

#### The numbers worth saying out loud

All of these are assumptions for the interview, not figures from a real system.

| Question | Working | Result |
|---|---|---|
| Documents a day | given | **500,000** |
| Peak documents per second | 500,000 ÷ 86,400 × 4 | **about 23** |
| Model memory, 2B in 16-bit | 2 billion × 2 bytes | **about 4 GB** |
| Model memory, 1B in 16-bit | 1 billion × 2 bytes | **about 2 GB** |
| Synthetic training images | 4 languages × 250,000 | **1 million** |

A small model fits easily on one modest GPU, so throughput comes from batching and replicas, and you control p99 because nothing else shares the hardware.

## In practice

### In practice

#### What every vision-model design gets asked

- **Why not keep the API?** Cost isn't the only reason: tail latency and accuracy on your scripts can rule it out. Data residency and control can too.

- **Base model choice:** check tokenizer coverage for your languages, image resolution handling, size versus your GPUs, and licence.

- **LoRA or full fine-tuning:** LoRA adapts behaviour cheaply; it struggled when the vision encoder had never seen the script. Teaching new visual text needed full training of the vision parts.

- **Synthetic data:** rendered text gives unlimited, perfectly labelled examples of your scripts; real labelled documents teach layouts and fields.

- **Evaluation:** field-level accuracy per document type and language, on held-out real documents, plus p50 and p99 latency.

- **Privacy:** ID documents are highly sensitive: restrict access to training data, keep data in-region, and audit usage.

##### Rollout

Shadow the current pipeline, compare field by field per country, then switch over one document type and country at a time, keeping human review for low-confidence fields.

#### What the real system reported

- **Use case:** extracting fields from ID cards, driver's licences and registration certificates for eKYC, in Indonesian, Thai, Vietnamese and English.

- **Why build:** traditional OCR struggled with template variety; proprietary models fell short on Southeast Asian languages, hallucinated and had high latency, with API p99 3–4× p50; open models weren't accurate enough out of the box.

- **Base:** Qwen2-VL 2B, for full fine-tuning on limited GPU memory, an efficient tokenizer for Thai and Vietnamese, and native-resolution input.

- **Training:** LoRA worked for Indonesian but not Thai or Vietnamese; two-stage full fine-tuning (vision pre-training on synthetic text, then document data) lifted Thai by about 70 points and Vietnamese by about 40.

- **Custom ~1B model:** Qwen2-VL's vision encoder with a Qwen2.5 0.5B decoder, trained in four stages; within about 3 points of the 2B model and faster. Skipping the language-specific visual stage dropped non-Latin accuracy by up to 10%.

The company's own figures, from the post's text. Its result tables were images we couldn't read, so exact accuracy and latency values aren't included.

### The answer that sounds right

#### "The API is accurate on average, so it's good enough"

It sounds right, since the average looks fine. But users wait at the tail, where API latency can be several times the median, and averages hide languages where accuracy is poor. Measure p99 and accuracy per language before deciding.

## Say it

### Your onboarding flow reads ID cards and licences in four languages. API models are slow at the tail and struggle with non-Latin scripts. Design an in-house vision model, and decide when it's worth building.

#### The interviewer pushes further

Follow-up 1 of 3

When would you not build your own model?

When an API meets accuracy and latency needs on our own test set, and data rules allow it. Building and maintaining a model costs engineering time, GPUs and ongoing retraining, so it needs a clear gap to justify it.

Follow-up 2 of 3

Why did LoRA work for Indonesian but not Thai?

LoRA adapts a model's behaviour with few parameters, which works when the model can already read the text. If the vision encoder never learned to see Thai script, small adapters can't teach it; the vision parts need full training on Thai text images.

Follow-up 3 of 3

How do you get enough labelled data for four languages?

Synthetic rendering for reading text, which is unlimited and perfectly labelled, plus an auto-labelling pipeline on real documents with human review for the fields and layouts.

#### The 30-second answer

First I'd clarify the document types, languages, fields, and latency needs, especially p99. I'd try what exists first: OCR, an API model and a small open model, measured on our own documents per language. If the API is too slow at the tail or fails on our scripts, I'd build. I'd pick a small open vision model whose tokenizer handles our languages, that reads native resolution, and that we can fully fine-tune on our GPUs. For data, I'd render text in our languages into synthetic images, and auto-label real documents with a detect, rotate, OCR and extract pipeline, checked by people. Training goes in stages: teach the vision encoder our scripts, then fine-tune on extraction. LoRA may be enough for Latin scripts, but new scripts need full fine-tuning. Then I'd build a smaller model from a vision encoder and a small decoder to cut latency, accepting a small accuracy gap. I'd evaluate per field, document type and language, and roll out in shadow mode, one country at a time.

**Key terms and sources**

Based on a super-app's published post: [Grab's "How we built a custom vision LLM to improve document processing"](https://engineering.grab.com/custom-vision-llm-at-grab) (November 2025). We couldn't read the post's three result tables, so the lab's accuracy and latency numbers are illustrative, shaped by the gaps the post states in its text. Uses vision-language models, LoRA and distillation. · checked 5 Nov 2026
