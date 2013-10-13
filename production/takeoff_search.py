from simulator import *
from pareto import pareto_filter


efficient_engines = {}
for stage in Stage.all():
    gisp = stage.engine.isp_vac * G
    max_mass = stage.num_engines * stage.engine.thrust / MIN_TAKEOFF_ACCEL
    efficient_engines[max_mass, gisp] = None

efficient_engines = pareto_filter(
    efficient_engines,
    lambda (m1, gisp1), (m2, gisp2): m1 >= m2 and gisp1 >= gisp2)

efficient_engines = sorted(efficient_engines)
#for m, gisp in sorted(efficient_engines):
#    print m, gisp
#exit()


def find_takeoff(max_depth, ar, required_dv, allowed_stages=None, max_mass=1e10):

    def filter_allowed_stages(ar, allowed_stages):
        simple_ar = ar._replace(can_mount_sides=True, need_large_decoupler=False)
        filtered_allowed_stages = []
        for stage in allowed_stages:
            try:
                new_ar, accel = simple_ar.try_mount(stage, atmosphere=False)
            except MountFailure:
                continue
            if accel >= MIN_TAKEOFF_ACCEL:
                filtered_allowed_stages.append(stage)
        return filtered_allowed_stages

    if allowed_stages is None:
        allowed_stages = Stage.all()

    best_mass = [max_mass]
    best_stages = [None]

    def rec(max_depth, prev_stages, ar, allowed_stages):
        if ar.mass >= best_mass[0]:
            return

        potential_dv = 0
        prev_m = ar.mass
        for m, gisp in efficient_engines:
            if m < ar.mass:
                continue
            potential_dv += log(min(m, best_mass[0])/prev_m) * gisp
            if m >= best_mass[0]:
                break
            prev_m = m
        if ar.dv + potential_dv < required_dv:
            return

        allowed_stages = filter_allowed_stages(ar, allowed_stages)

        for stage in allowed_stages:
            try:
                new_ar, accel = ar.try_mount(stage, atmosphere=True)
            except MountFailure:
                continue

            if accel >= MIN_TAKEOFF_ACCEL and new_ar.dv >= required_dv:
                if new_ar.mass < best_mass[0]:
                    best_mass[0] = new_ar.mass
                    best_stages[0] = prev_stages + [stage]

        if max_depth <= 1:
            return
        for stage in allowed_stages:
            try:
                new_ar, accel = ar.try_mount(stage, atmosphere=False)
            except MountFailure as e:
                continue

            if accel < MIN_TAKEOFF_ACCEL:
                continue

            rec(max_depth-1, prev_stages + [stage], new_ar, allowed_stages)

    rec(max_depth, [], ar, allowed_stages)
    return best_stages[0]


if __name__ == '__main__':

    required_dv = 7000

    ar = AbstractRocket.make_payload(10.4)
    d = {ar: []}
    stages = [Stage.from_json({
        "fuel": "FL-T100 Fuel Tank",
        "engine": "LV-T30 Liquid Fuel Engine",
        "central": True,
        "numSideParts": 2,
        "numEngines": 1,
        "height": 3
    })]
    for stage in stages:#Stage.all():
        try:
            new_ar, _ = ar.try_mount(stage)
        except MountFailure:
            continue
        if new_ar.dv <= required_dv - TAKEOFF_DV:
            d[new_ar] = [stage]

    for ar, stages in d.items():
        cnt = 0
        print 'looking for takeoff for', ar
        print find_takeoff(2, ar, required_dv)
