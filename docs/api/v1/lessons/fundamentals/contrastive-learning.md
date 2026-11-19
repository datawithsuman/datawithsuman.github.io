# Contrastive Learning (SimCLR, CLIP)

> How did CLIP learn to match photos and text without labels?

- Track: Fundamentals › Deep Learning › Representation and generative models
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/contrastive-learning/
- Before this: Embeddings and Representation Learning (`fundamentals/embeddings`)
- Quiz topic: `genm`

## Intuition

### The situation

Customers want to search dish photos by typing, and new dishes keep appearing. Labelling millions of photos is too slow, but restaurants already upload each photo with a caption. The interviewer asks:

> How do you learn a shared embedding space from pairs, without labels?

**Running example:** restaurants upload dish photos with captions. We want one embedding space where a photo of biryani sits next to the text "biryani", so customers can search photos by typing, and new dishes can be tagged without labelling thousands of images.

#### Labels are expensive; pairs are free

Labelling millions of dish photos by hand is slow and limited to a fixed list of classes. But we already have free pairs: a photo and its caption, or two crops of the same photo. If an encoder learns to match pairs among many distractors, it must capture what makes each thing distinctive, which is exactly a good embedding.

### The idea

Think of a matching game. You get a photo and a pile of captions, and you have to pick its partner. To win against a big pile, you have to notice what makes each dish distinctive. Those noticed details are the embedding.

[Figure: A grid of photos against captions. Each photo's own caption is darkest, along the diagonal. Biryani and pulao are also a little similar, so they are hard negatives.]

_Illustrative. Training darkens the diagonal. Biryani and pulao stay a little alike, which makes them hard negatives._

### Play

**Try to break it.** Start with trained encoders at a temperature of 0.1. Raise it to 1. Then switch to untrained encoders, and compare the loss with chance.

#### A batch of 5 dish photos and their captions

Rows: photos; columns: captions; cell = softmax over the row of cosine similarity / τ (darker = higher). 8-dimensional hand-set embeddings where biryani and pulao are deliberately similar (both rice dishes), illustrative. The loss averages photo→caption and caption→photo, as in CLIP.

With trained encoders and τ = 0.1, all 5 photos pick their own caption and the loss is **0.15**, but the **biryani** photo still gives **21%** to "pulao" (79% to its own caption): a hard negative the loss keeps pushing apart. Raise τ to 1 and the softmax flattens: matches are still correct, but the biryani photo gives only 33% to its caption and the loss rises to **1.03**. With random encoders only 1 of 5 matches; at τ = 1 the loss is 1.43, near chance level **ln 5 ≈ 1.61** (at τ = 0.1 random similarities get exaggerated and it's even worse, 2.26). With N candidates chance is ln N, so a CLIP batch of 32,768 makes every step a 32,768-way classification.

**Now say why:** at a temperature of 1 every match is still right, so why does the loss rise?

## Maths

### Maths

#### In one breath

**Contrastive learning** trains an encoder so that two views of the same thing land close together (a **positive pair**) and views of different things land far apart (**negatives**). For each example, the **InfoNCE** loss is a softmax classification: "which of the N candidates in this batch is my partner?", over cosine similarities divided by a **temperature** τ. **SimCLR** makes the pairs from two random augmentations of the same image; **CLIP** pairs each image with its caption from 400 million web image–text pairs, producing a shared space where text can search images and zero-shot classification works by comparing an image with prompts like "a photo of biryani". More negatives (bigger batches or a queue, as in MoCo) usually help.What you'll be able to do after this: write and compute the InfoNCE loss, explain temperature and negatives, and contrast SimCLR with CLIP.

#### InfoNCE: find your partner among N

$$ \ell_i = -\log \frac{\exp\big(\mathrm{sim}(z_i, z_i^{+})/\tau\big)}{\sum_{j=1}^{N}\exp\big(\mathrm{sim}(z_i, z_j)/\tau\big)}, \qquad \mathrm{sim}(a,b) = \frac{a^{\top}b}{\lVert a\rVert\lVert b\rVert} $$

Oord, Li & Vinyals (2018) introduced InfoNCE and showed it bounds the mutual information between the pair: the lower bound can be at most log N, one reason more negatives help. It's cross-entropy where the "class" is the partner's index (loss functions). Wang & Isola (2020) describe what it optimises as **alignment** (positives close) and **uniformity** (embeddings spread over the sphere).

- **similarity**: Cosine similarity between L2-normalised embeddings: 1 means identical direction.

- **positive pair**: Example i and its partner (its caption, or another augmentation of the same image).

- **all candidates**: The partner plus every other item in the batch, which act as negatives. N candidates in total.

- **temperature**: Divides the similarities before the softmax. Small τ sharpens the softmax and focuses the loss on the hardest negatives; large τ treats all negatives alike.

InfoNCE maximises a lower bound on mutual information between two views.

## In practice

### In practice

#### SimCLR and CLIP

| | SimCLR (Chen et al. 2020) | CLIP (Radford et al. 2021) |
|---|---|---|
| **Positive pair** | two random augmentations of the same image (crop, colour distortion, blur) | an image and its caption |
| **Encoders** | one image encoder + small projection head | an image encoder and a text encoder |
| **Data** | unlabelled images (ImageNet) | 400 million image–text pairs from the web |
| **Negatives** | the other images in a large batch (up to 8,192) | the other captions/images in a batch of 32,768 |
| **Result** | 76.5% ImageNet top-1 with a linear classifier on frozen features | zero-shot classification by comparing an image with "a photo of a {class}" prompts |

SimCLR found strong augmentation (especially crop + colour) and the projection head essential arXiv:2002.05709. MoCo (He et al. 2020) keeps a queue of past embeddings from a slowly updated encoder to get many negatives without huge batches. CLIP arXiv:2103.00020 learns τ as a parameter.

#### Learning without negatives: BYOL, DINO and MAE

Negatives need large batches, and can push apart items that are really similar. Why not just pull two views together? Because the easy answer is **collapse**: output the same vector for everything. Three methods avoid it in different ways.

| Method | How it works | What stops collapse | Reported ImageNet top-1 |
|---|---|---|---|
| **BYOL** | An online network predicts a target network's output for another view. | A predictor on one side, and a target that's a slow average, with no gradients. | 74.3% with ResNet-50 |
| **DINO** | A student matches the output of a slow-average teacher. | Centering and sharpening of the teacher's output. | 80.1% linear, with ViT-Base |
| **MAE** | Hide most image patches, and reconstruct them. | It's reconstruction, so no pairs are needed. | 87.8% with ViT-Huge |

DINO and BYOL report a linear classifier on frozen features. MAE's figure is after fine-tuning, so they aren't directly comparable.

- **DINO's balance:** centering stops one dimension dominating, but pushes towards uniform outputs. Sharpening does the opposite. Together, they avoid both kinds of collapse.

- **MAE's trick:** it hides about 75% of patches, and the encoder processes only the visible ones, which makes training 3 or more times faster. A light decoder is used only during pretraining.

- **Which to use:** contrastive training still suits matching across types, like image and text. These methods suit pretraining a vision backbone from unlabelled images.

Sources: BYOL, DINO and MAE.

#### What contrastive embeddings power

- **Search and retrieval:** text-to-image search, and dense text retrieval for RAG (dual encoders trained contrastively on question–passage pairs).

- **Zero-shot classification and tagging** with CLIP-style models: new classes need only a text prompt.

- **Multimodal LLMs:** many use a CLIP-style image encoder to turn images into tokens the language model can read; text-to-image models use CLIP-style text encoders for conditioning.

- **Recommendation:** two-tower models trained contrastively on user–item interactions (covered later in ML System Design).

### The answer that sounds right

#### "Temperature is just a small tuning detail"

It sounds right, since every photo still picks its own caption when you raise it from 0.1 to 1. But the biryani photo's share on its own caption falls from 79% to 33%, and the loss rises from 0.15 to 1.03. Temperature sets how sharp the softmax is, which strongly affects which negatives dominate the gradient. CLIP learns it as a parameter.

## Say it

### How do you learn a shared embedding space from pairs, without labels?

#### The interviewer pushes further

Follow-up 1 of 3

Why normalise the embeddings?

So similarity is cosine, bounded in [−1, 1]; the temperature then controls the softmax sharpness consistently and the model can't cheat by growing vector lengths.

Follow-up 2 of 3

What are false negatives?

Other items in the batch that are actually similar (two photos of biryani) but get pushed apart. They hurt more with fine-grained data; mitigations include de-duplication and soft targets.

Follow-up 3 of 3

Do you need negatives at all?

Methods like BYOL and SimSiam avoid explicit negatives using a predictor and stop-gradient to prevent collapse, but contrastive losses remain standard for multimodal retrieval.

#### The 30-second answer

Contrastive learning trains encoders so positive pairs, like two augmentations of one image or an image and its caption, have high cosine similarity and all other items in the batch act as negatives. The InfoNCE loss is a softmax cross-entropy over similarities divided by a temperature: pick your partner among N candidates. Low temperature focuses on hard negatives; more negatives, via large batches or a MoCo queue, give a tighter bound and usually better embeddings. SimCLR does it with augmented image pairs and gets strong linear-probe accuracy; CLIP does it with 400 million image–text pairs, giving a shared space for text-to-image search and zero-shot classification.

**Go further**

#### What not to say

- "Contrastive learning needs labels." It needs pairs, which are usually free.

- "Temperature doesn't matter." It strongly affects which negatives dominate the gradient.

**Key terms and sources**

Learning embeddings without labels by pulling matching pairs together and pushing everything else apart: positive and negative pairs, the InfoNCE loss and its temperature, SimCLR's augmented views, CLIP's image–text pairs, why batch size matters, and what these embeddings are used for · built from Oord, Li & Vinyals (2018), Chen et al. (SimCLR, ICML 2020), He et al. (MoCo, CVPR 2020), Radford et al. (CLIP, ICML 2021), Wang & Isola (ICML 2020) and Wu et al. (2018) · checked 29 Oct 2026

#### Sources

1. A. van den Oord, Y. Li & O. Vinyals, "Representation Learning with Contrastive Predictive Coding", arXiv:1807.03748, 2018.

2. T. Chen, S. Kornblith, M. Norouzi & G. Hinton, "A Simple Framework for Contrastive Learning of Visual Representations" (SimCLR), ICML 2020, arXiv:2002.05709.

3. K. He, H. Fan, Y. Wu, S. Xie & R. Girshick, "Momentum Contrast for Unsupervised Visual Representation Learning" (MoCo), CVPR 2020, arXiv:1911.05722.

4. A. Radford et al., "Learning Transferable Visual Models From Natural Language Supervision" (CLIP), ICML 2021, arXiv:2103.00020.

5. T. Wang & P. Isola, "Understanding Contrastive Representation Learning through Alignment and Uniformity on the Hypersphere", ICML 2020, arXiv:2005.10242.
