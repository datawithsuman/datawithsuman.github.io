# Deep Learning Practice

> Shapes, parameters, attention cost and IoU: can you work them out by hand?

- Track: Fundamentals › Deep Learning › Representation and generative models
- Type: Interview · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/deep-learning-practice/
- Before this: Multi-Head Attention (`fundamentals/multi-head-attention`), Pooling, Stride, Padding and Output Shapes (`fundamentals/pooling-stride-padding`)
- Quiz topic: `genm`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-19 · Version: a8bb93f79d

How to use this page

Give yourself about 5 minutes per question, as in an interview. Say your approach out loud, then open the answer and compare the method, not just the number.

**Tools for this page:** write out the shape at each step, and remember that a dense layer costs n × m + m, a convolution K²·Cin·Cout + Cout, and attention 4d².

Question 1 · Easy · MLP parameters

### How many parameters does an MLP with layers 784 → 128 → 10 have, including biases?

Answer: **101,770**

1. First layer: 784 × 128 + 128 = 100,480.

2. Second layer: 128 × 10 + 10 = 1,290.

3. Add them: 101,770.

A dense layer from n to m has n × m weights, plus m biases.

Question 2 · Easy · conv shape

### Input 64×64×3, then a 3×3 convolution with 32 filters, stride 2 and padding 1. What's the output shape, and how many parameters?

Answer: **32×32×32, with 896 parameters**

1. Width: ⌊(64 + 2 − 3) / 2⌋ + 1 = 31 + 1 = 32.

2. Parameters: 3 × 3 × 3 × 32 + 32 = 896.

Parameters don't depend on the image size.

Question 3 · Easy · receptive field

### What's the receptive field of three stacked 3×3 layers with stride 1? How do their weights compare with one 7×7 layer?

Answer: **7×7, with 27 weights against 49**

1. Each layer adds k − 1 = 2, starting from 1: 1 + 2 + 2 + 2 = 7.

2. Weights per channel pair: 3 × 9 = 27, against 49.

You also gain two extra non-linearities.

Question 4 · Easy · initial loss

### A new 1,000-class classifier starts training. What loss should you expect at step 0?

Answer: **About 6.91**

1. An untrained model should predict nearly evenly.

2. Cross-entropy is then ln 1000 ≈ 6.91.

A much higher value suggests the initial logits are too large.

Question 5 · Medium · attention

### A layer has d = 512 and 8 heads, with 512 tokens. What's the head size, the number of attention parameters, and the scores per head?

Answer: **Head size 64, about 1.05 million parameters, 262,144 scores**

1. Head size: 512 / 8 = 64.

2. Parameters: 4d² = 4 × 262,144 = 1,048,576.

3. Scores: 512² = 262,144.

Adding heads at a fixed d doesn't add parameters.

Question 6 · Medium · depthwise

### With K = 3, 64 channels in and 128 out, what's the cost per position of a standard and a depthwise separable convolution?

Answer: **73,728 against 8,768, about 8.4 times cheaper**

1. Standard: 9 × 64 × 128 = 73,728.

2. Separable: 9 × 64 + 64 × 128 = 576 + 8,192 = 8,768.

3. Ratio: 73,728 / 8,768 ≈ 8.4.

It matches 1/N + 1/K² = 1/128 + 1/9 ≈ 0.119.

Question 7 · Medium · ViT

### A ViT takes 224×224 colour images with 16×16 patches. How many tokens are there, and how many numbers does a flattened patch hold?

Answer: **197 tokens, 768 numbers**

1. Patches: (224 / 16)² = 14² = 196, plus a class token = 197.

2. Per patch: 16 × 16 × 3 = 768.

In ViT-Base, the projection also outputs 768, but that's a design choice.

Question 8 · Hard · IoU

### Box A is (0, 0) to (4, 4), and box B is (2, 2) to (6, 6). What's the IoU? Would B count as correct at a 0.5 threshold?

Answer: **About 0.14, so no**

1. Overlap: 2 × 2 = 4.

2. Union: 16 + 16 − 4 = 28.

3. IoU: 4 / 28 ≈ 0.14, below 0.5.

Even boxes that look close can have a low IoU.

Question 9 · Hard · upsampling

### A transposed convolution has K = 4, S = 2 and P = 1, on a 16×16 map. What's the output size?

Answer: **32×32**

1. Output: S(n − 1) + K − 2P.

2. 2 × 15 + 4 − 2 = 32.

This setting exactly doubles any input size.

**More practice and sources**

9 interview questions, easy to hard · answers hidden until you click · checked 6 Nov 2026

Keep practising

Review MLPs, output shapes, multi-head attention, CNN architectures and object detection. For debugging, see part 1 and part 2.
