# Dropout

> Why does randomly switching off neurons make a network generalise?

- Track: Fundamentals › Deep Learning › Regularisation and debugging
- Type: Concept · 20 min
- Page: https://aimlrounds.com/tracks/fundamentals/dropout/
- Before this: The Bias–Variance Trade-off (`fundamentals/bias-variance`)
- Quiz topic: `train`
- Sources checked: 2026-10-29 · Text last changed: 2026-11-20 · Version: 6c1913e795

## Intuition

### The situation

Your 257-parameter network, trained on just 60 orders, hits 100% training accuracy and is wildly overconfident on new ones. The interviewer asks:

> Why does randomly switching off neurons make a network generalise?

**Running example (Regularisation lessons):** the late-delivery classifier from From Perceptron to MLP, but now trained on only **60 orders**, and about **12% of their labels are wrong** (a rider marked the order late by mistake). The network is big for this data: 64 tanh hidden units, 257 parameters. We check it on 400 fresh, correctly labelled orders.

#### A big network memorises the noise

With 257 parameters and 60 examples, the network can carve a little island around every mislabelled order. Training accuracy hits 100%, but the boundary it learned is full of bumps that don't exist in reality, and it is wildly overconfident: it predicts 0.99 for orders it gets wrong. We want to keep the capacity (we don't know in advance how complex the real pattern is) but stop it being spent on noise.

### The idea

Think of a team where anyone might call in sick on any day. Nobody can rely on one colleague to cover their mistakes, so everyone has to be useful on their own. Dropout trains a network the same way.

[Figure: A small network where some hidden units are switched off with a cross. A different set would be off at the next step.]

_Illustrative. At test time, dropout is switched off and every unit is used._

### Play

**Try to break it.** Compare no dropout, 0.2 and 0.5, then try 0.8. Watch train accuracy, test accuracy and test log loss.

#### Same network, different dropout rates

64 tanh hidden units, 800 full-batch Adam steps, a fresh dropout mask per example per step, fixed seed. Shaded: predicted late (orange) or on time (teal). Dots: the 60 training orders (some mislabelled).

Without dropout the network reaches **100%** training accuracy and a test log loss of **1.26**: it is confidently wrong on many new orders. With **p = 0.2**, training accuracy drops to 85% (it stops fitting the mislabelled points), test accuracy edges up to 79%, and the test log loss falls to **0.43**, three times better. Push p to 0.8 and the network **underfits**: 72% test accuracy. The biggest gain here is in confidence, not accuracy, which is typical on small noisy data.

**Now say why:** why does test performance improve while training accuracy falls, and why does 0.8 go too far?

## Maths

### Maths

#### In one breath

A big network can memorise a small dataset, including its mistakes. **Dropout** fights this by randomly setting each hidden unit's output to zero with probability p on every training step, so the network can't rely on any one unit or on fragile combinations of units (**co-adaptation**). Each step trains a different "thinned" sub-network, and the full network at test time behaves roughly like an **average of all of them**. Modern code uses **inverted dropout**: surviving units are scaled up by 1/(1 − p) during training, so nothing changes at test time; you just switch dropout off with `model.eval()`. Typical p is 0.1–0.5. What you'll be able to do after this: explain why dropout regularises, implement inverted dropout, pick a rate, and avoid the train/eval-mode bug.

#### Drop units at random, scale the survivors

$$ {\tilde{h}_k} = \frac{{m_k}}{{1-p}}\, h_k, \qquad {m_k \sim \mathrm{Bernoulli}(1-p)} $$

Srivastava et al. (2014) describe the equivalent original form: keep units with probability p during training and multiply the outgoing weights by p at test time. Their experiments used a retention probability of 0.5 for hidden units and 0.8 for inputs. Frameworks today use the inverted form above; note PyTorch's `p` is the _drop_ probability.

- **random mask**: For every example and every training step, each hidden unit is kept with probability 1 − p and zeroed with probability p. A new mask is drawn each time.

- **inverted scaling**: Divide the survivors by 1 − p so the expected value of each unit’s output is unchanged. Then the network at test time needs no adjustment.

- **what the next layer sees**: A noisy version of the hidden layer. At test time (model.eval()), the mask is all ones and nothing is scaled.

#### No co-adaptation, and a cheap ensemble

- **Co-adaptation:** without dropout, units can form fragile teams where one cancels another's mistake. With dropout, any teammate may vanish, so each unit has to be useful on its own (Hinton et al. 2012).

- **Ensemble:** a network with n droppable units contains 2n thinned networks that share weights. Training samples one per step; the full network at test time approximates their geometric-mean prediction (Srivastava et al. 2014).

- **Noise as regulariser:** like data augmentation, but injected inside the network.

**Results:** Srivastava et al. (2014) report that dropout improved neural networks on supervised tasks in vision, speech recognition, document classification and computational biology, giving state-of-the-art results on many benchmarks at the time.

## In practice

### In practice

#### Dropout in today's architectures

- **MLP heads and classic CNN classifiers** (AlexNet, VGG): p = 0.5 on the big fully connected layers.

- **Transformers:** dropout of 0.1 on attention weights and residual outputs in the original Transformer and BERT.

- **Modern CNNs with BatchNorm** use little or no dropout: BatchNorm's batch noise already regularises, and the two can interact badly.

- **Large LLM pre-training** often uses **no dropout** at all: with trillions of tokens there is little overfitting, and every unit is needed. Dropout is common again during fine-tuning on small datasets.

- **MC dropout:** keeping dropout on at test time and averaging several predictions gives a cheap uncertainty estimate.

### The answer that sounds right

#### "Just use a smaller network"

A smaller network overfits less but may be too simple for the real pattern, and finding the right size takes many runs. Dropout keeps the large network's capacity but makes each unit useful on its own, because it can't count on its neighbours being there. The second trap is the bug that breaks dropout in production: **forgetting `model.eval()`**, so predictions stay random at inference.

## Say it

### Why does randomly switching off neurons make a network generalise?

#### The interviewer pushes further

Follow-up 1 of 3

Why scale by 1/(1 − p)?

So each unit's expected output during training equals its output at test time. Without scaling, the next layer would see activations about (1 − p) times smaller in training than at inference.

Follow-up 2 of 3

Why can validation loss be lower than training loss with dropout?

Training loss is measured with dropout on (a handicapped network); validation runs the full network. It's expected, not a bug.

Follow-up 3 of 3

Dropout vs L2?

L2 shrinks all weights towards zero; dropout adds multiplicative noise to activations and adapts to the data. They can be combined, and for linear models dropout behaves like a data-dependent L2 penalty.

#### The 30-second answer

Dropout randomly zeros each unit's output with probability p during training, with a fresh mask every step, and scales the survivors by 1 over 1 minus p so the expected activation is unchanged. That stops units from co-adapting, since no unit can rely on another being present, and it trains an exponential family of weight-sharing sub-networks whose average the full network approximates at test time. At inference you switch it off with eval mode. Typical rates are 0.1 to 0.5; too high underfits. It's standard in fully connected layers and transformers, less so in BatchNorm CNNs and large-scale LLM pre-training.

**Go further**

#### What not to say

- "Dropout removes neurons permanently." The mask is random per step; all units are used at test time.

- "Higher dropout is always safer." Too much dropout underfits.

**Key terms and sources**

Randomly switching off units during training, why that stops co-adaptation and acts like an ensemble, inverted dropout scaling, train vs eval mode, and where dropout is (and isn't) used today · built from Hinton et al. (2012), Srivastava et al. (2014), Goodfellow et al. §7.12 and the PyTorch `nn.Dropout` docs · checked 29 Oct 2026

#### Sources

1. G. Hinton, N. Srivastava, A. Krizhevsky, I. Sutskever & R. Salakhutdinov, "Improving neural networks by preventing co-adaptation of feature detectors", [arXiv:1207.0580](https://arxiv.org/abs/1207.0580), 2012.

2. N. Srivastava, G. Hinton, A. Krizhevsky, I. Sutskever & R. Salakhutdinov, "Dropout: A Simple Way to Prevent Neural Networks from Overfitting", _JMLR_ 15, 2014, [jmlr.org](https://jmlr.org/papers/v15/srivastava14a.html).

3. I. Goodfellow, Y. Bengio & A. Courville, _Deep Learning_, MIT Press 2016, §7.12, [deeplearningbook.org](https://www.deeplearningbook.org/).

4. PyTorch documentation, [torch.nn.Dropout](https://docs.pytorch.org/docs/stable/generated/torch.nn.Dropout.html).
