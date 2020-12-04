from ds.gensym import Gensym, Sym
from typing import Dict, NamedTuple

from ..level import UnloadedLevel
from ..level.gen import apartment
from .realtor import Demand, Realtor


class LevelHandle(NamedTuple):
    ident: Sym


class Levels(object):
    def __init__(self):
        self._all: Dict[LevelHandle, UnloadedLevel] = {}
        self._sym = Gensym("LVL")

        self._realtor_apartments = Realtor(apartment)

    def get(self, level: LevelHandle) -> UnloadedLevel:
        assert isinstance(level, LevelHandle)
        assert level in self._all
        return self._all[level]

    def generate_apartment(self, demand: Demand) -> LevelHandle:
        assert isinstance(demand, Demand)
        level = self._realtor_apartments.gen(demand)
        handle = LevelHandle(self._sym.gen())
        self._all[handle] = level
        return handle
