# ResNets and Skip Connections

> Why did deeper networks train worse, and how did ResNet fix it?

- Track: Fundamentals › Deep Learning › CNNs
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/resnets-and-skip-connections/
- Before this: Vanishing & Exploding Gradients (`fundamentals/vanishing-exploding-gradients`), Convolution and Receptive Field (`fundamentals/convolution-and-receptive-field`)
- Quiz topic: `cnn`

## Intuition

### The situation

A deeper network can always copy a shallower one, so it should never do worse. Yet a 34-layer plain CNN had higher training error than an 18-layer one on ImageNet. The interviewer asks:

> Why did deeper networks train worse, and how did ResNet fix it?

**Running example:** to see the training problem directly, we fit a wiggly curve (think: demand for dish photos across the day) with a deep, narrow network of 12 units per layer, plain vs residual, and watch the training loss.

#### Deeper should never be worse, but it was

A deeper network can always copy a shallower one: let the extra layers be the identity. So its training error should be at most as high. In practice, He et al. found a 34-layer plain CNN had **higher training error** than an 18-layer one on ImageNet. The solver simply couldn't find the identity-like solution through many non-linear layers. BatchNorm had already ruled out vanishing gradients as the main cause, so this was a new optimisation obstacle.

### The idea

Think of editing a draft instead of rewriting it from memory. Each block starts from the existing text and only adds corrections. If there's nothing to change, it leaves the text alone, while a plain layer would have to retype the whole thing perfectly.

[Figure: A residual block: the input x goes through layers to give F of x, and a shortcut carries x around them. The two are added.]

_The residual block. Learning F(x) = 0 is easy, so doing nothing is easy._

### Play

**Try to break it.** Compare plain and residual at 5 layers, then at 20 and 30.

#### Plain vs residual, same depth, same budget

40 points of a wiggly curve; tanh layers of 12 units; Adam, learning rate 0.01, 250 steps; same initialisation scale family; fixed seed. Training loss (MSE, log scale). This toy is an MLP, not a CNN; the effect is the same.

At 5 and 10 layers both networks fit the curve. At **20 layers** the plain network gets **stuck at a training loss of about 0.33** (0.31 at 30 layers): it can't fit even the training data, the degradation problem in miniature. The residual network with the same depth trains to **0.0002** at 20 layers and 0.002 at 30. Nothing about capacity changed; only the shortcut did.

**Now say why:** why does the plain network stop training as it gets deeper, when in principle it could learn at least as well?

## Maths

### Maths

#### In one breath

By 2015, stacking more layers made plain CNNs **worse even on their training data**: not overfitting, but an optimisation failure called the **degradation problem**. ResNet's fix is a **skip connection**: each block outputs x + F(x), so it only has to learn a **residual** correction F, and doing nothing (F = 0) is easy. The identity path also gives gradients a direct route back to early layers. ResNets trained to 152 layers on ImageNet (and over 1,000 on CIFAR-10), won ILSVRC 2015 with 3.57% top-5 error, and the same residual stream now runs through every transformer.What you'll be able to do after this: explain the degradation problem, draw a residual and a bottleneck block, and say why skip connections make deep nets trainable.

#### The residual block

$$ y = x + F(x;\,W) \qquad\Rightarrow\qquad \frac{\partial y}{\partial x} = I + \frac{\partial F}{\partial x} $$

When x and F(x) have different shapes (after a stride-2 block or a channel increase), the shortcut uses a 1×1 convolution, a **projection shortcut**. The deeper ResNets (50/101/152) use a **bottleneck**: 1×1 conv to shrink channels, 3×3 conv, 1×1 conv to expand, so deep blocks stay cheap.

- **identity shortcut**: The block’s input is carried around the layers unchanged and added at the end. No parameters.

- **residual branch**: Two (or three) conv + BatchNorm + ReLU layers that learn only the change to apply to x. If the best thing is to do nothing, the weights just go to zero.

- **gradient**: The derivative of the block is I + ∂F/∂x: the identity term passes the gradient straight back even when the branch’s gradient is tiny.

#### Why skip connections work

- **Easy identity:** pushing F towards zero is easier than making a stack of non-linear layers imitate the identity.

- **Gradient highway:** the I term in ∂y/∂x carries gradients straight back (vanishing gradients). He et al. (ECCV 2016) showed that keeping the shortcut a clean identity (pre-activation ResNet: BN and ReLU inside the branch) trains even better, up to 1,001 layers.

- **Smoother loss surface:** visualisations show skip connections turn chaotic, non-convex loss landscapes into smooth ones (Li et al., NeurIPS 2018).

- **Ensemble view:** a ResNet behaves like a collection of many shorter paths; deleting single blocks at test time hurts only a little (Veit et al., NeurIPS 2016).

**Results:** an ensemble of ResNets won ILSVRC 2015 classification with **3.57%** top-5 error; ResNet-152 has fewer FLOPs than VGG-19 despite being 8× deeper (He et al. 2016).

## In practice

### In practice

#### Skip connections everywhere

- **Transformers:** every attention and feed-forward sub-layer is wrapped as x + Sublayer(x) (Vaswani et al. 2017); the "residual stream" is the backbone of every LLM.

- **U-Net:** long skips from encoder to decoder carry fine detail for segmentation and diffusion models.

- **DenseNet:** concatenates (instead of adds) every earlier layer's features.

To compare with other designs, see CNN Architectures.

### The answer that sounds right

#### "Deeper networks do worse because they overfit"

It sounds right, because overfitting is the usual reason a bigger model disappoints. But the deeper plain network had higher **training** error, not just higher test error. That makes it an optimisation problem, and regularisation wouldn't have fixed it.

## Say it

### Why did deeper networks train worse, and how did ResNet fix it?

#### The interviewer pushes further

Follow-up 1 of 3

Is the degradation problem overfitting?

No: the deeper plain network had higher _training_ error, so it's an optimisation problem.

Follow-up 2 of 3

Add or concatenate?

ResNet adds (keeps width fixed, encourages refinement); DenseNet concatenates (reuses features, grows channels).

Follow-up 3 of 3

What's a pre-activation ResNet?

BN and ReLU moved inside the branch before each conv, so the shortcut path is a pure identity from input to output; it trains better at extreme depth, like pre-norm transformers.

#### The 30-second answer

Before ResNet, deeper plain networks had higher training error than shallower ones: the degradation problem, an optimisation failure rather than overfitting. ResNet adds an identity shortcut so each block computes x plus F of x and only learns a residual correction; doing nothing is easy, and the identity gives the gradient a direct path, since the block's Jacobian is I plus dF/dx. Projection shortcuts handle shape changes, and bottleneck blocks keep deep nets cheap. That let ResNets train to 152 layers and win ImageNet 2015, and the same residual pattern is the backbone of transformers.

**Go further**

#### What not to say

- "ResNets solved vanishing gradients." BatchNorm had largely handled that; ResNets solved degradation (and help gradients further).

- "Skip connections add parameters." Identity shortcuts have none.

**Key terms and sources**

The degradation problem (deeper plain networks train worse), residual blocks that learn a correction F(x) on top of an identity shortcut, bottleneck blocks, projection shortcuts, and why every modern architecture has skip connections · built from He, Zhang, Ren & Sun (CVPR 2016), He et al. (ECCV 2016, identity mappings), Veit et al. (2016), Li et al. (2018) and Vaswani et al. (2017) · checked 29 Oct 2026

#### Sources

1. K. He, X. Zhang, S. Ren & J. Sun, "Deep Residual Learning for Image Recognition", CVPR 2016, arXiv:1512.03385.

2. K. He, X. Zhang, S. Ren & J. Sun, "Identity Mappings in Deep Residual Networks", ECCV 2016, arXiv:1603.05027.

3. A. Veit, M. Wilber & S. Belongie, "Residual Networks Behave Like Ensembles of Relatively Shallow Networks", NeurIPS 2016, arXiv:1605.06431.

4. H. Li, Z. Xu, G. Taylor, C. Studer & T. Goldstein, "Visualizing the Loss Landscape of Neural Nets", NeurIPS 2018, arXiv:1712.09913.

5. A. Vaswani et al., "Attention Is All You Need", NeurIPS 2017, arXiv:1706.03762.
