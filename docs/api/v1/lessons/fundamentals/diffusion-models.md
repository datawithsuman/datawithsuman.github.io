# Diffusion Models

> How does denoising noise produce new images?

- Track: Fundamentals › Deep Learning › Representation and generative models
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/diffusion-models/
- Before this: Autoencoders and VAEs (`fundamentals/autoencoders-and-vaes`)
- Quiz topic: `genm`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 8dddadaf1c

## Intuition

### The situation

You need new delivery times with both peaks intact. GANs dropped a peak, and VAEs came out blurry. A teammate proposes diffusion. The interviewer asks:

> How does a diffusion model generate, and why does it need so many steps?

**Running example:** the same two-peaked delivery times as in GANs (nearby ≈ 25 min, far ≈ 45 min), shown in standardised units (peaks at −1.2 and +1.2) so the noise has a natural scale. A 1-D example lets us compute everything exactly.

#### Generating in one jump is hard

GANs map noise to data in a single pass but are unstable and drop modes; VAEs are stable but blurry. Diffusion splits the impossible jump "noise → photo" into hundreds of small, easy denoising steps, each of which is just a regression problem.

### The idea

Think of a photo buried under static. Adding static is easy, and you know exactly how. Removing it all in one go is close to impossible, but removing a little is a simple task. So you train a model on that small task and repeat it many times.

[Figure: Two peaks at step 0 get blurrier with added noise. By step 500 they have merged into one bump, and by step 1,000 it is pure noise. Adding noise is fixed; removing it is what the model learns.]

_Illustrative shapes, using the lesson's noise schedule with T = 1,000._

### Play

**Try to break it.** Sample with 1 step, then 3, 10 and 100. Watch how many samples get stranded between the peaks.

#### From noise to delivery times

4,000 samples start as N(0, 1) noise and are denoised with the deterministic DDIM sampler using the **exact** noise prediction for this distribution (a trained network learns an approximation of it). Teal line: real distribution; orange bars: generated samples. Fixed seed.

With a single step, the sampler can only jump to the **average** prediction, so **every** sample lands between the peaks, at delivery times that rarely happen. With 3 steps the two peaks appear but 31% of samples are still stranded in the middle. By 10 steps the samples split 48/48 with 4% in between, and with 100 steps 49/49 with 1.6%, close to the real data's 1.3%. More steps buy accuracy at the cost of more network calls: the central trade-off of diffusion sampling.

**Now say why:** this lab uses the exact noise prediction, so why does 1 step still land everything between the peaks?

## Maths

### Maths

#### In one breath

A **diffusion model** learns to generate by learning to **denoise**. The **forward process** adds a little Gaussian noise at each of T steps (e.g. 1,000) until the data becomes pure noise; it has a closed form, so any noise level can be sampled in one shot. A network is trained to look at a noisy sample and **predict the noise** that was added: a simple regression loss. To **generate**, start from pure noise and repeatedly remove the predicted noise, step by step, until a clean sample appears. Training is stable (no adversary), samples are high quality and diverse, and the cost is **many network calls per sample**, reduced by smarter samplers (DDIM), distillation and by running in a compressed **latent space** (Stable Diffusion). **Classifier-free guidance** steers generation towards a text prompt. What you'll be able to do after this: write the forward process and the training loss, explain sampling and why step count matters, and explain guidance and latent diffusion.

#### The forward process: add noise, with a closed form

$$ x_t = {\sqrt{\bar{\alpha}_t}\,x_0} + {\sqrt{1-\bar{\alpha}_t}\,\varepsilon}, \qquad \varepsilon\sim\mathcal{N}(0,I), \qquad {\bar{\alpha}_t = \textstyle\prod_{s\le t}(1-\beta_s)} $$

- **signal kept**: √ᾱ_t: how much of the original sample survives at step t. ᾱ_t is the running product of (1 − β), so it shrinks from 1 towards 0.

- **noise added**: √(1 − ᾱ_t) times standard Gaussian noise ε. Variances add up to 1, so the data ends as N(0, 1).

- **noise schedule**: DDPM used β rising linearly from 0.0001 to 0.02 over T = 1,000 steps.

Teal: the data at t = 0. Orange: the exact distribution of xt. Grey dashed: N(0, 1). Linear β schedule 10⁻⁴ → 0.02, T = 1,000.

At t = 200, 81% of the signal remains and the two peaks are still visible; by t = 500 only 28% is left and they've merged into one bump; by t = 1,000 the signal is 0.6% and the distribution is indistinguishable from pure noise.

#### Training: predict the noise

$$ {L = \mathbb{E}_{x_0,t,\varepsilon}\Big[\big\lVert {\varepsilon} - {\varepsilon_\theta\big(\sqrt{\bar\alpha_t}x_0 + \sqrt{1-\bar\alpha_t}\,\varepsilon,\; t\big)}\big\rVert^2\Big]} $$

Ho, Jain & Abbeel, NeurIPS 2020 [arXiv:2006.11239](https://arxiv.org/abs/2006.11239): with this objective DDPM reached an FID of 3.17 on CIFAR-10 (state of the art at the time). Predicting the noise is equivalent to learning the **score** ∇ log q(xt), the direction towards more likely data (Song et al., ICLR 2021).

- **true noise**: Sample a clean x₀, a random step t and noise ε; build x_t with the closed form.

- **network’s guess**: A U-Net or Transformer sees the noisy x_t and t, and predicts ε.

- **simple loss**: Mean squared error between them. That’s the whole training objective in DDPM’s simplified form.

## In practice

### In practice

#### Faster sampling, guidance, latent space

- **Fewer steps:** DDPM sampled with all 1,000 steps; DDIM (Song, Meng & Ermon, ICLR 2021) gives a deterministic sampler that works with tens of steps; distillation and consistency models cut this to a few steps or one.

- **Guidance:** classifier-free guidance (Ho & Salimans 2022) trains one model with and without the text prompt and extrapolates between the two predictions, trading diversity for prompt-faithfulness.

- **Latent diffusion:** Stable Diffusion runs diffusion in the compressed latent space of an autoencoder rather than on pixels, making high-resolution generation affordable (Rombach et al., CVPR 2022; autoencoders).

- **Beyond images:** audio, video, molecules and robot actions; recent image and video systems often use Transformer backbones (diffusion Transformers) and the closely related flow-matching objective.

#### Flow matching and consistency models

Diffusion's paths from noise to data are curved, so sampling takes many steps. Two newer ideas aim for far fewer.

$$ {X_t = tX_1 + (1-t)X_0}, \qquad {\min_v\ \mathbb{E}\big\|{(X_1 - X_0)} - v(X_t, t)\big\|^2} $$

The rectified flow form. Flow matching with optimal-transport paths is closely related.

- **a straight path**: Mix a data point X₁ and a noise point X₀ in a straight line. Here t runs from noise at 0 to data at 1.

- **the target**: The direction of that line, which stays the same along the path.

- **the training loss**: Train a network v to predict the direction. It’s plain regression, with no simulation during training.

**A worked example, with illustrative numbers.** Take noise X₀ = −1 and data X₁ = 3, at t = 0.25. Then X_t = 0.25 × 3 + 0.75 × (−1) = 0, and the target is 3 − (−1) = 4. To sample, start from noise, and follow the predicted direction in small steps. The straighter the paths, the fewer steps you need.

- **Compared with noise prediction:** the two are closely related, and differ mainly in the path and the training target. Flow matching chooses simple, straight paths.

- **Consistency models:** these learn to jump to the end of a path, so one step is enough, with more steps possible for quality. The paper reports an FID of 3.55 on CIFAR-10 in one step.

- **The trade-off:** one-step models are very fast, but several steps usually still improve quality.

Sources: [Flow Matching](https://arxiv.org/abs/2210.02747), [Rectified Flow](https://arxiv.org/abs/2209.03003) and [Consistency Models](https://arxiv.org/abs/2303.01469).

### The answer that sounds right

#### "With a good enough network, one step is enough"

It sounds right, since a perfect denoiser seems like it should finish the job. But the lab uses the exact noise prediction, and one step still puts every sample between the peaks. A single step can only jump to the average of what's possible, at delivery times that rarely happen. Getting down to a few steps takes methods built for it, like distillation and consistency models.

## Say it

### How does a diffusion model generate, and why does it need so many steps?

#### The interviewer pushes further

Follow-up 1 of 3

Why predict the noise instead of the clean image?

They're equivalent up to reparameterisation, but noise prediction gives a well-scaled target at every noise level and worked best empirically in DDPM.

Follow-up 2 of 3

Why do few-step samplers lose quality?

Each large step uses one prediction for a long stretch of the trajectory; when the best prediction is an average over several possible outputs (as in the lab), samples land between modes or look blurry.

Follow-up 3 of 3

Diffusion vs GAN?

Diffusion: stable training, better mode coverage, slow sampling. GAN: one-step, sharp, unstable, mode collapse.

#### The 30-second answer

A diffusion model defines a forward process that gradually adds Gaussian noise over T steps until data becomes pure noise; it has a closed form x_t = √ᾱ_t x₀ + √(1 − ᾱ_t) ε, so training samples a random step, noises the data, and trains a network to predict the noise with a mean-squared-error loss, which is equivalent to learning the score. Generation starts from noise and repeatedly removes the predicted noise. It's stable to train and gives high-quality, diverse samples, but needs many network evaluations, reduced with samplers like DDIM, distillation and running in a latent space as in Stable Diffusion. Classifier-free guidance steers generation to a prompt.

**Go further**

#### What not to say

- "The model learns the forward process." The forward process is fixed; only the reverse (denoiser) is learned.

- "Diffusion generates the image in one pass." It iterates over many denoising steps.

**Key terms and sources**

Generating data by learning to reverse a gradual noising process: the forward process and its closed form, training a network to predict the noise, sampling step by step, fewer-step samplers (DDIM), guidance, and latent diffusion · built from Sohl-Dickstein et al. (ICML 2015), Ho, Jain & Abbeel (DDPM, NeurIPS 2020), Song et al. (DDIM, ICLR 2021; score SDEs, ICLR 2021), Dhariwal & Nichol (2021), Ho & Salimans (2022) and Rombach et al. (CVPR 2022) · checked 29 Oct 2026

#### Sources

1. J. Sohl-Dickstein et al., "Deep Unsupervised Learning using Nonequilibrium Thermodynamics", ICML 2015, [arXiv:1503.03585](https://arxiv.org/abs/1503.03585).

2. J. Ho, A. Jain & P. Abbeel, "Denoising Diffusion Probabilistic Models", NeurIPS 2020, [arXiv:2006.11239](https://arxiv.org/abs/2006.11239).

3. J. Song, C. Meng & S. Ermon, "Denoising Diffusion Implicit Models", ICLR 2021, [arXiv:2010.02502](https://arxiv.org/abs/2010.02502); Y. Song et al., "Score-Based Generative Modeling through Stochastic Differential Equations", ICLR 2021, [arXiv:2011.13456](https://arxiv.org/abs/2011.13456).

4. J. Ho & T. Salimans, "Classifier-Free Diffusion Guidance", [arXiv:2207.12598](https://arxiv.org/abs/2207.12598), 2022.

5. R. Rombach et al., "High-Resolution Image Synthesis with Latent Diffusion Models", CVPR 2022, [arXiv:2112.10752](https://arxiv.org/abs/2112.10752).

6. P. Dhariwal & A. Nichol, "Diffusion Models Beat GANs on Image Synthesis", NeurIPS 2021, [arXiv:2105.05233](https://arxiv.org/abs/2105.05233).
