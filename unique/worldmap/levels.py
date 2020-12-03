from ds.gensym import Gensym, Sym
from typing import Dict, NamedTuple

from ..level import UnloadedLevel
from ..level.gen import apartment
from .realtor import Realtor


class LevelHandle(NamedTuple):
    ident: Sym


class Levels(object):
    def __init__(self):
        self._all: Dict[LevelHandle, UnloadedLevel] = {}
        self._sym = Gensym("LVL")

        self._realtor_apartments = Realtor(apartment)
