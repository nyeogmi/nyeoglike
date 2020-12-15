import os.path
from typing import Dict, Iterator, List, Optional, Set

from ds.relational import OneToMany
from ds.vecs import V2

from ..item import Item, common
from ..npc import NPCHandle
from .block import Block


class LoadedLevel(object):
    def __init__(
        self,
        blocks: Dict[V2, Block],
        items: Dict[V2, List[Item]],
        npc_sites: OneToMany[V2, NPCHandle],
    ):
        self.blocks: Dict[V2, Block] = blocks
        self.seen: Set[V2] = set()  # every time the player sees a tile, add it to this
        self.items: Dict[V2, List[Item]] = items
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
