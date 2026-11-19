# Early Stopping and Label Smoothing

> When should training stop, and why soften the labels?

- Track: Fundamentals › Deep Learning › Regularisation and debugging
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/early-stopping-and-label-smoothing/
- Before this: The Bias–Variance Trade-off (`fundamentals/bias-variance`)
- Quiz topic: `train`

## Intuition

### The situation

Your training loss keeps falling, but somewhere along the way the model started memorising noise and getting overconfident. The interviewer asks:

> When should training stop, and why soften the labels?

**Running example:** the same 60 noisy delivery orders and 64-unit network as Dropout, trained for 1,500 steps, with 400 separate orders as the validation set. Later: a dish classifier that predicts one of 10 cuisines.

#### How long should we train?

Too few steps and the model underfits; too many and it memorises the noise. The right number depends on the data, model and learning rate, so it can't be fixed in advance. Training also pushes the model towards 100% confidence: with one-hot targets, cross-entropy is only zero when the correct logit is infinitely larger than the others.

### The idea

Think of revising for an exam from a practice paper with a few typos. Past a point, you're memorising the typos, so you stop and go back to your best day. And a teacher who never claims 100% certainty keeps you from being overconfident, which is what label smoothing does.

[Figure: Training loss keeps falling. Validation loss falls, reaches a low point and rises. A marker at the low point shows the checkpoint to keep.]

_Illustrative. Patience sets how long you wait before stopping._

### Play

**Try to break it.** Compare no early stopping with a patience of 4 and of 20. Read where the best checkpoint is, and where training stopped.

#### Training loss keeps falling, validation loss doesn't

One check = 25 steps. Teal: training loss; orange: validation loss (400 orders). Green line: best checkpoint; grey line: where training stops.

Validation loss is lowest at step **125** (0.48), then climbs to **1.43** by step 1,500 while training loss heads to almost zero. Without early stopping you keep the last model and pay a 3× worse validation loss. With patience 4, training stops at step 225 and restores the step-125 checkpoint. Patience 20 trains longer (step 625) but still keeps the same best model; it only wastes compute. Too little patience is the real risk: noisy validation curves can trigger a stop before the true minimum.

**Now say why:** why do you restore the best checkpoint instead of keeping the last one?

## Maths

### Maths

#### In one breath

Training loss keeps falling for as long as you train, but **validation loss** usually falls, bottoms out, then rises as the network starts memorising. **Early stopping** watches validation loss, waits a set number of checks (the **patience**) for an improvement, then stops and restores the **best checkpoint**. **Label smoothing** replaces the one-hot target with 1 − ε for the true class and spreads ε over all classes, so the best possible logit is finite instead of infinite. It reduces overconfidence and improves calibration; the catch is that a smoothed teacher is a worse teacher for distillation.What you'll be able to do after this: set up early stopping with patience and checkpoints, compute a smoothed target, and explain the trade-offs of both.

#### Label smoothing

$$ y^{\mathrm{LS}}_k = \begin{cases}1-\varepsilon+\varepsilon/K & k = \text{true}\\ \varepsilon/K & \text{otherwise}\end{cases} \qquad \Delta z^{*} = \log\frac{1-\varepsilon+\varepsilon/K}{\varepsilon/K} $$

Introduced in Inception-v3 (Szegedy et al., CVPR 2016) with ε = 0.1, now a common default. In PyTorch: `CrossEntropyLoss(label_smoothing=0.1)`.

- **true class**: Gets 1 − ε plus its share of the spread: 1 − ε + ε/K. With ε = 0.1 and 10 classes, that is 0.91.

- **every other class**: Each gets ε/K, e.g. 0.01. The model is now rewarded for leaving a little probability on other classes.

- **best logit gap**: The optimal difference between the correct logit and the others becomes finite: log((1 − ε + ε/K) / (ε/K)). Without smoothing it is infinite.

"Best confidence" = the predicted probability for the true class that minimises the smoothed cross-entropy (it equals the smoothed target).

With 10 classes and ε = 0.1 the target for the true class is **0.91**, the best logit gap is **4.51**, and the loss is minimised at 91% confidence, so the network has no reason to blow its logits up. Set ε = 0 and the gap becomes infinite: the loss always wants more confidence.

## In practice

### In practice

#### Early stopping with patience

1. Every few steps (or each epoch), compute the validation loss.

2. If it's the best so far, **save a checkpoint**.

3. If it hasn't improved for **patience** checks in a row, stop.

4. **Restore the best checkpoint**, not the last one.

Goodfellow et al. §7.8 show that for a simple quadratic model, early stopping behaves like L2 regularisation: the number of steps × learning rate plays the role of 1/λ. Prechelt (1998) studied stopping criteria and the trade-off between training time and final error.

### The answer that sounds right

#### What label smoothing helps and hurts

- **Helps:** generalisation and calibration; Müller, Kornblith & Hinton (NeurIPS 2019) show it improves calibration and beam search in translation arXiv:1906.02629.

- **Hurts distillation:** a teacher trained with label smoothing makes a worse teacher, because smoothing pulls same-class examples into tight clusters and erases information about which other classes an example resembles.

- **Interacts with mixup**, which already softens targets; use one or tune both.

- **Early stopping** needs a validation set the model never trains on, and a metric that matches what you care about (loss vs accuracy can bottom out at different steps).

For more on teachers and students, see Distillation.

## Say it

### When should training stop, and why soften the labels?

#### The interviewer pushes further

Follow-up 1 of 3

Why restore the best checkpoint instead of keeping the last?

By the time patience runs out, the model has trained "patience" checks past its best point and may already be overfitting.

Follow-up 2 of 3

Validation loss rises but validation accuracy still improves. Stop?

Rising loss with stable accuracy means growing overconfidence on wrong predictions. Choose the metric you deploy on; often track both and keep the checkpoint with the best target metric.

Follow-up 3 of 3

What's ε for 2 classes with label_smoothing = 0.1?

Targets become 0.95 and 0.05 (1 − 0.1 + 0.1/2 and 0.1/2).

#### The 30-second answer

Early stopping monitors validation loss during training, saves the best checkpoint, and stops once it hasn't improved for a patience number of checks, then restores the best weights. It's a free regulariser and roughly acts like L2. Label smoothing replaces one-hot targets with 1 minus epsilon on the true class and epsilon over K on every class, typically epsilon 0.1, so the optimal logits are finite and the model can't become 100% confident; it improves calibration and often accuracy, but teachers trained with it distil worse, and it overlaps with mixup.

**Go further**

#### What not to say

- "Stop when training loss stops decreasing." It's validation loss that matters.

- "Label smoothing adds noise to labels." It's deterministic softening, not random flipping.

**Key terms and sources**

Two cheap regularisers: stop training when validation loss stops improving (and keep the best checkpoint), and soften one-hot targets so the model can't push its confidence to 100% · built from Prechelt (1998), Goodfellow et al. §7.8, Szegedy et al. (2016), Müller, Kornblith & Hinton (NeurIPS 2019) and the PyTorch `CrossEntropyLoss` docs · checked 29 Oct 2026

#### Sources

1. L. Prechelt, "Early Stopping – But When?", in _Neural Networks: Tricks of the Trade_, Springer 1998.

2. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, §7.8, deeplearningbook.org.

3. C. Szegedy, V. Vanhoucke, S. Ioffe, J. Shlens & Z. Wojna, "Rethinking the Inception Architecture for Computer Vision", CVPR 2016, arXiv:1512.00567.

4. R. Müller, S. Kornblith & G. Hinton, "When Does Label Smoothing Help?", NeurIPS 2019, arXiv:1906.02629.

5. PyTorch documentation, torch.nn.CrossEntropyLoss.
