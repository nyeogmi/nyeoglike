from ds.gensym import Gensym, Sym
from ds.relational import OneToMany
from typing import NamedTuple

from ..npc import NPCHandle


class HouseholdHandle(NamedTuple):
    ident: Sym


# TODO: When asking about an NPC's household -- if they don't have one, create a household of one.
class Households(object):
    def __init__(self):
        self._sym = Gensym("HH")
        self._members: OneToMany[HouseholdHandle, NPCHandle] = OneToMany()

    def generate(self, world: "World", n_npcs: int) -> HouseholdHandle:
        # TODO: Consider having NPCs share a last name

        handle = HouseholdHandle(self._sym.gen())
        for i in range(n_npcs):
            self._members.add(handle, world.npcs.generate())

        return handle


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..world import World