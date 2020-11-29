from ds.relational import OneToMany
from ds.vecs import V2
from typing import Dict, List, Iterator
import os.path
from .npc import NPCHandle


class Level(object):
    def __init__(
        self,
        player_start_xy: V2,
        blocks: Dict[V2, bool],
        npc_sites: OneToMany[V2, NPCHandle]
    ):
        assert isinstance(player_start_xy, V2)

        # TODO: These will be expensive to validate, maybe don't do it now
        assert isinstance(blocks, dict) and all(isinstance(k, V2) and isinstance(v, bool) for k, v in blocks.items())

        self.player_start_xy = player_start_xy
        self.blocks: Dict[V2, bool] = blocks
        self.npc_sites: OneToMany[V2, NPCHandle] = npc_sites

    @classmethod
    def load(cls, world: "World", name):
        fname = os.path.join("ascii/levels", name)

        player_xy = None
        blocks = {}
        npc_sites = OneToMany()

        with open(fname, "rt") as f:
            text = f.read()
            for y, line in enumerate(text.splitlines()):
                for x, c in enumerate(line):
                    v = V2.new(x, y)
                    if c == "@":
                        assert player_xy is None
                        player_xy = v
                    elif c == "$":
                        # TODO: Don't generate, fetch?
                        npc_sites.add(v, world.npcs.generate())
                    elif c == "#":
                        blocks[v] = True
                    elif c == " ":
                        pass
                    else:
                        raise AssertionError("unrecognized character: %r" % (c,))

        assert player_xy is not None

        return Level(
            player_xy,
            blocks,
            npc_sites,
        )

    def npc_location(self, npc: NPCHandle) -> V2:
        return self.npc_sites.get_a(npc)

    def loaded_npcs(self) -> Iterator[NPCHandle]:
        for npc in self.npc_sites.all_bs():
            yield npc


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .world import World