from ds.gensym import Gensym, Sym
from ds.relational import OneToOne, OneToMany
from typing import NamedTuple, Optional, Iterator

from ..npc import NPCHandle
from ..worldmap import LevelHandle, Demand, ZoneType


class HouseholdHandle(NamedTuple):
    ident: Sym


# TODO: When asking about an NPC's household -- if they don't have one, create a household of one.
#  (Or consider generating more NPCs and putting them together in a household. Or take another householdless NPC and
#   make the two roommates.)
class Households(object):
    def __init__(self):
        self._sym = Gensym("HH")

        self._members: OneToMany[HouseholdHandle, NPCHandle] = OneToMany()
        self._lives_at: OneToOne[HouseholdHandle, LevelHandle] = OneToOne()

    def generate(self, world: "World", n_npcs: int) -> HouseholdHandle:
        # TODO: Consider having NPCs share a last name
        from ..world import World
        assert isinstance(world, World)
        assert isinstance(n_npcs, int)

        handle = HouseholdHandle(self._sym.gen())
        for i in range(n_npcs):
            self._members.add(handle, world.npcs.generate())

        return handle

    def get_home(self, world: "World", household: HouseholdHandle) -> LevelHandle:
        from ..world import World
        assert isinstance(world, World)
        assert isinstance(household, HouseholdHandle)

        if self._lives_at.get_b(household) is None:
            self._lives_at.add(
                household,
                world.levels.zone(ZoneType.Residence, self._demand(household))
            )

        level = self._lives_at.get_b(household)
        assert isinstance(level, LevelHandle)

        return level

    def living_at(self, level: LevelHandle) -> Optional[HouseholdHandle]:
        assert isinstance(level, LevelHandle)

        return self._lives_at.get_a(level)

    def household_of(self, npc: NPCHandle) -> Optional[HouseholdHandle]:
        assert isinstance(npc, NPCHandle)

        return self._members.get_a(npc)

    def members(self, household: HouseholdHandle) -> Iterator[NPCHandle]:
        assert isinstance(household, HouseholdHandle)

        for member in self._members.get_bs(household):
            yield member

    def _demand(self, household: HouseholdHandle) -> Demand:
        return Demand()


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..world import World