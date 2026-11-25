# Interpreting Networks and Adversarial Examples

> How can you see what a network is using, and why can tiny changes fool it?

- Track: Fundamentals › Deep Learning › Computer vision
- Type: Concept · 18 min
- Page: https://aimlrounds.com/tracks/fundamentals/interpreting-networks-and-adversarial-examples/
- Before this: Backpropagation Through a Network (`fundamentals/backpropagation`), Convolution and Receptive Field (`fundamentals/convolution-and-receptive-field`)
- Quiz topic: `cnn`
- Sources checked: 2026-11-06 · Text last changed: 2026-11-20 · Version: b80bbb1070

## Intuition

### The situation

Your image model works well, but a heat map suggests it's looking at a watermark. Separately, a security review shows that tiny pixel changes, invisible to people, make it confidently wrong. The interviewer asks:

> How can you see what a network is using, and why can tiny changes fool it?

#### Why it matters

Heat maps can reveal a model using the wrong clue, such as a watermark rather than the object. Adversarial examples matter wherever someone gains by fooling a model. Both topics appear in vision courses and in reviews of high-stakes systems. For tabular models, see Explaining Models.

### The idea

Think of a thousand people each adding one rupee to a bill. Nobody would notice a single rupee, but the total changes a lot. Adversarial changes work the same way. Each pixel moves too little to see, but all of them push in the same harmful direction.

[Figure: Two uses of one gradient. Heat maps show where the model looked. Attacks use it to raise the loss. Adversarial training defends against them.]

_The same gradient that explains a model can attack it._

### Play

**Try to break it.** Lower the number of inputs. Then raise the change per input.

#### Why dimensions make attacks easy

Our seeded linear model: a logistic classifier with weight length ‖w‖₂ = 1, and a clean score of 2, so the clean probability is the same for every d. 3,072 is the size of a 32×32 colour image.

Keep ε at 0.05, and lower the inputs. The attack stops working, even though the change per input is the same. For scale, 0.05 on a 0-to-1 pixel range is about 13 levels out of 255. This shows the linear argument only, and real networks aren't exactly linear.

**Now say why:** why does the same small change matter more with more inputs?

## Maths

### Maths

#### In one breath

Two tools ask how an input affects the output. **Saliency maps** use the gradient for each pixel. **Grad-CAM** weights the last feature maps by their gradients, to give a coarse heat map. Some of these maps can look convincing while barely depending on the model, so test them. The same gradient also gives an attack: an **adversarial example** nudges each pixel slightly in the harmful direction. In high dimensions, those tiny changes add up. **Adversarial training** helps, at a cost.

#### Explaining, then attacking

##### Saliency and Grad-CAM

- **Saliency map:** the gradient of the class score with respect to each input pixel. It's cheap, but often noisy.

- **Grad-CAM:** take the last convolutional maps. Average each map's gradient to get its importance, add the maps using those weights, and keep the positive part. It's coarse, but class-specific and easy to read.

##### Sanity-check your explanations

Adebayo et al. found that "some existing saliency methods are independent both of the model and of the data generating process". They can resemble edge detectors, which need no model at all. So randomise the model's weights, and see if the map changes. If it doesn't, it isn't explaining the model.

A heat map shows where the model looked, not why, and doesn't show cause. Attention weights have the same limit.

##### Adversarial examples

Goodfellow et al. attributed these mainly to networks' **linear** behaviour. If each of d inputs changes by ε, in the sign of its weight, the score moves by ε‖w‖₁, which grows with d. So a change too small to see in each pixel can add up to a large change in the score.

| Attack | Method | Reported result |
|---|---|---|
| **FGSM** | One step of size ε, in the sign of the gradient. | On MNIST at ε = 0.25, a maxout network was wrong on 89.4%, with 97.6% average confidence. |
| **PGD** | Many small steps, staying within the allowed change. | A stronger attack, also used for training. |

##### Defending

**Adversarial training** trains on attacked examples. Madry et al. framed this as a contest: find the worst allowed change, then minimise the loss on it. In the FGSM paper, error on attacked examples fell from 89.4% to 17.9%. It's slower, and can reduce accuracy on clean data. Be careful about claimed defences, because they must be tested against strong attacks designed for them.

The idea goes beyond images. Text attacks on LLMs are a related problem, covered in guardrails and prompt injection.

#### The maths

$$ {L^c_{\text{Grad-CAM}}} = \mathrm{ReLU}\Big(\sum_k {\alpha_k^c}\, {A^k}\Big), \qquad {\tilde{x} = x + \epsilon\, \mathrm{sign}\big(\nabla_x J(\theta, x, y)\big)} $$

Grad-CAM from Selvaraju et al., Equations 1 and 2. FGSM from Goodfellow et al., Section 4.

- **the heat map**: For class c. It has the same coarse grid as the feature maps.

- **a map’s importance**: The average gradient of the class score across that map.

- **a feature map**: An output from the last convolutional layer.

- **FGSM**: Add ε to each input, in the direction that raises the loss.

## In practice

### In practice

#### In practice

- **Use heat maps for debugging:** they're good at catching a model relying on a background, watermark or text overlay.

- **Test your explanations:** randomise the weights, and check that the map changes.

- **Define the threat first:** what can an attacker change, and what do they gain? Most systems need ordinary robustness more than this.

- **Evaluate defences with strong attacks:** FGSM alone isn't enough, so use PGD or stronger ones.

- **Layer your defences:** rate limits, human review and monitoring can matter more than the model.

### The answer that sounds right

#### "The heat map highlights the object, so the model is right"

It sounds right, as the picture looks convincing. But some saliency methods barely change when the model's weights are randomised, so a nice picture proves little. Sanity-check the method, and test the claim directly: change or remove that area, and see if the prediction changes.

## Say it

### How can you see what a network is using, and why can tiny changes fool it?

#### The interviewer pushes further

Follow-up 1 of 3

Why are high-dimensional models easier to attack?

Each input can change a little, and the effects add up. For a linear model, the score moves by ε times the L1 norm of the weights, which grows with the number of inputs. So many tiny changes make a big one.

Follow-up 2 of 3

Your Grad-CAM highlights the hospital's marker on X-rays. What does this tell you?

The model may be using that marker, not the medical features. That's a form of leakage, and it would likely fail at other hospitals. I'd test on outside data, remove or mask the marker, and retrain. The map is a clue, so confirm it by changing the input.

Follow-up 3 of 3

What makes a defence trustworthy?

It should hold against strong attacks designed specifically to beat it, not just FGSM. Be suspicious if gradients seem to vanish, because this can hide the attack rather than stop it. Report robust accuracy, along with clean accuracy.

#### The 30-second answer

Saliency maps use the gradient of a class score for each pixel. Grad-CAM weights the last feature maps by their average gradients, and gives a coarse, class-specific heat map. They help catch a model using the wrong clue, but they show where it looked, not why, and I'd sanity-check by randomising the weights. Adversarial examples use the same gradient. FGSM adds a small change to each input in the sign of the gradient, and with many inputs, these add up, as the score moves by epsilon times the L1 norm. PGD is a stronger, iterative version, and adversarial training is the main defence, at a cost in speed and sometimes clean accuracy.

**Key terms and sources**

Saliency maps, Grad-CAM and their sanity checks, then adversarial examples: FGSM, PGD, why high dimensions make them easy, and adversarial training. · checked 6 Nov 2026

#### Sources

- [Simonyan et al., Saliency Maps](https://arxiv.org/abs/1312.6034)

- [Selvaraju et al., Grad-CAM](https://arxiv.org/abs/1610.02391)

- [Adebayo et al., Sanity Checks for Saliency Maps](https://arxiv.org/abs/1810.03292)

- [Goodfellow et al., Explaining and Harnessing Adversarial Examples](https://arxiv.org/abs/1412.6572)

- [Madry et al., Towards Deep Learning Models Resistant to Adversarial Attacks](https://arxiv.org/abs/1706.06083)

Explanations are ours, built from these sources. Lab numbers are illustrative, and worked examples were checked by calculation.
