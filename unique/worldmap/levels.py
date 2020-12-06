from ds.gensym import Gensym, Sym
from typing import Dict, NamedTuple

from ..level import UnloadedLevel
from ..level.gen import residence, restaurant
from .realtor import Demand, Realtor

from enum import Enum


class LevelHandle(NamedTuple):
    ident: Sym


class ZoneType(Enum):
    Residence = 0
    Restaurant = 1


class Zoning(NamedTuple):
    zone_type: ZoneType
    demand: Demand


class Levels(object):
    def __init__(self):
        self._zoning: Dict[LevelHandle, Zoning] = {}
        self._generation: Dict[LevelHandle, UnloadedLevel] = {}
        self._sym = Gensym("LVL")

        self._realtors: Dict[ZoneType, Realtor] = {
            ZoneType.Residence: Realtor(residence),
            ZoneType.Restaurant: Realtor(restaurant),
        }

    def get(self, level: LevelHandle) -> UnloadedLevel:
        assert isinstance(level, LevelHandle)

        if level not in self._generation:
            assert level in self._zoning
            zoning = self._zoning[level]
            self._generation[level] = self._realtors[zoning.zone_type].gen(zoning.demand)

        return self._generation[level]

    def zone(self, zone_type: ZoneType, demand: Demand) -> LevelHandle:
        assert isinstance(zone_type, ZoneType)
        assert isinstance(demand, Demand)
        handle = LevelHandle(self._sym.gen())
        self._zoning[handle] = Zoning(zone_type, demand)
        return handle
