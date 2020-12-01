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


class CreateRoom(NamedTuple):
    room_type: RoomType


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


# TODO: Support random rotation/mirroring of this
# TODO: Veto if a room becomes too small
class Carve(object):
    def __init__(self):
        self._rooms = FastGensym()
        self._room_tiles: OneToMany[RoomHandle, V2] = OneToMany()
        self._room_types: Dict[RoomHandle, RoomType] = {}

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

    def _create_room(self, room_type: RoomType) -> RoomHandle:
        return self._do_log(CreateRoom(room_type))

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
            rh = RoomHandle(self._rooms.gen())
            self._room_types[rh] = operation.room_type
            return rh
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
            rh = self._rooms.ungen()
            del self._room_types[RoomHandle(rh)]
        elif isinstance(operation, CarveTile):
            if operation.old_owner is None:
                self._room_tiles.remove_b(operation.position)
            else:
                self._room_tiles.add(operation.old_owner, operation.position)
        elif isinstance(operation, FreezeRoom):
            self._room_frozen.discard(operation.room)
        else:
            raise AssertionError("what is {}?".format(operation))

    def carve(self, r: R2, room_type: RoomType, ignore: List[RoomHandle] = None) -> RoomHandle:
        ignore = ignore or []
        assert isinstance(ignore, List)
        assert isinstance(r, R2)

        h = self._create_room(room_type)

        affected_rooms = {}
        for v in r.expand(V2.new(1, 1)):
            existing_room = self._room_tiles.get_a(v)
            if existing_room in ignore:
                continue

            if existing_room in self._room_frozen:
                self.veto()

            affected_rooms[existing_room] = len(list(self._room_tiles.get_bs(v)))

            if v in r:
                self._carve_point(v, h)
            else:
                self._carve_point(v, None)

        for r, previous_area in affected_rooms.items():
            new_area = len(list(self._room_tiles.get_bs(r)))
            if self._ruined(r, previous_area, new_area):
                self.veto()

        return h

    def _ruined(self, r, previous_area, new_area):
        if r in self._room_frozen:
            return True

        if new_area < 0.5 * previous_area:
            return True

        if (previous_area > 6) and (new_area < 6):
            return True

        # TODO: Check for no longer contiguous?
        # TODO: Check for wonky shape

        return False

    def expand_densely(self, r: RoomHandle):
        claimed = lambda tile: self._room_tiles.get_a(tile) is not None
        claimed_me = lambda tile: self._room_tiles.get_a(tile) == r

        change_made = True
        while change_made:
            to_add = set()
            for d in [V2.new(-1, 0), V2.new(0, -1), V2.new(1, 0), V2.new(0, 1)]:
                for t in self._room_tiles.get_bs(r):
                    # True if the tile is claimed
                    t1 = claimed(t + d)
                    if t1: continue

                    if claimed_me(t + d + d):
                        to_add.add(t + d)
                        continue

                    t2 = claimed(t + d + d)
                    if t2: continue

                    t3 = claimed(t + d + d + d)
                    t4 = claimed(t + d + d + d + d)
                    # t5 = claimed(t + d + d + d + d + d)

                    if (
                        # (t5 and not any([t4, t3])) or
                        (t4 and not any([t3])) or
                        t3
                    ):
                        to_add.add(t + d)

            change_made = len(to_add) > 0
            for t in to_add:
                self._carve_point(t, r)

    def erode(self, r: RoomHandle, iterations):
        claimed = lambda tile: self._room_tiles.get_a(tile) is not None

        directions1 = [V2.new(-1, 0), V2.new(0, -1), V2.new(1, 0), V2.new(0, 1)]
        directions2 = directions1[1:] + directions1[:1]

        for i in range(iterations):
            to_remove = set()
            for d1, d2 in zip(directions1, directions2):
                for t in self._room_tiles.get_bs(r):
                    tu1 = claimed(t + d1)
                    tu2 = claimed(t + d1 + d1)
                    tl1 = claimed(t + d2)
                    tl2 = claimed(t + d2 + d2)
                    if not (tu1 or tu2 or tl1 or tl2):
                        to_remove.add(t)

            for t in to_remove:
                self._carve_point(t, None)

    def erode_1tile_wonk(self, r: RoomHandle):  # removes one-tile bacon strips
        claimed = lambda tile: self._room_tiles.get_a(tile) is not None

        to_remove = set()
        directions = [V2.new(-1, 0), V2.new(0, -1)]
        for d in directions:
            for t in self._room_tiles.get_bs(r):
                tl = claimed(t + d)
                tr = claimed(t - d)
                if not (tl or tr):
                    to_remove.add(t)

        for t in to_remove:
            self._carve_point(t, None)

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
                    room_tile = self._room_types[room].tile()  # chr(ord("A") + (room.ident % 26))
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

    def ident_rooms(self, room_type: RoomType) -> List[RoomHandle]:
        found = []
        for room in self._room_tiles.all_as():
            if self._room_types[room] != room_type: continue
            found.append(room)

        return found

    def snake(self, room: RoomHandle, direction: "Cardinal") -> "Snake":
        return Snake(self, room, direction)

    def tunnel_east(self, room_handle: RoomHandle, size: V2, room_type: RoomType, min_contact=None, use_ignore=False, rule: Rule = Rule.RNG) -> RoomHandle:
        assert isinstance(room_handle, RoomHandle)
        tiles = list(self._room_tiles.get_bs(room_handle))
        max_x = max(t.x for t in tiles)
        rhs_tiles = [t for t in tiles if t.x == max_x]

        if min_contact is None:
            min_contact = size.y if use_ignore else 1

        return self._tunnel(room_handle, size, room_type, min_contact, use_ignore, rhs_tiles, V2.new(1, 0), rule)

    def tunnel_south(self, room_handle: RoomHandle, size: V2, room_type: RoomType, min_contact=None, use_ignore=False, rule: Rule = Rule.RNG) -> RoomHandle:
        assert isinstance(room_handle, RoomHandle)
        tiles = list(self._room_tiles.get_bs(room_handle))
        max_y = max(t.y for t in tiles)
        bot_tiles = [t for t in tiles if t.y == max_y]

        if min_contact is None:
            min_contact = size.x if use_ignore else 1

        return self._tunnel(room_handle, size, room_type, min_contact, use_ignore, bot_tiles, V2.new(0, 1), rule)

    def tunnel_west(self, room_handle: RoomHandle, size: V2, room_type: RoomType, min_contact=None, use_ignore=False, rule: Rule = Rule.RNG) -> RoomHandle:
        assert isinstance(room_handle, RoomHandle)
        tiles = list(self._room_tiles.get_bs(room_handle))
        min_x = min(t.x for t in tiles)
        lhs_tiles = [t - V2.new(size.x - 1, 0) for t in tiles if t.x == min_x]

        if min_contact is None:
            min_contact = size.y if use_ignore else 1

        return self._tunnel(room_handle, size, room_type, min_contact, use_ignore, lhs_tiles, V2.new(-1, 0), rule)

    def tunnel_north(self, room_handle: RoomHandle, size: V2, room_type: RoomType, min_contact=None, use_ignore=False, rule: Rule = Rule.RNG) -> RoomHandle:
        assert isinstance(room_handle, RoomHandle)
        tiles = list(self._room_tiles.get_bs(room_handle))
        min_y = min(t.y for t in tiles)
        lhs_tiles = [t - V2.new(0, size.y - 1) for t in tiles if t.y == min_y]

        if min_contact is None:
            min_contact = size.x if use_ignore else 1

        return self._tunnel(room_handle, size, room_type, min_contact, use_ignore, lhs_tiles, V2.new(0, -1), rule)

    def _tunnel(self, room_handle: RoomHandle, size: V2, room_type: RoomType, min_contact: int, use_ignore: bool, tiles: List[V2], direction: V2, rule: Rule):
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

        return self.carve(self._choose(sites, rule), room_type, ignore=[room_handle] if use_ignore else [])

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


def apartment() -> Carve:
    carve = Carve()

    cell_sz_x = random.randint(3, 4)

    living_room_width = random.randint(cell_sz_x + 3, cell_sz_x * 2 + 1)
    living_room_height = random.randrange(6, 8)
    living_room = carve.carve(V2.new(0, 0).sized(V2.new(living_room_width, living_room_height)), RoomType.LivingRoom)
    carve.freeze(living_room)

    def build_kitchen(snake: Snake):
        kitchen_width = random.randint(living_room_width - 1, living_room_width)
        kitchen_height = random.randint(living_room_height - 4, living_room_height - 2)
        kitchen_height = max(kitchen_height, 2)
        carve.freeze(snake.tunnel(V2.new(kitchen_width, kitchen_height), RoomType.Kitchen, min_contact=kitchen_width))

    build_kitchen(carve.snake(living_room, Cardinal.North))

    def build_antechamber_once(snake: Snake):
        choice = random.choice([0, 0, 0, 1, 1])
        if choice == 0:
            # tiny room -- _just_ an entry zone
            carve.freeze(snake.tunnel(V2.new(3, 3), RoomType.EntryZone, min_contact=3))
        else:
            # yard-like
            carve.freeze(snake.tunnel(V2.new(living_room_height, 3), RoomType.Antechamber, min_contact=living_room_height))
            if random.choice([False, True]):
                snake.turn_right()
                carve.freeze(snake.tunnel(V2.new(3, 3), RoomType.Antechamber))

            random.choice([lambda: None, snake.turn_left])()
            carve.freeze(snake.tunnel(V2.new(3, 3), RoomType.EntryZone, min_contact=3))

    def build_antechamber(snake: Snake):
        for try_ in range(5):
            with snake.veto_point() as vetoed:
                return build_antechamber_once(snake)
        snake.veto()

    build_antechamber(carve.snake(living_room, Cardinal.West))

    bedroom_depth_l = random.randint(living_room_height // 2, living_room_height)
    bedroom_depth_r = random.randint(living_room_height // 2, living_room_height)

    def build_hall_room(snake: Snake, master: bool, depth: int) -> bool:
        for sz_x in range(cell_sz_x, 2, -1):
            room_type = (
                RoomType.Bedroom if master else
                RoomType.Bathroom if len(carve.ident_rooms(RoomType.Bathroom)) == 0 else
                RoomType.Bedroom
            )
            size = V2.new(sz_x + (random.randint(2, 4) if master else 0), depth + (random.randint(0, 1) if master else 0))
            size = V2.new(size.x, min(size.y, int(size.x * 1.5)))

            with snake.veto_point() as vetoed:
                # TODO: Bathroom
                snake.tunnel(
                    size,
                    room_type,
                    min_contact=min(cell_sz_x, sz_x),
                    rule=Rule.Dense
                )

            if not vetoed:
                return True

        return False

    def build_bathroom(snake: Snake) -> bool:
        for sz_x in range(4, 2, -1):
            room_type = RoomType.Bathroom
            size = V2.new(sz_x, 3)

            with snake.veto_point() as vetoed:
                carve.freeze(snake.tunnel(size, room_type, min_contact=min(cell_sz_x, sz_x - 1), rule=Rule.Dense))

            if not vetoed:
                return True

        return False

    def build_closet(snake: Snake) -> bool:
        for sz_x in range(5, 1, -1):
            room_type = RoomType.Closet
            size = V2.new(sz_x, 1)

            with snake.veto_point() as vetoed:
                r = snake.tunnel(size, room_type, min_contact=sz_x, rule=Rule.Dense)
                carve.freeze(r)  # should be frozen, closets are easy to wipe out

            if not vetoed:
                return True

        return False

    def build_hallway(snake: Snake, n_hall_nodes: int):
        if n_hall_nodes == 0:
            build_hall_room(snake, master=True, depth=living_room_width)
            return

        # bend
        for i in range(n_hall_nodes):
            carve.freeze(snake.tunnel(V2.new(3, cell_sz_x), RoomType.Hallway, min_contact=3))

            def build_l():
                room1 = snake.branch()
                room1.turn_left()
                build_hall_room(room1, False, bedroom_depth_l)

            def build_r():
                room2 = snake.branch()
                room2.turn_right()
                build_hall_room(room2, False, bedroom_depth_r)

            # we assign bathroom first, so assign it to the smaller side
            if bedroom_depth_l < bedroom_depth_r:
                build_l()
                build_r()
            else:
                build_r()
                build_l()

        build_hall_room(snake, True, cell_sz_x)  # master bedroom


    has_junction = random.choice([False, True])

    if has_junction:
        n_hall_nodes = random.choice([0, 0, 1, 2])
        junc = carve.snake(living_room, Cardinal.East)
        junc.tunnel(V2.new(3, 3), RoomType.Hallway, min_contact=3)

        h1 = junc.branch()
        h1.turn_right()
        build_hallway(h1, n_hall_nodes=n_hall_nodes)

        if random.choice([False, True, True]):
            n_hall_nodes = random.choice([0, 0, 1])
            h1 = junc.branch()
            if random.choice([False, False, True]):
                h1.turn_left()
            build_hallway(h1, n_hall_nodes=n_hall_nodes)
    else:
        n_hall_nodes = random.choice([0, 0, 0, 1, 1, 2, 3])
        h1 = carve.snake(living_room, Cardinal.East)
        build_hallway(h1, n_hall_nodes=n_hall_nodes)

    # TODO: Veto if the number of rooms is wrong

    bedrooms = carve.ident_rooms(room_type=RoomType.Bedroom)
    bathrooms = carve.ident_rooms(room_type=RoomType.Bathroom)
    hallways = carve.ident_rooms(room_type=RoomType.Hallway)
    # Freeze rooms
    for br in bedrooms: carve.freeze(br)
    for br in bathrooms: carve.freeze(br)
    for hw in hallways: carve.freeze(hw)

    # give every bedroom a closet if possible
    for br in bedrooms:
        for card in Cardinal.all_shuffled():
            if build_closet(carve.snake(br, card)):
                break
        else:
            # try really hard to have a closet
            carve.veto()

    bathroom_bedrooms = list(bedrooms)
    # if there aren't enough bathrooms, try to add some
    for try_ in range(10):
        bathrooms = carve.ident_rooms(room_type=RoomType.Bathroom)
        if len(bathrooms) >= len(bedrooms):
            break

        random_bedroom = random.choice(bathroom_bedrooms)
        for card in Cardinal.all_shuffled():
            if build_bathroom(carve.snake(random_bedroom, card)):
                bathroom_bedrooms.remove(random_bedroom)
                break

        if hallways:
            random_hallway = random.choice(hallways)
            for card in Cardinal.all_shuffled():
                if build_bathroom(carve.snake(random_hallway, card)):
                    break

    # now improve various room types
    for room_type in [RoomType.Bedroom, RoomType.Kitchen, RoomType.LivingRoom]:
        for r in carve.ident_rooms(room_type):
            carve.expand_densely(r)

    for room_type in [RoomType.Bedroom, RoomType.Kitchen, RoomType.LivingRoom]:
        for r in carve.ident_rooms(room_type):
            carve.erode_1tile_wonk(r)

    # erode room types that are often pointlessly large
    if random.choice([False, False, True]):
        for room_type in [RoomType.LivingRoom, RoomType.Kitchen]:
            for r in carve.ident_rooms(room_type):
                carve.erode(r, 1)

    return carve

