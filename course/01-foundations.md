# 01 · What AI systems learn

Prerequisite: basic programming. Outcomes: distinguish AI terms, frame a learning problem, and make a split before fitting anything.

A support team receives 100 tickets but can review only 15 today. Can a learned score help it find urgent cases sooner? Begin with that decision; the names of model families will make more sense once you can trace inputs, predictions and actions.

## From rules to learned functions

A support ticket arrives. A hand-written rule might say: “If its text contains `outage`, put it in the urgent queue.” The program follows that rule exactly. A learned model instead uses labeled past tickets to adjust a scoring function. It may use several clues, such as prior contacts and words in the message, rather than one fixed rule.

A **feature** is an input measurement available when the ticket arrives. The **target** is the outcome we want to predict: urgent or not urgent, as later adjudicated. One **example** pairs an input x with its target y; a dataset collects many examples. The model's adjustable numbers are its **parameters**, written together as theta in `f_theta(x)`. This notation means “apply the scoring function with these currently chosen parameters.” It does not explain or guarantee what the model learned.

**Training** selects parameters using examples and a loss that measures prediction error. **Inference** applies the selected parameters to new input. Using a model does not automatically keep training it. A product may collect feedback for later retraining under its data policy.

A **hyperparameter** configures the procedure rather than being fitted in the same way as the ordinary model weights: examples include tree depth or learning rate. We will use validation data to choose such settings. For now, keep the distinction between the numbers learned inside a model and the settings used to train it.

Now place this example in the larger vocabulary. Artificial intelligence includes methods for tasks such as search, planning and learning. Machine learning is the family that improves a behavior using data. Deep learning uses neural networks with multiple learned transformations. A generative model describes or samples a data distribution; a discriminative model predicts a target or decision boundary. These categories overlap: a language model can generate a reply and also be used to classify a ticket.

The way training targets arise gives us another distinction. Supervised learning uses supplied labels, like our urgent/not-urgent judgments. Regression predicts a numeric target such as delay; classification predicts a category. Unsupervised learning seeks structure without that supervised target, such as groups of similar tickets. Self-supervised learning derives targets from the data itself, such as predicting the next token. Reinforcement learning learns actions using rewards across interactions; a reward is a chosen proxy, not a direct measurement of human benefit. These are names to recognize now; later chapters develop their mechanisms.

Transfer the same reasoning to library returns. An exact overdue rule checks whether today is after the due date. Predicting at checkout whether a patron will return late is uncertain: it needs a target defined later and features available at checkout. That change in decision time leads to the most important contract below.

## The first contract: what information exists when?

Suppose each row is a checkout. You predict lateness at checkout time. `number_of_past_late_returns` may be legitimate if computed using history then available. `final_reminder_count` is not: reminders happen after checkout. A model can learn the latter perfectly and still be unusable. This is target leakage.

Before training, write: unit of prediction, decision time, target definition, target observation delay, eligible population, action taken, and success measure. For a support queue, the unit might be a ticket at arrival, target urgent/not-urgent adjudicated within two days, and action ordering human review. Customer satisfaction is a downstream outcome, not interchangeable with classification accuracy.

Separate training data (fit parameters), validation data (select model and thresholds), and a test set (final estimate after choices are frozen). If deployment predicts the future, split chronologically. If multiple rows belong to one customer, consider group separation to measure generalization to unseen customers. The right split mirrors the intended use; there is no universally correct random split.

Learn preprocessing only from training data. A mean, vocabulary, feature selector or imputation value is a fitted parameter too. Cross-validation repeatedly holds out one portion of the development data while fitting on the others. Each held-out portion is a fold. Repeat the entire fitted pipeline inside each training fold so even preprocessing cannot learn from its held-out examples. See the [scikit-learn leakage guide](https://scikit-learn.org/stable/common_pitfalls.html) for this distinction.

## A worked baseline

Imagine 100 tickets, 10 urgent. An always-normal classifier is 90% accurate and catches zero urgent cases. If humans can review only 15 tickets daily, a useful objective could be urgent cases found in the top 15, with a strict latency budget. Compare against a simple keyword rule, existing queue order, and human-only processing before building an LLM agent.

The baseline is a reference behavior. To learn whether an added feature helps, compare the same system with that feature removed; this controlled removal is an ablation.

A prediction is only one part of the process. If people can inspect only 15 tickets, a higher test score helps only if it improves which tickets they review. Evaluate the full chain: what data arrives, what the model predicts, what action follows, and who handles mistakes. This combined human/software process is often called a socio-technical system.

## Practice: try before revealing

On a phone, work through a question mentally or use the optional notes in Practice Q&A. On a computer, you can also run the linked lab. Compare your reasoning before marking a self-check.

Run [foundations.py](../labs/foundations.py). Trace the synthetic split and confusion-count example. The tiny labels are instructional, not a benchmark.

**Basic:** training versus inference. Answer anchor: parameter selection versus applying selected parameters; show an example.

**Deeper:** why might a random split overestimate future performance? Answer anchor: repeated entities, temporal dependencies, policy changes, or post-decision information.

**Senior:** a stakeholder asks for “AI.” What do you do? Answer anchor: clarify decision, action, measurable value, data availability, risks, baseline and stop criteria before choosing model complexity.

1. Is clustering unlabeled support tickets a classifier? Solution: not by itself; it produces groups without supervised urgency labels. A human mapping groups to categories adds a separate decision step.
2. A model predicts churn using `account_closed_at`. What is wrong? Solution: closure is likely the target or a future consequence. Remove it and audit timestamps and feature lineage.
3. Why retain a test set if cross-validation exists? Solution: repeated choices using CV scores can overfit those scores; a held-out final set gives a less selection-biased estimate if truly untouched.

## Interview rehearsal and vocabulary

Vocabulary: parameter, hyperparameter, feature, target, label, inference, supervised, unsupervised, self-supervised, reinforcement learning, baseline, leakage.

## What to carry forward

A model learns a pattern from information available at a defined time. Its prediction is useful only through the decision it improves. Next, [turn those inputs into numbers](02-math.md) so you can follow the calculation instead of treating the score as magic.
