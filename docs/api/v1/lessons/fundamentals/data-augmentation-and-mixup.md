# Data Augmentation and Mixup

> How do you get more training data without collecting any?

- Track: Fundamentals › Deep Learning › Regularisation and debugging
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/data-augmentation-and-mixup/
- Before this: The Bias–Variance Trade-off (`fundamentals/bias-variance`)
- Quiz topic: `train`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 68a674ff06

## Intuition

### The situation

You have only 60 labelled orders, and more labels are expensive. The interviewer asks:

> How do you get more training data without collecting any?

**Running example:** the same 60 noisy delivery orders and 64-unit network as Dropout. With only two numbers per order there are no "flips" to apply, but mixup works on any input: blend two orders' distance and hour, and blend their late/on-time labels too.

#### Too few examples, too many parameters

Collecting and labelling more data is the most reliable fix for overfitting, and the most expensive. Augmentation manufactures new examples for free, as long as we know which changes leave the label unchanged. A photo of biryani flipped left-to-right is still biryani; a review with one synonym swapped is still positive.

### The idea

Think of showing a child the same dish from different angles: it's still biryani, so they learn what really matters. Augmentation makes those new views for free. Mixup goes further, blending two examples and blending their labels too.

[Figure: An order labelled late blended with an order labelled on time gives a new mixed order labelled 70 percent late.]

_Illustrative, with λ = 0.7. In practice, λ is drawn from a Beta distribution._

### Play

**Try to break it.** Compare no mixup with α = 0.2, 0.4 and 1. Watch train accuracy against test log loss.

#### Add 240 mixed orders and retrain

240 blended orders (random pairs, λ ~ Beta(α, α), soft labels) are added to the 60 originals; 64 tanh units, 800 Adam steps, fixed seed. Large dots: original orders; small grey dots: blended ones.

Without mixup, the test log loss is **1.26**: the model is confidently wrong. With **α = 0.2** it falls to **0.83** and with **α = 0.4** to **0.70**, while test accuracy stays around 76–79%. The blends fill the gaps between orders with "in-between" answers, so the model stops making extreme predictions near the boundary. At **α = 1**, heavy blending starts to hurt: accuracy drops to 72% and the loss rises to 1.01. Like the paper's ImageNet results, small α works best.

**Now say why:** why can mixed orders that never really existed make the model better on real ones?

## Maths

### Maths

#### In one breath

The best regulariser is more data. **Data augmentation** creates new training examples by applying transformations that don't change the label: flip, crop, rotate or recolour an image; paraphrase or back-translate a sentence; add noise to audio. The model learns that those changes don't matter (invariance), and it can't memorise exact pixels. **Mixup** goes further: it trains on **blends** of two random examples, x = λxi + (1 − λ)xj, with the label blended the same way, λ drawn from a Beta(α, α) distribution. That teaches the model to behave linearly between examples, which gives smoother boundaries and **better-calibrated** confidence. What you'll be able to do after this: choose label-preserving augmentations for a data type, explain mixup and CutMix, and say what α controls.

#### Label-preserving transforms

| Data | Common augmentations | Careful with |
|---|---|---|
| **Images** | random crop + resize, horizontal flip, colour jitter, rotation, Cutout / random erasing | flips for text-in-image or digits (6 vs 9) |
| **Text** | back-translation, synonym replacement, random deletion / swap, paraphrasing with an LLM | changes that flip sentiment or meaning |
| **Audio** | noise, time shift, speed / pitch change, SpecAugment (mask time and frequency bands) | pitch shifts for speaker ID |
| **Tabular** | small noise, SMOTE-style interpolation for rare classes | creating impossible rows |

AlexNet (Krizhevsky et al. 2012) used random 224×224 crops, flips and PCA colour noise and called augmentation essential to avoid overfitting. Survey: Shorten & Khoshgoftaar, _Journal of Big Data_ 2019. Augment only the **training** data; evaluate on clean data.

#### Mixup: train on blends

$$ {\lambda \sim \mathrm{Beta}(\alpha,\alpha)}, \qquad {\tilde{x} = \lambda x_i + (1-\lambda)x_j}, \qquad {\tilde{y} = \lambda y_i + (1-\lambda)y_j} $$

Zhang, Cissé, Dauphin & Lopez-Paz, "mixup: Beyond Empirical Risk Minimization", ICLR 2018 [arXiv:1710.09412](https://arxiv.org/abs/1710.09412): on ImageNet, α in [0.1, 0.4] improved on standard training while large α underfit; mixup also reduced memorisation of corrupt labels and improved robustness. **CutMix** (Yun et al. 2019) pastes a patch of one image into another and mixes labels by area.

- **mixing weight**: λ is drawn from Beta(α, α). Small α (0.1–0.4) gives λ near 0 or 1 most of the time: mostly one example with a bit of the other. α = 1 gives uniform λ.

- **blended input**: A weighted average of two random training inputs (two images pixel by pixel, or two orders’ features).

- **blended label**: The labels are blended with the same λ: a soft target like 70% late, 30% on time. Train with ordinary cross-entropy against it.

## In practice

### In practice

#### Augmentation in modern training

- **Vision:** RandAugment / TrivialAugment + mixup and CutMix are standard in strong ImageNet and ViT recipes; ViTs in particular rely on heavy augmentation when data is limited.

- **Self-supervised learning:** augmentation _defines_ the task: SimCLR learns by making two augmented views of one image agree (covered later in Contrastive Learning).

- **Speech:** SpecAugment is standard for ASR.

- **LLMs:** classic augmentation is rare in pre-training (data is huge); synthetic data from other models plays a similar role in fine-tuning.

### The answer that sounds right

#### "Augment everything, as strongly as possible"

An augmentation that can change the label teaches the model something false: heavy crops that cut the dish out of the photo, or a "synonym" that reverses a review. Too-strong augmentation also **underfits**, because the training task becomes harder than the real one. Policies like RandAugment (Cubuk et al. 2020) tune just two numbers, how many transforms and how strong, on validation data.

## Say it

### How do you get more training data without collecting any?

#### The interviewer pushes further

Follow-up 1 of 3

Should validation data be augmented?

No. Validation and test measure real-world performance, so they stay clean. (Test-time augmentation, averaging predictions over a few augmented copies, is a separate trick.)

Follow-up 2 of 3

How do you pick augmentations?

Ask which changes the label is invariant to in the real deployment, then tune their strength on validation data; check a grid of augmented samples by eye before training.

Follow-up 3 of 3

Why does mixup help calibration?

Soft, blended targets punish 100% confident predictions; the model learns intermediate outputs between classes.

#### The 30-second answer

Data augmentation creates new training examples with transformations that don't change the label, like crops, flips and colour jitter for images, back-translation for text or SpecAugment for audio, so the model learns invariances and can't memorise the exact training set. It's only applied to training data, and it must not change the label. Mixup trains on convex combinations of pairs of examples and their labels, with lambda drawn from a Beta distribution; small alpha like 0.2 works best. It regularises, smooths decision boundaries, improves calibration and makes the model more robust to label noise. CutMix pastes patches instead of blending pixels.

**Go further**

#### What not to say

- "Augment the test set to get better scores." That inflates metrics.

- "Mixup only works for images." It works on any vector input (and on hidden representations: manifold mixup).

**Key terms and sources**

Making more training data from the data you have: label-preserving transforms for images, text and audio, then mixup, which blends pairs of examples and their labels · built from Krizhevsky et al. (2012), Shorten & Khoshgoftaar (2019), Zhang et al. (ICLR 2018), Yun et al. (2019) and Cubuk et al. (2020) · checked 29 Oct 2026

#### Sources

1. A. Krizhevsky, I. Sutskever & G. Hinton, "ImageNet Classification with Deep Convolutional Neural Networks", NeurIPS 2012.

2. C. Shorten & T. Khoshgoftaar, "A survey on Image Data Augmentation for Deep Learning", _Journal of Big Data_ 6, 2019.

3. H. Zhang, M. Cissé, Y. Dauphin & D. Lopez-Paz, "mixup: Beyond Empirical Risk Minimization", ICLR 2018, [arXiv:1710.09412](https://arxiv.org/abs/1710.09412).

4. S. Yun et al., "CutMix: Regularization Strategy to Train Strong Classifiers with Localizable Features", ICCV 2019, [arXiv:1905.04899](https://arxiv.org/abs/1905.04899).

5. E. Cubuk, B. Zoph, J. Shlens & Q. Le, "RandAugment", CVPR Workshops 2020, [arXiv:1909.13719](https://arxiv.org/abs/1909.13719).

6. D. Park et al., "SpecAugment", Interspeech 2019, [arXiv:1904.08779](https://arxiv.org/abs/1904.08779).
