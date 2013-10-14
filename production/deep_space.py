from simulator import *
from pareto import recursive_pareto_filter

import logging
logger = logging.getLogger(__name__)


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

    for num_stages in range(1, MAX_STAGES+1):
        logger.info('Stage {}'.format(num_stages))
        cnt = 0
        for ar, stages in d.items():
            if ar.num_stages == num_stages - 1:
                cnt += 1
                for stage in Stage.all():
                    try:
                        ar2, _ = ar.try_mount(stage, atmosphere=False)
                    except MountFailure as e:
                        continue
                    if ar2.dv <= required_dv - TAKEOFF_DV:
                        d[ar2] = stages + [stage]
        if cnt == 0:
            break
        logger.info('{} points'.format(len(d)))
        d = recursive_pareto_filter(d, ar_better)
        logger.info('{} pareto-optimal points'.format(len(d)))

    return d


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    d = prepair_deep_space_solutions(10.4, 9000)
    exit()

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
