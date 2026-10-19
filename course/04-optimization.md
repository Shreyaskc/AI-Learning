# 04 · Optimization: how learning changes parameters

Prerequisites: 02–03. Outcomes: derive a training update, diagnose optimization versus generalization failure, and understand regularization.

## An objective connects data to parameters

For examples (x_i,y_i), empirical risk is an average loss `J(theta)=(1/n)sum_i L(f_theta(x_i),y_i)`. It measures fit on this sample. Population risk is the expectation over future examples; minimizing sample loss does not guarantee minimizing that expectation. Add a regularizer to prefer certain solutions: `J_reg=J+(lambda/2)||w||²`. L2 penalizes large coefficients; it is a modeling choice related to smoothness or a Gaussian prior in some formulations, not universal protection against leakage.

Gradient descent updates `w_new=w-eta*gradient(J)`, with learning rate eta>0. In one-feature regression with `J=(wx-y)²/2`, gradient is `(wx-y)x`. At x=2,y=5,w=1, gradient=-6. With eta=.1, new w=1.6, prediction 3.2, loss drops from 4.5 to 1.62. With eta=1, w=7 and loss becomes 40.5. The direction was right locally, but the step overshot.

For many examples, average the per-example gradients. Full-batch descent uses the entire training set for each update; stochastic gradient descent uses one or a small batch. A minibatch trades noisy estimates for cheaper and more frequent updates. Shuffle only in ways compatible with the data and model; sequence labels and time-based evaluation still require care. An epoch is a pass through the training examples, not a universal unit of compute across datasets.

## Curvature and conditioning

A convex function lies below the line joining any two points on its graph. For a differentiable convex objective, a stationary point is a global minimum. Linear least squares is convex in its coefficients; a deep network's objective generally is not. The Hessian contains second partial derivatives and describes local curvature. A narrow valley with very different curvature across directions is ill-conditioned: one learning rate may oscillate in one direction and crawl in another. Scaling inputs can help; it does not eliminate every source of poor conditioning.

Momentum smooths gradient history: `v_t=beta*v_(t-1)+(1-beta)*g_t`, then step along v_t. Adam tracks a first moment and squared-gradient second moment, uses bias corrections, and divides by a stabilized square root of the second moment. It adapts coordinate step scales. AdamW decouples weight decay from the adaptive gradient calculation. These are optimization procedures, not substitutes for validation. Scheduler, batch size, precision and initialization can all alter behavior.

## Generalization and regularization

Underfitting means the model or procedure cannot fit relevant structure; both train and validation errors can be high. Overfitting means training fit improves while validation performance worsens. More parameters are not the only cause: repeated hyperparameter search can overfit validation, and clean labels matter.

Regularization options include L2, L1 (which can induce sparse coefficients), early stopping using validation, data augmentation that preserves the target, and dropout in neural networks. The train/validation gap is a clue, not a diagnosis by itself. Distribution shift and mislabeled validation data can create similar symptoms.

For regression with both X and y centered (recover the intercept as mean(y)-mean(X)·w), solving normal equations `XᵀXw=Xᵀy` is possible when the system is suitably nonsingular. Avoid computing a literal matrix inverse in numerical software; factorization or least-squares solvers are typically more stable. Gradient methods matter when data or models make direct solvers inappropriate.

## Lab and reasoning

Run [learning.py](../labs/learning.py). It trains a tiny logistic model using analytic gradients and checks a gradient numerically. Logistic prediction is p=sigmoid(z)=1/(1+exp(-z)); z=w·x+b. Combining sigmoid with binary log loss yields `dL/dz=p-y`, hence `dL/dw=(p-y)x`. Derivation: dL/dp=(p-y)/(p(1-p)); dp/dz=p(1-p); the factors cancel. This cancellation is why the training update has a simple form.

1. Add L2 with coefficient lambda to the one-feature update. Solution: gradient becomes `(wx-y)x+lambda*w`; usually specify separately whether bias is penalized.
2. Why not tune learning rate on the final test set? Solution: that turns the test into a validation set and biases the final estimate.
3. Loss is NaN after a few steps. Investigate? Solution: check invalid inputs, overflow/log-zero, learning rate, gradient magnitudes and precision before adding more model capacity.

Interview: derive one update at basic depth; discuss convexity and conditioning at deeper depth; define a bounded training-debug plan with reproducible configurations at senior depth. Vocabulary: empirical risk, objective, gradient descent, batch, epoch, regularization, momentum, Adam, early stopping, conditioning.
