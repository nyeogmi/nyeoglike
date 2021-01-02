import os.path
from typing import Dict, Iterator, List, NamedTuple, Optional, Set

from ds.gensym import Gensym, Sym
from ds.relational import OneToMany
from ds.vecs import V2

from ..item import Item
from ..npc import NPCHandle
from .block import Block
from .wallpaper import Wallpaper


class SpawnHandle(NamedTuple):
    ident: Sym


class Spawn(NamedTuple):
    handle: SpawnHandle
    item: Item
    ephemeral: bool
    is_junk: bool

    @classmethod
    def new(cls, handle: SpawnHandle, item: Item, ephemeral: bool) -> "Spawn":
        assert isinstance(handle, SpawnHandle)
        assert isinstance(item, Item)
        assert isinstance(ephemeral, bool)

        is_junk = ephemeral and "junk" in item.keywords
        return Spawn(handle, item, ephemeral, is_junk)


class Items(object):
    def __init__(self):
        self._sym: Gensym = Gensym("SPN")
        self._values: Dict[SpawnHandle, Spawn] = {}
        self._placement: OneToMany[V2, SpawnHandle] = OneToMany()

        self._junk_left = 0

    def put(self, at: V2, item: Item, ephemeral: bool) -> SpawnHandle:
        handle = SpawnHandle(self._sym.gen())

        self._values[handle] = Spawn.new(handle, item, ephemeral)
        self._placement.add(at, handle)

        if self._values[handle].is_junk:
            self._junk_left += 1

        return handle

    def has(self, sh: SpawnHandle) -> bool:
        return sh in self._values

    def take(self, sh: SpawnHandle) -> Item:
        assert sh in self._values
        spawn = self._values[sh]
        self._placement.remove_b(sh)
        del self._values[sh]

        if spawn.is_junk:
            self._junk_left -= 1

        return spawn.item

    def view(self, at: V2) -> List[Spawn]:
        return [
            self._values[sh]
            for sh in sorted(self._placement.get_bs(at), key=lambda sh: sh.ident)
        ]

    @property
    def junk_left(self):
        return self._junk_left


class LoadedLevel(object):
    def __init__(
        self,
        ident: "LevelHandle",
        wallpaper: Wallpaper,
        in_bounds: Set[V2],
        blocks: Dict[V2, Block],
        items: Dict[V2, List[Item]],
        npc_sites: OneToMany[V2, NPCHandle],
    ):
        self.ident = ident
        self.wallpaper = wallpaper
        self.in_bounds: Set[V2] = in_bounds
        self.blocks: Dict[V2, Block] = blocks
        self.seen: Set[V2] = set()  # every time the player sees a tile, add it to this
        self.items: Items = Items()
        for v2, items in items.items():
            for item in items:
                self.items.put(v2, item, False)  # no ephemeral items
        self.npc_sites: OneToMany[V2, NPCHandle] = npc_sites

    def npc_location(self, npc: NPCHandle) -> Optional[V2]:
        assert isinstance(npc, NPCHandle)
        return self.npc_sites.get_a(npc)

    def loaded_npcs(self) -> Iterator[NPCHandle]:
        for npc in self.npc_sites.all_bs():
            yield npc


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world import World
    from ..worldmap import LevelHandle
