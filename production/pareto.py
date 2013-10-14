import random

from simulator import *


def pareto_filter(d, better):
    ars = list(d)
    new_d = {}
    for i, ar in enumerate(ars):
        if any(better(ar2, ar) for ar2 in new_d):
            continue
        if any(better(ars[j], ar) for j in range(i+1, len(ars))):
            continue
        new_d[ar] = d[ar]
    return new_d


def recursive_pareto_filter(d, better):
    if len(d) < 1000:
        return pareto_filter(d, better)
    d1 = {}
    d2 = {}
    for k, v in d.items():
        if random.randrange(2) == 0:
            d1[k] = v
        else:
            d2[k] = v
    d1 = recursive_pareto_filter(d1, better)
    d2 = recursive_pareto_filter(d2, better)
    d1.update(d2)
    return pareto_filter(d1, better)
