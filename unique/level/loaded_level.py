from ds.relational import OneToMany
from ds.vecs import V2
from typing import Dict, List, Set, Iterator
import os.path
from ..item import Item, common
from ..npc import NPCHandle


class LoadedLevel(object):
    def __init__(
        self,
        blocks: Dict[V2, bool],
        items: Dict[V2, List[Item]],
        npc_sites: OneToMany[V2, NPCHandle]
    ):
        # TODO: These will be expensive to validate, maybe don't do it now
        assert isinstance(blocks, dict) and all(isinstance(k, V2) and isinstance(v, bool) for k, v in blocks.items())

        self.blocks: Dict[V2, bool] = blocks
        self.seen: Set[V2] = set()  # every time the player sees a tile, add it to this
        self.items: Dict[V2, List[Item]] = items
        self.npc_sites: OneToMany[V2, NPCHandle] = npc_sites

    def npc_location(self, npc: NPCHandle) -> V2:
        return self.npc_sites.get_a(npc)

    def loaded_npcs(self) -> Iterator[NPCHandle]:
        for npc in self.npc_sites.all_bs():
            yield npc


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..world import World