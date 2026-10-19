# 03 · Probability, statistics and uncertainty

Prerequisites: 02, especially logs. Outcomes: reason with base rates, distinguish distributions from samples, and interpret uncertainty without turning correlation into causation.

A detector raises an alert. Before trusting it, ask how often alerts correspond to actual faults. Count cases first; probability notation will give us a shorter way to express the same reasoning. You need only the log and weighted-sum ideas from [02](02-math.md), not the optional SVD section.

## Probability is a model of uncertainty

A machine fault occurs in 1% of cases. A detector catches 90% of faults, but also flags 10% of normal machines. Is a positive alert usually a real fault? Count 10,000 machines: 100 have faults, of which 90 are flagged. Of the 9,900 normal machines, 990 are also flagged. Only 90 of 1,080 alerts are real faults: 90/1080≈.0833.

The conditions distinguish two questions. `P(positive|fault)=.9` asks how often a faulty machine triggers the detector. `P(fault|positive)≈.0833` asks how often a triggered alert corresponds to a fault. The vertical bar means “given.” Reversing that condition changes the denominator and the answer.

An event is a set of outcomes. Write P(A and B) for the chance that both occur. Conditional probability is `P(A|B)=P(A and B)/P(B)` when P(B)>0. Write the same joint event in the opposite order and obtain Bayes' rule: `P(A|B)=P(B|A)P(A)/P(B)`. The formula expresses the count calculation above; it does not remove the need to know the population's base rate.

The prior describes uncertainty before this evidence. A likelihood describes how probable the evidence is under a hypothesis; the posterior is the updated distribution after using it. Independence is another assumption: `P(A and B)=P(A)P(B)`. Do not multiply marginal probabilities without establishing that assumption or using the correct conditional factorization.

A random variable maps an outcome to a number, such as fault=1 or normal=0. Its distribution describes how probability is allocated. Our examples so far are discrete. For a continuous measurement, probability is assigned to intervals using a density; adding density over an interval becomes integration. A density value at one point is not itself a point probability. You do not need integration to follow the fault example or the binary losses below.

## Expectations and variation

Suppose an outcome is equally likely to be 0 or 1. Its probability-weighted average is .5. Each outcome differs from .5 by .5 in magnitude, so the average squared deviation is .25. These are the expectation and variance. The standard deviation is sqrt(.25)=.5, back in the original units.

For a discrete variable, `E[X]=sum_x x P(X=x)` means multiply each possible value by its chance and add. Variance is `E[(X-E[X])²]`. A 0/1 variable with probability p of 1 is called Bernoulli; its mean is p and variance is p(1-p). The name adds no new mechanism beyond our two-outcome example.

Now take a sample and estimate the average. Another small sample can give a different result even when the population has not changed. Under independent, identically distributed observations with finite population variance sigma², the sample mean has variance sigma²/n. Its standard error therefore falls like 1/sqrt(n): four times the data approximately halves this sampling uncertainty. That is not a promise to halve every kind of model error. Repeated sessions or time dependence can invalidate naive independence.

A bootstrap approximates repeated sampling by resampling the observed units with replacement and recomputing a statistic. If customers contribute multiple rows, resample whole customers when that is the independent unit. A bootstrap cannot repair unrepresentative sampling and can behave poorly with rare events, severe bias or tiny samples.

An interval makes the uncertainty more explicit. A frequentist 95% confidence-interval procedure covers the fixed parameter in 95% of repeated samples under its assumptions. It is not automatically a 95% probability statement about that fixed parameter after this particular sample. A Bayesian credible interval makes a posterior probability statement under its prior and model. This distinction is a second-pass topic; first be able to explain why repeated samples vary.

Covariance describes how centered measurements vary together, and correlation divides it by their standard deviations. Neither establishes an intervention effect. The reminder example below shows why describing an observed association is different from changing a policy.

## Information and loss

A model predicts a positive event with probability .9, and the event occurs. Its negative log loss is -log(.9)≈.105. If it had assigned only .01, the loss would be -log(.01)≈4.605. Both predictions named the same possible event, but the confident miss receives a much larger penalty.

For binary target y (0 or 1) and predicted positive probability p, the general form is `-[y log p+(1-y) log(1-p)]`. When y=1 only -log(p) remains; when y=0 only -log(1-p) remains. This scores a probability prediction. Choosing an action threshold is a separate decision.

The same idea extends to a distribution over many possible outcomes. Let P describe the outcome frequencies and Q the predicted probabilities. Entropy `H(P)=-sum_x P(x) log P(x)` averages surprise when using P itself. Cross-entropy `H(P,Q)=-sum_x P(x) log Q(x)` averages surprise using Q. In each expression, `sum_x` means add over possible outcomes, weighted by P(x).

Their difference is KL divergence: `KL(P||Q)=sum_x P(x) log(P(x)/Q(x))`. It is nonnegative when defined, but asymmetric: swapping P and Q changes it. It is not a geometric distance metric. These definitions will help distinguish language-model and preference objectives later; start by being able to reproduce the binary loss example.

Keep demonstration probabilities away from exact zero when a logarithm requires positive input, while documenting any clipping: clipping changes the score. The later implementations use stable formulas rather than blindly exponentiating large values.

## From association to decisions

If customers receiving reminders return books later, reminders may be targeted at patrons already late. The association does not establish that reminders cause delay. Covariance and correlation describe co-variation; they do not tell us what would happen if we changed one measurement or policy. A causal claim compares interventions: what would happen if reminder policy changed, holding the relevant comparison valid? Random assignment can identify a policy effect under assumptions about compliance, interference and measurement. Observational adjustment requires causal assumptions; adding many features does not automatically remove confounding.

Aleatoric uncertainty is variability in outcomes given available information. Epistemic uncertainty concerns what is unknown about the model or parameters. More representative data may reduce the latter; it cannot remove irreducible ambiguity from omitted information. These categories are useful models, not perfectly separable observable labels.

## Practice: try before revealing

On a phone, work through a question mentally or use the optional notes in Practice Q&A. On a computer, you can also run the linked lab. Compare your reasoning before marking a self-check.

Run [foundations.py](../labs/foundations.py), then alter prevalence from .01 to .10 while retaining detector rates. Expected precision becomes `.09/(.09+.09)=.5`. A detector's precision depends on the deployment population.

1. Can two uncorrelated variables be dependent? Solution: yes; let X be uniform on {-1,0,1} and Y=X². Their covariance can be zero while Y is determined by X.
2. A test has no errors in 20 cases. Is error probability zero? Solution: no. Small samples permit substantial uncertainty; report counts, intervals and sample selection.
3. Why do logs appear in language-model training? Solution: joint sequence probabilities factor into conditional probabilities; negative logs turn their product into an additive objective with gradients that penalize assigned low probability on observed outcomes.

## Interview rehearsal and vocabulary

Interview: explain the base-rate example; derive binary log loss; then design a sampling plan for subgroup confidence intervals and delayed outcomes. Vocabulary: prior, likelihood, posterior, expectation, variance, standard error, entropy, cross-entropy, KL, confounding, intervention.

## What to carry forward

Base rates, conditional probabilities and sampling determine what a prediction can establish. Loss then measures how much probability the model assigned to what happened. Next, [use that loss to adjust a model](04-optimization.md).
