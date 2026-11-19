# Autoencoders and VAEs

> How does a VAE turn compression into generation?

- Track: Fundamentals › Deep Learning › Representation and generative models
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/autoencoders-and-vaes/
- Before this: Embeddings and Representation Learning (`fundamentals/embeddings`), Entropy, Cross-Entropy & KL Divergence (`fundamentals/entropy-cross-entropy-kl`)
- Quiz topic: `genm`

## Intuition

### The situation

The app stores 64-pixel icons of dishes. A teammate trains an autoencoder that redraws them well, then feeds it random codes to get new icons, and gets garbage. The interviewer asks:

> Why can't a plain autoencoder generate, and what does a VAE change?

**Running example:** the app stores thumbnail icons of dishes: 8 × 8 = 64 pixels each, showing a plate, a cup or a fork in slightly different positions. Can a few numbers describe each icon, and can we generate new, plausible icons?

#### Learn structure without labels

Most data is unlabelled. Yet 64-pixel icons don't fill the 64-dimensional space: they are a few shapes in a few positions. If a network can describe each icon with a handful of numbers and still redraw it, it has learned that structure. That gives compression, denoising, anomaly detection (bad reconstructions = unusual inputs) and, with a VAE, a way to generate new examples.

### The idea

Think of describing an icon over the phone with a few numbers. A plain autoencoder only learns the codes it has seen, with empty space between them. A VAE gives each icon a small fuzzy region and packs those regions around the centre, so any point you pick means something.

[Figure: Left: an autoencoder's codes form separate clumps with empty space between them, so a random code decodes to garbage. Right: a VAE's codes are overlapping regions packed around the centre, so any code decodes to something plausible.]

_Illustrative, in two dimensions. The dashed circle is the prior, N(0, I)._

### Play

**Try to break it.** Set the bottleneck to 1, then 3, then 12. Watch the reconstructions and the share of variance lost.

#### How many numbers does an icon need?

180 icons (plates, cups, forks, shifted by up to 1 pixel, with noise), fixed seed. The optimal **linear** autoencoder for each k (computed with SVD, i.e. PCA). Top row: originals; bottom row: reconstructions from k numbers.

With **k = 1** every reconstruction is a blur of all three shapes (84% of the pixel variance lost). At **k = 3** the plate, cup and fork are already told apart from 3 numbers instead of 64, even though 63% of the variance is still lost, mostly the 1-pixel shifts and noise, which a linear code handles badly. By k = 12 only 19% is lost, and the rest is largely noise that a bottleneck is supposed to throw away. A plain autoencoder only learns to compress; nothing makes its code space orderly, so a random code usually decodes to garbage. That's the gap the VAE closes.

**Now say why:** at 3 numbers, why can you tell the shapes apart even though most of the variance is still lost?

## Maths

### Maths

#### In one breath

An **autoencoder** squeezes each input through a narrow **bottleneck** (the encoder) and rebuilds it (the decoder), trained only to make the output match the input. To succeed it must keep the most important structure in a few numbers: a learned compression. A **linear** autoencoder learns exactly the same subspace as PCA. But a plain autoencoder's latent space has gaps, so picking a random code rarely decodes to anything sensible. A **VAE** fixes that: the encoder outputs a **mean and variance**, a code is **sampled** from it (via the **reparameterisation trick**), and a **KL penalty** pulls every code distribution towards a standard normal. The latent space becomes smooth and filled, so sampling z ~ N(0, I) and decoding generates new data.What you'll be able to do after this: explain the bottleneck, connect linear autoencoders to PCA, and write and interpret the VAE loss.

#### Encode, squeeze, decode

$$ z = f_{\text{enc}}(x) \in \mathbb{R}^{k}, \qquad \hat{x} = f_{\text{dec}}(z), \qquad L = \lVert x - \hat{x}\rVert^2 $$

Baldi & Hornik (1989): a linear autoencoder with squared error learns the same subspace as PCA (PCA; SVD). Hinton & Salakhutdinov (_Science_ 2006) showed deep non-linear autoencoders compress far better than PCA. Denoising autoencoders (Vincent et al. 2008) corrupt the input and learn to recover the clean version.

- **encoder**: A network that maps the 64-pixel input to a k-dimensional code z, with k much smaller than 64.

- **decoder**: Maps the code back to 64 pixels.

- **reconstruction loss**: How far the output is from the input, e.g. mean squared error. No labels needed: the input is its own target.

#### The variational autoencoder

$$ \mathcal{L} = \mathbb{E}_{q(z\mid x)}\big[\log p(x\mid z)\big] - \mathrm{KL}\big(q(z\mid x)\,\Vert\,\mathcal{N}(0,I)\big), \qquad z = \mu + \sigma\odot\varepsilon $$

Kingma & Welling, "Auto-Encoding Variational Bayes", ICLR 2014 arXiv:1312.6114; Rezende, Mohamed & Wierstra (2014). The objective is the evidence lower bound (ELBO) on log p(x); training maximises it. For Gaussians the KL term has a closed form (below). KL itself: entropy & KL.

- **encoder outputs a distribution**: For each input, a mean μ and a standard deviation σ for every latent dimension: a little Gaussian cloud instead of a single point.

- **reparameterisation**: Sample z = μ + σ·ε with ε ~ N(0, 1). The randomness is in ε, so gradients flow through μ and σ (Kingma & Welling 2014).

- **reconstruction term**: Decode z and score how well it reproduces x (log-likelihood, e.g. squared error).

- **KL term**: How far each code cloud is from the standard normal prior. It pulls clouds towards the origin and stops σ from shrinking to zero, filling the space.

One latent dimension. Teal: the encoder's q(z | x) = N(μ, σ²); grey: the prior N(0, 1). KL = ½(μ² + σ² − 1 − ln σ²).

With μ = 1.5 and σ = 0.3 the KL is **1.87 nats** (1.13 from the off-centre mean, 0.75 from the narrow width): the code sits off-centre and is too narrow. Set μ = 0 and σ = 1 and it's exactly **0**, but then the code carries no information about the input. Training balances the two terms: enough information to reconstruct, close enough to the prior that the space has no holes. β-VAE (Higgins et al. 2017) weights the KL by β > 1 for more disentangled codes.

## In practice

### In practice

#### Autoencoders and VAEs today

- **Generation:** VAE samples tend to be blurry (squared error averages over possibilities), so GANs and then diffusion models took over image generation.

- **Latent diffusion:** Stable Diffusion runs diffusion inside the compressed latent space of an autoencoder trained with a mild KL term, about 48× fewer numbers than the 512 × 512 × 3 image (Rombach et al. 2022).

- **Anomaly detection:** train on normal data; inputs that reconstruct badly are flagged (anomaly detection).

- **Representation learning:** masked autoencoders (MAE) pre-train vision Transformers by reconstructing hidden image patches.

### The answer that sounds right

#### "An autoencoder is a generative model"

It sounds right, since it has a decoder that produces images. But nothing makes a plain autoencoder's code space orderly, so a random code usually decodes to garbage. The VAE's KL term is what fixes that, so you can't drop it as optional regularisation. Without it, you just have a noisy autoencoder.

## Say it

### Why can't a plain autoencoder generate, and what does a VAE change?

#### The interviewer pushes further

Follow-up 1 of 3

Why is the reparameterisation trick needed?

You can't backpropagate through a random sampling step. Writing z = μ + σ·ε moves the randomness into ε, which doesn't depend on the parameters.

Follow-up 2 of 3

What's posterior collapse?

A powerful decoder ignores z, the KL drives q(z|x) to the prior, and the code carries no information. Fixes: KL annealing, weaker decoders, free bits.

Follow-up 3 of 3

Why are VAE samples blurry?

A Gaussian likelihood (squared error) rewards predicting the average of plausible outputs, which looks blurry.

#### The 30-second answer

An autoencoder compresses an input to a low-dimensional code and reconstructs it, trained only on reconstruction error, so it learns the data's main structure without labels; a linear one learns the PCA subspace. Its latent space isn't organised, so you can't sample from it. A VAE makes the encoder output a Gaussian, mean and variance, samples the code with the reparameterisation trick z = μ + σ·ε so gradients flow, and maximises the ELBO: reconstruction log-likelihood minus the KL from the code distribution to a standard normal. The KL keeps the latent space smooth and filled, so sampling from N(0, I) and decoding generates new data. VAEs are blurrier than diffusion models but their autoencoders underpin latent diffusion.

**Go further**

#### What not to say

- "An autoencoder is a generative model." A plain one isn't: sampling random codes doesn't work reliably.

- "The KL term is regularisation you can drop." Without it, the VAE is just a noisy autoencoder.

**Key terms and sources**

Compressing data through a bottleneck and reconstructing it; what a linear autoencoder learns (PCA); denoising autoencoders; and the variational autoencoder: an encoder that outputs a distribution, the reparameterisation trick, and the ELBO with its reconstruction and KL terms · built from Hinton & Salakhutdinov (Science 2006), Baldi & Hornik (1989), Vincent et al. (2008), Kingma & Welling (ICLR 2014), Rezende et al. (2014), Higgins et al. (β-VAE, 2017) and Rombach et al. (2022) · checked 29 Oct 2026

#### Sources

1. P. Baldi & K. Hornik, "Neural networks and principal component analysis: learning from examples without local minima", _Neural Networks_ 2, 1989.

2. G. Hinton & R. Salakhutdinov, "Reducing the Dimensionality of Data with Neural Networks", _Science_ 313, 2006.

3. P. Vincent, H. Larochelle, Y. Bengio & P.-A. Manzagol, "Extracting and composing robust features with denoising autoencoders", ICML 2008.

4. D. Kingma & M. Welling, "Auto-Encoding Variational Bayes", ICLR 2014, arXiv:1312.6114.

5. I. Higgins et al., "β-VAE: Learning Basic Visual Concepts with a Constrained Variational Framework", ICLR 2017.

6. R. Rombach, A. Blattmann, D. Lorenz, P. Esser & B. Ommer, "High-Resolution Image Synthesis with Latent Diffusion Models", CVPR 2022, arXiv:2112.10752.
