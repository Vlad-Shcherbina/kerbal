import random

from simulator import *


def naive_pareto_frontier(ds):
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


def pareto_frontier(ds, key=lambda d:d):
    assert all(isinstance(key(d), tuple) for d in ds)
    ds = sorted(ds, key=key)
    frontier = []
    result = []
    for d in ds:
        k = key(d)
        if any(all(x <= y for x, y in zip(f, k)) for f in frontier):
            continue
        frontier.append(k)
        result.append(d)
    return result
