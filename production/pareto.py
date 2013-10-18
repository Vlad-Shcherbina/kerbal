import random
import multiprocessing

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


def _better(a, b):
    for i in range(len(a)):
        if a[i] > b[i]:
            return False
    return True


def pareto_frontier(ds, key=lambda d:d):
    assert all(isinstance(key(d), tuple) for d in ds)
    ds = sorted(ds, key=key)
    frontier = []
    result = []
    for d in ds:
        k = key(d)
        if any(_better(f, k) for f in frontier):
            continue
        frontier.append(k)
        result.append(d)
    return result


def _pareto_shard((ks, shard)):
    result = []
    for d in shard:
        if not any(_better(k, d) and k != d for k in ks):
            result.append(d)
    return result


def parallel_pareto_frontier(ds, key=lambda d:d, pool=None):
    keys = map(key, ds)
    keys.sort(key=lambda k: k[::-1])

    if pool is None:
        pool = multiprocessing.Pool()
    n = pool._processes
    shards = [keys[i::n] for i in range(n)]

    shards = pool.imap_unordered(pareto_frontier, shards)

    result = []
    for ks in pool.imap_unordered(pareto_frontier, shards):
        result.extend(ks)

    result = list(set(result))
    shards = [(result, result[i::n]) for i in range(n)]
    frontier = []
    for r in pool.imap_unordered(_pareto_shard, shards):
        frontier.extend(r)

    frontier = set(frontier)
    result = []
    for d in ds:
        if not frontier:
            break
        k = key(d)
        if k in frontier:
            frontier.remove(k)
            result.append(d)
    return result
