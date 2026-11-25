# CNN Architectures: AlexNet to ConvNeXt

> How did CNN architectures evolve, and what idea did each one add?

- Track: Fundamentals › Deep Learning › CNNs
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/cnn-architectures/
- Before this: ResNets and Skip Connections (`fundamentals/resnets-and-skip-connections`)
- Quiz topic: `cnn`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: 95fb74285f

## Intuition

### The situation

You're choosing a backbone for an image model. One colleague wants the newest large model, and another says it must run on a cheap phone. A third asks why anyone still uses 1×1 convolutions. The interviewer asks:

> How did CNN architectures evolve, and what idea did each one add?

#### Why it matters

Interviewers often ask how you'd choose a backbone, or what a 1×1 convolution is for. These ideas also explain trade-offs you'll meet in production: accuracy against memory, latency and battery. This builds on convolutions and ResNets.

### The idea

Think of how buildings developed. Each new design solved one problem: taller frames, lifts, lighter materials. You don't need to memorise every building, just what each one made possible. CNNs are similar: each famous model added one idea that later ones kept.

[Figure: Three ideas that changed CNNs. Skip connections allowed depth. Depthwise separable filters cut cost. Compound scaling grew models in balance.]

_Each architecture is one idea, plus a trade-off._

### Play

**Try to break it.** Raise the channels out, N. Then change the feature map size.

#### What does separating cost?

Exact calculation, using the MobileNet formulas. Weights leave out biases.

Raise N, and the saving approaches K². Raise K to **7**, and it's up to about 49 times, which is why large depthwise filters are affordable in ConvNeXt. Change F: both costs move together, so the saving stays the same.

**Now say why:** why doesn't the saving depend on the size of the feature map?

## Maths

### Maths

#### In one breath

Each famous CNN added one idea. **VGG:** stack small 3×3 filters. **Inception:** run filter sizes in parallel, and shrink channels with 1×1 convolutions. **ResNet:** add skip connections. **DenseNet:** reuse all earlier features. **MobileNet:** split a convolution in two, for about 8 to 9 times less compute. **EfficientNet:** scale depth, width and resolution together. **ConvNeXt:** borrow Transformer design choices, and stay a pure CNN.

#### One idea per architecture

| Model | Year | The idea | A reported result |
|---|---|---|---|
| **AlexNet** | 2012 | A deep CNN on GPUs, with ReLU and dropout. | 15.3% top-5 error, winning ImageNet 2012. |
| **VGG** | 2014 | Only 3×3 filters, up to 19 layers. | 7.0% top-5 for a single net, with 138 to 144 million parameters. |
| **Inception** | 2014 | Parallel filter sizes, and 1×1 convolutions to cut cost. | 22 layers, 12 times fewer parameters than AlexNet. 6.67% with an ensemble. |
| **ResNet** | 2015 | Skip connections. | 152 layers, 11.3 billion FLOPs against VGG-19's 19.6. 3.57% with an ensemble. |
| **DenseNet** | 2016 | Each layer receives all earlier feature maps. | L(L + 1)/2 direct connections for L layers. |
| **MobileNet** | 2017 | Depthwise separable convolutions. | 70.6% top-1 at 569 million multiply-adds, against 71.7% at 4,866 million. |
| **EfficientNet** | 2019 | Scale depth, width and resolution together. | 84.3% top-1 for B7, with 66 million parameters. |
| **ConvNeXt** | 2022 | A ResNet modernised using Transformer design choices. | 82.1% top-1 for its smallest version, on ImageNet-1K. |

Figures come from each paper, and they use different test setups, so don't compare them directly.

##### Why a 1×1 convolution helps

It mixes channels at each pixel, and can reduce their number. Inception uses this before its 3×3 and 5×5 filters, so those filters have fewer channels to process.

##### Depthwise separable convolutions

A normal convolution does two jobs at once: it looks at neighbouring pixels, and it mixes channels. MobileNet separates them:

- **Depthwise:** one K×K filter per input channel, with no mixing between channels.

- **Pointwise:** a 1×1 convolution that mixes the channels.

It has less capacity for the same channel count, and that's why accuracy falls slightly.

##### Compound scaling

Scaling only one dimension soon gives diminishing returns. A larger image needs more layers to see it, and more channels for its finer patterns. EfficientNet scales all three using one number φ, keeping compute growth at about 2φ.

##### What ConvNeXt changed

Its authors began with ResNet-50, and applied Transformer choices step by step: a different stage ratio, a patch-like 4×4 stem, 7×7 depthwise filters, GELU and a single LayerNorm. Top-1 accuracy rose from 78.8% at the stage-ratio step to 81.5% at the LayerNorm step. Much of the gap between CNNs and Transformers came from these design and training choices.

#### The maths

$$ {\underbrace{K^2 M N F^2}_{\text{standard}}} \;\to\; {\underbrace{K^2 M F^2}_{\text{depthwise}}} + {\underbrace{M N F^2}_{\text{pointwise}}}, \qquad {\text{ratio} = \frac{1}{N} + \frac{1}{K^2}} $$

From the MobileNet paper, Equations 2 and 5 and the ratio after them.

- **a standard convolution**: Filter size K, M channels in, N channels out, on an F×F map.

- **depthwise**: One K×K filter per input channel. This handles space.

- **pointwise**: A 1×1 convolution from M channels to N. This handles channels.

- **the saving**: Separable cost divided by standard cost. With K = 3, it’s about 1/9 if N is large.

## In practice

### In practice

#### In practice

- **Start from a pretrained backbone:** a well-known model is usually better than a new design.

- **Choose by constraint:** measure latency, memory and accuracy on your real device. FLOPs alone can mislead, because memory access matters too.

- **Phones and edge devices:** MobileNet-style models are the usual start. Width and resolution multipliers let you trade accuracy for speed.

- **Training recipes matter:** a better recipe can change results as much as a new architecture, so compare models under the same recipe.

- **CNN or Transformer:** with limited data, CNNs are a safe start. See Vision Transformers.

### The answer that sounds right

#### "The newest model is always the best choice"

It sounds right, as results keep improving. But published scores assume particular data, training recipes and hardware. With limited data or a cheap device, an older, well-understood backbone can do better in your setting. Measure accuracy, latency and memory on your own problem.

## Say it

### How did CNN architectures evolve, and what idea did each one add?

#### The interviewer pushes further

Follow-up 1 of 3

Why is a depthwise separable convolution cheaper?

It splits the work. Depthwise filters handle space, one per channel, and a 1×1 convolution mixes channels. The cost ratio is 1/N + 1/K². With 3×3 filters, that's about 8 to 9 times cheaper. The trade-off is less capacity, and a small loss in accuracy.

Follow-up 2 of 3

Why stack two 3×3 filters instead of using one 5×5?

They see the same 5×5 area with 18 weights rather than 25, per channel pair, and they add an extra non-linearity. That was the main insight in VGG.

Follow-up 3 of 3

You need image classification on a low-end phone. What would you do?

Start with a pretrained MobileNet-style model. Tune the width and resolution multipliers against measured latency on the actual device. Then consider quantisation. I'd also measure memory, as FLOPs alone won't predict real speed.

#### The 30-second answer

Each architecture added one idea. VGG stacked small 3×3 filters. Inception ran filter sizes in parallel, using 1×1 convolutions to cut cost. ResNet added skip connections, so very deep networks could train. MobileNet split a convolution into depthwise and pointwise parts, which is about 8 to 9 times cheaper with 3×3 filters. EfficientNet scaled depth, width and resolution together. ConvNeXt showed that a CNN with Transformer-style design choices competes with Transformers. In practice, I'd start from a pretrained backbone, and choose by accuracy, latency and memory on the real device.

**Key terms and sources**

AlexNet, VGG, Inception, ResNet, DenseNet, MobileNet, EfficientNet and ConvNeXt: the one idea each added, and how depthwise separable convolutions cut cost. · checked 6 Nov 2026

#### Sources

- [Krizhevsky et al., AlexNet (2012)](https://papers.nips.cc/paper_files/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html)

- [Simonyan and Zisserman, VGG](https://arxiv.org/abs/1409.1556)

- [Szegedy et al., Inception](https://arxiv.org/abs/1409.4842)

- [He et al., ResNet](https://arxiv.org/abs/1512.03385)

- [Huang et al., DenseNet](https://arxiv.org/abs/1608.06993)

- [Howard et al., MobileNets](https://arxiv.org/abs/1704.04861)

- [Tan and Le, EfficientNet](https://arxiv.org/abs/1905.11946)

- [Liu et al., ConvNeXt](https://arxiv.org/abs/2201.03545)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
