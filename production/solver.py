import json
import sys
import traceback
from timeit import default_timer
import argparse
import multiprocessing
import signal

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


# To avoid Ctrl-C problems.
# See http://noswap.com/blog/python-multiprocessing-keyboardinterrupt
def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def f(best_mass, depth, (ar, stages)):
    try:
        return (
            stages,
            find_takeoff(depth, ar, required_dv, max_mass=best_mass))
    except (KeyboardInterrupt, SystemExit):
        print "Exiting..."
        return stages, None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)


    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('payload', type=float)
    parser.add_argument('dv', type=float)
    parser.add_argument('--time_limit', type=float,
                       default=115,
                       help='time limit in seconds')
    parser.add_argument('--processes', type=int,
                       default=2,
                       help='')

    args = parser.parse_args()

    payload = args.payload
    required_dv = args.dv

    start = default_timer()

    d = prepair_deep_space_solutions(payload, required_dv)

    deep_space_solutions = sorted(d.items(), key=lambda (ar, _): -ar.dv)

    pool = multiprocessing.Pool(args.processes, init_worker)
    map = pool.map

    try:
        tasks = [(depth, q)
            for depth in range(3, 4+1)
            for q in deep_space_solutions]
        tasks.reverse()
        total_tasks = len(tasks)

        results = []
        prev_progress = -1
        while tasks or results:
            if default_timer() > start + args.time_limit:
                raise TimeLimit()
            while tasks and len(results) < args.processes:
                depth, q = tasks.pop()
                results.append(pool.apply_async(f, [best_mass, depth, q]))
            for result in results:
                try:
                    stages, stages2 = result.get(timeout=0.01)
                    results.remove(result)
                    if stages2 != None:
                        update_best(stages + stages2)
                    progress = 100 * (total_tasks - len(results) - len(tasks)) // total_tasks
                    if progress > prev_progress:
                        logging.info("{}%".format(progress))
                        prev_progress = progress
                except multiprocessing.TimeoutError:
                    pass

    except KeyboardInterrupt as e:
        traceback.print_exc()
    except TimeLimit:
        logging.warning('time limit')

    print '=' * 30
    print best_mass, best_dv
    print json.dumps(map(Stage.to_json, best_stages), indent=4)
    print 'it took {:.1f}s'.format(default_timer() - start)
