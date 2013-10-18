from nose.tools import eq_
import random

from pareto import pareto_frontier, naive_pareto_frontier


def eq_unordered(a, b):
    eq_(sorted(a), sorted(b))


def check_pareto_frontier(ds, key=lambda d:d):
    """Run all implementations and compare results"""
    naive = naive_pareto_frontier(ds, key=key)
    result = pareto_frontier(ds, key=key)
    eq_unordered(map(key, naive), map(key, result))
    return result


def test_small():
    eq_(check_pareto_frontier([]), [])
    eq_unordered(check_pareto_frontier([(1, 2), (2, 2), (2, 1)]), [(1, 2), (2, 1)])
    eq_(check_pareto_frontier([(2,), (1,)]), [(1,)])


def test_key():
    def key(x):
        return x//10, x%10
    eq_unordered(check_pareto_frontier([11, 20, 31, 04], key=key), [11, 20, 04])


def test_random():
    def t(n, d, A):
        r = random.Random(42)
        ds = set(tuple(r.randrange(A) for _ in range(d)) for _ in range(n))
        print ds
        check_pareto_frontier(ds)

    yield t, 10, 1, 100
    yield t, 1000, 2, 100
    yield t, 1000, 10, 100
    yield t, 1000, 10, 3
