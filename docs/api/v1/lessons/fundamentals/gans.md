# GANs

> Why are GANs so hard to train?

- Track: Fundamentals › Deep Learning › Representation and generative models
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/gans/
- Before this: From Perceptron to MLP (`fundamentals/perceptron-to-mlp`)
- Quiz topic: `genm`

## Intuition

### The situation

You need realistic delivery times to load-test the app, and real ones have two peaks, at about 25 and 45 minutes. A teammate trains a GAN, and it only ever produces the 25-minute kind. The interviewer asks:

> How does a GAN learn, and why is it so hard to train?

**Running example:** to test the app under load, we want to **generate realistic delivery times**. Real deliveries have two peaks: about 25 minutes (nearby orders) and about 45 minutes (far away or rush hour). A 1-D example keeps every quantity exactly computable.

#### Generate new samples that look real

We want a model that produces new delivery times (or images, or voices) that look like they came from the real distribution, without writing down that distribution. For images, "looks real" is hard to measure with a fixed loss: squared error rewards blurry averages (VAEs). The GAN idea: learn the loss too, as a classifier that spots fakes.

### The idea

Think of a forger and an inspector. The inspector learns to spot fakes, and the forger learns only from the inspector's reaction, never from the real paintings. If the inspector rejects everything with total confidence, the forger learns nothing about what to change.

[Figure: Noise goes into the generator, which makes fakes. Fakes and real data go to the discriminator, which says real or fake. The discriminator's reaction goes back to the generator, which never sees real data directly.]

_After training, you keep only the generator._

### Play

**Try to break it.** Click far away, covers one peak, wide, covers both, and between the peaks. Then drag the mean yourself, and watch the JSD and its gradient.

#### What the optimal discriminator sees

Teal: real delivery times, ½·N(25, 4²) + ½·N(45, 5²). Orange: the generator, a single Gaussian N(μ, σ²). Green dashed: the optimal discriminator D*(x) (0 to 1). All values computed exactly by numerical integration over 0–120 minutes.

Put the generator **far away** (μ = 80): D* is 1 on the real data and 0 on the fakes, the JSD sits at its maximum **ln 2 ≈ 0.693**, and its gradient with respect to μ is essentially **zero**. The generator gets no signal about which direction to move, the vanishing-gradient problem Arjovsky & Bottou (2017) analysed. A generator that **covers one peak** scores a much lower JSD (0.21), even though it ignores half the data: KL(gen ‖ real) is only 0.66 while KL(real ‖ gen) is 5.6. A **wide** Gaussian over both peaks scores lower still (0.07), but a single Gaussian can never match two peaks exactly. Nothing in the game forces it to find the second peak, which is how **mode collapse** starts.

**Now say why:** why does the generator get almost no signal exactly when it's furthest from the data?

## Maths

### Maths

#### In one breath

A **GAN** trains two networks against each other. The **generator** turns random noise into fake samples; the **discriminator** tries to tell fake from real. Each improves by exploiting the other's weaknesses until fakes are indistinguishable. Goodfellow et al. showed that with an optimal discriminator, the generator is minimising the **Jensen–Shannon divergence** between real and generated data. In practice training is fragile: the generator can cover only a few kinds of output (**mode collapse**), and when the two distributions barely overlap the discriminator wins easily and the generator's **gradients vanish**. Tricks like the non-saturating loss and the **Wasserstein** distance help. GANs produced the first photorealistic faces (StyleGAN) and still power fast one-step generators, but diffusion models now lead on quality and diversity.What you'll be able to do after this: write the GAN objective, derive the optimal discriminator, and explain mode collapse, vanishing gradients and the WGAN fix.

#### A two-player minimax game

$$ \min_G \max_D\; \mathbb{E}_{x\sim p_{\text{data}}}\big[\log D(x)\big] + \mathbb{E}_{z\sim p_z}\big[\log\big(1 - D(G(z))\big)\big] $$

Goodfellow et al., "Generative Adversarial Nets", NeurIPS 2014 arXiv:1406.2661. For a fixed G the best discriminator is D*(x) = pdata(x) / (pdata(x) + pg(x)), and plugging it in gives the value 2·JSD(pdata, pg) − log 4, minimised exactly when pg = pdata.

- **discriminator on real data**: D outputs the probability that a sample is real. It wants D(x) close to 1 for real samples…

- **discriminator on fakes**: …and D(G(z)) close to 0 for generated ones. G takes random noise z and produces a sample.

- **min over G, max over D**: D maximises this value (classify well); G minimises it (fool D). Trained by alternating gradient steps.

## In practice

### In practice

#### Making GANs trainable

- **Non-saturating loss:** instead of minimising log(1 − D(G(z))), whose gradient is tiny when D confidently rejects fakes early in training, the generator maximises log D(G(z)). Proposed in the original paper and used almost everywhere.

- **Wasserstein GAN:** replace JSD with the earth mover's distance, which keeps a useful gradient even when distributions don't overlap: it measures _how far_ mass must move, not just whether it overlaps (Arjovsky et al. 2017). WGAN-GP enforces the needed smoothness with a gradient penalty (Gulrajani et al. 2017).

- **Architecture and training tricks:** DCGAN guidelines (strided convs, BatchNorm; Radford et al. 2016), spectral normalisation, two time-scale learning rates, progressive growing.

- **StyleGAN** (Karras et al. 2019) produced photorealistic 1024 × 1024 faces with a style-based generator.

#### GANs after diffusion

- Dhariwal & Nichol (NeurIPS 2021), "Diffusion Models Beat GANs on Image Synthesis": diffusion models surpassed the best GANs on ImageNet sample quality while covering the data better (diffusion).

- GANs remain attractive where speed matters: one forward pass per sample, versus many denoising steps. Adversarial losses are used to distil diffusion models into few-step generators and as a sharpening loss in image autoencoders (e.g. the autoencoder in Stable Diffusion).

- Evaluation: FID (Fréchet Inception Distance) compares feature statistics of real and generated images; lower is better.

### The answer that sounds right

#### "The discriminator always tells the generator where to go"

It sounds right, since that's the whole idea of the game. But with the generator far away, at a mean of 80, the JSD sits at its maximum and its gradient is essentially zero. And a generator covering only one peak scores a JSD of 0.21 while ignoring half the data, and nothing in the game forces it to find the other peak. That's how mode collapse starts.

## Say it

### How does a GAN learn, and why is it so hard to train?

#### The interviewer pushes further

Follow-up 1 of 3

What is mode collapse and how do you spot it?

The generator produces only a few kinds of output that fool the discriminator. Spot it with low diversity in samples, precision/recall metrics or clustering of outputs; mitigate with minibatch discrimination, WGAN losses or unrolled training.

Follow-up 2 of 3

Why does the non-saturating loss help?

Early on D easily rejects fakes, so log(1 − D(G(z))) is flat near D = 0; −log D(G(z)) has a large gradient there.

Follow-up 3 of 3

GAN vs VAE vs diffusion?

VAE: stable, likelihood-based, blurry. GAN: sharp and fast, unstable, mode collapse. Diffusion: stable, high quality and diversity, slower sampling.

#### The 30-second answer

A GAN trains a generator that maps noise to samples and a discriminator that classifies real versus fake, in a minimax game. With the optimal discriminator, D star equals p data over p data plus p g, the generator minimises the Jensen–Shannon divergence, which is zero only when the generated distribution equals the data. In practice training is unstable: if the distributions don't overlap the JSD saturates and gradients vanish, and the generator can collapse onto a few modes. Fixes include the non-saturating generator loss, Wasserstein GANs with gradient penalty, and spectral normalisation. GANs give fast one-step sampling and great sharpness, but diffusion models now lead on quality and diversity.

**Go further**

#### What not to say

- "The discriminator is used at inference." Only the generator is kept.

- "GAN training converges like normal training." It's a game; losses oscillate and don't directly show quality.

**Key terms and sources**

Generative adversarial networks: a generator and a discriminator in a minimax game, the optimal discriminator and the Jensen–Shannon divergence, the non-saturating loss, mode collapse and vanishing gradients, Wasserstein GANs, and where GANs stand after diffusion · built from Goodfellow et al. (NeurIPS 2014), Radford et al. (DCGAN, 2016), Arjovsky & Bottou (2017), Arjovsky et al. (WGAN, 2017), Gulrajani et al. (2017), Karras et al. (StyleGAN, 2019) and Dhariwal & Nichol (2021) · checked 29 Oct 2026

#### Sources

1. I. Goodfellow et al., "Generative Adversarial Nets", NeurIPS 2014, arXiv:1406.2661.

2. A. Radford, L. Metz & S. Chintala, "Unsupervised Representation Learning with Deep Convolutional GANs" (DCGAN), ICLR 2016, arXiv:1511.06434.

3. M. Arjovsky & L. Bottou, "Towards Principled Methods for Training Generative Adversarial Networks", ICLR 2017, arXiv:1701.04862.

4. M. Arjovsky, S. Chintala & L. Bottou, "Wasserstein GAN", ICML 2017, arXiv:1701.07875; I. Gulrajani et al., "Improved Training of Wasserstein GANs", NeurIPS 2017, arXiv:1704.00028.

5. T. Karras, S. Laine & T. Aila, "A Style-Based Generator Architecture for Generative Adversarial Networks", CVPR 2019, arXiv:1812.04948.

6. P. Dhariwal & A. Nichol, "Diffusion Models Beat GANs on Image Synthesis", NeurIPS 2021, arXiv:2105.05233.
