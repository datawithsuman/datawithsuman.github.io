# Loss Functions for Deep Learning

> Why is cross-entropy the classifier loss, not MSE?

- Track: Fundamentals › Deep Learning › Neural network basics
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/loss-functions/
- Before this: From Perceptron to MLP (`fundamentals/perceptron-to-mlp`), Maximum Likelihood & MAP (`fundamentals/mle-and-map`)
- Quiz topic: `nn`

## Intuition

### The situation

Your model says 2% chance of late for an order that was late, and it barely gets corrected. You're training with squared error on the probability. The interviewer asks:

> Why is cross-entropy the classifier loss, not MSE?

**Running example:** the delivery network outputs p = the predicted probability that an order is late (classification), and a second head predicts the delivery time in minutes (regression).

#### The loss decides what "better" means

The network will do exactly what the loss rewards. If the loss barely changes when the model says "2% chance of late" for an order that was late, the model gets no push to fix it. If one 2-hour delivery in the training set dominates the loss, the model bends every prediction towards it. The loss has to match the output type and the kind of mistakes you care about, and it has to give useful gradients.

### The idea

Think of two teachers marking a student who was confidently wrong. One takes off a limited number of marks and moves on. The other marks it harder the more confident the student was. Cross-entropy is the second teacher, so the biggest mistakes get the strongest correction.

[Figure: Penalty against the predicted probability for an order that was late. Cross-entropy shoots up as the prediction approaches zero. Squared error levels off at one.]

_Illustrative. The two curves show the penalty for a single late order._

### Play

**Try to break it.** Drag the predicted chance of late down towards zero, and compare the gradients. Then raise the focal loss γ.

#### One late order: how hard does each loss push?

Curves: loss vs predicted probability for a late order (y = 1). Gradients are with respect to the logit z (what the network actually updates through); negative = "raise p".

At p = 0.05 (confidently wrong) the cross-entropy gradient is **−0.95** while MSE's is only **−0.09**, ten times weaker. Drag p to 0.01 and MSE's push shrinks to −0.02 while cross-entropy's stays near −1. Focal loss with γ = 2 behaves like cross-entropy on this hard example, but at p = 0.9 (an easy, already-correct case) its loss is **about 100× smaller** than cross-entropy's, so easy examples stop dominating the total.

**Now say why:** why does the MSE gradient fade just when the model is most wrong?

## Maths

### Maths

#### In one breath

The loss turns "how wrong was this prediction" into one number, and its **gradient** is what training actually follows. For classification, use **cross-entropy** (log loss): it's the negative log-likelihood, and with a sigmoid or softmax output its gradient with respect to the logit is simply **p − y**, large when confidently wrong. MSE on probabilities has a gradient that **vanishes** exactly when the model is confidently wrong. For regression, **MSE** predicts the mean and punishes outliers quadratically, **MAE** predicts the median and shrugs them off, and **Huber** is quadratic for small errors and linear for big ones. **Focal loss** down-weights easy examples so a rare class gets attention. What you'll be able to do after this: pick a loss for a task, explain why cross-entropy beats MSE for classifiers, and explain what MSE, MAE, Huber and focal loss each optimise.

#### Cross-entropy: the default for classifiers

$$ {L_{\mathrm{CE}} = -\big[y\ln p + (1-y)\ln(1-p)\big]}, \qquad {\frac{\partial L_{\mathrm{CE}}}{\partial z} = p - y} $$

For K classes with softmax, L = −ln ptrue and ∂L/∂zk = pk − yk. Minimising it is maximum likelihood (MLE & MAP) and equals minimising KL to the labels (entropy & KL). In PyTorch, pass logits to `BCEWithLogitsLoss` / `CrossEntropyLoss`, which fuse the sigmoid/softmax for numerical stability.

- **binary cross-entropy**: Minus the log of the probability given to what actually happened. If the order was late and p = 0.02, loss = −ln 0.02 ≈ 3.9; if p = 0.9, loss ≈ 0.11.

- **gradient w.r.t. the logit**: With p = σ(z), the derivative of the loss with respect to the logit z is just p − y: proportional to how wrong the prediction is, never saturating.

#### Focal loss: down-weight what's already easy

$$ L_{\mathrm{focal}} = -\,{\alpha}\,{(1-p_t)^{\gamma}}\,\ln p_t $$

Lin, Goyal, Girshick, He & Dollár, "Focal Loss for Dense Object Detection" (RetinaNet), ICCV 2017 [arXiv:1708.02002](https://arxiv.org/abs/1708.02002): a one-stage detector faces ~100k candidate boxes per image, almost all easy background; focal loss let it match two-stage detectors. For tabular imbalance, also see class imbalance.

- **modulating factor**: (1 − p)^γ is near 0 for easy examples (p close to 1) and near 1 for hard ones, so the loss focuses on mistakes. γ = 0 gives plain cross-entropy; the paper used γ = 2.

- **class weight**: An optional α balances positives vs negatives, as in weighted cross-entropy.

To see this in use, read Object Detection.

## In practice

### In practice

#### MSE, MAE and Huber: what each one predicts

Nine normal deliveries (24–38 min) plus one outlier. Each loss's best single prediction is found by minimising the total loss over the ten deliveries.

With a 180-minute outlier, MSE's best guess jumps to **45.9 min**, later than every normal delivery, because squaring makes the one outlier dominate. MAE stays at the median, **31.5 min**, whatever the outlier does. Huber with δ = 5 lands at **31.8 min**: robust like MAE, but smooth near zero like MSE. Drag the outlier to 300 minutes: MSE moves to 57.9, the other two don't move at all. Rule of thumb: MSE when big errors are truly costly and data is clean, MAE or Huber when there are outliers or heavy tails.

#### Cheat sheet

| Task | Output | Loss |
|---|---|---|
| Binary classification | 1 logit → sigmoid | binary cross-entropy (optionally weighted / focal) |
| Multi-class (one label) | K logits → softmax | categorical cross-entropy (optionally label smoothing) |
| Multi-label | K logits → K sigmoids | binary cross-entropy per label |
| Regression | linear output | MSE (mean), MAE (median), Huber (robust), quantile loss (any quantile) |
| Language modelling | vocab logits | next-token cross-entropy |
| Embeddings / retrieval | vectors | contrastive (InfoNCE) or triplet loss |

### The answer that sounds right

#### "Use MSE on the probability"

MSE on p gives L = (p − y)², and through the sigmoid its gradient is 2(p − y)·p(1 − p). When the model is confidently wrong (p ≈ 0 for a late order), the factor p(1 − p) ≈ 0, so the gradient vanishes exactly when the model most needs to learn. Goodfellow et al. (§6.2.2) note that MSE and MAE often give poor results with gradient-based training for exactly this reason: saturating outputs give very small gradients. See it in the Play lab, in the Intuition tab.

## Say it

### Why is cross-entropy the classifier loss, not MSE?

#### The interviewer pushes further

Follow-up 1 of 3

Why pass logits instead of probabilities to the loss?

Computing log(sigmoid(z)) separately can underflow to log(0) = −∞ for large |z|. Fused versions use the log-sum-exp trick and are numerically stable.

Follow-up 2 of 3

What does MSE assume?

Minimising MSE is maximum likelihood under Gaussian noise with constant variance; MAE corresponds to Laplace noise.

Follow-up 3 of 3

When would you use quantile loss?

When you need a percentile, e.g. "promise a delivery time that's met 90% of the time": the pinball loss with τ = 0.9 estimates the 90th percentile.

#### The 30-second answer

For classification I use cross-entropy on logits: it's the negative log-likelihood, it heavily penalises confident mistakes, and with sigmoid or softmax the gradient on the logits is just predicted minus true, so it never saturates. MSE on probabilities has a gradient that vanishes when the model is confidently wrong. For regression, MSE estimates the conditional mean and is sensitive to outliers, MAE estimates the median and is robust, and Huber combines the two. For heavy class imbalance or many easy negatives, I'd use class weights or focal loss, which down-weights easy examples.

**Go further**

#### What not to say

- "Accuracy as a loss." It isn't differentiable; train on cross-entropy, report accuracy.

- "MSE and cross-entropy are interchangeable for classifiers." They differ sharply in gradients.

**Key terms and sources**

Cross-entropy vs MSE for classification, MSE vs MAE vs Huber for regression, focal loss for imbalance, and how the loss shapes the gradient · built from Goodfellow et al. §6.2, Huber (1964), Lin et al. (2017) and the PyTorch loss documentation · checked 29 Oct 2026

#### Sources

1. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, §6.2, [deeplearningbook.org](https://www.deeplearningbook.org/).

2. P. Huber, "Robust estimation of a location parameter", _Annals of Mathematical Statistics_ 35(1), 1964.

3. T.-Y. Lin, P. Goyal, R. Girshick, K. He & P. Dollár, "Focal Loss for Dense Object Detection", ICCV 2017, [arXiv:1708.02002](https://arxiv.org/abs/1708.02002).

4. PyTorch documentation, [BCEWithLogitsLoss](https://docs.pytorch.org/docs/stable/generated/torch.nn.BCEWithLogitsLoss.html) and [HuberLoss](https://docs.pytorch.org/docs/stable/generated/torch.nn.HuberLoss.html).
