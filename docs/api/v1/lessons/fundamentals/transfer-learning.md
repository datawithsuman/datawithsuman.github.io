# Transfer Learning and Fine-Tuning

> Only 15 labelled examples? Reuse a model trained on 1,000.

- Track: Fundamentals › Deep Learning › CNNs
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/transfer-learning/
- Before this: ResNets and Skip Connections (`fundamentals/resnets-and-skip-connections`)
- Quiz topic: `cnn`

## Intuition

### The situation

Your delivery app launches in a new city with only 15 labelled orders, and you already have a model trained on 1,000 orders from another city. The interviewer asks:

> With only 15 labelled examples, how would you reuse a pre-trained model?

**Running example:** the late-delivery model was trained on **1,000 orders from city A**. The app launches in **city B**, where the rush hours are a little different (lunch peaks around 12:30, dinner around 21:00) and distance matters slightly less. City B has only a few labelled orders so far. Train a new model, or reuse city A's?

#### Small datasets can't train big models

A model trained from scratch on 15 or 30 examples has to discover everything ("rush hours exist", "distance matters") from almost no evidence. But a related task already taught a network those ideas. Reusing it is like hiring someone who knows the food business and only needs to learn the new city.

### The idea

Think of hiring someone who already knows the food business and teaching them your city, instead of training a complete beginner. You keep what they know, and you adjust gently, so you don't wipe out what made them valuable.

[Figure: A row of pre-trained layers shown as frozen, followed by one new head that gets trained.]

_Illustrative. Early layers tend to be general, and later ones specific to the task._

### Play

**Try to break it.** Start at 15 orders and compare from scratch, frozen features and fine-tuning. Then move up to 200.

#### City B accuracy, by how many labelled orders it has

All models: 16 tanh hidden units. Source model trained on 1,000 city-A orders. Test: 500 city-B orders. Frozen = only the output layer trains; fine-tune = all layers from city-A weights with learning rate 0.01 instead of 0.05. Fixed seeds.

With only **15** city-B orders, a model from scratch reaches **69%**; reusing city A's hidden layer and training just a new output layer reaches **89%**, already better than city A's model unchanged (85%). Fine-tuning everything is close behind (85%): with so little data, updating every weight is riskier than updating a few. At **200** orders the picture flips: from scratch catches up (93%) and **fine-tuning wins (95%)**, because it can adapt the hidden features to city B's different rush hours, which a frozen layer can't.

**Now say why:** why does the best choice change as you get more data?

## How it works

### How it works

#### In one breath

Features learned on a big dataset (ImageNet photos, web text) are useful far beyond it: early layers learn general things like edges and colours, later layers more task-specific ones. So instead of training from scratch, start from a **pre-trained** model. With little data, **freeze** it and train only a new output layer (**feature extraction**). With more data, **fine-tune** all layers with a **small learning rate**, often unfreezing from the top down. Transfer works best when the new task resembles the original, and it is how almost every vision, language and speech model is built today.What you'll be able to do after this: choose between from-scratch, frozen features and full fine-tuning for a given dataset size, and describe a safe fine-tuning recipe.

#### Three ways to use a pre-trained network

| Option | What trains | Use when |
|---|---|---|
| **Use as-is** | nothing | the tasks are the same (or zero-shot models) |
| **Feature extraction** | a new head on frozen features | little target data; similar domain |
| **Fine-tuning** | all (or the top) layers, small learning rate | more target data, or the domain differs |
| **From scratch** | everything, random init | lots of data and a very different domain |

Razavian et al. (2014) showed that off-the-shelf CNN features plus a linear classifier were a strong baseline across many vision tasks; Kornblith et al. (CVPR 2019) found that better ImageNet models generally transfer better, especially with fine-tuning.

#### Which layers transfer?

- Yosinski et al. (NeurIPS 2014) arXiv:1411.1792: first-layer features (Gabor-like edges, colour blobs) are **general**; higher layers become **specific** to the original task. Transferability drops as the tasks become less similar, yet transferred features beat random ones even for distant tasks, and fine-tuning transferred weights improved generalisation.

- So: freeze more layers when data is scarce and the domain is close; unfreeze more (from the top down) as data grows or the domain drifts.

## In practice

### In practice

#### Fine-tuning without wrecking the pre-trained weights

1. Replace the head with one sized for the new classes; keep the pre-trained preprocessing (same normalisation, image size or tokenizer).

2. Train the head first with the body frozen (a few epochs), so random head gradients don't damage the body.

3. Unfreeze the top blocks (or everything) with a learning rate 10–100× smaller than from scratch; **discriminative learning rates** (smaller for lower layers) and **gradual unfreezing** come from ULMFiT (Howard & Ruder 2018).

4. Use warmup, early stopping and light regularisation; small datasets overfit within a few epochs.

For BERT-style models the usual setting is AdamW with learning rates of 2e-5 to 5e-5 for 2–4 epochs (Devlin et al. 2019). Very large models are often adapted with parameter-efficient methods like LoRA instead of full fine-tuning (covered in the LLMs track).

### The answer that sounds right

#### "Just fine-tune the whole model at your normal learning rate"

It sounds right, since more training usually helps. But pre-trained weights are already near a good solution, and large steps destroy useful features. With very little data, fine-tuning everything can also overfit, so you start with the head, then unfreeze from the top with a learning rate 10 to 100 times smaller.

## Say it

### With only 15 labelled examples, how would you reuse a pre-trained model?

#### The interviewer pushes further

Follow-up 1 of 3

Why a lower learning rate for fine-tuning?

The pre-trained weights are already near a good solution; large steps destroy useful features (catastrophic forgetting) before the new head has learned anything.

Follow-up 2 of 3

Medical X-rays with an ImageNet model: freeze or fine-tune?

The domain is far from ImageNet, so fine-tune more layers (keep early layers or use small rates there), and consider domain-specific pre-trained models.

Follow-up 3 of 3

What's negative transfer?

When the source task is so different that pre-trained features hurt compared with training from scratch; validate against a from-scratch baseline.

#### The 30-second answer

Transfer learning reuses a model pre-trained on a large dataset. Early layers learn general features like edges and textures, later layers more task-specific ones. With little target data and a similar domain, I freeze the backbone and train a new head; with more data or a different domain, I fine-tune, starting with the head, then unfreezing from the top with a learning rate 10 to 100 times smaller, often with discriminative learning rates, keeping the original preprocessing. It massively reduces the data and compute needed, and it's how nearly all modern vision and language models are deployed.

**Go further**

#### What not to say

- "Fine-tuning with the original learning rate." It erases what was learned.

- "Always freeze everything." With enough data, fine-tuning beats frozen features.

**Key terms and sources**

Reusing a network trained on a big dataset for a new task: feature extraction (freeze and train a new head), fine-tuning (update everything, gently), which layers transfer, how much data you need, and the usual recipe · built from Yosinski et al. (NeurIPS 2014), Razavian et al. (2014), Kornblith et al. (CVPR 2019), Howard & Ruder (ACL 2018) and Devlin et al. (2019) · checked 29 Oct 2026

#### Sources

1. J. Yosinski, J. Clune, Y. Bengio & H. Lipson, "How transferable are features in deep neural networks?", NeurIPS 2014, arXiv:1411.1792.

2. A. Razavian, H. Azizpour, J. Sullivan & S. Carlsson, "CNN Features off-the-shelf: an Astounding Baseline for Recognition", CVPR Workshops 2014, arXiv:1403.6382.

3. S. Kornblith, J. Shlens & Q. Le, "Do Better ImageNet Models Transfer Better?", CVPR 2019, arXiv:1805.08974.

4. J. Howard & S. Ruder, "Universal Language Model Fine-tuning for Text Classification" (ULMFiT), ACL 2018, arXiv:1801.06146.

5. J. Devlin, M.-W. Chang, K. Lee & K. Toutanova, "BERT", NAACL 2019, arXiv:1810.04805.
