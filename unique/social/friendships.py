import random
from typing import Iterator, List

from ds.relational import ManyToMany

from ..npc import NPCHandle


class Friendships(object):
    def __init__(self):
        self._likes = ManyToMany()

    # TODO: One-sided friendship
    # TODO: Negative feelings
    def like(self, npc1, npc2):
        assert isinstance(npc1, NPCHandle)
        self._likes.add(npc1, npc2)

    # mostly symmetrical many-to-many relationship
    def add_friend(self, npc1, npc2):
        assert isinstance(npc1, NPCHandle)
        assert isinstance(npc2, NPCHandle)

        self._likes.add(npc1, npc2)
        self._likes.add(npc2, npc1)

    def remove_friend(self, npc1, npc2):
        assert isinstance(npc1, NPCHandle)
        assert isinstance(npc2, NPCHandle)

        self._likes.remove(npc1, npc2)
        self._likes.remove(npc2, npc1)

    def friends(self, npc: NPCHandle) -> Iterator[NPCHandle]:
        for likee in self._likes.get_bs(npc):
            if self._likes.has(likee, npc):
                yield likee

    def npc_likes(self, npc1: NPCHandle, npc2: NPCHandle):
        return self._likes.has(npc1, npc2)

    def mingle(self, world: "World", friends_per_npc: int):
        npcs = list(world.npcs.all())
        for f in range(friends_per_npc):
            random.shuffle(npcs)

            for i0, i1 in zip(range(0, len(npcs), 2), range(1, len(npcs), 2)):
                self.add_friend(npcs[i0], npcs[i1])


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world import World
