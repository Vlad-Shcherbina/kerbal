import json
import sys
import traceback
from timeit import default_timer
import argparse
import multiprocessing
import signal

from simulator import *
from deep_space import prepair_deep_space_solutions

import logging
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)


    parser = argparse.ArgumentParser()
    parser.add_argument('payload', type=float)
    parser.add_argument('dv', type=float)

    args = parser.parse_args()

    payload = args.payload
    required_dv = args.dv

    start = default_timer()

    deep_space_solutions = prepair_deep_space_solutions(payload, required_dv)

    best_mass = 1e10
    best_dv = None
    best_stages = []
    try:
        for ar, stages in deep_space_solutions:
            for atm_stage in Stage.all():
                try:
                    ar2, _ = ar.try_mount(atm_stage, atmosphere=True)
                except MountFailure:
                    continue
                if ar2.dv >= required_dv and ar2.takeoff_dv >= TAKEOFF_DV:
                    if ar2.mass < best_mass:
                        logger.info(
                            'found better solution: m={}, dv={}'
                            .format(ar2.mass, ar2.dv))
                        best_mass = ar2.mass
                        best_dv = ar2.dv
                        best_stages = stages[:]
    except KeyboardInterrupt as e:
        traceback.print_exc()

    print '=' * 30
    print best_mass, best_dv
    print json.dumps(map(Stage.to_json, best_stages), indent=4)
    print 'it took {:.1f}s'.format(default_timer() - start)
