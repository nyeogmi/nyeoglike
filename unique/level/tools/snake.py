from enum import Enum
from .carve import Carve
from .recs import RoomHandle, RoomType, Rule

from contextlib import contextmanager

from typing import List, Optional


import random
from ds.vecs import V2


class Cardinal(Enum):
    North = 0
    East = 1
    South = 2
    West = 3

    def right(self):
        return Cardinal((self.value + 1) % 4)

    def left(self):
        return Cardinal((self.value - 1) % 4)

    @classmethod
    def all_shuffled(cls) -> List["Cardinal"]:
        base = [Cardinal.North, Cardinal.East, Cardinal.South, Cardinal.West]
        random.shuffle(base)
        return base


class Snake(object):
    def __init__(self, carve: Carve, room: RoomHandle, direction: Cardinal):
        self._carve = carve
        self._room = room
        self._direction = direction

    @contextmanager
    def veto_point(self):
        # TODO: Do anything else on veto?
        carve = self._carve
        room = self._room
        direction = self._direction
        with self._carve.veto_point() as vetoed:
            yield vetoed

        if vetoed:
            self._carve = carve
            self._room = room
            self._direction = direction

    def veto(self):
        self._carve.veto()

    def branch(self):
        return Snake(self._carve, self._room, self._direction)

    def turn_right(self):
        self._direction = self._direction.right()

    def turn_left(self):
        self._direction = self._direction.left()

    def tunnel(self, size: V2, room_type: RoomType, min_contact: Optional[int] = None, use_ignore: bool = False, rule: Rule = Rule.RNG):
        if self._direction in [Cardinal.East, Cardinal.West]:
            # Swap components for L/R
            size = V2.new(size.y, size.x)

        if self._direction == Cardinal.North:
            room = self._carve.tunnel_north(self._room, size, room_type, min_contact=min_contact, use_ignore=use_ignore, rule=rule)
        elif self._direction == Cardinal.East:
            room = self._carve.tunnel_east(self._room, size, room_type, min_contact=min_contact, use_ignore=use_ignore, rule=rule)
        elif self._direction == Cardinal.South:
            room = self._carve.tunnel_south(self._room, size, room_type, min_contact=min_contact, use_ignore=use_ignore, rule=rule)
        elif self._direction == Cardinal.West:
            room = self._carve.tunnel_west(self._room, size, room_type, min_contact=min_contact, use_ignore=use_ignore, rule=rule)
        else:
            raise AssertionError("direction: {}".format(self._direction))

        self._room = room
        return room

