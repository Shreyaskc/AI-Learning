"""Numeric multimodal orientation; no model/audio/image loading."""
import math
from foundations import softmax


def noise_sample(clean, retained_signal, noise):
    if not 0 < retained_signal <= 1:
        raise ValueError('retained signal must be in (0,1]')
    return math.sqrt(retained_signal)*clean + math.sqrt(1-retained_signal)*noise


def main():
    probabilities = softmax([1.,0.])
    print('correct-pair probability/loss =', probabilities[0], -math.log(probabilities[0]))
    noisy = noise_sample(2., .64, 1.)
    print('noisy/reconstructed scalar =', noisy, (noisy-math.sqrt(.36))/math.sqrt(.64))
    print('word error rate =', (1+1+0)/10)


if __name__ == '__main__':
    main()
