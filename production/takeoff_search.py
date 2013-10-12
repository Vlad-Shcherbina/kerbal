from simulator import *

max_mass = max(
    stage.engine.thrust*stage.num_engines/MIN_TAKEOFF_ACCEL - stage.m_start()
    for stage in Stage.all())

print max_mass


def find_takeoff(max_depth, ar, required_dv, allowed_stages=None):
    if allowed_stages is None:
        allowed_stages = Stage.all()

    simple_ar = ar._replace(can_mount_sides=True, need_large_decoupler=False)
    filtered_allowed_stages = []
    for stage in allowed_stages:
        try:
            new_ar, accel = simple_ar.try_mount(stage, atmosphere=False)
        except MountFailure:
            continue
        if accel >= MIN_TAKEOFF_ACCEL:
            filtered_allowed_stages.append(stage)

    allowed_stages = filtered_allowed_stages
    #if ar.num_stages <= 2:
    #    print ' * ' * ar.num_stages, len(allowed_stages)

    for stage in allowed_stages:
        try:
            new_ar, accel = ar.try_mount(stage, atmosphere=True)
        except MountFailure:
            continue

        if accel >= MIN_TAKEOFF_ACCEL and new_ar.dv >= required_dv:
            yield [stage]

    if max_depth <= 1:
        return

    for stage in allowed_stages:
        #if ar.num_stages <= 2:
        #    print ' * ' * ar.num_stages
        try:
            new_ar, accel = ar.try_mount(stage, atmosphere=False)
        except MountFailure as e:
            continue

        if accel < MIN_TAKEOFF_ACCEL:
            continue

        if new_ar.mass > max_mass + 1e-6:
            #print 'mass cut'
            continue

        for stages in find_takeoff(max_depth-1, new_ar, required_dv, allowed_stages):
            yield [stage] + stages



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
        for s in find_takeoff(2, ar, required_dv):
            #print stages + s
            cnt += 1

        print cnt, 'total'
