# 07 · Neural networks and representation learning

Prerequisites: 02–06. Outcomes: trace forward and backward passes, distinguish architectures, and understand why learned representations help.

## Composition creates features

A dense layer computes `h=phi(Wx+b)`. W is output-width×input-width under column-vector convention; b has output width. phi is a nonlinear activation. With no nonlinearity, stacking affine layers collapses into one affine map: `W2(W1x+b1)+b2=(W2W1)x+(W2b1+b2)`. Depth alone would not create a more expressive nonlinear boundary.

ReLU is max(0,z); it keeps positive values and blocks negatives. Its derivative is 1 for z>0 and 0 for z<0; software chooses a convention at zero, where the derivative is not unique. Sigmoid saturates for large positive or negative scores; repeatedly multiplying small derivatives can make early-layer gradients tiny. Residual connections add an identity path, letting layers learn a correction rather than the entire transformation.

Representation learning trains intermediate features that make an objective easier. These features can transfer to other tasks if useful structure overlaps, but can also encode spurious shortcuts. A picture classifier may learn a background watermark rather than the object. Training loss alone cannot distinguish the intended mechanism.

## A complete backprop calculation

Take x=2, hidden h=ReLU(w1*x+b1), output z=w2*h+b2, and L=(z-y)²/2. Choose w1=.5,b1=0,w2=3,b2=0,y=4. Forward: hidden preactivation 1, h=1, z=3, L=.5. Backward: dL/dz=-1; dL/dw2=-1×h=-1; dL/db2=-1. Through the hidden layer, dL/dh=-1×3=-3. Since preactivation is positive, dL/dw1=-3×1×x=-6 and dL/db1=-3. Every gradient follows local chain-rule multiplication.

A computation graph stores operations and dependencies. Reverse-mode automatic differentiation accumulates derivatives from outputs back to parameters, efficiently producing many parameter gradients for a scalar loss. It is neither symbolic algebra for arbitrary expressions nor finite differences. Gradients must be zeroed or intentionally accumulated between updates in frameworks that accumulate them. Training mode and evaluation mode affect operations such as dropout; disabling gradients alone is not the same thing as switching mode.

Run [learning.py](../labs/learning.py), which checks this two-layer gradient by finite differences. Compare a hand derivative to the numerical approximation rather than trusting either implementation blindly.

## Architectural biases

Convolutional networks share local filters across spatial positions. This encodes a useful locality/translation bias for images and signals. A 3×3 convolution from 3 input channels to 16 output channels has 3×3×3×16=432 weights, plus 16 biases if used. Spatial dimensions and padding alter output size, not this count.

Recurrent networks update a state across sequence steps; LSTM/GRU gates help manage information flow and gradients. They naturally process variable-length sequences but sequential computation can limit parallel training. Transformers use attention to mix positions; they have different compute and memory tradeoffs. Graph neural networks aggregate neighbor information on graph structures, with risks including oversmoothing, noisy edges and graph leakage across splits.

An autoencoder compresses input to a latent representation then reconstructs it. A variational autoencoder learns a probabilistic latent model using reconstruction and a distribution regularizer. Contrastive learning brings related views closer and separates negatives according to its objective; “negative” may be an accidentally related example, so sampling matters.

## Train a model responsibly

Initialize to avoid identical hidden units and unstable scales. Normalize inputs, inspect loss curves and gradients, and overfit a tiny batch as a debugging check. Dropout randomly suppresses activations during training and changes behavior at evaluation; it discourages certain dependencies but is not universally helpful. Batch normalization uses batch statistics during training and running estimates for inference; layer normalization normalizes within a representation and is common in transformers.

1. Why can a network with zero hidden activations stop learning some weights? Solution: a ReLU inactive for all observed inputs passes zero gradient through that path.
2. What does transfer learning freeze? Solution: selected pretrained parameters remain fixed; trainable layers or adapters still update. Frozen does not imply unbiased or appropriate for the new task.
3. Is universal approximation a training guarantee? Solution: no; representational existence says little about finite data, optimization, compute or generalization.

Interview: trace the numerical backward pass; contrast convolution, recurrence and attention; then explain how to detect shortcuts before deploying. Vocabulary: activation, hidden layer, representation, residual, autograd, convolution, recurrence, transfer learning, contrastive learning.
