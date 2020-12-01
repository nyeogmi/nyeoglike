from .carve_op import *
from .recs import *


# TODO: Support random rotation/mirroring of this
# TODO: Veto if a room becomes too small
class Carve(object):
    def __init__(self, door_spread: DoorSpread):
        self._door_spread = door_spread

        self._rooms = FastGensym()
        self._room_tiles: OneToMany[RoomHandle, V2] = OneToMany()
        self._room_types: Dict[RoomHandle, RoomType] = {}
        self._room_frozen = set()
        self._links: List[Link] = []

        self._operation_log = []

    def permute_at_random(self):
        _room_tiles_2: OneToMany[RoomHandle, V2] = OneToMany()

        # TODO: Is one rotation more likely than another w/ this?
        mul_x = random.choice([-1, 1])
        mul_y = random.choice([-1, 1])
        swap = random.choice([True, False])

        for rh, v2 in self._room_tiles.all():
            v2 = V2.new(mul_x * v2.x, mul_y * v2.y)
            if swap: v2 = V2.new(v2.y, v2.x)
            _room_tiles_2.add(rh, v2)
        self._room_tiles = _room_tiles_2

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
                    room_tile = " " # self._room_types[room].tile()  # chr(ord("A") + (room.ident % 26))
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
                        s.write("#")
                    else:
                        s.write(" ")
            s.write("\n")
        return s.getvalue().strip("\n")

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

    def link_rooms(self, link_type: LinkType, rh0: RoomHandle, rh1: RoomHandle):
        self._do_log(LinkRooms(link_type, rh0, rh1))

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
        elif isinstance(operation, LinkRooms):
            self._links.append(Link(operation.link_type, operation.room0, operation.room1))
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
        elif isinstance(operation, LinkRooms):
            self._links.pop()
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

    def ident_rooms(self, room_type: RoomType) -> List[RoomHandle]:
        found = []
        for room in self._room_tiles.all_as():
            if self._room_types[room] != room_type: continue
            found.append(room)

        return found

    def build_links(self):
        claimed = lambda owner, tile: self._room_tiles.get_a(tile) == owner
        not_claimed = lambda tile: claimed(None, tile)

        links_hallway = self._create_room(RoomType.Hallway)

        for link in self._links:
            if link.link_type == LinkType.Ignore:
                continue

            room0 = link.room0
            room1 = link.room1
            dw = lambda label, direction: [
                (label, t + direction)
                for t in self._room_tiles.get_bs(room0)
                if not_claimed(t + direction) and claimed(room1, t + direction * 2)
            ]
            door_worthy = set(
                dw("horiz", V2.new(0, 1)) + dw("horiz", V2.new(0, -1)) +
                dw("vert", V2.new(1, 0)) + dw("vert", V2.new(-1, 0))
            )

            if len(door_worthy) == 0:
                self.veto()

            # Find the door segment
            if link.link_type == LinkType.Door:
                if any(self._room_types[r] in [RoomType.EntryZone, RoomType.Closet] for r in [room0, room1]):
                    # must be centered
                    # all of the xs will be the same or all the ys, so it doesn't matter
                    sorted_spots = sorted(door_worthy, key=lambda i: (i[1].x, i[1].y))
                    door = sorted_spots[len(sorted_spots)//2][1]
                else:
                    scores = [self._door_score(*v) for v in door_worthy]
                    max_score = max(scores)
                    spots_best = [site for site, score in zip(door_worthy, scores) if score == max_score]
                    door = random.choice(list(spots_best))[1]

                self._carve_point(door, links_hallway)

            elif link.link_type == LinkType.Complete:
                for i in door_worthy:
                    self._carve_point(i[1], room0)  # add to room0
            else:
                raise AssertionError("unrecognized link type: {}".format(link.link_type))

    def _door_score(self, label: str, v2: V2):
        if label == "horiz" and v2.x % self._door_spread.x == self._door_spread.cx:
            return 1
        if label == "vert" and v2.y % self._door_spread.y == self._door_spread.cy:
            return 1
        return 0

    # == snake support
    def snake(self, room: RoomHandle, direction: "Cardinal") -> "Snake":
        from .snake import Snake
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


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .snake import Snake