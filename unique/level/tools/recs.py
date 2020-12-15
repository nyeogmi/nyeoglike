from ds.vecs import V2
from enum import Enum
from typing import NamedTuple

from ..unloaded_level import SpawnType


class RoomHandle(NamedTuple):
    ident: int


class LinkType(Enum):
    Ignore = 0
    Door = 1
    Complete = 2
    Counter = 3
    # TODO: Fat door, antidoor
    # A fat door looks like this  |-    -|
    # An antidoor looks like this | ---- |


class Hint(Enum):
    # TODO: Hint for counterside tiles
    Counter = 0
    Counterside = 1


class Spawn(NamedTuple):
    spawn_type: SpawnType
    location: V2


class Grid(NamedTuple):
    # linear
    x: int
    y: int

    # constants
    cx: int
    cy: int


class Link(NamedTuple):
    link_type: LinkType
    room0: RoomHandle
    room1: RoomHandle


class RoomType(Enum):
    EntryZone = 0
    Hallway = 1
    Antechamber = 2
    LivingRoom = 3
    Bedroom = 4
    Kitchen = 5
    Bathroom = 6
    Closet = 7

    Gallery = 8

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
        elif self == RoomType.Gallery:
            return "g"


class Rule(Enum):
    RNG = 0
    Dense = 1
    # TODO: Dense should try to avoid creating corners on the outside world. ex. this is bad:
    # (Feature to detect is highlighted)
    # #####!
    # #   ####
    # #   #  #
    # #   #  #
    # #   ####
    # #   #!
    # #####


class Veto(Exception):
    pass


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
