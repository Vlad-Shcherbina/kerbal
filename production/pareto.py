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


def ar_better(ar1, ar2):
    return (
        ar1.height <= ar2.height and
        ar1.num_stages <= ar2.num_stages and
        ar1.can_mount_sides >= ar2.can_mount_sides and
        ar1.need_large_decoupler <= ar2.need_large_decoupler and
        ar1.dv >= ar2.dv and
        ar1.mass <= ar2.mass)


def prepair_deep_space_solutions(payload, required_dv):
    ar = AbstractRocket.make_payload(payload)
    d = {ar: []}

    for num_stages in range(1, 10):
        print '*', num_stages
        cnt = 0
        for ar, stages in d.items():
            if ar.num_stages == num_stages - 1:
                cnt += 1
                for stage in Stage.all():
                    stages2 = stages + [stage]
                    try:
                        ar, _ = simulate(payload, stages2)
                    except MountFailure:
                        continue
                    if ar.dv <= required_dv - TAKEOFF_DV:
                        d[ar] = stages2
        if cnt == 0:
            break
        print len(d)
        d = recursive_pareto_filter(d, ar_better)
        print len(d)

    return d


if __name__ == '__main__':
    d = prepair_deep_space_solutions(10.4, 7000)

    import matplotlib.pyplot as plt

    for i in range(10):
        xs = []
        ys = []
        for ar in d:
            if ar.num_stages == i:
                xs.append(ar.mass)
                ys.append(ar.dv)

        plt.plot(xs, ys, '.')

    plt.show()
