"""Small paired bootstrap, illustrative rather than a product experiment."""
import random


def paired_bootstrap(a, b, repetitions=2000, seed=7):
    if len(a) != len(b) or not a:
        raise ValueError('nonempty paired samples required')
    rng = random.Random(seed)
    differences = [y-x for x,y in zip(a,b)]
    draws = sorted(sum(rng.choice(differences) for _ in differences)/len(differences)
                   for _ in range(repetitions))
    return sum(differences)/len(differences), draws[int(.025*repetitions)], draws[int(.975*repetitions)]


def main():
    print('paired uplift / bootstrap interval =', paired_bootstrap([1,0,1,0,1,0,1,0], [1,1,1,0,1,1,1,0]))
    print('illustrative sample size per arm =', 2*(1.96+.84)**2*.25/.05**2)
    print('at least one false positive in 20 null tests =', 1-.95**20)


if __name__ == '__main__':
    main()
