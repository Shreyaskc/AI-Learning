"""Small, explicit causal attention. Lists keep every operation visible."""
import math
from foundations import dot, softmax


def attention(queries, keys, values, causal=True):
    if not queries or len(keys) != len(values) or not keys:
        raise ValueError('nonempty keys/values must have equal sequence length')
    dim = len(keys[0])
    if not dim or any(len(k) != dim for k in keys) or any(len(q) != dim for q in queries):
        raise ValueError('query/key dimensions must agree')
    if not values[0] or any(len(v) != len(values[0]) for v in values):
        raise ValueError('value dimensions must agree')
    if causal and len(queries) != len(keys):
        raise ValueError('this toy causal implementation requires equal sequence lengths')
    weights, outputs = [], []
    for i, query in enumerate(queries):
        scores = [dot(query, key)/math.sqrt(dim) if not causal or j <= i else -math.inf
                  for j, key in enumerate(keys)]
        row = softmax(scores)
        weights.append(row)
        outputs.append([sum(row[j]*values[j][c] for j in range(len(values)))
                        for c in range(len(values[0]))])
    return weights, outputs


def sequence_loss(probabilities):
    if not probabilities or any(not 0 < p <= 1 for p in probabilities):
        raise ValueError('target probabilities must be in (0,1]')
    loss = -sum(math.log(p) for p in probabilities)/len(probabilities)
    return loss, math.exp(loss)


def main():
    q, k, v = [[1., 0.], [1., 0.]], [[1., 0.], [0., 1.]], [[2., 0.], [0., 4.]]
    weights, outputs = attention(q, k, v)
    print('causal weights =', [[round(x, 6) for x in row] for row in weights])
    print('causal outputs =', [[round(x, 6) for x in row] for row in outputs])
    changed_v = [v[0], [1000., -1000.]]
    assert attention(q, k, changed_v)[1][0] == outputs[0]
    print('future-value invariance = PASS')
    print('loss/perplexity =', [round(x, 6) for x in sequence_loss([.5, .25, .8])])
    print('full/LoRA update parameters =', 1024**2, 2*1024*8)


if __name__ == '__main__':
    main()

# A small complete block, intentionally fixed weights rather than a trained model.
def matmul(a, b):
    if not a or not b or any(len(row) != len(b) for row in a):
        raise ValueError('incompatible matrix dimensions')
    if any(len(row) != len(b[0]) for row in b):
        raise ValueError('ragged matrix')
    return [[sum(a[i][k]*b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def layer_norm(row, epsilon=1e-5):
    mean = sum(row)/len(row)
    var = sum((x-mean)**2 for x in row)/len(row)
    return [(x-mean)/math.sqrt(var+epsilon) for x in row]


def tiny_block(inputs, causal=True):
    wq = [[1., 0.], [1., 0.]]
    wk = [[1., 0.], [0., 1.]]
    wv = [[2., 0.], [0., 4.]]
    q, k, v = matmul(inputs, wq), matmul(inputs, wk), matmul(inputs, wv)
    weights, mixed = attention(q, k, v, causal=causal)
    hidden = [layer_norm([x+a for x,a in zip(row, att)]) for row,att in zip(inputs,mixed)]
    ff = [[max(0., x) for x in row] for row in hidden]
    final = [layer_norm([x+y for x,y in zip(row,f)]) for row,f in zip(hidden,ff)]
    logits = matmul(final, [[1., 0., -1.], [0., 1., 0.]])
    return dict(q=q, k=k, v=v, weights=weights, mixed=mixed, final=final,
                logits=logits, probabilities=[softmax(row) for row in logits])


if __name__ == '__main__':
    block = tiny_block([[1., 0.], [0., 1.]])
    print('block first-row probabilities =', [round(x, 6) for x in block['probabilities'][0]])
