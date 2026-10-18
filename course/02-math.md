# 02 · Vectors, matrices, logs and derivatives

Prerequisite: 01. Outcomes: track dimensions, compute similarity, interpret logarithms, and apply the chain rule. These tools describe computations; notation should expose mistakes rather than hide them.

## Vectors are ordered measurements

A scalar is one number. A vector is an ordered list: a ticket might have x = (length, customer_age_days, prior_contacts). Order and units matter. A matrix stacks vectors into rows. With n examples and d features, X has shape n×d. A parameter vector w has shape d; Xw gives n scores. Add a scalar bias b to every score: `z_i = sum_j X_ij w_j + b`. The bias permits a nonzero score when all features are zero.

A dot product `x·w = sum_j x_j w_j` computes a weighted sum. For x=(2,1), w=(3,-1), the result is 5. The Euclidean norm `||x|| = sqrt(sum_j x_j²)` measures magnitude. Cosine similarity is `(x·y)/(||x|| ||y||)` for nonzero vectors. With x=(1,0), y=(1,1), cosine is 1/sqrt(2), about .707. It measures direction; it is not a probability that two items mean the same thing. Scaling y by 10 changes dot product and Euclidean distance, but leaves cosine unchanged.

A transpose swaps rows and columns. If A is m×k and B is k×n, AB is m×n. Each result is a dot product of a row of A with a column of B. Multiplication is generally not commutative. Attention later uses QKᵀ: if Q and K are T×d, the product is T×T, one score for every pair of positions.

Scaling features by training-set standard deviation keeps a unit change from being dominated merely by units. Standardization `z=(x-mu)/s` uses training mu and s; handle s=0 explicitly. It does not remove outliers or make a distribution Gaussian.

## Geometry behind compression

An eigenvector of a square matrix keeps its direction under that transformation: Av=λv. The eigenvalue λ is the scale along that direction. Singular value decomposition writes a rectangular matrix as UΣVᵀ, separating input directions, scales and output directions. Principal component analysis centers data and finds orthogonal directions of maximum sample variance. Projecting onto fewer directions compresses data, but maximum variance need not preserve the information needed for a target. Fit PCA on training data only.

A rank-r approximation retains at most r independent directions. This will reappear in low-rank adapters: representing a d×d update as a d×r matrix times an r×d matrix uses 2dr parameters rather than d², when r is small. That is a structural constraint, not proof the best task update is low rank.

## Exponentials and logarithms

`exp(a+b)=exp(a)exp(b)` and `log(ab)=log(a)+log(b)` for positive a,b. Natural logarithm is the inverse of exp, with base e. log(1)=0; log of a probability near zero is a large negative number. Adding log probabilities is numerically safer than multiplying thousands of tiny probabilities. If a sequence assigns P(t1)=.5 and P(t2|t1)=.25, its joint probability is .125 and log probability is log(.5)+log(.25)=log(.125).

Softmax turns finite scores z into normalized positive weights: `p_i = exp(z_i)/sum_j exp(z_j)`. Subtract the maximum score before exponentiation to avoid overflow; the common factor cancels. Scores (0,log(3)) produce (.25,.75). Normalization makes numbers sum to one; it does not establish empirical calibration or truth.

## Change, gradients and the chain rule

A derivative measures a local rate of change. For f(w)=w², the difference quotient is `((w+h)²-w²)/h = 2w+h`; taking h toward zero gives 2w. A partial derivative changes one coordinate while holding others fixed. A gradient collects all partial derivatives into a vector pointing toward steepest local increase under Euclidean geometry.

The chain rule handles composition: if L depends on z and z depends on w, `dL/dw=(dL/dz)(dz/dw)`. Let z=wx+b and L=(z-y)²/2. Then dL/dz=z-y, dz/dw=x, and dL/dw=(z-y)x. At x=2, y=5, w=1, b=0, prediction is 2, residual -3 and gradient -6. Increasing w slightly lowers the loss. This is a local statement, not a guarantee for any step size.

Run [foundations.py](../labs/foundations.py) for stable softmax, cosine and a finite-difference gradient check. The finite difference `(f(w+h)-f(w-h))/(2h)` approximates a derivative. Too large h causes approximation error; too small h causes floating-point cancellation.

## Practice and solutions

1. X is 20×3; W is 3×7. What shape is XW? Solution: 20×7. W X is undefined because the inner dimensions differ.
2. Why can raw Euclidean distance be misleading for age in years plus income in dollars? Solution: unit scale can dominate geometry. Standardization is one option, selected for the task and fit on train only.
3. Derive d[(wx-y)²]/dw. Solution: 2(wx-y)x. Removing the one-half multiplies the gradient by two, which interacts with learning rate.
4. A vector has zero norm. What should cosine code do? Solution: reject or define a documented fallback; dividing by zero has no mathematical cosine interpretation.

Interview: explain dot product versus cosine at basic depth; derive stable softmax at deeper depth; discuss when compression can remove rare but decision-critical signals at senior depth. Vocabulary: scalar, tensor (an array with multiple axes), shape, transpose, norm, rank, eigenvector, SVD, logit (an unnormalized model score), gradient, chain rule.


## Data representation bridge and depth boundary

A tensor is an array with named-by-convention axes, not necessarily a geometric object in beginner library code. For a batch of 8 RGB images with height/width 32, one convention is shape (8,3,32,32); another is (8,32,32,3). Both contain 24,576 scalar entries, but a layer expecting channels in the second axis cannot silently accept the other convention. Float32 storage for the raw entries takes 98,304 bytes before container overhead. A dtype specifies numeric representation; an array's shape specifies arrangement, not units.

Broadcasting in array libraries can implicitly expand dimensions. An (n,1) prediction minus an (n,) target can produce an unintended (n,n) result under common trailing-axis rules. Assert shapes at boundaries rather than relying on plausible scalar loss output. Missing values should have explicit validity masks or semantics; NaN is not a valid class label and zero is not a universal missing-value code. Floating-point addition is not exact real arithmetic: `0.1+0.2 == 0.3` can be false. Compare with justified tolerances, not arbitrary rounding everywhere.

SVD, eigenvectors and PCA above are recognition/explanation level. A full SVD derivation, numerical eigensolver or PCA implementation is not taught here. As a small projection example, centered points (1,1) and (-1,-1) lie on direction u=(1,1)/sqrt(2). Their scalar coordinates along u are ±sqrt(2); reconstructing as coordinate×u recovers each point. Projecting onto (1,0) loses the second coordinate. Maximum variance is useful for this compression example but does not guarantee preserving a target signal.
