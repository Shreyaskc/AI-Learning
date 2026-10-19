# 05 · Classical machine learning and useful baselines

Prerequisites: 01–04. Outcomes: select a model family from assumptions, fit a simple classifier, and recognize when a neural network is unnecessary.

## Linear and probabilistic models

Linear regression predicts `y_hat=w·x+b` and often minimizes squared error. It assumes a linear form for the conditional mean if interpreted statistically; the input may contain nonlinear basis features such as x². Outliers receive a large squared penalty. Absolute error instead has a median interpretation and is less sensitive to extreme residuals.

Logistic regression maps a linear score through sigmoid to a binary probability. “Regression” in its name does not make it a continuous-target model. Its decision boundary at p=.5 is `w·x+b=0`, but the chosen action threshold need not be .5. Naive Bayes combines a class prior with feature likelihoods while assuming conditional feature independence given the class. The assumption is often false, yet the model can be a useful fast baseline. Correlated evidence can produce overconfident probabilities.

A support vector machine seeks a large-margin boundary; kernels allow implicit nonlinear features. Margin is separation from the decision surface, not calibrated probability. A nearest-neighbor model stores examples and predicts from nearby cases; its distance metric and serving cost become critical as dimension and dataset size grow.

## Trees and ensembles

A decision tree partitions feature space by questions such as `prior_contacts > 2`. At a leaf it predicts a value or class distribution. A split can reduce Gini impurity `1-sum_k p_k²` for classification. A leaf with equal class fractions has impurity .5 in the binary case; a pure leaf has zero. Greedy split selection does not guarantee the best entire tree. Deep trees can memorize noise.

Bagging trains models on resampled datasets and averages them, reducing variance when errors are not perfectly correlated. Random forests also randomize feature choices. Boosting fits successive learners to improve the current ensemble objective; gradient boosting uses loss gradients as directions for correction. Boosting is not simply another name for bagging. Trees naturally capture nonlinear thresholds and interactions, but extrapolate poorly outside learned regions and need care with missing values and high-cardinality categories.

A practical tabular workflow starts with a constant baseline, a regularized linear model, and a tree ensemble. Compare with consistent splits and tuning budgets. Deep models become attractive for learned representations across high-dimensional unstructured data, but “more advanced” is not a measured advantage.

## A worked prediction

Let urgency score z=-2+1.5×prior_contacts+.5×has_outage_word. A ticket with one prior contact and an outage word gets z=0 and p=.5. Another with zero prior contacts and the word gets z=-1.5 and p≈.182. If missing an urgent ticket costs 20 units and unnecessary review costs 1, the equal-cost threshold .5 may be inappropriate. Under calibrated probabilities and these simplified costs, act when `20p > 1(1-p)`, so p>1/21≈.0476. Capacity limits and downstream effects complicate this rule.

Run [learning.py](../labs/learning.py) to fit logistic regression on synthetic one-dimensional cases. Inspect the analytic gradient, fitted weight, held-out probabilities and log loss. Because the dataset is tiny and deliberately simple, high classification accuracy is not evidence that the algorithm will work on real tickets.

## Unsupervised structure

K-means assigns points to k centers and alternates assignment with center updates to reduce within-cluster squared distances. It assumes that this geometry is useful; clusters can be unstable, differently scaled, or socially meaningless. PCA compresses variance directions rather than discovering labels. Anomaly detection flags departures from a reference pattern; rare does not mean harmful, and harmful behavior can resemble common behavior.

## Practice and solutions

1. Explain why duplicating a feature can hurt naive Bayes confidence. Solution: the conditional independence model can count the same evidence twice, making likelihood ratios too extreme.
2. A tree performs well on delays 0–10 days; will it extrapolate linearly to 100-day delays? Solution: ordinary regression trees predict leaf averages, so they do not naturally extrapolate a trend.
3. A model beats a baseline by .2% after 1,000 trials. What next? Solution: account for selection and uncertainty, use a preserved evaluation set, inspect slices and compare value and complexity before adoption.

Interview depths: describe linear versus tree assumptions; derive logistic gradient and a cost threshold; defend a baseline choice under latency, interpretability and maintenance constraints. Misconception: feature importance is not a causal effect. Vocabulary: margin, kernel, tree, ensemble, bagging, boosting, cluster, anomaly, interpretability.


## One complete logistic update

Start with scalar x=2, positive target y=1, w=0,b=0 and learning rate eta=.1. Forward: z=wx+b=0, p=sigmoid(0)=.5, loss=-log(.5)=.693147. From chapter 04, dL/dz=p-y=-.5. Therefore dL/dw=-.5×2=-1 and dL/db=-.5. Gradient descent gives w=.1 and b=.05. The new z=.1×2+.05=.25, so p≈.562177 and positive-label loss≈.575939. One sample update improved its own loss; it says nothing by itself about held-out generalization.

If instead y=0 while inputs/initial parameters stay fixed, the gradients are +1 and +.5, giving w=-.1,b=-.05 and p≈.437823. This symmetric changed-target exercise checks the sign. Do not confuse the coefficient .1, the score .25, the probability .562 and a thresholded action: they have different meanings. A numeric coefficient's interpretation also depends on feature units and correlated inputs; it is not a causal effect.

## Practical extension: train and compare four families

Question: when does a flexible representation help more than a linear boundary? Run `python3 labs/model_comparison.py`. This trains a constant predictor, vector logistic regression, a greedy CART-style classification tree and a small tanh MLP. Unlike the earlier one-dimensional trace, these are actually fitted models compared on the same nonlinear task. The full implementation and recorded [result](../review/evidence/model-comparison.json) are inspectable.

Generate 320 independent examples with seed 31. Features x1 and x2 have different units: x1 is uniform on [-1,1], x2 on [-100,100]. The target is 1 when exactly one feature is positive, with 3% independent label flips. This XOR-shaped relationship has two disjoint positive quadrants. A single affine score cannot represent it exactly. The label noise deliberately prevents interpreting perfect training fit as the goal.

Freeze 160 training, 80 validation and 80 final-test rows before fitting. The data generator is IID here; this split is not a prescription for time series. Fit feature means and standard deviations on the training rows only, then apply that same transformation to all three sets. The constant predicts training prevalence. Logistic regression minimizes log loss with L2. The tree tests midpoint thresholds and chooses the greatest immediate weighted-Gini improvement, stopping by depth/minimum leaf size. It uses smoothed leaf probabilities `(positive_count+1)/(leaf_count+2)` to avoid exact zero/one probabilities on tiny leaves. That smoothing is an explicit design choice affecting log loss.

Train depths 2 and 4 as tree candidates and hidden widths 4 and 8 as MLP candidates; select the candidate within each family with lowest validation log loss. Logistic has one fixed configuration. Finally evaluate the selected instances once on the untouched test rows with threshold .5. Family tuning budgets differ, so this is an educational comparison, not a fair compute-efficiency benchmark.

| Selected model | Test accuracy | Test log loss | Test Brier |
| --- | --- | --- | --- |
| Constant | .4750 | .6982 | .2525 |
| Logistic | .4750 | .7004 | .2536 |
| Tree, depth 4 | .8625 | .3197 | .1010 |
| MLP, width 8 | .9250 | .3235 | .0857 |

These are recorded outputs for one synthetic split, not population estimates with strong uncertainty guarantees. The MLP catches more thresholded cases, yet the tree has slightly lower log loss. Accuracy and probability quality ask different questions. Never revise configuration after inspecting these test results and continue calling the same rows a final test. A new hypothesis requires new validation/test evidence.

A subtle failure: a perfectly balanced four-point XOR dataset has zero immediate Gini gain at each first axis split. This greedy tree stops before seeing the useful two-level interaction, even though a depth-2 tree could express it. The test suite demonstrates this limitation. On the noisy finite sample above, an immediate gain exists, permitting deeper splits. Expressiveness and a greedy training procedure are not identical.

Exercises: (1) Change the label to `x1>0` and define new splits before running. Predict which model should improve. Solution: a linear score and shallow tree can represent this boundary; complexity is no longer required, although finite data/noise still matter. (2) Increase maximum depth until training fit approaches perfection. What evidence would justify retaining it? Solution: validation improvement and useful error behavior under an unchanged protocol, not training accuracy. (3) Remove scaling for all models. Solution: trees are largely invariant to monotonic per-feature rescaling when thresholds transform correspondingly; gradient optimization is sensitive to scales. Compare convergence and loss with controlled training budgets rather than assuming every model changes identically.

Mastery gate: explain the four rows, reproduce the report, locate the training-only scaler, and defend a model using both metric and operational constraints. The next deeper gap is a public-data/library comparison with uncertainty over repeated valid splits.

## Identifiability, density and misleading geometry

If two input columns are identical, the linear score depends on their coefficient sum. For x1=x2, coefficients (1,0) and (0,1) produce the same predictions. Individual coefficients are not identifiable from this design alone. L2 can select a minimum-norm convention, but that does not reveal which feature caused an outcome. Near-duplicate columns can make coefficient estimates unstable even when predictions look stable. Audit units, rank, regularization and interpretation separately.

K-means is not the only definition of a cluster. DBSCAN groups points connected through sufficiently dense neighborhoods, using a radius epsilon and minimum-neighbor count. With points at 0,.1,.2,5 on a line, radius .15 and minimum count 2 including the point itself, the first three connect through neighborhoods while 5 is isolated. This can capture non-spherical structure and identify noise, but results depend strongly on scaling, density variation and epsilon. This lesson explains the mechanism; it does not claim an executed DBSCAN implementation.

In high dimensions, many irrelevant coordinates can dominate distance, and local neighborhoods become sparse at a fixed sample size. A nearest-neighbor method may need more data, better representations or task-informed metric choices. Adding dimensions is not automatically adding useful information. Two-dimensional visualizations such as t-SNE/UMAP can distort global distances and vary with settings; separated blobs do not establish real-world categories or causal subpopulations. Confirm conclusions with original-space evaluation and task evidence.
