import json
import sys
import traceback

from simulator import *
from pareto import prepair_deep_space_solutions
from takeoff_search import find_takeoff


best_mass = 1e10
best_dv = None
best_stages = None
def update_best(stages):
    global best_mass, best_dv, best_stages
    ar, _ = simulate(payload, stages)
    if ar.mass < best_mass:
        print 'found better solution', ar.mass, ar.dv
        best_mass = ar.mass
        best_dv = ar.dv
        best_stages = stages[:]



if __name__ == '__main__':
    try:
        payload, required_dv = map(float, sys.argv[1:])
    except:
        print 'Usage:'
        print '    solver.py <payload> <dv>'
        print
        raise

    d = prepair_deep_space_solutions(payload, required_dv)
    print len(d), 'deep space solutions'

    try:
        for depth in range(1, 3+1):
            for i, (ar, stages) in enumerate(d.items()):
                if depth == 3:
                    print 100 * i / len(d), '%'
                stages2 = find_takeoff(depth, ar, required_dv, max_mass=best_mass)
                if stages2 != None:
                    update_best(stages + stages2)
    except KeyboardInterrupt as e:
        traceback.print_exc()

    print '=' * 30
    print best_mass, best_dv
    print json.dumps(map(Stage.to_json, best_stages), indent=4)
