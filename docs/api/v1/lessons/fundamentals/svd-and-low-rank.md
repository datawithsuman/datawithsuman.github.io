# SVD & Low-Rank Approximation

> How LoRA and compression keep most of a matrix with a fraction of the numbers.

- Track: Fundamentals › Maths for ML › Linear algebra
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/svd-and-low-rank/
- Before this: Eigenvalues & Eigenvectors (`fundamentals/eigenvalues-and-eigenvectors`)
- Quiz topic: `la`

## Intuition

### The situation

You need to fine-tune a huge language model, and a teammate suggests training only a low-rank update to its weights. The interviewer asks:

> What is SVD, and what do you get by keeping only the top k singular values?

**Running example:** a 32 × 32 grayscale icon of a delivery scooter (1,024 pixel values), with a little random noise added, as if from a cheap camera. We compress it with the SVD and ask how many components we need, and whether dropping components can even remove noise.

#### Big matrices with little real information

A ratings matrix of 10 million users × 100,000 restaurants, a 12,288 × 12,288 weight matrix in a language model, an image: these are huge, but their content is often driven by a few underlying factors (taste profiles, dominant directions, shapes). We want to find those factors, store less, and throw away the noise. The eigendecomposition only works for square (and nicely behaved) matrices; the SVD works for **any** matrix.

### The idea

Think of a picture as a stack of transparent layers, sorted from most to least important. The first few layers give you almost the whole picture. Later layers add fine detail, and eventually mostly noise. SVD finds those layers for any matrix.

[Figure: A matrix equals a sum of layers, drawn darker for the most important layer and fainter for later layers.]

_Illustrative. Each layer is one rank-one term, and its singular value says how much it matters._

### Play

**Try to break it.** Slide the rank up from 1 and watch the error against the clean icon. Keep going all the way to 32.

#### Keep k singular values

Left: noisy image and its rank-k reconstruction. Right: the singular values, kept in teal.

The first singular value alone carries 74% of the energy; five carry 96%. Error against the noisy image falls steadily to zero at k = 32 (you reproduce the noise exactly). Error against the **clean** icon is lowest around k = 8 (13%, below the 18.7% error of the noisy image itself) and then rises again as later components add noise back. Truncation is a denoiser: the signal lives in a few strong directions, the noise is spread thinly over all of them.

**Now say why:** why does the error against the clean icon stop falling and then rise, even as you keep more of the image?

## Maths

### Maths

#### In one breath

**Every** matrix, any shape, can be written as A = UΣVᵀ: a rotation, a stretch along perpendicular axes, and another rotation. The stretches, the **singular values** σ₁ ≥ σ₂ ≥ …, say how important each direction is. Keep only the top k and you get the **best possible rank-k approximation** of A (Eckart–Young), stored in k(m + n + 1) numbers instead of m × n. Real data is often nearly low-rank, so a small k captures most of it and drops noise. That idea is PCA (SVD of centred data), matrix-factorisation recommenders (users × items ≈ low-rank), and LoRA (fine-tune a huge weight matrix by learning a rank-r update BA). What you'll be able to do after this: describe the three factors of the SVD, explain rank-k truncation and its error, compute the storage saving, and connect it to PCA, recommenders and LoRA.

#### The decomposition

$$ {A} = {U}\,{\Sigma}\,{V^{\top}} = {\textstyle\sum_{i} \sigma_i\, u_i v_i^{\top}} $$

MML §4.5. The singular values are the square roots of the eigenvalues of AᵀA, and V's columns are its eigenvectors (Eigenvalues).

- **any m × n matrix**: Our 32 × 32 image, or a users × items ratings table.

- **left singular vectors**: Orthonormal columns: the output-side directions (column patterns of the image).

- **singular values**: A diagonal of non-negative stretches σ₁ ≥ σ₂ ≥ … ≥ 0: how much each direction matters.

- **right singular vectors**: Orthonormal columns: the input-side directions (row patterns).

- **a sum of rank-1 layers**: Equivalently, A is a sum of simple outer products σᵢ uᵢ vᵢᵀ, each a rank-1 “layer”, from most to least important.

#### The best rank-k approximation

$$ {A_k = \textstyle\sum_{i=1}^{k} \sigma_i u_i v_i^{\top}}, \qquad {\lVert A - A_k\rVert_F = \sqrt{\textstyle\sum_{i>k} \sigma_i^2}}, \qquad {k(m + n + 1)} $$

C. Eckart & G. Young, "The approximation of one matrix by another of lower rank", _Psychometrika_, 1936; MML Theorem 4.25.

- **rank-k approximation**: Keep the first k terms of the sum.

- **its error**: Frobenius distance to A: exactly the root-sum-of-squares of the dropped singular values. No other rank-k matrix does better.

- **what you store**: k columns of U, k of V and k singular values: k(m + n + 1) numbers. For our 32 × 32 image and k = 5: 325 instead of 1,024.

#### LoRA: fine-tune with a rank-r update

$$ h = {W_0}\,x + {B}\,{A}\,x $$

Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models", Eq. 3 [p. 4](https://arxiv.org/pdf/2106.09685#page=4).

- **frozen pretrained weights**: A d × k matrix, never updated.

- **d × r**: Trainable, initialised to zero so training starts from the pretrained model.

- **r × k**: Trainable, random Gaussian initialisation. With r ≪ d, B and A together have r(d + k) parameters instead of d·k.

The authors hypothesise that the change in weights during fine-tuning has a low "intrinsic rank". On GPT-3 175B, LoRA "can reduce the number of trainable parameters by 10,000 times and the GPU memory requirement by 3 times" compared with full fine-tuning with Adam [abstract](https://arxiv.org/abs/2106.09685), and "a very low rank (i.e., r in Figure 1 can be one or two) suffices even when the full rank (i.e., d) is as high as 12,288" [p. 2](https://arxiv.org/pdf/2106.09685#page=2). Because BA has the same shape as W₀, it can be merged after training: no extra inference latency.

#### SVD and eigendecomposition, and very large matrices

##### How they connect

- **Scope:** eigendecomposition needs a square matrix, and may need complex numbers. SVD works for any matrix, and always gives real values.

- **The link:** AᵀA = VΣ²Vᵀ. So A's right singular vectors are the eigenvectors of AᵀA, and its eigenvalues are the squared singular values.

- **When they match:** for a symmetric positive semi-definite matrix, SVD and eigendecomposition are the same.

- **PCA:** for centred data X with n rows, the eigenvalues of the covariance matrix are σ²/(n − 1). Libraries often use the SVD of X, which avoids forming XᵀX and squaring its condition number.

##### Randomised SVD

A full SVD is too slow for very large matrices, and you usually only want the top k directions. So multiply A by a small random matrix, which captures most of its top directions with high probability. Then run an exact SVD on that much smaller matrix. With fast-decaying singular values, this gets close to the true result at far lower cost.

Next: the pseudoinverse uses SVD to solve systems with no ordinary inverse, and norms define the error sizes used here.

## In practice

### In practice

#### SVD across ML

- **PCA:** the SVD of the centred data X = UΣVᵀ gives the principal components (rows of Vᵀ) and variances σ²/(n − 1) (PCA).

- **Recommenders:** approximate the users × items ratings matrix by user factors × item factors of rank k (matrix factorisation, popularised by the Netflix Prize). Missing ratings need special solvers (alternating least squares, SGD), not plain SVD.

- **Latent semantic analysis:** truncated SVD of a term–document matrix finds topics.

- **Pseudo-inverse and least squares:** the SVD gives the stable solution to linear regression even when XᵀX is singular.

- **Model compression:** replace a big weight matrix by its rank-k factors to save memory and compute.

### The answer that sounds right

#### "Compress by keeping a subset of rows or pixels"

Dropping rows, columns or pixels throws away specific parts of the data. The SVD instead keeps the most important _patterns_ spread across all pixels. And there's a guarantee no ad-hoc scheme has: among all rank-k matrices, the truncated SVD is closest to A (Eckart–Young, 1936), with error equal to the root sum of squares of the dropped singular values.

#### Caveats

- Full SVD costs O(min(mn², m²n)); for big matrices use randomised or truncated SVD (`TruncatedSVD`, `svds`).

- Low rank works only if the data really is close to low rank; a full-rank weight change (e.g. a new language) needs larger r, as the LoRA authors note.

- Singular vectors are directions of variance, not guaranteed to be interpretable features.

## Say it

### What is SVD, and what do you get by keeping only the top k singular values?

#### The interviewer pushes further

Follow-up 1 of 3

SVD vs eigendecomposition?

Eigendecomposition needs a square matrix and may not exist or be orthogonal; SVD exists for every matrix and always has orthonormal factors. Singular values of A are square roots of eigenvalues of AᵀA.

Follow-up 2 of 3

How does PCA use SVD?

Centre X, compute its SVD; the right singular vectors are the principal directions and σ²/(n − 1) the variances. It avoids forming the covariance matrix and is more stable.

Follow-up 3 of 3

Why does LoRA work?

Fine-tuning updates appear to have low intrinsic rank; a rank-r update BA with r ≪ d captures most of it, cutting trainable parameters and optimizer memory, and it can be merged into W₀ at inference.

#### The 30-second answer

The singular value decomposition writes any matrix as UΣVᵀ: orthonormal input directions, non-negative singular values, and orthonormal output directions, or equivalently a sum of rank-one layers ordered by importance. Keeping the top k gives the best rank-k approximation in Frobenius norm, by the Eckart–Young theorem, with error equal to the root sum of squares of the dropped singular values, and storage of k(m + n + 1) numbers. It underlies PCA, matrix-factorisation recommenders, latent semantic analysis and LoRA, which fine-tunes a large model by learning a low-rank update BA.

**Go further**

#### What not to say

- "SVD only works on square matrices." It works on any shape.

- "Keeping more components is always better." Against noisy data, too many components reproduce the noise.

**Key terms and sources**

The singular value decomposition, rank-k truncation and the Eckart–Young theorem, compression and denoising, and how low rank powers PCA, recommenders and LoRA · built from Deisenroth et al., _Mathematics for Machine Learning_ (ch. 4), Eckart & Young (1936) and Hu et al., "LoRA" (2021) · checked 28 Oct 2026

#### Key terms

| Term | Meaning |
|---|---|
| **SVD** | A = UΣVᵀ for any matrix. |
| **Singular value** | Non-negative stretch σᵢ; importance of a direction. |
| **Rank** | Number of non-zero singular values. |
| **Truncated SVD** | Keep the top k terms. |
| **Eckart–Young** | Truncated SVD is the best rank-k approximation. |

#### Sources

1. M. P. Deisenroth, A. A. Faisal & C. S. Ong, _Mathematics for Machine Learning_, CUP 2020, [mml-book.github.io](https://mml-book.github.io/) (ch. 4.5–4.6).

2. C. Eckart & G. Young, "The approximation of one matrix by another of lower rank", _Psychometrika_ 1, 1936.

3. E. Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models", ICLR 2022, [arXiv:2106.09685](https://arxiv.org/abs/2106.09685).

The icon is generated procedurally with fixed-seed noise; the SVD is computed live in your browser (Jacobi eigen-decomposition of AᵀA).
