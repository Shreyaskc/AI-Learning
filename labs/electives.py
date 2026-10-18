"""Tiny horizon and ranking examples; no external data."""
from foundations import dot
from retrieval import ranking_metrics


def main():
    history = [10,12,11,13]
    errors = [abs(current-previous) for previous,current in zip(history,history[1:])]
    print('last-value forecast MAE =', sum(errors)/len(errors))
    print('recommendation ranking =', ranking_metrics(['B','A','C'], {'A','C'}))
    print('factor score =', dot([1,.5], [.2,.8]))


if __name__ == '__main__':
    main()
