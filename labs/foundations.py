"""Offline foundations: run python3 labs/foundations.py from the repo root."""
import math


def dot(a, b):
    if len(a) != len(b):
        raise ValueError('dot product requires equal dimensions')
    return sum(x * y for x, y in zip(a, b))


def cosine(a, b):
    norm = math.sqrt(dot(a, a) * dot(b, b))
    if norm == 0:
        raise ValueError('cosine is undefined for a zero vector')
    return dot(a, b) / norm


def softmax(scores):
    if not scores or max(scores) == -math.inf:
        raise ValueError('need at least one unmasked score')
    peak = max(scores)
    values = [math.exp(s - peak) for s in scores]
    return [v / sum(values) for v in values]


def posterior_positive(prevalence, sensitivity, false_positive_rate):
    for v in (prevalence, sensitivity, false_positive_rate):
        if not 0 <= v <= 1:
            raise ValueError('probabilities must be in [0,1]')
    numerator = prevalence * sensitivity
    denominator = numerator + (1 - prevalence) * false_positive_rate
    if not denominator:
        raise ValueError('positive event has zero probability')
    return numerator / denominator


def finite_difference(function, x, step=1e-5):
    return (function(x + step) - function(x - step)) / (2 * step)


def split_then_scale(train, test):
    """Fit population mean/std on training values only, then transform both sets."""
    mean = sum(train) / len(train)
    std = math.sqrt(sum((x - mean) ** 2 for x in train) / len(train))
    if std == 0:
        std = 1.0
    return ([((x - mean) / std) for x in train],
            [((x - mean) / std) for x in test], mean, std)


def main():
    print('dot =', dot([1, 2], [3, 4]))
    print('cosine =', round(cosine([1, 0], [1, 1]), 6))
    print('softmax =', [round(x, 6) for x in softmax([0, math.log(3)])])
    print('rare fault precision =', round(posterior_positive(.01, .9, .1), 6))
    print('squared error gradient =', round(finite_difference(lambda w: (2*w-5)**2/2, 1), 6))
    train_z, test_z, mean, std = split_then_scale([1, 2, 3], [100])
    print('training-only mean/std =', mean, round(std, 6))
    print('future outlier transformed =', round(test_z[0], 6))
    tp, fp, fn, tn = 0, 0, 10, 90
    print('always-normal accuracy/recall =', (tp+tn)/(tp+fp+fn+tn), tp/(tp+fn))


if __name__ == '__main__':
    main()
