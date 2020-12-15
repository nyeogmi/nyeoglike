import random
from io import StringIO
from typing import Dict, Iterator, List, Optional, Set

from ds.relational import OneToMany
from ds.vecs import V2
from unique.item import Item
from unique.level.unloaded_level import UnloadedLevel

from ..block import Block
from .recs import Hint, RoomHandle, RoomType, Spawn, SpawnType


# TODO: Item spawns that are randomized at level load time
class InteriorDesigner(object):
    def __init__(
        self,
        room_tiles: OneToMany[RoomHandle, V2],
        room_types: Dict[RoomHandle, RoomType],
        hints: Dict[Hint, Set[V2]],
    ):
        assert isinstance(room_tiles, OneToMany)
        assert isinstance(room_types, dict)
        assert isinstance(hints, dict)

        self._player_start_xy = V2(0, 0)
        self._room_tiles: OneToMany[RoomHandle, V2] = room_tiles
        self._room_types: Dict[RoomHandle, RoomType] = room_types
        self._cell_objects: Dict[V2, List[Item]] = dict()
        self._npc_spawns: Set[Spawn] = set()
        self._exits: Set[V2] = set()
        self._hints = hints

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

    def merge_rooms(self, room0: "Room", room1: "Room"):
        rh0 = room0._room_handle
        rh1 = room1._room_handle
        assert isinstance(rh0, RoomHandle)
        assert isinstance(rh1, RoomHandle)

        for i in list(self._room_tiles.get_bs(rh1)):
            self._room_tiles.add(rh0, i)

        self._rooms[rh0] = self._calculate_room(rh0)
        self._rooms[rh1] = self._calculate_room(rh1)

        for door in self._all_doors:
            self._rooms[rh0].boundary_avoid_door(door)
            self._rooms[rh1].boundary_avoid_door(door)

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

        return Room(
            self,
            room_handle,
            all_tiles=list(all_tiles),
            doors=list(doors),
            boundary=list(boundary),
            center=list(center),
        )

    def ident_rooms(self, room_type: RoomType) -> List["Room"]:
        found = []
        for rh in self._room_tiles.all_as():
            if self._room_types[rh] != room_type:
                continue
            found.append(self._rooms[rh])

        return found

    def to_level(self):
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

        blocks = {}
        items = {}
        spawns = {}
        for y in range(mn_y - 1, mx_y + 2):
            for x in range(mn_x - 1, mx_x + 2):
                xy = V2.new(x, y)

                if xy in self._exits:
                    blocks[xy] = Block.Exit

                elif self._room_tiles.get_a(xy):
                    # This is a room, so leave it carved out
                    # TODO: Items, spawns
                    if xy in self._cell_objects:
                        items[xy] = list(self._cell_objects[xy])

                else:
                    needed = False
                    for x1 in range(-1, 2):
                        for y1 in range(-1, 2):
                            if V2.new(x + x1, y + y1) in carved:
                                needed = True

                    if needed:
                        blocks[xy] = Block.Normal

        for spawn in self._npc_spawns:
            if spawn.location not in carved:
                continue
            if any(i.occludes_walk for i in items.get(spawn.location, [])):
                continue

            spawns[spawn.spawn_type] = spawns.get(spawn.spawn_type, set())
            spawns[spawn.spawn_type].add(spawn.location)

        return UnloadedLevel(
            player_start_xy=self._player_start_xy,
            blocks=blocks,
            items=items,
            npc_spawns=spawns,
        )


# TODO: Support vault placement in the future
class Room(object):
    def __init__(
        self,
        interior: InteriorDesigner,
        room_handle: RoomHandle,
        all_tiles: List[V2],
        doors: List[V2],
        boundary: List[V2],
        center: List[V2],
    ):
        assert isinstance(interior, InteriorDesigner)
        assert isinstance(room_handle, RoomHandle)
        assert isinstance(all_tiles, list)
        assert isinstance(doors, list)
        assert isinstance(boundary, list)
        assert isinstance(center, list)

        self._interior = interior
        self._room_handle = room_handle

        self._all_tiles: List[V2] = all_tiles

        self._original_doors: List[V2] = list(doors)
        self._original_center: List[V2] = list(center)

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

    def all_tiles(self) -> Iterator[V2]:
        for t in self._all_tiles:
            yield t

    def hinted(self, hint: Hint) -> Iterator[V2]:
        # TODO: Allow the user to also specify that it is in the doors, boundary, or center
        if hint not in self._interior._hints:
            return

        hint_table = self._interior._hints[hint]
        for v in self._all_tiles:
            if v in hint_table:
                yield v

    def door(self, item: Optional[Item] = None) -> bool:
        return self._add(self._doors, item)

    def boundary(self, item: Optional[Item] = None) -> bool:
        return self._add(self._boundary, item)

    def center(self, item: Optional[Item] = None) -> bool:
        return self._add(self._center, item)

    def at(self, v2: V2, item: Optional[Item] = None) -> bool:
        if v2 not in self._all_tiles:
            return False  # TODO: Keep a set of all tiles for this reason?

        return self._add([v2], item)

    def fill_with_exits(self):
        for i in self._all_tiles:
            self._interior._exits.add(i)

        for i in self._interior._all_doors:
            self._interior._exits.discard(i)
            for n in i.ortho_neighbors():
                self._interior._exits.discard(n)

        for i in self._original_center:
            self._interior._player_start_xy = i
            self._interior._exits.discard(i)

    def _add(self, v2s: List[V2], item: Optional[Item]) -> bool:
        assert isinstance(v2s, list)
        assert item is None or isinstance(item, Item)

        if len(v2s) == 0:
            return False

        v2 = v2s.pop()
        if item:
            cell_objs = self._interior._cell_objects
            cell_objs[v2] = cell_objs.get(v2, [])
            cell_objs[v2].append(item)
        self._last_location = v2

        return True

    def mark_spawn(self, spawn_type: SpawnType) -> bool:
        assert isinstance(spawn_type, SpawnType)
        if self._last_location is None:
            return False

        self._mark_spawn_at(spawn_type, self._last_location)
        return True

    def mark_spawn_neighbors(self, spawn_type: SpawnType) -> bool:
        assert isinstance(spawn_type, SpawnType)
        if self._last_location is None:
            return False

        for n in self._last_location.neighbors():
            self._mark_spawn_at(spawn_type, self._last_location)
        return True

    def _mark_spawn_at(self, spawn_type: SpawnType, loc: V2):
        if self._interior._room_tiles.get_a(loc) != self._room_handle:
            return

        self._interior._npc_spawns.add(Spawn(spawn_type, loc))
