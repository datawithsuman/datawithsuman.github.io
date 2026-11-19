# Convolution and Receptive Field

> Why does a 3×3 filter beat a dense layer on images?

- Track: Fundamentals › Deep Learning › CNNs
- Type: Concept · 25 min
- Page: https://aimlrounds.com/tracks/fundamentals/convolution-and-receptive-field/
- Before this: From Perceptron to MLP (`fundamentals/perceptron-to-mlp`)
- Quiz topic: `cnn`

## Intuition

### The situation

You need to tag dish photos. A dense layer of 1,000 units on one 224×224 colour photo would need 150 million weights. The interviewer asks:

> Why does a 3×3 filter beat a dense layer on images?

**Running example (CNN lessons):** the delivery app tags dish photos (biryani, pizza, noodles…) uploaded by restaurants. To keep the maths visible we use a tiny 16×16 greyscale crop: the rim of a plate and the handle of a spoon.

#### Dense layers don't fit images

A 224×224 colour photo has 150,528 numbers. A dense layer with just 1,000 units would need 150 million weights, and it would have to learn "edge at the top-left" and "edge at the bottom-right" as two unrelated things. Images have structure we can exploit: nearby pixels matter together (locality), and the same pattern can appear anywhere (translation equivariance).

### The idea

Think of scanning a photo with a small stencil. You use the same stencil everywhere, so it finds an edge wherever that edge happens to be. A dense layer would have to learn a separate detector for every spot.

[Figure: A small 3 by 3 filter slides over an image grid, and each position gives one value in the output map.]

_Illustrative. Each filter produces one full output map._

### Play

**Try to break it.** Pick the vertical edges filter and slide it across the crop. Then switch to horizontal edges and compare the output, and the parameter count against a dense layer.

#### Hand-made filters on a 16×16 crop

Left: input (white = bright). Middle: the 3×3 filter. Right: the 14×14 feature map (orange = strong positive response, blue = strong negative). The orange box shows the window feeding the highlighted output.

The **vertical-edge** filter (a Sobel filter) responds on the left and right sides of the plate rim and on both sides of the spoon handle (orange where brightness rises left-to-right, blue where it falls), and stays near zero on flat areas. Switch to **horizontal edges** and the top and bottom of the rim light up instead; the spoon handle almost disappears. The whole layer has **10 parameters**. A dense layer mapping the same 256 pixels to 196 outputs needs **50,372**, and it would have to learn the edge detector separately at every position. In a real CNN, nobody hand-designs these filters: they are learned, and the first layer of trained networks ends up looking much like these edge and colour detectors.

**Now say why:** how does one small filter do a job that would take a dense layer so many weights?

## Maths

### Maths

#### In one breath

A **convolution** slides a small grid of weights (a **filter** or kernel, e.g. 3×3) across the image and, at every position, takes the dot product with the patch underneath, producing a **feature map**. The same weights are used at every position (**weight sharing**), and each output only looks at a small neighbourhood (**local connectivity**), so a conv layer needs a tiny fraction of a dense layer's parameters and detects a pattern wherever it appears. Stacking layers grows the **receptive field**, the patch of the original image an output can see: early layers find edges, deeper ones find textures, parts and whole objects.What you'll be able to do after this: compute a convolution by hand, count a conv layer's parameters, and calculate the receptive field of a stack of layers.

#### Slide, multiply, add

$$ y_{i,j} = \sum_{u=0}^{K-1}\sum_{v=0}^{K-1} w_{u,v}\;x_{i+u,\,j+v} + b $$

Strictly this is cross-correlation (true convolution flips the filter); deep learning libraries use this form and still call it convolution. Goodfellow et al. ch. 9.

- **one output value**: The feature-map value at row i, column j.

- **the filter**: A small grid of learned weights, the same at every position. With C input channels, the filter is K × K × C.

- **the patch underneath**: The K × K window of the input starting at (i, j). Multiply element-wise with the filter and add everything up, plus one bias.

#### The receptive field grows layer by layer

$$ r_l = r_{l-1} + (k_l - 1)\cdot j_{l-1}, \qquad j_l = j_{l-1}\cdot s_l, \qquad r_0 = j_0 = 1 $$

- **receptive field after layer l**: How many input pixels (along one side) can influence one unit of layer l.

- **what this layer adds**: Each layer extends the view by (kernel size − 1) steps, measured in the previous layer’s step size.

- **jump (cumulative stride)**: How far apart neighbouring units of the previous layer are in input pixels. Strides and pooling multiply it, so later layers grow the field much faster.

Bars: receptive field after each layer (C = conv, P = pool). Theoretical receptive field; in practice the centre pixels dominate (the "effective receptive field" is smaller, Luo et al. 2016).

Four 3×3 conv layers see a **9×9** patch. Two stacked 3×3 layers see 5×5, the same as one 5×5 layer, with 18 weights instead of 25 and an extra non-linearity: the reason VGG used only 3×3 filters. Add a stride-2 pool after every two convs and the same four convs see **16×16**; with 12 layers it reaches **316×316**, more than a whole 224×224 photo.

## In practice

### In practice

#### Many filters, many channels

- A layer has many filters; each produces one **output channel**. A layer from Cin to Cout channels with K×K filters has **K·K·Cin·Cout + Cout** parameters.

- AlexNet's first layer: 96 filters of 11×11×3 → 96·11·11·3 + 96 = **34,944** parameters, producing a 55×55×96 output (CS231n). Without weight sharing, every one of the 290,400 output units would need its own 363 weights: over 100 million.

- Trained first-layer filters look like oriented edge and colour-blob detectors; deeper layers respond to textures, then object parts (Zeiler & Fergus 2014; Yosinski et al. 2014).

- **1×1 convolutions** mix channels at each pixel without looking at neighbours: cheap "dense layers per pixel" used to shrink channel counts (Inception, ResNet bottlenecks).

For how these ideas shaped real models, see CNN Architectures.

### The answer that sounds right

#### "Just flatten the image and use a dense layer"

It sounds simple, and a dense layer can in principle learn anything. But on a 224×224 colour photo, 1,000 units already need 150 million weights. It also has to learn "edge at the top-left" and "edge at the bottom-right" as two unrelated things, because it ignores the fact that nearby pixels belong together.

## Say it

### Why does a 3×3 filter beat a dense layer on images?

#### The interviewer pushes further

Follow-up 1 of 3

Is a CNN translation invariant?

Convolution is translation _equivariant_ (shift the input, the feature map shifts). Pooling and global pooling add some invariance, but strided CNNs are not perfectly shift-invariant.

Follow-up 2 of 3

Why 3×3 filters?

Two 3×3 layers cover a 5×5 view with fewer weights (18 vs 25 per channel pair) and an extra non-linearity; three cover 7×7 with 27 vs 49 (VGG, Simonyan & Zisserman 2015).

Follow-up 3 of 3

What does a 1×1 convolution do?

Mixes channels at each pixel: a per-pixel dense layer, used to reduce or expand channel depth cheaply.

#### The 30-second answer

A convolution layer slides small learned filters over the input and takes a dot product with each local patch, producing one feature map per filter. Weights are shared across positions and each output is connected only to a local neighbourhood, so it has far fewer parameters than a dense layer, K times K times C-in times C-out plus biases, and it detects a pattern wherever it appears. Early layers learn edges and colours, deeper layers textures and parts. Stacking layers grows the receptive field, by kernel size minus one times the cumulative stride per layer, and downsampling makes it grow much faster.

**Go further**

#### What not to say

- "Each filter has K×K weights." It has K×K×Cin (it spans all input channels).

- "The receptive field is the kernel size." It accumulates over all layers below.

**Key terms and sources**

What a convolution layer computes, why weight sharing and local connections make it so efficient for images, how filters become edge and texture detectors, channels, and how the receptive field grows with depth · built from LeCun et al. (1998), Krizhevsky et al. (2012), Zeiler & Fergus (2014), Luo et al. (2016), Goodfellow et al. ch. 9 and Stanford CS231n notes · checked 29 Oct 2026

#### Sources

1. Y. LeCun, L. Bottou, Y. Bengio & P. Haffner, "Gradient-based learning applied to document recognition", _Proc. IEEE_ 86(11), 1998.

2. A. Krizhevsky, I. Sutskever & G. Hinton, "ImageNet Classification with Deep Convolutional Neural Networks", NeurIPS 2012.

3. M. Zeiler & R. Fergus, "Visualizing and Understanding Convolutional Networks", ECCV 2014, arXiv:1311.2901.

4. W. Luo, Y. Li, R. Urtasun & R. Zemel, "Understanding the Effective Receptive Field in Deep Convolutional Neural Networks", NeurIPS 2016, arXiv:1701.04128.

5. K. Simonyan & A. Zisserman, "Very Deep Convolutional Networks for Large-Scale Image Recognition" (VGG), ICLR 2015, arXiv:1409.1556.

6. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, ch. 9; Stanford CS231n, Convolutional Neural Networks notes.
