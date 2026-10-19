# 01 · What AI systems learn

Prerequisite: basic programming. Outcomes: distinguish AI terms, frame a learning problem, and make a split before fitting anything.

## From rules to learned functions

Artificial intelligence is a broad field concerned with tasks associated with intelligent behavior, including search, planning and learning. Machine learning is a family of methods that improves a behavior using data. Deep learning uses neural networks with multiple learned transformations. Generative models describe or sample data distributions; discriminative models predict targets or decision boundaries. These categories overlap: a language model is generative, but can also classify a ticket.

A rule-based library system might flag a book as overdue when `today > due_date`. That rule is clear and exact. Predicting whether a patron will return a book late is different: patterns are uncertain and context changes. We might learn a function `f_theta(x)` where x contains information known now and theta is a collection of adjustable numbers called parameters. A target y records what happened later. An example is one pair (x,y), a feature is a measurable input, and a dataset is a collection of examples.

Training selects parameters using examples and an objective. Inference applies selected parameters to new input. Hyperparameters configure the training procedure or model family, such as tree depth or learning rate; validation helps choose them. Training does not automatically continue when someone uses a deployed model. A product may log feedback for later retraining, subject to its policy.

Supervised learning uses labeled targets. Regression predicts numbers such as return delay; classification predicts categories such as late/on-time. Unsupervised learning seeks structure without that target, such as clusters. Self-supervised learning derives a training target from the data itself, such as hiding a word or predicting the next token. Reinforcement learning learns actions through rewards over sequences of interactions. A reward is a measurement chosen by a designer, not a direct measurement of human benefit.

## The first contract: what information exists when?

Suppose each row is a checkout. You predict lateness at checkout time. `number_of_past_late_returns` may be legitimate if computed using history then available. `final_reminder_count` is not: reminders happen after checkout. A model can learn the latter perfectly and still be unusable. This is target leakage.

Before training, write: unit of prediction, decision time, target definition, target observation delay, eligible population, action taken, and success measure. For a support queue, the unit might be a ticket at arrival, target urgent/not-urgent adjudicated within two days, and action ordering human review. Customer satisfaction is a downstream outcome, not interchangeable with classification accuracy.

Separate training data (fit parameters), validation data (select model and thresholds), and a test set (final estimate after choices are frozen). If deployment predicts the future, split chronologically. If multiple rows belong to one customer, consider group separation to measure generalization to unseen customers. The right split mirrors the intended use; there is no universally correct random split.

Learn preprocessing only from training data. A mean, vocabulary, feature selector or imputation value is a fitted parameter too. In cross-validation, repeat the entire fitted pipeline inside each training fold. See the [scikit-learn leakage guide](https://scikit-learn.org/stable/common_pitfalls.html) for this distinction.

## A worked baseline

Imagine 100 tickets, 10 urgent. An always-normal classifier is 90% accurate and catches zero urgent cases. If humans can review only 15 tickets daily, a useful objective could be urgent cases found in the top 15, with a strict latency budget. Compare against a simple keyword rule, existing queue order, and human-only processing before building an LLM agent.

The baseline is a reference behavior. An ablation removes one component to learn its contribution. A deployment is a socio-technical system: data collection, prediction, action, feedback and human ownership. A better offline score may not improve the action if the queue is already capacity constrained.

## Practice and solutions

1. Is clustering unlabeled support tickets a classifier? Solution: not by itself; it produces groups without supervised urgency labels. A human mapping groups to categories adds a separate decision step.
2. A model predicts churn using `account_closed_at`. What is wrong? Solution: closure is likely the target or a future consequence. Remove it and audit timestamps and feature lineage.
3. Why retain a test set if cross-validation exists? Solution: repeated choices using CV scores can overfit those scores; a held-out final set gives a less selection-biased estimate if truly untouched.

Run [foundations.py](../labs/foundations.py). Trace the synthetic split and confusion-count example. The tiny labels are instructional, not a benchmark.

## Explain in an interview

**Basic:** training versus inference. Answer anchor: parameter selection versus applying selected parameters; show an example.

**Deeper:** why might a random split overestimate future performance? Answer anchor: repeated entities, temporal dependencies, policy changes, or post-decision information.

**Senior:** a stakeholder asks for “AI.” What do you do? Answer anchor: clarify decision, action, measurable value, data availability, risks, baseline and stop criteria before choosing model complexity.

Vocabulary: parameter, hyperparameter, feature, target, label, inference, supervised, unsupervised, self-supervised, reinforcement learning, baseline, leakage.
