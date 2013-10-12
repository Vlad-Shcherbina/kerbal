import json
from collections import OrderedDict

from nose.tools import assert_almost_equal

from simulator import Stage, simulate


def run_rocket_tests():
    with open('../data/rocket_tests.json') as fin:
        tests = json.load(fin, object_pairs_hook=OrderedDict)

    for test in tests:
        stages = map(Stage.from_json, test['rocket'])
        payload = test['payload']
        ar, dyns = simulate(payload, stages)
        print dyns
        test['resulting_dyns'] = map(repr, dyns)

        expected_dv = test['expected_total_dv']
        assert_almost_equal(ar.dv, expected_dv, delta=1e-3)


    with open('../data/rocket_tests.json', 'w') as fout:
        json.dump(tests, fout, indent=4)
