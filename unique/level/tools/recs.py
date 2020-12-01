from enum import Enum
from typing import NamedTuple


class RoomHandle(NamedTuple):
    ident: int


class RoomType(Enum):
    EntryZone = 0
    Hallway = 1
    Antechamber = 2
    LivingRoom = 3
    Bedroom = 4
    Kitchen = 5
    Bathroom = 6
    Closet = 7

    def tile(self) -> str:
        if self == RoomType.EntryZone:
            return "e"
        elif self == RoomType.Hallway:
            return "."
        elif self == RoomType.Antechamber:
            return "a"
        elif self == RoomType.LivingRoom:
            return "l"
        elif self == RoomType.Bedroom:
            return "b"
        elif self == RoomType.Kitchen:
            return "k"
        elif self == RoomType.Bathroom:
            return "r"
        elif self == RoomType.Closet:
            return "c"


class Rule(Enum):
    RNG = 0
    Dense = 1


class Veto(Exception): pass


class VetoBox(object):
    def __init__(self):
        self._vetoed = None

    @property
    def vetoed(self):
        if self._vetoed is None:
            raise AssertionError("can't check yet: save point not escaped")

        return self._vetoed

    def __bool__(self):
        return self.vetoed

