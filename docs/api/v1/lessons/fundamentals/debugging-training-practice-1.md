# Debugging Training: Loss Won't Go Down

> Stuck loss, NaNs and a model that can't overfit 8 examples.

- Track: Fundamentals › Deep Learning › Regularisation and debugging
- Type: Interview · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/debugging-training-practice-1/
- Before this: Backpropagation Through a Network (`fundamentals/backpropagation`)
- Quiz topic: `train`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: b9461391cb

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your diagnosis out loud (most likely cause first, then how you'd confirm it), then open the answer and compare.

**The debugging recipe:** check the loss at step 0 against what random guessing should give, then make the model overfit one tiny batch, then add data, regularisation and tricks back one at a time, watching the loss and gradient norms after each change (Karpathy, “A Recipe for Training Neural Networks”, 2019).

Question 1 · Easy · loss at init

### Your 10-class image classifier starts at a loss of 2.30 and is still at 2.30 after 1,000 steps. What does 2.30 tell you, and what do you check first?

Answer: **2.30 = ln 10: the model predicts all 10 classes equally and isn't learning at all**

1. Cross-entropy for a uniform guess over K classes is ln K; ln 10 ≈ 2.303. So the starting value is perfect, but nothing has moved.

2. A loss that doesn't move at all usually means the weights aren't being updated: `optimizer.step()` not called, the optimiser built on the wrong parameters, gradients zeroed after backward instead of before, or a learning rate of 0.

3. Check: print the gradient norm and one weight before and after a step. If the weight doesn't change, it's the training loop, not the model.

**Follow-up:** What if the loss at step 0 were 9.5 instead? The initial logits are far too large (overconfident at random). Initialise the last layer smaller (or zero) so the first loss is near ln K.

Question 2 · Easy · overfit one batch

### You try to overfit a single batch of 8 examples for 500 steps and the loss stays high. Should you add more data or more regularisation?

Answer: **Neither: this is a bug in the model, loss or data pipeline**

1. Any reasonable network can memorise 8 examples. If it can't, more data or regularisation won't help.

2. Usual culprits: labels misaligned with inputs (shuffled separately), applying softmax before a loss that expects logits (`CrossEntropyLoss` already includes it), wrong label format (one-hot vs index), inputs not normalised, or a frozen layer.

3. Turn off dropout and augmentation, print a few (input, label) pairs right before the forward pass, and check the loss on a hand-computed example.

**Follow-up:** Once it can overfit one batch, what next? Train on the full training set with no regularisation and confirm training loss falls; only then add regularisation to close the train–validation gap.

Question 3 · Medium · NaN loss

### Training looks fine for 300 steps, then the loss becomes NaN. List the most likely causes and how you'd find the right one.

Answer: **Usually exploding updates or an invalid operation: too-high learning rate, log(0) or division by zero, fp16 overflow, or bad data**

1. Log the gradient norm every step. A sharp rise just before the NaN points to exploding gradients: lower the learning rate, add warmup and gradient clipping (e.g. max norm 1.0).

2. If gradients are calm, look for invalid maths: a hand-written `log(softmax(x))` (use a fused loss on logits), dividing by a std of 0, `sqrt` of a negative.

3. With mixed precision, fp16 can overflow: use loss scaling or bf16.

4. Check the batch that triggered it for NaN/inf inputs; `torch.autograd.set_detect_anomaly(True)` reports the operation that produced the NaN.

**Follow-up:** Why does a NaN in one batch ruin the whole model? One NaN gradient makes the weights NaN, and every later output becomes NaN. Skip or clip before the update, and checkpoint so you can resume.

Question 4 · Medium · imbalance

### A fraud model (5% fraud) reaches 95% accuracy in the first epoch and never improves. The loss settles at about 0.20. What's happening?

Answer: **It predicts “not fraud” for everything; 0.20 is just the entropy of the 5% base rate**

1. Predicting the base rate p = 0.05 for every example gives loss −[0.05 ln 0.05 + 0.95 ln 0.95] ≈ 0.199: exactly where it's stuck.

2. Accuracy hides it: 95% is what “always no” scores. Look at recall, precision and PR-AUC instead (class imbalance).

3. Fixes: class weights or focal loss, re-sampling, and check the features actually carry signal. Initialising the output bias to ln(0.05/0.95) ≈ −2.94 starts the model at the base rate so it doesn't waste the first steps learning it.

**Follow-up:** After reweighting, recall is high but precision is terrible. Is that a bug? No: it's the threshold. Choose the operating threshold on validation data for the cost of a missed fraud vs a false alarm.

Question 5 · Medium · learning rate

### With SGD at learning rate 0.5, the training loss drops quickly, then bounces up and down around a high value and never settles. What do you change?

Answer: **The learning rate is too high for the later phase: lower it or add a decay schedule**

1. Fast early progress then noisy bouncing is the classic sign that steps overshoot the minimum.

2. Try 10× smaller, or keep the peak but add cosine or step decay so late steps are small (learning-rate schedules).

3. For a principled start, run an LR range test: increase the learning rate exponentially over a short run and pick a value somewhat below where the loss blows up.

**Follow-up:** Loss decreases smoothly but extremely slowly. Same cure? The opposite: the learning rate is probably too small (or gradients vanish). Check per-layer gradient norms before raising it.

Question 6 · Hard · BatchNorm

### Training loss falls nicely, but when you evaluate the trained model on the same training data in eval mode, the loss is far higher. Nothing else changed. Why?

Answer: **BatchNorm's running statistics don't match the batch statistics used in training**

1. In train mode BatchNorm normalises with each batch's own mean and variance; in eval mode it uses running averages collected during training.

2. If batches are unrepresentative (data sorted by class or source, tiny batch sizes) or the running averages are stale, the eval-mode normalisation differs and outputs shift.

3. Fix: shuffle the data, use larger batches, recompute BatchNorm statistics with a pass over the training data, or switch to GroupNorm/LayerNorm for small batches (normalisation layers).

**Follow-up:** What other layer behaves differently between train and eval? Dropout: but it usually makes eval loss _lower_, not higher.

**More practice and sources**

6 interview questions, easy to hard · answers hidden until you click · checked 29 Oct 2026

Keep practising

Based on common failure modes collected in Andrej Karpathy, [“A Recipe for Training Neural Networks”](https://karpathy.github.io/2019/04/25/recipe/) (2019) and Goodfellow et al., _Deep Learning_, §11.5 (debugging strategies). Related lessons: Vanishing & Exploding Gradients, Weight Initialisation. Part 2: It Trains, But Something's Off.
