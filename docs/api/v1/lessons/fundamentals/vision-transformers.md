# Vision Transformers

> How does a Transformer process an image, and when would you use one instead of a CNN?

- Track: Fundamentals › Deep Learning › Computer vision
- Type: Concept · 15 min
- Page: https://aimlrounds.com/tracks/fundamentals/vision-transformers/
- Before this: The Transformer, End to End (`fundamentals/transformer-end-to-end`), Convolution and Receptive Field (`fundamentals/convolution-and-receptive-field`)
- Quiz topic: `cnn`

## Intuition

### The situation

Your team wants to replace a CNN image classifier with a Vision Transformer. You have 20,000 labelled images. In the first test, the ViT does noticeably worse. Someone concludes that Transformers just don't work on images. The interviewer asks:

> How does a Transformer process an image, and when would you use one instead of a CNN?

#### Why it matters

ViTs are common backbones in image models, and in the image part of multimodal LLMs. They're also a good interview test of whether you understand both CNNs and Transformers.

### The idea

Think of a jigsaw. Cut a photo into square pieces, and describe each piece with a list of numbers. Now each piece is like a word in a sentence, and any piece can look at any other right away. But nobody told the model that neighbouring pieces usually belong together, so it has to learn that from examples.

[Figure: Three steps. Cut the image into patches. Turn each into a token. Run a standard Transformer on them.]

_Less built-in knowledge means more data, or pretraining._

### Play

**Try to break it.** Halve the patch size. Then increase the image size.

#### Turn an image into tokens

Exact calculation. Colour images have 3 channels. The chart shows the patch grid.

Halve the patch size from 16 to **8**: tokens grow four times, and attention scores about 16 times. That's why finer patches and larger images get expensive so fast, and why windows like Swin's help.

**Now say why:** why does halving the patch size multiply attention scores by about 16?

## Maths

### Maths

#### In one breath

A **Vision Transformer** cuts an image into patches, turns each into a vector, and treats them like words. A 224×224 image with 16×16 patches gives 196 tokens. It has much less built-in knowledge about images than a CNN, so it needs more data to do well on its own. **DeiT** showed strong training recipes reduce this need, **Swin** uses local windows to keep cost linear in image size, and pretraining helps a lot.

#### From pixels to tokens

1. **Split:** cut the image into N = HW/P² patches of size P×P.

2. **Embed:** flatten each patch, and apply one shared linear projection to get a D-sized vector.

3. **Add a class token:** a learned extra vector, whose final state is used for classification.

4. **Add positions:** learned 1-D position embeddings, so the model knows where each patch came from.

5. **Run a standard Transformer encoder:** every patch can attend to every other from the first layer.

| Version | Layers | Width D | Heads | Parameters |
|---|---|---|---|---|
| ViT-Base | 12 | 768 | 12 | 86 million |
| ViT-Large | 24 | 1,024 | 16 | 307 million |
| ViT-Huge | 32 | 1,280 | 16 | 632 million |

##### CNN or ViT?

| | CNN | ViT |
|---|---|---|
| Built-in assumptions | Locality and translation equivariance | Very few, so it learns them from data |
| Seeing the whole image | Grows slowly with depth | From the first layer |
| With little data | Usually stronger | Needs pretraining or a strong recipe |
| Cost as images grow | Linear in pixels | Quadratic in tokens, for plain attention |

The ViT paper found that these models "do not generalize well when trained on insufficient amounts of data", while at 14 to 300 million images "large scale training trumps inductive bias".

##### What came next

- **DeiT:** trained on ImageNet alone in under 3 days on one computer, reaching 83.1% top-1 with 86 million parameters, using strong augmentation and regularisation. A distillation token, learning from a CNN teacher, took this up to 85.2%.

- **Swin:** attention within local windows, which shift between layers. Cost becomes linear in image size, and that suits detection and segmentation.

- **Self-supervised pretraining:** masked autoencoders and DINO reduce the need for labels.

#### The maths

$$ {N = \frac{HW}{P^2}}, \qquad {z_0 = [x_{\text{class}};\; x_1 E;\; \dots;\; x_N E]} + {E_{\text{pos}}} $$

From Dosovitskiy et al., Equation 1. After this, it’s a standard Transformer encoder.

- **the number of patches**: Image height and width, divided by the patch area.

- **the token sequence**: A class token, then each flattened patch multiplied by the shared projection E.

- **the positions**: A learned vector for each position, added to the tokens.

## In practice

### In practice

#### In practice

- **Use pretrained weights:** this is usually the right start, unless you have a very large dataset.

- **Changing resolution:** position embeddings are tied to a grid, so they need interpolating for a new image size.

- **Augment heavily:** ViT recipes lean on mixup, CutMix and RandAugment.

- **Dense tasks:** plain ViTs produce one coarse scale. Hierarchical designs like Swin make detection and segmentation easier.

- **Compare fairly:** ConvNeXt shows a modern CNN can match them, so test both on your data.

### The answer that sounds right

#### "ViTs always beat CNNs"

It sounds right, as they lead many benchmarks. But the ViT paper itself says they don't generalise well without enough data, and its strong results rely on 14 to 300 million images for pretraining. ConvNeXt also shows a modern CNN can match them. Use pretrained weights, and compare both.

## Say it

### How does a Transformer process an image, and when would you use one instead of a CNN?

#### The interviewer pushes further

Follow-up 1 of 3

What does a ViT lose compared with a CNN?

Built-in assumptions, namely locality and translation equivariance. Only the patch cutting and the MLPs have a little of this. So it must learn image structure from data, which is why it can do worse on small datasets unless pretrained or strongly regularised.

Follow-up 2 of 3

How would you run a trained ViT on larger images?

Keep the patch size, so you get more tokens. The learned position embeddings no longer match, so interpolate them in 2-D onto the new grid. Then fine-tune briefly if you can. Cost rises, as attention is quadratic in tokens.

Follow-up 3 of 3

What's the role of the class token?

It's a learned vector added to the sequence. Through attention, it collects information from all patches, and its final state goes to the classifier. Averaging all the patch outputs is a common alternative.

#### The 30-second answer

A Vision Transformer cuts an image into patches, flattens them, and projects each to a vector. It adds a class token and learned position embeddings, then runs a standard encoder. A 224 image with 16-pixel patches gives 196 patches. Unlike a CNN, it has little built-in knowledge of locality, so it needs more data, or strong augmentation and pretraining. Every patch can attend to all others from the first layer, but plain attention is quadratic in tokens. Swin uses shifted windows to make that linear. With limited data, I'd start from pretrained weights, and compare against a modern CNN.

**Key terms and sources**

Patches as tokens, class tokens, position embeddings, why ViT needs more data than a CNN, and how DeiT, Swin and self-supervised training responded. · checked 6 Nov 2026

#### Sources

- [Dosovitskiy et al., An Image is Worth 16x16 Words](https://arxiv.org/abs/2010.11929)

- [Touvron et al., DeiT](https://arxiv.org/abs/2012.12877)

- [Liu et al., Swin Transformer](https://arxiv.org/abs/2103.14030)

- [Liu et al., ConvNeXt](https://arxiv.org/abs/2201.03545)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
