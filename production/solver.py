import json
import sys
import traceback
from timeit import default_timer
import argparse

from simulator import *
from pareto import prepair_deep_space_solutions
from takeoff_search import find_takeoff

import logging
logger = logging.getLogger(__name__)


best_mass = 1e10
best_dv = None
best_stages = None
def update_best(stages):
    global best_mass, best_dv, best_stages
    ar, _ = simulate(payload, stages)
    if ar.mass < best_mass:
        logging.info('found better solution: m={}, dv={}'.format(ar.mass, ar.dv))
        best_mass = ar.mass
        best_dv = ar.dv
        best_stages = stages[:]


class TimeLimit(Exception):
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)


    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('payload', type=float)
    parser.add_argument('dv', type=float)
    parser.add_argument('--time_limit', type=float,
                       default=110,
                       help='time limit in seconds')

    args = parser.parse_args()

    payload = args.payload
    required_dv = args.dv

    start = default_timer()

    d = prepair_deep_space_solutions(payload, required_dv)

    deep_space_solutions = sorted(d.items(), key=lambda (ar, _): -ar.dv)

    try:
        for depth in range(3, 4+1):
            for i, (ar, stages) in enumerate(deep_space_solutions):
                if default_timer() > start + args.time_limit:
                    raise TimeLimit()
                if depth >= 3:
                    logging.info('search for depth {}: {}%'.format(
                        depth, 100 * i / len(d), '%'))
                stages2 = find_takeoff(depth, ar, required_dv, max_mass=best_mass)
                if stages2 != None:
                    update_best(stages + stages2)
    except KeyboardInterrupt as e:
        traceback.print_exc()
    except TimeLimit:
        logging.warning('time limit')

    print '=' * 30
    print best_mass, best_dv
    print json.dumps(map(Stage.to_json, best_stages), indent=4)
    print 'it took {:.1f}s'.format(default_timer() - start)
