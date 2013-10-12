"""
data Diam = Small | Large
data Fuel = F String Float Float Diam -- name m_full m_empty size

allFuels = [
  F "FL-T100 Fuel Tank" 0.5625 0.0625 Small,
  F "FL-T200 Fuel Tank" 1.125 0.125 Small,
  F "FL-T400 Fuel Tank" 2.25 0.25 Small,
  F "FL-T800 Fuel Tank" 4.5 0.5 Small,
  F "Rockomax X200-8 Fuel Tank" 4.5 0.5 Large,
  F "Rockomax X200-16 Fuel Tank" 9 1 Large,
  F "Rockomax X200-32 Fuel Tank" 18 2 Large,
  F "Rockomax Jumbo-64 Fuel Tank" 36 4 Large]

--              name   size mass  thrust  Isp_atm Isp_vac
data Engine = E String Diam Float Float   Float   Float
allEngines = [
 E "LV-T30 Liquid Fuel Engine" Small 1.25 215 320 370,
 E "LV-T45 Liquid Fuel Engine" Small 1.5  200 320 370,
 E "LV-909 Liquid Fuel Engine" Small 0.5  50  300 390,
 E "Toroidal Aerospike Rocket" Small 1.5  175 388 390,
 E "Rockomax \"Poodle\" Liquid Engine"   Large 2.5 220  270 390,
 E "Rockomax \"Mainsail\" Liquid Engine" Large 6   1500 280 330,
 E "Rockomax \"Skipper\" Liquid Engine"  Large 4   650  300 350,
 E "LV-N Atomic Rocket Engine" Small 2.25 60  220 800 ]
"""


from math import log
from collections import namedtuple, OrderedDict

MAX_HEIGHT = 7
MAX_STAGES = 7
MIN_ACCEL = 5.0 + 1e-6

# sizes
SMALL = 'Small'
LARGE = 'Large'

Fuel = namedtuple('Fuel', 'name m_full m_empty size')

ALL_FUELS = [
    Fuel("FL-T100 Fuel Tank", 0.5625, 0.0625, SMALL),
    Fuel("FL-T200 Fuel Tank", 1.125, 0.125, SMALL),
    Fuel("FL-T400 Fuel Tank", 2.25, 0.25, SMALL),
    Fuel("FL-T800 Fuel Tank", 4.5, 0.5, SMALL),
    Fuel("Rockomax X200-8 Fuel Tank", 4.5, 0.5, LARGE),
    Fuel("Rockomax X200-16 Fuel Tank", 9, 1, LARGE),
    Fuel("Rockomax X200-32 Fuel Tank", 18, 2, LARGE),
    Fuel("Rockomax Jumbo-64 Fuel Tank", 36, 4, LARGE),
]

Engine = namedtuple('Engine', 'name size mass thrust isp_atm isp_vac')

ALL_ENGINES = [
    Engine("LV-T30 Liquid Fuel Engine", SMALL, 1.25, 215, 320, 370),
    Engine("LV-T45 Liquid Fuel Engine", SMALL, 1.5,  200, 320, 370),
    Engine("LV-909 Liquid Fuel Engine", SMALL, 0.5,  50,  300, 390),
    Engine("Toroidal Aerospike Rocket", SMALL, 1.5,  175, 388, 390),
    Engine("Rockomax \"Poodle\" Liquid Engine", LARGE, 2.5, 220,  270, 390),
    Engine("Rockomax \"Mainsail\" Liquid Engine", LARGE, 6,   1500, 280, 330),
    Engine("Rockomax \"Skipper\" Liquid Engine",  LARGE, 4,   650,  300, 350),
    Engine("LV-N Atomic Rocket Engine", SMALL, 2.25, 60,  220, 800),
]

Stage = namedtuple('Stage', 'fuel engine central num_side_parts num_engines height')


class Stage(Stage):
    def to_json(self):
        d = OrderedDict()
        d['fuel'] = self.fuel.name
        d['engine'] = self.engine.name
        d['central'] = self.central
        d['numSideParts'] = self.num_side_parts
        d['numEngines'] = self.num_engines
        d['height'] = self.height
        return d

    @staticmethod
    def from_json(d):
        f, = [f for f in ALL_FUELS if f.name == d['fuel']]
        e, = [e for e in ALL_ENGINES if e.name == d['engine']]
        central = d['central']
        num_side_parts = d['numSideParts']
        assert num_side_parts in [0, 2, 3, 4, 6]
        num_engines = d['numEngines']
        if central:
            assert num_engines in [1, 1 + num_side_parts]
        else:
            assert num_engines == num_side_parts
        height = d['height']
        assert height in [1, 2, 3]
        return Stage(f, e, central, num_side_parts, num_engines, height)

    @staticmethod
    def all():
        toroidal = ALL_ENGINES[3]
        assert toroidal.name.startswith('Toroidal')
        for f in ALL_FUELS:
            for e in ALL_ENGINES:
                for height in 1, 2, 3:
                    for num_side_parts in 0, 2, 3, 4, 6:
                        if e != toroidal:
                            yield Stage(f, e, True, num_side_parts, 1, height)
                        if num_side_parts > 0:
                            if e != toroidal:
                                yield Stage(
                                    f, e, True,
                                    num_side_parts, 1 + num_side_parts, height)
                            yield Stage(
                                f, e, False,
                                num_side_parts, num_side_parts, height)

    def num_tanks(self):
        return self.height * (self.num_side_parts + int(self.central))

    def m_fuel(self):
        return (self.fuel.m_full - self.fuel.m_empty) * self.num_tanks()

    def m_start(self):
        return (
            self.num_engines * self.engine.mass +
            self.fuel.m_full * self.num_tanks())

    def gisp(self, atmosphere):
        if atmosphere:
            return self.engine.isp_atm * 9.816
        else:
            return self.engine.isp_vac * 9.816


class MountFailure(Exception):
    pass


AbstractRocket = namedtuple(
    'AbstractRocket',
    'num_stages height can_mount_sides need_large_decoupler dv mass')
class AbstractRocket(AbstractRocket):
    @staticmethod
    def make_payload(payload):
        return AbstractRocket(0, 0, False, None, 0, payload)

    def try_mount(self, stage, atmosphere=False):
        # return tuple (new_abstract_rocket, stage_accel) or raise MountFailure

        num_stages, height, can_mount_sides, need_large_decoupler, dv, mass =\
            self

        num_stages += 1
        if num_stages > MAX_STAGES:
            raise MountFailure('too many stages')

        if stage.central:
            height += stage.height
            if height > MAX_HEIGHT:
                raise MountFailure('rocket is too high')
            if self.num_stages > 0:
                if stage.fuel.size == LARGE and need_large_decoupler:
                    mass += 0.4
                else:
                    mass += 0.05
            need_large_decoupler = stage.engine.size == LARGE
            can_mount_sides = stage.num_side_parts == 0
        else:
            if not can_mount_sides:
                raise MountFailure("can't mount sides")
            mass += 0.025 * stage.num_side_parts
            can_mount_sides = False

        mass += stage.m_start()
        accel = stage.engine.thrust * stage.num_engines / mass
        if accel < MIN_ACCEL:
            raise MountFailure('acceleration is too low')

        m_end = mass - stage.m_fuel()
        dv += log(mass / m_end) * stage.gisp(atmosphere)

        new_abstract_rocket = AbstractRocket(
            num_stages, height, can_mount_sides, need_large_decoupler, dv, mass)

        return new_abstract_rocket, accel


Dyn = namedtuple('Dyn', 'dv accel')


def simulate(payload, stages):
    ar = AbstractRocket.make_payload(payload)
    prev_dv = ar.dv

    dyns = []
    for i, stage in enumerate(stages):
        ar, accel = ar.try_mount(stage, atmosphere=(i == len(stages) - 1))
        dyns.append(Dyn(ar.dv - prev_dv, accel))
        prev_dv = ar.dv
    return ar, dyns


def check_takeoff_condition(dyns):
    dv = 0
    takeoff_dv = 5000
    for dyn in reversed(dyns):
        if dyn.accel < 15 + 1e-3:
            return False
        dv += dyn.dv
        if dv >= takeoff_dv + 1e-3:
            break
    return True
