from ds.relational import OneToMany
from ds.vecs import V2, R2
from ds.gensym import FastGensym
from enum import Enum
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


class FreezeRoom(NamedTuple):
    room: RoomHandle


CarveOp = Union[CreateRoom, CarveTile, FreezeRoom]


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


# TODO: Support random permutation of this
class Carve(object):
    def __init__(self):
        self._rooms = FastGensym()
        self._room_tiles: OneToMany[RoomHandle, V2] = OneToMany()

        self._room_frozen = set()

        self._operation_log = []

    @contextmanager
    def veto_point(self):
        pt = len(self._operation_log)
        box = VetoBox()
        try:
            yield box
            box._vetoed = False
        except Veto as v:
            while len(self._operation_log) > pt:
                self._undo_op(self._operation_log.pop())
            box._vetoed = True

    def veto(self):
        raise Veto

    def _create_room(self) -> RoomHandle:
        return self._do_log(CreateRoom())

    def _carve_point(self, v2: V2, new_owner: Optional[RoomHandle]):
        old_owner = self._room_tiles.get_a(v2)
        self._do_log(CarveTile(position=v2, old_owner=old_owner, new_owner=new_owner))

    def freeze(self, rh: RoomHandle):
        if rh in self._room_frozen: return
        self._do_log(FreezeRoom(rh))

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
        elif isinstance(operation, FreezeRoom):
            self._room_frozen.add(operation.room)
        else:
            raise AssertionError("what is {}?".format(operation))

    def _undo_op(self, operation: CarveOp):
        if isinstance(operation, CreateRoom):
            self._rooms.ungen()
        elif isinstance(operation, CarveTile):
            if operation.old_owner is None:
                self._room_tiles.remove_b(operation.position)
            else:
                self._room_tiles.add(operation.old_owner, operation.position)
        elif isinstance(operation, FreezeRoom):
            self._room_frozen.discard(operation.room)
        else:
            raise AssertionError("what is {}?".format(operation))

    def carve(self, r: R2, ignore: List[RoomHandle] = None) -> RoomHandle:
        ignore = ignore or []
        assert isinstance(ignore, List)
        assert isinstance(r, R2)

        h = self._create_room()

        affected_rooms = set()
        for v in r.expand(V2.new(1, 1)):
            existing_room = self._room_tiles.get_a(v)
            if existing_room in ignore:
                continue

            if existing_room in self._room_frozen:
                self.veto()

            affected_rooms.add(existing_room)

            if v in r:
                self._carve_point(v, h)
            else:
                self._carve_point(v, None)

        for r in affected_rooms:
            if r in self._room_frozen:
                self.veto()

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
                if x == 0 and y == 0:
                    s.write(".")
                    continue

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

    def snake(self, room: RoomHandle, direction: "Cardinal") -> "Snake":
        return Snake(self, room, direction)

    def tunnel_east(self, room_handle: RoomHandle, size: V2, min_contact=None, use_ignore=False, rule: Rule = Rule.RNG) -> RoomHandle:
        assert isinstance(room_handle, RoomHandle)
        tiles = list(self._room_tiles.get_bs(room_handle))
        max_x = max(t.x for t in tiles)
        rhs_tiles = [t for t in tiles if t.x == max_x]

        if min_contact is None:
            min_contact = size.y if use_ignore else 1

        return self._tunnel(room_handle, size, min_contact, use_ignore, rhs_tiles, V2.new(1, 0), rule)

    def tunnel_south(self, room_handle: RoomHandle, size: V2, min_contact=None, use_ignore=False, rule: Rule = Rule.RNG) -> RoomHandle:
        assert isinstance(room_handle, RoomHandle)
        tiles = list(self._room_tiles.get_bs(room_handle))
        max_y = max(t.y for t in tiles)
        bot_tiles = [t for t in tiles if t.y == max_y]

        if min_contact is None:
            min_contact = size.x if use_ignore else 1

        return self._tunnel(room_handle, size, min_contact, use_ignore, bot_tiles, V2.new(0, 1), rule)

    def tunnel_west(self, room_handle: RoomHandle, size: V2, min_contact=None, use_ignore=False, rule: Rule = Rule.RNG) -> RoomHandle:
        assert isinstance(room_handle, RoomHandle)
        tiles = list(self._room_tiles.get_bs(room_handle))
        min_x = min(t.x for t in tiles)
        lhs_tiles = [t - V2.new(size.x - 1, 0) for t in tiles if t.x == min_x]

        if min_contact is None:
            min_contact = size.y if use_ignore else 1

        return self._tunnel(room_handle, size, min_contact, use_ignore, lhs_tiles, V2.new(-1, 0), rule)

    def tunnel_north(self, room_handle: RoomHandle, size: V2, min_contact=None, use_ignore=False, rule: Rule = Rule.RNG) -> RoomHandle:
        assert isinstance(room_handle, RoomHandle)
        tiles = list(self._room_tiles.get_bs(room_handle))
        min_y = min(t.y for t in tiles)
        lhs_tiles = [t - V2.new(0, size.y - 1) for t in tiles if t.y == min_y]

        if min_contact is None:
            min_contact = size.x if use_ignore else 1

        return self._tunnel(room_handle, size, min_contact, use_ignore, lhs_tiles, V2.new(0, -1), rule)

    def _tunnel(self, room_handle: RoomHandle, size: V2, min_contact: int, use_ignore: bool, tiles: List[V2], direction: V2, rule: Rule):
        sites = []
        for t in tiles:
            if use_ignore:
                sites.append((t + direction).sized(size))
            else:
                sites.append((t + direction * 2).sized(size))

        # TODO: Only look at a representative set of tiles from the site
        sites = [
            site
            for site in sites
            if len([
                t
                for t in site
                if self._has_contact(room_handle, site, t, 1 if use_ignore else 2, -direction)
            ]) >= min_contact
        ]
        if len(sites) == 0: self.veto()

        return self.carve(self._choose(sites, rule), ignore=[room_handle] if use_ignore else [])

    def _choose(self, sites: List[R2], rule: Rule):
        if rule == Rule.RNG:
            return random.choice(sites)

        if rule == Rule.Dense:
            scores = [
                len([t for t in site if self._has_contact(None, site, t, 2)])
                for site in sites
            ]
            max_score = max(scores)
            sites_with_max = [site for site, score in zip(sites, scores) if score == max_score]
            return random.choice(sites_with_max)

        raise AssertionError("unknown rule: %s" % rule)

    def _has_contact(self, room_handle: Optional[RoomHandle], site: R2, tile: V2, distance: int, direction: Optional[V2] = None) -> bool:
        assert direction is None or isinstance(direction, V2)

        for dir in [direction] if direction is not None else [
            V2.new(1, 0),
            V2.new(0, 1),
            V2.new(-1, 0),
            V2.new(0, -1),
        ]:
            t = tile
            if room_handle is None:
                # contact w/ any room
                if self._room_tiles.get_a(t + dir * distance) is not None:
                    continue
            else:
                # contact period
                if self._room_tiles.get_a(t + dir * distance) != room_handle:
                    continue

            for i in range(distance - 1):
                t = t + dir
                if t in site or self._room_tiles.get_a(t) is not None:
                    break
            else:
                # ends in the right place and all the tiles on the way are empty
                return True


class Cardinal(Enum):
    North = 0
    East = 1
    South = 2
    West = 3

    def right(self):
        return Cardinal((self.value + 1) % 4)

    def left(self):
        return Cardinal((self.value - 1) % 4)


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

    def tunnel(self, size: V2, min_contact: Optional[int] = None, use_ignore: bool = False, rule: Rule = Rule.RNG):
        if self._direction in [Cardinal.East, Cardinal.West]:
            # Swap components for L/R
            size = V2.new(size.y, size.x)

        if self._direction == Cardinal.North:
            room = self._carve.tunnel_north(self._room, size, min_contact=min_contact, use_ignore=use_ignore, rule=rule)
        elif self._direction == Cardinal.East:
            room = self._carve.tunnel_east(self._room, size, min_contact=min_contact, use_ignore=use_ignore, rule=rule)
        elif self._direction == Cardinal.South:
            room = self._carve.tunnel_south(self._room, size, min_contact=min_contact, use_ignore=use_ignore, rule=rule)
        elif self._direction == Cardinal.West:
            room = self._carve.tunnel_west(self._room, size, min_contact=min_contact, use_ignore=use_ignore, rule=rule)
        else:
            raise AssertionError("direction: {}".format(self._direction))

        self._room = room
        return room


def apartment() -> Carve:
    carve = Carve()

    cell_sz_x = random.randint(3, 5)

    living_room_width = random.randint(cell_sz_x + 3, cell_sz_x * 2 + 1)
    living_room_height = random.randrange(6, 8)
    living_room = carve.carve(V2.new(0, 0).sized(V2.new(living_room_width, living_room_height)))
    carve.freeze(living_room)

    bedroom_depth = random.randint(living_room_height // 2, living_room_height)

    def hall_room(snake: Snake) -> bool:
        for sz_x in range(cell_sz_x, 0, -1):
            with snake.veto_point() as vetoed:
                snake.tunnel(V2.new(sz_x, bedroom_depth), min_contact=min(cell_sz_x, sz_x), rule=Rule.Dense)

            if not vetoed:
                return True

        return False

    def hallway(snake: Snake, n_hall_nodes: int):
        if n_hall_nodes == 0:
            hall_room(snake)
            return

        # bend
        bend = None
        if n_hall_nodes > 1 and random.choice([False, True, True]):
            bend = random.randrange(1, n_hall_nodes)

        for i in range(n_hall_nodes):
            if i == bend:
                snake.tunnel(V2.new(3, 3), min_contact=3)
                snake.turn_left()
                snake.tunnel(V2.new(3, cell_sz_x), min_contact=3)

                room1 = snake.branch()
                room1.turn_left()
                hall_room(room1)

                room2 = snake.branch()
                room2.turn_right()
                hall_room(room2)

                snake.tunnel(V2.new(3, 3), min_contact=3)
                snake.turn_right()
                snake.tunnel(V2.new(3, cell_sz_x), min_contact=3)
            else:
                snake.tunnel(V2.new(3, cell_sz_x), min_contact=3)

                room1 = snake.branch()
                room1.turn_left()
                hall_room(room1)

                room2 = snake.branch()
                room2.turn_right()
                hall_room(room2)

    has_junction = random.choice([False, True])

    if has_junction:
        n_hall_nodes = random.choice([1, 1, 1, 2 ])
        junc = carve.snake(living_room, Cardinal.East)
        junc.tunnel(V2.new(3, 3), min_contact=3)

        h1 = junc.branch()
        h1.turn_right()
        hallway(h1, n_hall_nodes=n_hall_nodes)

        if random.choice([False, True, True]):
            n_hall_nodes = random.choice([0])
            h1 = junc.branch()
            if random.choice([False, False, True]):
                h1.turn_left()
            hallway(h1, n_hall_nodes=n_hall_nodes)
    else:
        n_hall_nodes = random.choice([1, 1, 1, 2, 2, 3])
        h1 = carve.snake(living_room, Cardinal.East)
        hallway(h1, n_hall_nodes=n_hall_nodes)



    return carve

    """
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
    """

