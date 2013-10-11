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

    def can_mount_on(self, other):
        if self.central:
            return True
        else:
            return other.num_side_parts == 0

    def decoupler_weight(self, mounted_on_large):
        if self.central:
            if mounted_on_large and self.fuel.size == LARGE:
                return 0.4
            return 0.05
        else:
            return 0.025 * self.num_side_parts

    def num_tanks(self):
        return self.height * (self.num_side_parts + int(self.central))

    def m_fuel(self):
        return (self.fuel.m_full - self.fuel.m_empty) * self.num_tanks()

    def m_start(self):
        return (
            self.num_engines * self.engine.mass +
            self.fuel.m_full * self.num_tanks())

    def gisp(self, atmosphere=False):
        if atmosphere:
            return self.engine.isp_atm# * 9.816
        else:
            return self.engine.isp_vac# * 9.816


Dyn = namedtuple('Dyn', 'dv accel')


def total_mass(stages):
    m = 0
    on_large = None

    for i, stage in enumerate(stages):
        if i != 0:
            m += stage.decoupler_weight(on_large)
        m += stage.m_start()

        if stage.central:
            on_large = stage.engine.size == LARGE

    return m


def simulate(payload, stages):
    m_start = payload
    on_large = None

    dyns = []

    for i, stage in enumerate(stages):
        if i != 0:
            m_start += stage.decoupler_weight(on_large)
        m_start += stage.m_start()
        m_end = m_start - stage.m_fuel()

        #print 'ms', m_start, m_end
        dv = log(m_start/m_end) * stage.gisp(atmosphere=(i == len(stages)-1)) * 9.816
        #print dv
        accel = stage.engine.thrust * stage.num_engines / m_start
        dyns.append(Dyn(dv, accel))

        if stage.central:
            on_large = stage.engine.size == LARGE
        first = False

    return dyns


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


def check_accel_condition(dyns):
    return all(dyn.accel >= 5 + 1e-3 for dyn in dyns)


def check_rocket(stages):
    if len(stages) > 7:
        return False
    height = 0
    for i, stage in enumerate(stages):
        if stage.central:
            height += stage.height
            if height > 7:
                return False
        if i == 0 and not stage.central:
            return False
        if i > 0 and not stage.can_mount_on(stages[i-1]):
            return False
    return True
