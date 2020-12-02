from ds.relational import OneToMany
from ds.vecs import V2
from unique.item import Item
import random
from typing import Dict, List, Set, Optional
from io import StringIO

from .recs import RoomHandle, RoomType, Spawn, SpawnType


# TODO: Item spawns that are randomized at level load time
class InteriorDesigner(object):
    def __init__(
        self,
        room_tiles: OneToMany[RoomHandle, V2],
        room_types: Dict[RoomHandle, RoomType],
    ):
        assert isinstance(room_tiles, OneToMany)
        assert isinstance(room_types, dict)

        self._room_tiles: OneToMany[RoomHandle, V2] = room_tiles
        self._room_types: Dict[RoomHandle, RoomType] = room_types
        self._cell_objects: Dict[V2, List[Item]] = dict()
        self._npc_spawns: Set[Spawn] = set()

        self._rooms: Dict[RoomHandle, Room] = {}
        for rh in self._room_tiles.all_as():
            self._rooms[rh] = self._calculate_room(rh)

        self._all_doors = set()
        for rh, room in self._rooms.items():
            for door in room._doors:
                self._all_doors.add(door)

        for door in self._all_doors:
            for rh, room in self._rooms.items():
                room.boundary_avoid_door(door)

    def _calculate_room(self, room_handle: RoomHandle) -> "Room":
        all_tiles = set()
        for v in self._room_tiles.get_bs(room_handle):
            all_tiles.add(v)

        blocked = lambda v: self._room_tiles.get_a(v) is None

        doors = set()
        boundary = set()
        center = set()

        for v in all_tiles:
            if blocked(v - V2.new(1, 0)) and blocked(v + V2.new(1, 0)):
                doors.add(v)
                continue

            if blocked(v - V2.new(0, 1)) and blocked(v + V2.new(0, 1)):
                doors.add(v)
                continue

            for v2 in v.neighbors():
                if blocked(v2):
                    boundary.add(v)
                    break
            else:
                center.add(v)

        return Room(self, room_handle, doors=list(doors), boundary=list(boundary), center=list(center))

    def ident_rooms(self, room_type: RoomType) -> List["Room"]:
        found = []
        for rh in self._room_tiles.all_as():
            if self._room_types[rh] != room_type: continue
            found.append(self._rooms[rh])

        return found

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
                    for obj in self._cell_objects.get(V2.new(x, y), []):
                        room_tile = obj.profile.ascii_icon

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


# TODO: Support vault placement in the future
class Room(object):
    def __init__(
        self,
        interior: InteriorDesigner,
        room_handle: RoomHandle,

        doors: List[V2],
        boundary: List[V2],
        center: List[V2],
    ):
        assert isinstance(interior, InteriorDesigner)
        assert isinstance(room_handle, RoomHandle)
        assert isinstance(doors, list)
        assert isinstance(boundary, list)
        assert isinstance(center, list)

        self._interior = interior
        self._room_handle = room_handle

        self._doors: List[V2] = doors
        self._boundary: List[V2] = boundary
        self._center: List[V2] = center

        self._last_location: Optional[V2] = None

        random.shuffle(self._doors)
        random.shuffle(self._boundary)
        random.shuffle(self._center)

    def boundary_avoid_door(self, door: V2):
        # TODO: Boundary is not an efficient data structure for this
        for n in door.neighbors():
            try:
                self._boundary.remove(n)
            except ValueError as ve:
                pass

    def door(self, item: Item) -> bool:
        return self._add(self._doors, item)

    def boundary(self, item: Item) -> bool:
        return self._add(self._boundary, item)

    def center(self, item: Item) -> bool:
        return self._add(self._center, item)

    def _add(self, v2s: List[V2], item: Item) -> bool:
        assert isinstance(v2s, list)
        assert isinstance(item, Item)

        if len(v2s) == 0: return False

        v2 = v2s.pop()
        cell_objs = self._interior._cell_objects
        cell_objs[v2] = cell_objs.get(v2, [])
        cell_objs[v2].append(item)
        self._last_location = v2

        return True

    def mark_spawn(self, spawn_type: SpawnType) -> bool:
        assert isinstance(spawn_type, SpawnType)
        if self._last_location is None: return False

        self._mark_spawn_at(spawn_type, self._last_location)
        return True

    def mark_spawn_neighbors(self, spawn_type: SpawnType) -> bool:
        assert isinstance(spawn_type, SpawnType)
        if self._last_location is None: return False

        for n in self._last_location.neighbors():
            self._mark_spawn_at(spawn_type, self._last_location)
        return True

    def _mark_spawn_at(self, spawn_type: SpawnType, loc: V2):
        if self._interior._room_tiles.get_a(loc) != self._room_handle:
            return

        self._interior._npc_spawns.add(Spawn(spawn_type, loc))
