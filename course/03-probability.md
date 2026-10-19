# 03 · Probability, statistics and uncertainty

Prerequisites: 02, especially logs. Outcomes: reason with base rates, distinguish distributions from samples, and interpret uncertainty without turning correlation into causation.

## Probability is a model of uncertainty

An event is a set of outcomes. A random variable maps an outcome to a number. Its distribution assigns probability mass to discrete outcomes or density to continuous regions. A density value is not itself a point probability; for a continuous variable, probabilities come from integrating density over an interval.

Conditional probability is `P(A|B)=P(A and B)/P(B)` when P(B)>0. Independence means `P(A and B)=P(A)P(B)`; it is stronger than zero correlation. Bayes' rule follows by writing the joint event two ways: `P(A|B)=P(B|A)P(A)/P(B)`. Prior is belief before this evidence, likelihood is the probability of evidence given a hypothesis, posterior is the updated distribution. They are different quantities.

A machine fault occurs in 1% of cases. A detector catches 90% of faults and falsely flags 10% of normal machines. In 10,000 machines, expect 100 faults, 90 true positives, 9,900 normal machines and 990 false positives. Thus P(fault|positive)=90/1080≈.0833. Sensitivity P(positive|fault) and precision P(fault|positive) reverse the condition; confusing them causes expensive errors.

## Expectations and variation

Expectation is a probability-weighted average: `E[X]=sum_x x P(X=x)` for discrete X. Variance is `E[(X-E[X])²]`, spread around that average. Standard deviation is its square root, in the original units. A Bernoulli label is 1 with probability p, otherwise 0; mean p and variance p(1-p). Covariance measures joint centered variation, and correlation normalizes it by standard deviations. Neither supplies an intervention model.

The sample average estimates the population expectation when the sampling process supports that inference. Under independent identically distributed observations with finite variance, the average's variance is σ²/n; its standard error falls like 1/sqrt(n). Four times the data approximately halves standard error, not necessarily model error. Correlated customers, repeated sessions or time dependence reduce effective information.

A bootstrap resamples the observed units with replacement and recomputes a statistic. If units are customers, resample customers, not individual repeated rows. Bootstrap intervals can fail with severe small-sample bias, rare events or unrepresentative sampling. A frequentist 95% confidence interval describes the coverage of a procedure over repeated samples under assumptions; it is not automatically a 95% posterior probability for a fixed parameter. A Bayesian credible interval is a posterior statement under the chosen model and prior.

## Information and loss

Entropy `H(P)=-sum_x P(x) log P(x)` measures average surprise under P. Cross-entropy `H(P,Q)=-sum_x P(x) log Q(x)` measures surprise using predicted Q when outcomes follow P. Their difference is KL divergence `KL(P||Q)=sum P log(P/Q)`, nonnegative when defined. KL is asymmetric and is not a geometric distance metric.

For one observed binary label y and predicted p, negative log likelihood is `-[y log p+(1-y) log(1-p)]`. Predicting .9 for a positive gives loss about .105; predicting .01 gives 4.605. Confident errors are heavily penalized. This objective rewards distribution prediction; a classification threshold is a separate action choice. Keep probabilities away from exact zero in numeric demonstrations, but remember clipping changes the reported score.

## From association to decisions

If customers receiving reminders return books later, reminders may be targeted at patrons already late. The association does not establish that reminders cause delay. A causal claim compares interventions: what would happen if reminder policy changed, holding the relevant comparison valid? Random assignment can identify a policy effect under assumptions about compliance, interference and measurement. Observational adjustment requires causal assumptions; adding many features does not automatically remove confounding.

Aleatoric uncertainty is variability in outcomes given available information. Epistemic uncertainty concerns what is unknown about the model or parameters. More representative data may reduce the latter; it cannot remove irreducible ambiguity from omitted information. These categories are useful models, not perfectly separable observable labels.

## Practice and solutions

Run [foundations.py](../labs/foundations.py), then alter prevalence from .01 to .10 while retaining detector rates. Expected precision becomes `.09/(.09+.09)=.5`. A detector's precision depends on the deployment population.

1. Can two uncorrelated variables be dependent? Solution: yes; let X be uniform on {-1,0,1} and Y=X². Their covariance can be zero while Y is determined by X.
2. A test has no errors in 20 cases. Is error probability zero? Solution: no. Small samples permit substantial uncertainty; report counts, intervals and sample selection.
3. Why do logs appear in language-model training? Solution: joint sequence probabilities factor into conditional probabilities; negative logs turn their product into an additive objective with gradients that penalize assigned low probability on observed outcomes.

Interview: explain the base-rate example; derive binary log loss; then design a sampling plan for subgroup confidence intervals and delayed outcomes. Vocabulary: prior, likelihood, posterior, expectation, variance, standard error, entropy, cross-entropy, KL, confounding, intervention.
