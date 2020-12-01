from ds.relational import OneToMany
from ds.vecs import V2, R2
from ds.gensym import FastGensym
from typing import Dict, List, NamedTuple, Optional, Union
from io import StringIO

import random
from contextlib import contextmanager


# TODO: Faster representation
class RoomHandle(NamedTuple):
    ident: int


class CreateRoom(NamedTuple):
    pass


class CarveTile(NamedTuple):
    position: V2
    old_owner: RoomHandle
    new_owner: RoomHandle


CarveOp = Union[CreateRoom, CarveTile]


class Veto(Exception): pass


# TODO: Support random permutation of this
class Carve(object):
    def __init__(self):
        self._rooms = FastGensym()
        self._room_tiles: OneToMany[RoomHandle, V2] = OneToMany()

        self._room_frozen = set()

        self._operation_log = []

    @contextmanager
    def _veto_point(self):
        pt = len(self._operation_log)
        try:
            yield
        except Veto as v:
            while len(self._operation_log) > pt:
                self._undo_op(self._operation_log.pop())

    def _veto(self):
        raise Veto

    def create_room(self) -> RoomHandle:
        return self._do_log(CreateRoom())

    def carve_point(self, v2: V2, new_owner: Optional[RoomHandle]):
        old_owner = self._room_tiles.get_a(v2)
        self._do_log(CarveTile(position=v2, old_owner=old_owner, new_owner=new_owner))

    def _do_log(self, operation: CarveOp):
        self._operation_log.append(operation)
        return self._do_op(operation)

    def _do_op(self, operation: CarveOp):
        if isinstance(operation, CreateRoom):
            return RoomHandle(self._rooms.gen())
        elif isinstance(operation, CarveTile):
            if operation.new_owner is None:
                self._room_tiles.remove_b(operation.position)
            else:
                self._room_tiles.add(operation.new_owner, operation.position)
        else:
            raise AssertionError("what is {}?".format(operation))

    def _undo_op(self, operation: CarveOp):
        if isinstance(operation, CreateRoom):
            self._rooms.gen()
        elif isinstance(operation, CarveTile):
            if operation.old_owner is None:
                self._room_tiles.remove_b(operation.position)
            else:
                self._room_tiles.add(operation.old_owner, operation.position)
        else:
            raise AssertionError("what is {}?".format(operation))

    def carve(self, r: R2, ignore: List[RoomHandle] = None) -> Optional[RoomHandle]:
        with self._veto_point():
            ignore = ignore or []
            assert isinstance(ignore, List)
            assert isinstance(r, R2)

            h = self.create_room()

            affected_rooms = set()
            for v in r.expand(V2.new(1, 1)):
                existing_room = self._room_tiles.get_a(v)
                if existing_room in ignore:
                    continue

                if existing_room in self._room_frozen:
                    self._veto()

                affected_rooms.add(existing_room)

                if v in r:
                    self.carve_point(v, h)
                else:
                    self.carve_point(v, None)

            for r in affected_rooms:
                if r in self._room_frozen:
                    self._veto()

            return h

    def to_s(self):
        carved = {}
        for room, v in self._room_tiles.all():
            carved[v] = room

        if len(carved) == 0:
            mn_x, mn_y, mx_x, mx_y = 0, 0, 0, 0
        else:
            mn_x = min(xy.x for xy in carved)
            mn_y = min(xy.y for xy in carved)
            mx_x = max(xy.x for xy in carved)
            mx_y = max(xy.y for xy in carved)

        s = StringIO()
        for y in range(mn_y - 1, mx_y + 2):
            for x in range(mn_x - 1, mx_x + 2):
                room = carved.get(V2.new(x, y))
                if room:
                    room_tile = chr(ord("A") + (room.ident % 26))
                else:
                    room_tile = None
                if room_tile:
                    s.write(room_tile)
                else:
                    needed = False
                    for x1 in range(-1, 2):
                        for y1 in range(-1, 2):
                            if V2.new(x + x1, y + y1) in carved:
                                needed = True
                    if needed:
                        s.write("-")
                    else:
                        s.write(" ")
            s.write("\n")
        return s.getvalue().strip("\n")


def floorplan() -> Carve:
    living_room_width = random.randrange(6, 12)
    living_room_height = random.randrange(6, 8)

    xy0 = V2.new(0, 0)
    xy1 = V2.new(living_room_width, living_room_height)
    living_room = xy0.to(xy1)

    bedroom_width = random.randrange(6, 8)
    bedroom_depth = random.randrange(5, 7)

    n_bedrooms = random.choice([1, 1, 1, 2, 2, 3])

    width_hallway = random.randint(2, 3)
    len_hallway = (bedroom_width + 1) * n_bedrooms
    y_hallway = random.randrange(0, living_room_height - width_hallway)

    hallway = V2.new(living_room_width, y_hallway).to(V2.new(living_room_width + len_hallway, y_hallway + width_hallway))

    carve = Carve()
    living_room = carve.carve(living_room)
    carve.carve(hallway, ignore=[living_room])

    rooms_orientation = random.choice([0, 1, 2])

    br_x = hallway.top.x
    for i in range(n_bedrooms):
        if rooms_orientation in [0, 2]:
            bedroom_tr = V2.new(br_x + 1, hallway.top.y - bedroom_depth - 1)
            bedroom_bl = V2.new(br_x + 1 + bedroom_width, hallway.top.y - 1)
            carve.carve(bedroom_tr.to(bedroom_bl))
        if rooms_orientation in [1, 2]:
            bedroom_tr = V2.new(br_x + 1, hallway.bot_exclusive.y + 1)
            bedroom_bl = V2.new(br_x + 1 + bedroom_width, hallway.bot_exclusive.y + 1 + bedroom_depth)
            carve.carve(bedroom_tr.to(bedroom_bl))

        br_x += bedroom_width + 1

    have_master_bedroom = random.choice([False, True, True]) if n_bedrooms > 1 else False  # TODO: Randomize
    if have_master_bedroom:
        mbr_tr = V2.new(br_x + 1, hallway.top.y - (random.randint(2, 3) if rooms_orientation in [1, 2] else 0))
        mbr_bl = V2.new(br_x + 1 + bedroom_depth, hallway.bot_exclusive.y + (random.randint(1, 3) if rooms_orientation in [1, 2] else 0))
        carve.carve(mbr_tr.to(mbr_bl))

    return carve

