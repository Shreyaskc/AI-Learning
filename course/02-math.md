# 02 · Vectors, matrices, logs and derivatives

Prerequisite: 01. Outcomes: track dimensions, compute similarity, interpret logarithms, and apply the chain rule. These tools describe computations; notation should expose mistakes rather than hide them.

How can a ticket become a calculation? We will start with two measurable inputs, build one weighted score, and then learn the tools needed to change that score. The optional compression section is a later revisit; it is not required to understand your first training update.

## Vectors are ordered measurements

A scalar is one number, such as two prior contacts. A vector is an ordered list of measurements. For one ticket, let x=(2,1): two prior contacts and an outage-word indicator equal to one. If the weights are w=(3,-1), the weighted score is `2*3 + 1*(-1) = 5`. The dot product x·w is the name for this add-the-products operation.

The order matters: swapping the measurements while keeping the weights would change their meaning. A feature's units matter too. “Age in days” and “age in years” describe the same quantity but require different coefficients to produce the same score.

A matrix organizes several vectors. Here are two tickets with the same two feature columns:

```
X = [ [2, 1],      w = [ 3 ]      Xw = [ 5 ]
      [0, 1] ]        [-1 ]           [-1 ]
```

X has shape 2×2: two rows and two columns. Multiplying it by the two weights produces one score for each row. A scalar bias b can shift every score: with b=.5, the predictions are 5.5 and -.5.

Now generalize the notation. If n is the number of examples and d is the number of features, X has shape n×d and w has d coordinates. The score for row i is `z_i = sum_j X_ij w_j + b`. Here i selects an example, j selects a feature, and `sum_j` means add all the feature contributions. This is the same calculation as the two-row example, with compact names for the rows and columns.

A transpose swaps rows and columns. Matrix multiplication combines a row from the first matrix with a column from the second using a dot product. If A has shape m×k and B has shape k×n, AB has shape m×n; the inner widths k must match. AB and BA generally differ, and BA may not even be defined. Later, attention uses QKᵀ: with Q and K each T×d, the result has T×T entries, one comparison for every position pair.

To measure magnitude, square each coordinate, add the squares and take their square root. This gives the Euclidean norm `||x|| = sqrt(sum_j x_j²)`. Cosine similarity divides a dot product by both magnitudes: `(x·y)/(||x|| ||y||)` for nonzero vectors. With x=(1,0),y=(1,1), the result is 1/sqrt(2)≈.707. Scaling y by ten changes a raw dot product but leaves this directional comparison unchanged. Cosine is not a calibrated probability of shared meaning.

Raw distance can be dominated by units. Standardization subtracts a training mean and divides by a training standard deviation: `z=(x-mu)/s`. For now, read s as a typical spread in the data; [03](03-probability.md) develops that measure. Learn mu and s only from training data, handle s=0 explicitly, and apply the same transform at inference. This operation does not remove outliers or force a Gaussian distribution.

## Data representation bridge and depth boundary

An array's shape tells us how entries are arranged; its numeric representation, or dtype, tells us how each entry is stored. A float32 normally uses four bytes. A tensor in ordinary library code is a multi-axis array: a batch of 8 RGB images of height and width 32 may use shape (8,3,32,32), with channels second, or (8,32,32,3), with channels last. Both contain 24,576 values, or 98,304 float32 bytes before overhead. A layer expecting one convention cannot silently accept the other.

Array libraries sometimes expand compatible dimensions automatically; this is broadcasting. It saves writing repeated values, but can hide shape mistakes. Under common trailing-axis rules, subtracting an (n,) target from an (n,1) prediction can produce an unintended (n,n) array. A scalar loss computed afterward may still look plausible. Check the intended axes at each boundary rather than accepting any calculation that runs.

Missing values also need a meaning. Zero is not a universal missing-value marker, and NaN is not a valid class label. Use explicit validity information or a documented imputation rule. Finally, computer floats approximate real numbers: `0.1+0.2 == 0.3` can be false. Compare numeric results using justified tolerances rather than expecting every identity to be bitwise exact.

## Exponentials and logarithms

`exp(a+b)=exp(a)exp(b)` and `log(ab)=log(a)+log(b)` for positive a,b. The exponential exp(x) means e raised to x, where e is approximately 2.718. Natural logarithm undoes that operation: log(e^x)=x, and log(.5)≈-.693. log(1)=0; log of a probability near zero is a large negative number. Adding log probabilities is numerically safer than multiplying thousands of tiny probabilities. For ordinary positive factors .5 and .25, their product is .125 and log(.5)+log(.25)=log(.125). In the next chapter, we will explain when probabilities can be multiplied; the log identity itself needs no probability assumption.

Softmax turns finite scores z into normalized positive weights: `p_i = exp(z_i)/sum_j exp(z_j)`. Subtract the maximum score before exponentiation to avoid overflow; the common factor cancels. Scores (0,log(3)) produce (.25,.75). Normalization makes numbers sum to one; it does not establish empirical calibration or truth.

## Change, gradients and the chain rule

A derivative measures a local rate of change. For f(w)=w², the difference quotient is `((w+h)²-w²)/h = 2w+h`; taking h toward zero gives 2w. A partial derivative changes one coordinate while holding others fixed. A gradient collects all partial derivatives into a vector pointing toward steepest local increase under Euclidean geometry.

The chain rule handles composition: if L depends on z and z depends on w, `dL/dw=(dL/dz)(dz/dw)`. Let z=wx+b and L=(z-y)²/2. Then dL/dz=z-y, dz/dw=x, and dL/dw=(z-y)x. At x=2, y=5, w=1, b=0, prediction is 2, residual -3 and gradient -6. Increasing w slightly lowers the loss. This is a local statement, not a guarantee for any step size.

Run [foundations.py](../labs/foundations.py) for stable softmax, cosine and a finite-difference gradient check. The finite difference `(f(w+h)-f(w-h))/(2h)` approximates a derivative. Too large h causes approximation error; too small h causes floating-point cancellation.

## Geometry behind compression

This is an optional deeper pass. You can continue to probability and return here before studying embeddings or low-rank updates.

Imagine centered points (1,1) and (-1,-1). Both lie on the same diagonal, so one coordinate along that line describes each point. The unit direction is u=(1,1)/sqrt(2). Their dot products with u are sqrt(2) and -sqrt(2); multiplying those coordinates by u reconstructs the original points. This is projection: keep coordinates along selected directions. Keeping only the first ordinary coordinate instead loses the second.

Principal component analysis (PCA) chooses orthogonal directions capturing the most sample variation. That is a compression objective, not a guarantee of preserving what a prediction target needs. Fit the projection using training data only. The next section estimates one direction numerically; it does not derive a full PCA solver.

An eigenvector of a square transformation keeps its direction: Av=lambda*v. The eigenvalue lambda gives the scale along that direction. Singular value decomposition (SVD) extends the direction-and-scale view to a rectangular matrix: UΣVᵀ separates input directions, scales and output directions. These terms are recognition-level here; a full factorization derivation is further work.

Rank counts independent directions. Constraining a d×d update to a product of a d×r and r×d matrix uses 2dr coefficients instead of d² when r is small. This previews low-rank adapters in [09](09-llm-training.md). It is a structural restriction, not proof that the best update for every task has low rank.

## Practical extension: estimate a principal direction

[representations.py](../labs/representations.py) now implements a tiny PCA direction estimator by power iteration. Center the rows, form covariance `C_ij=mean(centered_x_i*centered_x_j)`, then repeatedly normalize C times a candidate direction. If the largest eigenvalue is separated and the initial vector has a nonzero component in its direction, repeated multiplication magnifies that component relative to smaller ones. This is not a complete numerically robust eigensolver or SVD implementation.

For rows (-2,0),(-1,0),(1,0),(2,0), the mean is (0,0), covariance is [[2.5,0],[0,0]], and the leading direction is (1,0), up to sign. Projection preserves these points exactly along the x axis. The test checks both direction and eigenvalue. An initial vector orthogonal to the leading direction can fail; equal leading eigenvalues make the principal direction nonunique. These assumptions matter when moving from a hand example to a robust library.

The same lab fits k-means on these points with two centers initialized at opposite endpoints. It converges to centers (-1.5,0) and (1.5,0), assignments [0,0,1,1] and within-cluster squared distance 1. The objective describes geometry only; it does not establish that the clusters correspond to real categories. Try a new initialization and rescaled coordinates, and distinguish optimizer behavior from the meaning of the resulting groups.

## Practice: try before revealing

On a phone, work through a question mentally or use the optional notes in Practice Q&A. On a computer, you can also run the linked lab. Compare your reasoning before marking a self-check.

1. X is 20×3; W is 3×7. What shape is XW? Solution: 20×7. W X is undefined because the inner dimensions differ.
2. Why can raw Euclidean distance be misleading for age in years plus income in dollars? Solution: unit scale can dominate geometry. Standardization is one option, selected for the task and fit on train only.
3. Derive d[(wx-y)²]/dw. Solution: 2(wx-y)x. Removing the one-half multiplies the gradient by two, which interacts with learning rate.
4. A vector has zero norm. What should cosine code do? Solution: reject or define a documented fallback; dividing by zero has no mathematical cosine interpretation.

## Interview rehearsal and vocabulary

Interview: explain dot product versus cosine at basic depth; derive stable softmax at deeper depth; discuss when compression can remove rare but decision-critical signals at senior depth. Vocabulary: scalar, tensor (an array with multiple axes), shape, transpose, norm, rank, eigenvector, SVD, logit (an unnormalized model score), gradient, chain rule.

## What to carry forward

A vector stores measurements, a matrix organizes examples, and a derivative tells you how a calculation changes. You can now follow the inputs and the update direction. Next, [reason about uncertainty](03-probability.md): a score is not yet a statement about how often an outcome occurs.
