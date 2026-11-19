# Debugging Training: It Trains, But Something's Off

> 99.8% accuracy, a slow GPU and a model that fails in production.

- Track: Fundamentals › Deep Learning › Regularisation and debugging
- Type: Interview · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/debugging-training-practice-2/
- Before this: Debugging Training: Loss Won't Go Down (`fundamentals/debugging-training-practice-1`)
- Quiz topic: `train`

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your diagnosis out loud (most likely cause first, then how you'd confirm it), then open the answer and compare.

**The question to ask every time:** is this a real property of the model, or an artefact of how I measured it? Check the split, the mode (train vs eval), the metric, and whether training and serving see the same inputs.

Question 1 · Easy

### For the whole run, your validation loss is lower than your training loss. Is something broken?

Answer: **Usually not: dropout, augmentation and epoch averaging make training loss look worse**

1. Training loss is computed with dropout and augmentation on, a handicapped model on harder inputs; validation runs the full model on clean data.

2. Training loss is often averaged over the epoch while the model improved during it; validation is measured at the end.

3. Only suspect a problem if the gap is huge or appears with regularisation off: then check for an easier validation set or duplicated examples.

**Follow-up:** How would you confirm? Evaluate the training set in eval mode at the same moment as validation; the two should then be comparable.

Question 2 · Easy · too good

### On your first attempt at a hard medical-image task you get 99.8% validation accuracy. What do you check before celebrating?

Answer: **Data leakage between training and validation**

1. Same patient (or user, or session) in both splits: images of one patient are near-duplicates. Split by patient, not by image.

2. Exact or near duplicates across splits: hash or embed images and look for close pairs.

3. A feature that encodes the label (scanner type used only for sick patients, a timestamp, an ID), or preprocessing fit on all data before splitting.

4. Sanity check: train with shuffled labels; if validation is still high, the evaluation is leaking.

**Follow-up:** Which split strategy for time-series data? Split by time: train on the past, validate on the future (cross-validation & leakage).

Question 3 · Medium · fine-tuning

### You fine-tune a pre-trained BERT on 5,000 labelled reviews with Adam at learning rate 1e-3. Training loss spikes in the first steps, and the result is worse than a simple baseline. What went wrong?

Answer: **The learning rate is far too high for fine-tuning: it wrecks the pre-trained weights**

1. Pre-trained weights are already good; large updates destroy them (catastrophic forgetting). 1e-3 is a from-scratch learning rate.

2. Typical BERT fine-tuning uses AdamW with peak learning rates of 2e-5 to 5e-5, a short warmup, then linear decay.

3. With little data, also try freezing the encoder first and training only the head, then unfreezing (transfer learning).

**Follow-up:** Validation accuracy peaks after epoch 2 and then drops. Why? Small fine-tuning sets overfit quickly: use early stopping and only a few epochs.

Question 4 · Medium · offline vs prod

### Your model scores 92% offline but users report bad predictions in production. The model file is identical. Where do you look?

Answer: **Training–serving skew: production inputs differ from what the model saw in training**

1. Preprocessing differs: normalisation statistics recomputed on live data, a different tokenizer version, images in BGR instead of RGB, a resize with different interpolation.

2. The model runs in train mode in production (dropout on, BatchNorm using batch stats).

3. Features computed differently online than in the offline pipeline, or data drift since training.

4. Debug: log raw production inputs, replay them through the offline pipeline, and compare the model inputs and outputs value by value.

**Follow-up:** How do you prevent it? Share one preprocessing code path between training and serving, version it with the model, and monitor input distributions in production.

Question 5 · Medium · slow training

### Training is much slower than expected and the GPU shows about 20% utilisation. What's the likely bottleneck?

Answer: **The input pipeline: the GPU is waiting for data**

1. Data loading, decoding and augmentation on too few CPU workers can't keep up. Increase `num_workers`, enable `pin_memory` and prefetching, cache decoded data.

2. Tiny batches leave the GPU underused; raise the batch size if memory allows (and rescale the learning rate: batch size).

3. Hidden synchronisation: calling `.item()` or printing a GPU tensor every step forces the CPU to wait for the GPU.

4. Confirm with a profiler, or time a loop over the data loader alone.

**Follow-up:** GPU at 100% but still slow? Then compute is the limit: try mixed precision (bf16), a fused optimiser, a smaller model or lower-resolution inputs.

Question 6 · Hard · loss vs accuracy

### Validation accuracy keeps improving, but validation loss started rising several epochs ago. Which do you trust, and what is happening?

Answer: **Both are right: the model is getting more answers right but becoming overconfident on the ones it gets wrong**

1. Accuracy only checks the top class; log loss also measures confidence. One wrong prediction at 99.9% confidence costs −ln(0.001) ≈ 6.9 alone, enough to dominate the average.

2. So the model is overfitting in confidence (poor calibration) while still improving its rankings.

3. Pick the checkpoint by the metric you deploy on. If calibrated probabilities matter (ranking, thresholds, risk), fix it with label smoothing, temperature scaling or earlier stopping (early stopping & label smoothing).

**Follow-up:** How do you measure calibration directly? A reliability diagram and expected calibration error (ECE): bin predictions by confidence and compare each bin's average confidence with its accuracy.

**More practice and sources**

6 interview questions, easy to hard · answers hidden until you click · checked 29 Oct 2026

Keep practising

Based on Andrej Karpathy, “A Recipe for Training Neural Networks” (2019), Devlin et al., BERT (NAACL 2019) fine-tuning settings, and Sculley et al., “Hidden Technical Debt in Machine Learning Systems” (NeurIPS 2015) on training–serving skew. Part 1: Loss Won't Go Down.
