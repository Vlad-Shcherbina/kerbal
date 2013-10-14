from nose.tools import eq_
import random

from pareto import pareto_filter


def eq_unordered(a, b):
	eq_(sorted(a), sorted(b))


def test_small():
	eq_(pareto_filter([]), [])
	eq_unordered(pareto_filter([(1, 2), (2, 2), (2, 1)]), [(1, 2), (2, 1)])
	eq_(pareto_filter([(2,), (1,)]), [(1,)])
