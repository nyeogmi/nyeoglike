from typing import Callable, NamedTuple
from ..level import UnloadedLevel, Veto


N_PROPERTIES = 20
MAX_TIMES_UNSOLD = 5

TRIES_PER_PROPERTY = 5


class Property(NamedTuple):
    level: UnloadedLevel
    times_unsold: int


class Realtor(object):
    def __init__(self, level_generator: Callable[[], UnloadedLevel]):
        self._properties = []
        self._level_generator = level_generator

    def gen(self):
        self._restock()

    def _restock(self):
        tallies_to_add = []
        for tally in range(MAX_TIMES_UNSOLD):
            for xi in range(N_PROPERTIES // MAX_TIMES_UNSOLD):
                tallies_to_add.append(tally)

        properties_needed = MAX_TIMES_UNSOLD - len(self._properties)
        tallies_to_add = tallies_to_add[:properties_needed]

        max_tries = properties_needed * TRIES_PER_PROPERTY
        for t in range(max_tries):
            if len(self._properties) >= N_PROPERTIES:
                break

            try:
                level = self._level_generator()
                tally = tallies_to_add.pop(0)
                self._properties.append(Property(level=level, times_unsold=tally))
            except Veto as v:
                continue

        else:
            raise AssertionError("couldn't generate {} properties in {} tries".format(properties_needed, max_tries))
