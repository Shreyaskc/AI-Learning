"""Tiny logistic regression and gradient checks; illustrative synthetic data only."""
import math
from foundations import finite_difference


def sigmoid(z):
    if z >= 0:
        return 1 / (1 + math.exp(-z))
    ez = math.exp(z)
    return ez / (1 + ez)


def logistic_loss(z, y):
    # softplus(z)-y*z, stable even for very large positive/negative z
    return max(z, 0) + math.log1p(math.exp(-abs(z))) - y * z


def gradients(xs, ys, w, b):
    errors = [sigmoid(w*x+b)-y for x, y in zip(xs, ys)]
    return sum(e*x for e, x in zip(errors, xs))/len(xs), sum(errors)/len(xs)


def train(xs, ys, steps=800, rate=.1):
    w, b = 0., 0.
    for _ in range(steps):
        gw, gb = gradients(xs, ys, w, b)
        w -= rate * gw
        b -= rate * gb
    return w, b


def metrics(labels, probabilities, threshold=.5):
    tp = fp = fn = tn = 0
    for y, p in zip(labels, probabilities):
        pred = p >= threshold
        tp += int(pred and y == 1)
        fp += int(pred and y == 0)
        fn += int(not pred and y == 1)
        tn += int(not pred and y == 0)
    return dict(tp=tp, fp=fp, fn=fn, tn=tn,
                precision=tp/(tp+fp) if tp+fp else 0.,
                recall=tp/(tp+fn) if tp+fn else 0.,
                brier=sum((p-y)**2 for p, y in zip(probabilities, labels))/len(labels))


def neural_loss(w1, w2=3., x=2., y=4.):
    hidden = max(0., w1*x)
    return (w2*hidden-y)**2/2


def main():
    xs, ys = [-2., -1., 1., 2.], [0, 0, 1, 1]
    gw, gb = gradients(xs, ys, .2, .1)
    numeric = finite_difference(lambda w: sum(logistic_loss(w*x+.1, y) for x,y in zip(xs,ys))/len(xs), .2)
    print('analytic/numeric weight gradient =', round(gw, 6), round(numeric, 6))
    # Split already defined: no hyperparameter or threshold selection on this test set.
    w, b = train(xs, ys)
    test_x, test_y = [-1.5, -.5, .5, 1.5], [0, 0, 1, 1]
    probabilities = [sigmoid(w*x+b) for x in test_x]
    print('weight/bias =', round(w, 6), round(b, 6))
    print('held-out probabilities =', [round(p, 6) for p in probabilities])
    print('held-out metrics =', metrics(test_y, probabilities))
    print('two-layer w1 gradient =', round(finite_difference(neural_loss, .5), 6))
    print('one logistic update =', 'w=0.1 b=0.05 p=' + str(round(sigmoid(.25), 6)))


if __name__ == '__main__':
    main()
