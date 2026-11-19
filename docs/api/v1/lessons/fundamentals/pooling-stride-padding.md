# Pooling, Stride, Padding and Output Shapes

> What's the output shape of this conv layer? (The interview favourite.)

- Track: Fundamentals › Deep Learning › CNNs
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/pooling-stride-padding/
- Before this: Convolution and Receptive Field (`fundamentals/convolution-and-receptive-field`)
- Quiz topic: `cnn`

## Intuition

### The situation

An interviewer gives you a conv layer's input size, kernel, stride and padding, and wants the output shape on the spot. The interviewer asks:

> How do you work out the output shape of a conv layer?

**Running example:** the dish-photo classifier from Convolution and Receptive Field. A 224×224 photo has to shrink to a handful of numbers per channel before the final "which dish?" layer; stride and pooling decide how fast.

#### Feature maps are big and expensive

A 3×3 conv with 64 channels on a 224×224 map costs about 1.8 billion multiply-adds, and keeping full resolution through 50 layers is unaffordable. We also need deep units to see large regions. Both call for downsampling, and getting the shapes right is a constant source of bugs and a favourite interview question.

### The idea

Think of a window sliding along a strip of paper. The window's size is how much it covers, the stride is how far it jumps, and padding adds a margin so the edges count. The output width is simply how many positions fit.

[Figure: The output-size formula: width plus twice the padding minus the kernel, divided by the stride, plus one. For AlexNet's first layer that gives 55.]

_The worked example comes from the lesson. Output width is the number of positions that fit._

### Play

**Try to break it.** Set a stride of 2 and a width that doesn't divide evenly, and look at the pixels never covered. Then raise the padding.

#### Move the knobs, watch the windows

One row of the input (teal), with padding cells (blue outline). Orange brackets: where the window lands. Red: input pixels no window ever covers. MACs = multiply-adds for a W×W input.

With W = 7, K = 3, stride 2 and no padding, the window lands at 3 places: output width **3**. Set W = 8 and the output is still 3, but now the last pixel is **never covered**: the formula's floor silently throws it away, a classic source of shape bugs. Add P = 1 and every pixel is used again (output 4). With stride 1 and K = 3, P = 1 is "same" padding: output = input.

**Now say why:** why does an uneven fit drop pixels, and how does padding change that?

## Maths

### Maths

#### In one breath

Three knobs set a conv layer's output size: the **kernel size** K, the **stride** S (how far the window jumps) and the **padding** P (zeros added around the border). The output width is **⌊(W + 2P − K) / S⌋ + 1**. "Same" padding (P = (K − 1)/2 with stride 1) keeps the size; "valid" (P = 0) shrinks it by K − 1. **Pooling** downsamples with a fixed rule instead of learned weights: **max pooling** keeps the strongest response in each window, **average pooling** keeps the mean. Downsampling cuts compute and grows the receptive field; **global average pooling** collapses each channel to one number before the classifier.What you'll be able to do after this: compute any conv or pooling output shape, choose padding, and count a layer's parameters and FLOPs.

#### The output-size formula

$$ W_{\text{out}} = \left\lfloor \frac{W + 2P - K}{S} \right\rfloor + 1 $$

CS231n; Dumoulin & Visin, "A guide to convolution arithmetic for deep learning", 2016 arXiv:1603.07285. Check: AlexNet's first layer, W = 227, K = 11, S = 4, P = 0 → (227 − 11)/4 + 1 = 55.

- **input size**: Width (or height) of the input feature map, W.

- **padding**: P zero pixels added on each side, so 2P in total.

- **kernel**: The window covers K pixels, so it fits at W + 2P − K + 1 positions with stride 1.

- **stride**: Jump S pixels between windows: divide by S and round down. If it doesn’t divide evenly, the last few pixels are never covered.

#### Parameters and FLOPs of a conv layer

$$ \text{params} = K^2 C_{\text{in}} C_{\text{out}} + C_{\text{out}}, \qquad \text{MACs} = K^2 C_{\text{in}} C_{\text{out}}\, H_{\text{out}} W_{\text{out}} $$

Example: 3×3, 64 → 64 channels on 224×224 with same padding: 36,928 parameters and 64·64·9·224·224 ≈ 1.85 billion multiply-adds. FLOPs are often quoted as 2 × MACs.

- **parameters**: One K × K × C_in filter per output channel, plus one bias each. Independent of the image size.

- **multiply-adds**: Every output position of every output channel does K × K × C_in multiply-adds, so compute scales with the output area. Halving the width with stride 2 cuts compute 4×.

## In practice

### In practice

#### Max vs average pooling

##### Input 4×4 (one channel)

| 1 | 3 | 2 | 0 |
|---|---|---|---|
| 5 | **6** | 1 | **4** |
| **7** | 2 | 0 | 1 |
| 3 | 1 | **8** | 2 |

##### 2×2 pool, stride 2 → 2×2

**Max:** [6, 4; 7, 8]: keeps the strongest response in each window ("is the feature present anywhere here?").

**Average:** [3.75, 1.75; 3.25, 2.75]: keeps the overall level.

- Pooling has **no parameters**, keeps the channel count, and gives some robustness to small shifts.

- Many modern CNNs replace pooling with **strided convolutions**, which learn how to downsample (Springenberg et al. 2015, "all convolutional net"); ResNet uses a stride-2 conv plus one max pool at the stem.

- **Global average pooling** averages each whole channel to one number, so a 7×7×2048 map becomes 2,048 numbers for the classifier, with no huge dense layer (Lin et al., Network in Network, 2014; used by ResNet).

To make feature maps larger again, see Image Segmentation.

### The answer that sounds right

#### "Stride 2 just halves the width"

It sounds right, and it's close. But the formula rounds down: when (W + 2P − K) doesn't divide evenly by the stride, the edge pixels are simply dropped. An interviewer asking for the exact shape wants the formula, not the rule of thumb.

## Say it

### How do you work out the output shape of a conv layer?

#### The interviewer pushes further

Follow-up 1 of 3

Input 32×32×3, conv 5×5, 16 filters, stride 1, no padding. Output and parameters?

(32 − 5)/1 + 1 = 28, so 28×28×16; parameters 5·5·3·16 + 16 = 1,216.

Follow-up 2 of 3

Why might max pooling beat average pooling?

Features are detectors; the question is usually "is it present", which max answers. Average dilutes a strong local response with background.

Follow-up 3 of 3

What does padding do besides keeping size?

Lets border pixels be the centre of a window, so edges aren't under-represented as the network deepens.

#### The 30-second answer

The output width of a conv or pooling layer is floor of W plus 2P minus K, over S, plus 1. Same padding with stride 1, P equals K minus 1 over 2, keeps the size; valid padding shrinks it by K minus 1; stride S divides it roughly by S, and if it doesn't divide evenly the edge pixels are dropped. Pooling downsamples with a fixed max or average, has no parameters, and adds some shift robustness; many modern nets use strided convolutions instead, and global average pooling before the classifier. A conv layer has K squared times C-in times C-out plus C-out parameters, and its compute scales with the output area.

**Go further**

#### What not to say

- "Pooling has weights." It has none.

- "(W − K)/S + 1" without padding or flooring: say the full formula.

**Key terms and sources**

How stride and padding control a conv layer's output size, the output-shape formula interviewers love, "same" vs "valid" padding, max vs average pooling, global average pooling, and counting parameters and FLOPs · built from Stanford CS231n notes, Dumoulin & Visin (2016), Lin et al. (2014), Springenberg et al. (2015) and Goodfellow et al. §9.3 · checked 29 Oct 2026

#### Sources

1. Stanford CS231n, Convolutional Neural Networks for Visual Recognition, course notes.

2. V. Dumoulin & F. Visin, "A guide to convolution arithmetic for deep learning", arXiv:1603.07285, 2016.

3. M. Lin, Q. Chen & S. Yan, "Network In Network", ICLR 2014, arXiv:1312.4400.

4. J. Springenberg, A. Dosovitskiy, T. Brox & M. Riedmiller, "Striving for Simplicity: The All Convolutional Net", ICLR Workshop 2015, arXiv:1412.6806.

5. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, §9.3, deeplearningbook.org.
