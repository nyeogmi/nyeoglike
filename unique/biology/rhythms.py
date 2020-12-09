from ..npc import NPCHandle
from enum import Enum
from typing import Dict
from functools import total_ordering


# Notes:
# Each "_quantity" is 4 hours worth.
# Most creatures eat 2 meals/day, so each meal is worth 12 hours; 3
# Likewise, most creatures sleep 8 hours a day, so each 4 hour nap is worth 12 hours; 3.
# Some creatures sleep 12 hours a day, so each 4 hour nap is worth 8 hours for them; 2.  (Probably daytime naps work like this)
#  (Note that 4 hours of that is instantly depleted at the end of the nap.)
# The cap is 10: in other words, a maximally fed creature will be maximally hungry or sleepy in 40 hours

# The spectrum:
#  >= 10 - Capped. Doing it more causes no additional good
#  >=  8 - Satisfied. Users will deviate from their usual schedule if higher than this
#  >=  6 - Scheduled. Users will satisfy the need according to their usual schedule if higher than this.
#  >=  3 - Desperate. Users will deviate from unimportant items of their usual schedule if higher than this.
#  >=  0 - Emergency. The user can't need it any more than this


@total_ordering
class Spectrum(Enum):
    Capped = 0
    Satisfied = 1
    Scheduled = 2
    Desperate = 3
    Emergency = 4

    def __lt__(self, other):
        assert isinstance(other, Spectrum)
        return self.value < other.value


class Rhythm(object):
    def __init__(self):
        self._quantity: Dict[NPCHandle, int] = {}

    def advance_time(self):
        for k in list(self._quantity.keys()):
            self._quantity[k] = max(0, self._quantity[k] - 1)

    def feed(self, npc: NPCHandle, quantity: int):
        assert isinstance(npc, NPCHandle)
        assert isinstance(quantity, int)

        self._quantity[npc] = min(10, self._quantity.get(npc, 0) + quantity)

    def get(self, npc: NPCHandle) -> Spectrum:
        assert isinstance(npc, NPCHandle)

        value = self._quantity.get(npc, 0)
        return (
            Spectrum.Capped if value >= 10 else
            Spectrum.Satisfied if value >= 8 else
            Spectrum.Scheduled if value >= 6 else
            Spectrum.Desperate if value >= 3 else
            Spectrum.Emergency
        )


class Rhythms(object):
    def __init__(self):
        self._sleepiness = Rhythm()
        self._hunger = Rhythm()

    def advance_time(self):
        self._sleepiness.advance_time()
        self._hunger.advance_time()

    def sleep(self, npc: NPCHandle, quantity: int):
        self._sleepiness.feed(npc, quantity)

    def feed(self, npc: NPCHandle, quantity: int):
        self._hunger.feed(npc, quantity)

    def get_sleepiness(self, npc: NPCHandle) -> Spectrum:
        return self._sleepiness.get(npc)

    def get_hunger(self, npc: NPCHandle) -> Spectrum:
        return self._hunger.get(npc)

    def can_sleep(self, npc: NPCHandle) -> bool:
        # NOTE: Check this against the NPC's sleep schedule, don't say "yes" unless it's sleeping time
        return self.get_sleepiness(npc) >= Spectrum.Satisfied

    def is_sleepy(self, npc: NPCHandle) -> bool:
        return self.get_sleepiness(npc) >= Spectrum.Desperate

    def is_very_sleepy(self, npc: NPCHandle) -> bool:
        return self.get_sleepiness(npc) >= Spectrum.Emergency

    def can_eat(self, npc: NPCHandle) -> bool:
        # NOTE: Check this against the NPC's eating schedule, don't say "yes" unless it's eating time
        # Alternately, NPCs can just eat any old time
        return self.get_hunger(npc) >= Spectrum.Satisfied

    def is_hungry(self, npc: NPCHandle) -> bool:
        return self.get_hunger(npc) >= Spectrum.Desperate

    def is_very_hungry(self, npc: NPCHandle) -> bool:
        return self.get_hunger(npc) >= Spectrum.Emergency
