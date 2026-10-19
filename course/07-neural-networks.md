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

## Practical extension: train a complete MLP and verify every gradient

The MLP in [model_comparison.py](../labs/model_comparison.py) uses d=2 inputs, h hidden tanh units and one logistic output. W1 has h×d weights, b1 has h biases, v has h output weights and b2 is scalar. Its hidden state is `a_j=tanh(sum_k W1_jk x_k+b1_j)`, logit `z=sum_j v_j a_j+b2`, and probability sigmoid(z). For h=8,d=2, there are 16+8+8+1=33 trainable scalars. All are updated; there is no frozen hidden layer.

For one example, let delta=p-y. Backprop gives `dL/dv_j=delta*a_j`, `dL/db2=delta`, `dL/dW1_jk=delta*v_j*(1-a_j²)*x_k`, and `dL/db1_j=delta*v_j*(1-a_j²)`. These follow from the chain rule and derivative of tanh. Batch gradients average over examples; L2 adds lambda times each penalized weight. Biases are deliberately not regularized. The code's flattened parameter layout is documented so you can map every index back to these equations.

Initialization uses seeded small random weights and zero biases. Equal zero weights for all hidden units would make their behavior symmetric and prevent learning diverse features. Tanh is smooth, making numerical gradient checks less ambiguous than ReLU at its kink. It can still saturate when inputs are badly scaled; the train-only standardization is therefore part of the experiment.

The test `test_every_mlp_weight_and_bias_gradient` uses a two-hidden-unit network and two examples, computes analytic derivatives, then perturbs every parameter by ±1e-5 to obtain centered finite differences. It checks input weights, hidden biases, output weights and output bias, including L2. This is stronger than checking one convenient weight. A correct derivative test still does not prove correct labels, a valid split or convergence on every task.

The chosen width-8 model's regularized training objective decreases from .706401 to .213534 in 700 full-batch updates. Held-out metrics appear in chapter 05. This is actual training evidence, not simply an imported network returning a tensor. Two endpoint values establish a decrease for this run; they do not replace a detailed learning curve or prove monotonic loss at every update.

Exercises: (1) Set the output weights to zero and inspect first-step hidden gradients. Solution: delta can be nonzero, but the factor v_j makes initial hidden-weight gradients zero; output weights may learn first and later enable hidden updates. (2) Negate the hidden-bias gradient in a temporary copy. Solution: the all-parameter finite-difference check should fail, even if some training loss still decreases. (3) Replace tanh with a purely linear activation. Solution: the composition collapses to an affine score, losing the nonlinear representational mechanism needed by the XOR-shaped task. Re-derive the activation derivative rather than changing only the forward pass.

Mastery gate: identify the shapes and all 33 parameters, derive a hidden bias gradient, run the checks, and diagnose why correct gradients do not guarantee useful deployment. Framework autograd, convolutional training and large-model numerical debugging remain further practice.

## Trace convolution and recurrence without hiding the operations

Run [representations.py](../labs/representations.py). A 3×3 array containing rows [1,2,3], [4,5,6], [7,8,9] with a 2×2 kernel [[1,0],[0,-1]], valid padding and stride 1 produces a 2×2 result of -4 everywhere. The top-left output is 1-5=-4; moving the kernel reuses the same weights. This uses the cross-correlation convention common in neural-network software, where the kernel is not flipped. It illustrates weight sharing and shape, not a trained image recognizer.

The recurrent trace uses `h_t=tanh(x_t+.5*h_(t-1))`, starting at zero. Inputs [1,0] end near .3634; reversing them to [0,1] ends near .7616. A shared recurrence can observe order, unlike simply summing the inputs. Training this recurrence would require propagating derivatives through time; that full implementation is not claimed here.
