from ds.vecs import V2, R2
from ds.gensym import Gensym, Sym
from typing import Dict, NamedTuple
from io import StringIO

import random


# TODO: Support random permutation of this
class Carve(object):
    def __init__(self):
        self._carved = set()

    def carve(self, xy: V2):
        assert isinstance(xy, V2)
        self._carved.add(xy)

    def uncarve(self, xy: V2):
        assert isinstance(xy, V2)
        self._carved.discard(xy)

    def to_s(self):
        if len(self._carved) == 0:
            mn_x, mn_y, mx_x, mx_y = 0, 0, 0, 0
        else:
            mn_x = min(xy.x for xy in self._carved)
            mn_y = min(xy.y for xy in self._carved)
            mx_x = max(xy.x for xy in self._carved)
            mx_y = max(xy.y for xy in self._carved)

        s = StringIO()
        for y in range(mn_y - 1, mx_y + 2):
            for x in range(mn_x - 1, mx_x + 2):
                if V2.new(x, y) in self._carved:
                    s.write(" ")
                else:
                    needed = False
                    for x1 in range(-1, 2):
                        for y1 in range(-1, 2):
                            if V2.new(x + x1, y + y1) in self._carved:
                                needed = True
                    if needed:
                        s.write("#")
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
    for x in living_room: carve.carve(x)
    for x in hallway: carve.carve(x)

    rooms_orientation = random.choice([0, 1, 2])

    br_x = hallway.top.x
    for i in range(n_bedrooms):
        if rooms_orientation in [0, 2]:
            bedroom_tr = V2.new(br_x + 1, hallway.top.y - bedroom_depth - 1)
            bedroom_bl = V2.new(br_x + 1 + bedroom_width, hallway.top.y - 1)
            for x in bedroom_tr.to(bedroom_bl): carve.carve(x)
        if rooms_orientation in [1, 2]:
            bedroom_tr = V2.new(br_x + 1, hallway.bot_exclusive.y + 1)
            bedroom_bl = V2.new(br_x + 1 + bedroom_width, hallway.bot_exclusive.y + 1 + bedroom_depth)
            for x in bedroom_tr.to(bedroom_bl): carve.carve(x)

        br_x += bedroom_width + 1

    have_master_bedroom = random.choice([False, True, True]) if n_bedrooms > 1 else False  # TODO: Randomize
    if have_master_bedroom:
        mbr_tr = V2.new(br_x + 1, hallway.top.y - (random.randint(2, 3) if rooms_orientation in [1, 2] else 0))
        mbr_bl = V2.new(br_x + 1 + bedroom_depth, hallway.bot_exclusive.y + (random.randint(1, 3) if rooms_orientation in [1, 2] else 0))
        for x in mbr_tr.to(mbr_bl): carve.carve(x)



    # if rooms_orientation in [1, 2]:


    return carve

