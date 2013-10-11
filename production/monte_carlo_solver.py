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
        if k % 100000 == 0:
            if time.time() > end:
                break
            print '{:.1f}s remaining ...'.format(end - time.time())
        num_stages = random.randrange(1, 5)
        stages = [random.choice(all_stages) for _ in range(num_stages)]

        if not check_rocket(stages):
            continue

        dyns = simulate(payload, stages)
        m = payload + total_mass(stages)
        dv = sum(dyn.dv for dyn in dyns)

        if not check_accel_condition(dyns):
            continue
        if not check_takeoff_condition(dyns):
            continue

        if best_solution is None:
            if dv > best_dv:
                print 'found improvement', dv
                best_dv = dv

        if dv >= required_dv + 1e-3:
            print 'found solution', m, dv
            if m < best_mass:
                print 'BEST SOLUTION', m, dv
                best_dv = dv
                best_mass = m
                best_solution = json.dumps(map(Stage.to_json, stages), indent=4)

    print '-' * 20
    print best_mass, best_dv
    print best_solution
