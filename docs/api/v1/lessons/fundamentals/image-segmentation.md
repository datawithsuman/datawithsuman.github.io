# Image Segmentation

> How do networks label every pixel, and how do you measure and train them?

- Track: Fundamentals › Deep Learning › Computer vision
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/fundamentals/image-segmentation/
- Before this: CNN Architectures: AlexNet to ConvNeXt (`fundamentals/cnn-architectures`), Pooling, Stride, Padding and Output Shapes (`fundamentals/pooling-stride-padding`)
- Quiz topic: `cnn`

## Intuition

### The situation

A model that outlines tumours on scans reports 99% accuracy. Doctors say it's useless, as it misses most tumours. The tumours cover about 1% of each scan. The interviewer asks:

> How do networks label every pixel, and how do you measure and train them?

#### Why it matters

Medical scans, documents, road scenes and photo editing all need pixel-level results. The ideas here also travel: U-Net is the usual backbone in diffusion models. It extends detection from boxes to exact shapes.

### The idea

Think of tracing a map. First, zoom out to understand what the region is. Then, zoom back in to draw the exact borders. If you only had the zoomed-out view, your borders would be rough. So you keep the detailed version beside you. That's what a skip connection does.

[Figure: Three tasks. Semantic labels each pixel by class. Instance separates each object. Panoptic does both.]

_Encoder-decoders with skips recover the fine detail._

### Play

**Try to break it.** Tick predict background. Then make the object larger.

#### Why pixel accuracy lies

An illustrative 48×30 pixel image. Grey: predicted only. Orange: true object only. Green: both. Exact calculation.

Tick **predict background**: pixel accuracy barely falls, while IoU and Dice collapse to 0. Now make the object larger, and keep the same shift. The same mistake hurts IoU much less. That's why small objects are hard to score well on.

**Now say why:** why does pixel accuracy barely change when the object is missed?

## Maths

### Maths

#### In one breath

Segmentation labels every pixel. **Semantic** gives a class per pixel, **instance** separates each object, and **panoptic** does both. Most models shrink an image to understand it, then enlarge it back, with **skip connections** restoring fine detail, as in **U-Net**. **Transposed convolutions** enlarge, and **dilated convolutions** see more without shrinking. Don't trust pixel accuracy: when a target is small, predicting all background can score very high. Use **IoU** or **Dice**.

#### Tasks and tools

| Task | Output | Two people in a photo |
|---|---|---|
| **Semantic** | A class for each pixel | One "person" region |
| **Instance** | A mask per object | Two separate masks |
| **Panoptic** | Both together | Two masks, plus labels for sky and road |

##### Key models

| Model | Idea | A reported result |
|---|---|---|
| **FCN** | All convolutional, so any image size works. Skips are added. | 62.2% mean IoU on VOC 2012. |
| **U-Net** | Contracting and expanding paths, with skips by concatenation. | Trains from very few images. IoU of 92% in a cell tracking challenge. |
| **DeepLab** | Dilated filters at several rates (ASPP). | 79.7% mean IoU on VOC 2012. |
| **Mask R-CNN** | Adds a mask branch to Faster R-CNN. | Instance segmentation at 5 frames a second. |
| **SAM** | Returns masks for a prompt: points, a box or a mask. | Predicts 3 masks per prompt, to handle ambiguity. |

##### Why skip connections?

Shrinking keeps the meaning, but loses the exact location. Skips bring fine detail straight across to the matching decoder layer. FCN adds the features, and U-Net concatenates them.

##### Making images larger

A **transposed convolution** broadcasts each input through the kernel, so the output gets bigger. It's a learned way to upsample. Its output size is S(n − 1) + K − 2P. So a common choice of K = 4, S = 2, P = 1 exactly doubles the size. It can produce checkerboard patterns, so many models resize first, then apply a normal convolution.

##### Seeing more without shrinking

A **dilated (atrous) convolution** spaces out its filter weights. A 3×3 filter at rate 2 covers a 5×5 area with just 9 weights, and the output keeps its resolution.

##### Why pixel accuracy misleads

If a tumour covers 1% of a scan, predicting "no tumour" everywhere scores 99%. It's the class imbalance problem, at pixel level. IoU and Dice ignore true negatives, so that prediction scores 0. Mean IoU averages across classes.

#### The maths

$$ {\mathrm{Dice}} = \frac{2\,{|A \cap B|}}{{|A| + |B|}} = {\frac{2\,\mathrm{IoU}}{1 + \mathrm{IoU}}}, \qquad {\mathrm{Dice}_{\text{soft}} = \frac{2\sum_i p_i g_i}{\sum_i p_i^2 + \sum_i g_i^2}} $$

The soft form is from the V-Net paper. Training usually uses 1 − Dice, often combined with cross-entropy.

- **Dice**: A score from 0 to 1 for how well two masks agree.

- **the overlap**: Pixels in both the prediction and the truth.

- **the two sizes**: Total pixels in the prediction, plus those in the truth.

- **its link to IoU**: They always rank a single prediction the same way, and Dice is never lower.

- **the soft version for training**: Uses predicted probabilities p, so it can be trained with gradients.

## In practice

### In practice

#### In practice

- **Combine losses:** cross-entropy plus Dice is a common start, especially with small targets.

- **Pretrain the encoder:** a pretrained backbone helps a lot when you have few labelled images.

- **Augment image and mask together:** the same flip or crop must apply to both.

- **Report by class:** a good mean can hide a failing rare class, and rare classes are often the point.

- **Consider labelling cost:** pixel labels are expensive. Prompted tools like SAM can speed this up, but check their output.

### The answer that sounds right

#### "99% pixel accuracy means the model is great"

It sounds right, as nearly every pixel is correct. But most pixels are background, so predicting nothing also scores about 99%. Use IoU or Dice for each class, which ignore true negatives. Look at results for small objects, and at actual examples, too.

## Say it

### How do networks label every pixel, and how do you measure and train them?

#### The interviewer pushes further

Follow-up 1 of 3

What's the output shape of a transposed convolution?

S(n − 1) + K − 2P. For n = 16, K = 4, S = 2 and P = 1, that's 30 + 4 − 2 = 32, so it doubles. For K = 2, S = 2, P = 0, it's 30 + 2 = 32, which doubles too.

Follow-up 2 of 3

U-Net adds skips by concatenating. Why not add, as in ResNet?

Concatenating keeps fine encoder features separate, and lets later layers decide how to use them. Adding is cheaper, but it mixes the two. Both work: FCN adds, U-Net concatenates, and concatenation costs more channels.

Follow-up 3 of 3

Dice is 0.8. What's the IoU?

IoU = Dice / (2 − Dice) = 0.8 / 1.2 ≈ 0.67. They rank a single prediction the same way, but averages over many images can rank models differently.

#### The 30-second answer

Segmentation labels every pixel. Semantic gives classes, instance separates objects, and panoptic does both. Most models use an encoder-decoder. The encoder shrinks the image to understand it, and the decoder enlarges it, with skip connections restoring detail, as in U-Net. Dilated convolutions see more context without losing resolution. Mask R-CNN adds a mask branch to a detector for instances. I wouldn't use pixel accuracy, because small targets make predicting background look great. I'd use IoU or Dice by class, and train with cross-entropy plus Dice.

**Key terms and sources**

Semantic, instance and panoptic segmentation, FCN, U-Net, transposed and dilated convolutions, Mask R-CNN, SAM, and Dice and IoU. · checked 6 Nov 2026

#### Sources

- [Long et al., FCN](https://arxiv.org/abs/1411.4038)

- [Ronneberger et al., U-Net](https://arxiv.org/abs/1505.04597)

- [Chen et al., DeepLab](https://arxiv.org/abs/1606.00915)

- [He et al., Mask R-CNN](https://arxiv.org/abs/1703.06870)

- [Kirillov et al., Panoptic Segmentation](https://arxiv.org/abs/1801.00868)

- [Kirillov et al., Segment Anything](https://arxiv.org/abs/2304.02643)

- [Milletari et al., V-Net](https://arxiv.org/abs/1606.04797)

- [D2L on transposed convolution](https://d2l.ai/chapter_computer-vision/transposed-conv.html)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
