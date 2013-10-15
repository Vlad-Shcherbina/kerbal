from simulator import *
from pareto import pareto_frontier

import logging
logger = logging.getLogger(__name__)


# lower is better
def ar_qualities(ar):
    return (
        ar.height,
        ar.num_stages,
        -ar.can_mount_sides,
        ar.need_large_decoupler,
        -ar.dv,
        ar.mass,
        -ar.takeoff_dv)


def prepair_deep_space_solutions(payload, required_dv):
    ar = AbstractRocket.make_payload(payload)

    designs = [(ar, [])]

    for num_stages in range(1, MAX_STAGES+1):
        logger.info('Stage {}'.format(num_stages))
        cnt = 0
        for ar, stages in designs[:]:
            if ar.num_stages == num_stages - 1:
                cnt += 1
                for stage in Stage.all():
                    try:
                        ar2, _ = ar.try_mount(stage, atmosphere=False)
                    except MountFailure as e:
                        continue
                    if ar2.dv <= required_dv:
                        designs.append((ar2, stages + [stage]))
        if cnt == 0:
            break
        logger.info('{} points'.format(len(designs)))
        designs = pareto_frontier(designs, key=lambda (ar, _): ar_qualities(ar))
        logger.info('{} pareto-optimal points'.format(len(designs)))

    return designs


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    d = prepair_deep_space_solutions(10.4, 2500)
    exit()

    import matplotlib.pyplot as plt

    for i in range(10):
        xs = []
        ys = []
        for ar, _ in d:
            if ar.num_stages == i:
                xs.append(ar.mass)
                ys.append(ar.dv)

        plt.plot(xs, ys, '.')

    plt.show()
