# The Deep Learning part of the Fundamentals track. Lesson text comes from the live pages (see ml_import.py).
# Each lesson here adds what to read first. Interview questions live in the lesson's plan once it's converted.

GROUPS = [
    ("basics", "Neural network basics", "Neurons, MLPs, activations, losses and backpropagation."),
    ("training", "Training deep nets", "Initialisation, vanishing gradients, normalisation, schedules and batch size."),
    ("regularisation", "Regularisation and debugging", "Dropout, weight decay, augmentation, early stopping and debugging training."),
    ("cnns", "CNNs", "Convolutions, pooling, ResNets and transfer learning."),
    ("sequence", "Sequence models", "RNNs, LSTMs, GRUs and seq2seq with attention."),
    ("transformers", "Attention and Transformers", "Self-attention, multi-head attention, positional encodings and the full Transformer."),
    ("representation", "Representation and generative models", "Embeddings, VAEs, GANs, diffusion and contrastive learning."),
]

LESSONS = {
    "perceptron-to-mlp": {"prereqs": ["logistic-regression"]},
    "activation-functions": {"prereqs": ["perceptron-to-mlp"]},
    "loss-functions": {"prereqs": ["perceptron-to-mlp", "mle-and-map"]},
    "backpropagation": {"prereqs": ["derivatives-and-chain-rule", "perceptron-to-mlp"]},
    "weight-initialisation": {"prereqs": ["backpropagation"]},
    "vanishing-exploding-gradients": {"prereqs": ["backpropagation", "activation-functions"]},
    "normalisation-layers": {"prereqs": ["vanishing-exploding-gradients"]},
    "learning-rate-schedules": {"prereqs": ["gradient-descent"]},
    "batch-size-and-learning-rate": {"prereqs": ["gradient-descent"]},
    "dropout": {"prereqs": ["bias-variance"]},
    "weight-decay-and-adamw": {"prereqs": ["regularized-linear-models", "gradient-descent"]},
    "data-augmentation-and-mixup": {"prereqs": ["bias-variance"]},
    "early-stopping-and-label-smoothing": {"prereqs": ["bias-variance"]},
    "debugging-training-practice-1": {"type": "interview", "prereqs": ["backpropagation"]},
    "debugging-training-practice-2": {"type": "interview", "prereqs": ["debugging-training-practice-1"]},
    "convolution-and-receptive-field": {"prereqs": ["perceptron-to-mlp"]},
    "pooling-stride-padding": {"prereqs": ["convolution-and-receptive-field"]},
    "resnets-and-skip-connections": {"prereqs": ["vanishing-exploding-gradients", "convolution-and-receptive-field"]},
    "transfer-learning": {"prereqs": ["resnets-and-skip-connections"]},
    "rnns-and-backprop-through-time": {"prereqs": ["backpropagation"]},
    "lstm-and-gru": {"prereqs": ["rnns-and-backprop-through-time"]},
    "seq2seq-and-attention": {"prereqs": ["lstm-and-gru"]},
    "self-attention": {"prereqs": ["seq2seq-and-attention", "vectors-and-cosine-similarity"],
                       "related": ["papers/attention-is-all-you-need"]},
    "multi-head-attention": {"prereqs": ["self-attention"]},
    "positional-encodings": {"prereqs": ["self-attention"]},
    "transformer-block": {"prereqs": ["multi-head-attention", "normalisation-layers"]},
    "encoder-decoder-architectures": {"prereqs": ["transformer-block"]},
    "transformer-end-to-end": {"prereqs": ["transformer-block", "positional-encodings"], "related": ["papers/attention-is-all-you-need"]},
    "embeddings": {"prereqs": ["vectors-and-cosine-similarity", "backpropagation"], "related": ["ai-engineering/rag-end-to-end"]},
    "autoencoders-and-vaes": {"prereqs": ["embeddings", "entropy-cross-entropy-kl"]},
    "gans": {"prereqs": ["perceptron-to-mlp"]},
    "diffusion-models": {"prereqs": ["autoencoders-and-vaes"]},
    "contrastive-learning": {"prereqs": ["embeddings"]},
}
for _l in LESSONS.values():
    _l["prereqs"] = [f"fundamentals/{p}" for p in _l.get("prereqs", [])]
