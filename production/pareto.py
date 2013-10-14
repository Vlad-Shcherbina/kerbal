import random

from simulator import *


def pareto_filter(ds):
    def better(xs, ys):
        assert len(xs) == len(ys)
        return all(x <= y for x, y in zip(xs, ys))
    ds = list(ds)
    assert len(ds) == len(set(ds))
    new_ds = []
    for i, a in enumerate(ds):
        if any(better(b, a) for b in new_ds):
            continue
        if any(better(ds[j], a) for j in range(i+1, len(ds))):
            continue
        new_ds.append(a)
    return new_ds


def recursive_pareto_filter(d):
    if len(d) < 1000:
        return pareto_filter(d)
    d1 = []
    d2 = []
    for a in d:
        if random.randrange(2) == 0:
            d1.append(a)
        else:
            d2.append(a)
    d1 = recursive_pareto_filter(d1)
    d2 = recursive_pareto_filter(d2)
    return pareto_filter(d1 + d2)
