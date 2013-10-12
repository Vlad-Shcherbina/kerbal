# How to run:
#     python -u monte_carlo_solver.py 10.4 7000 | grep -e "\(BEST.*\|\)"

import sys
import random
from simulator import *
import json
from multiprocessing import Process, Queue
import time


TIME_LIMIT = 110


if __name__ == '__main__':
    random.seed(42)

    payload = 10.4
    required_dv = 7000

    try:
        payload, required_dv = map(float, sys.argv[1:])
    except:
        print 'Usage:'
        print '    monte_carlo_solver.py <payload> <dv>'
        print
        raise

    all_stages = list(Stage.all())

    best_dv = 0
    best_mass = 1e10
    best_solution = None

    start = time.time()
    end = start + TIME_LIMIT

    k = 0
    while True:
        k += 1
        if k % 1000000 == 0:
            t = time.time()
            if t > end:
                break
            print '{:.0f} tests per second;  {:.1f}s remaining ...'.format(
                k / (t - start), end - t)
        num_stages = random.randrange(1, 5)
        stages = [random.choice(all_stages) for _ in range(num_stages)]

        try:
            ar, dyns = simulate(payload, stages)
        except MountFailure:
            continue

        if not check_takeoff_condition(dyns):
            continue

        if best_solution is None:
            if ar.dv > best_dv:
                print '* found improvement', ar.dv
                best_dv = ar.dv

        if ar.dv >= required_dv + 1e-3:
            if ar.mass < best_mass:
                print '*** BEST SOLUTION', ar.mass, ar.dv
                best_dv = ar.dv
                best_mass = ar.mass
                best_solution = json.dumps(map(Stage.to_json, stages), indent=4)

    print '-' * 20
    print best_mass, best_dv
    print best_solution
