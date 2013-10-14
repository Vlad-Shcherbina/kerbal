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


def pareto_frontier(ds):
    assert all(isinstance(d, tuple) for d in ds)
    ds = sorted(ds)
    fs = []
    for d in ds:
        if any(all(x <= y for x, y in zip(f, d)) for f in fs):
            continue
        fs.append(d)
    return fs
