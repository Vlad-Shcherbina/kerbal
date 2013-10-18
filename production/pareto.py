import random

from simulator import *


def naive_pareto_frontier(ds, key=lambda d:d):
    def better(a, b):
        ka = key(a)
        kb = key(b)
        assert len(kb) == len(kb)
        return all(x <= y for x, y in zip(ka, kb))

    ds = list(ds)
    result = []
    for d in ds:
        result = [r for r in result if not better(d, r)]
        if not any(better(r, d) for r in result):
            result.append(d)
    return result


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
