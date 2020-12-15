from typing import Callable, List, NamedTuple
from ..level import UnloadedLevel, Veto


N_PROPERTIES = 20
MAX_TIMES_UNSOLD = 5

TRIES_PER_PROPERTY = 5


class Property(NamedTuple):
    level: UnloadedLevel
    times_unsold: int


class Demand(NamedTuple):
    # TODO: Flesh it out

    def score(self, property: Property) -> int:
        # TODO
        return 0.0


class Realtor(object):
    def __init__(self, level_generator: Callable[[], UnloadedLevel]):
        self._properties: List[Property] = []
        self._level_generator: Callable[[], UnloadedLevel] = level_generator

    def gen(self, demand: Demand) -> UnloadedLevel:
        self._restock()

        best_property_ix = max(
            range(len(self._properties)),
            key=lambda i: demand.score(self._properties[i]),
        )
        property = self._properties.pop(best_property_ix)

        for i in range(len(self._properties)):
            self._properties[i] = self._properties[i]._replace(
                times_unsold=self._properties[i].times_unsold + 1
            )

        return property.level

    def _restock(self):
        for i in range(len(self._properties))[::-1]:
            if self._properties[i].times_unsold > MAX_TIMES_UNSOLD:
                self._properties.pop(i)

        tallies_to_add = []
        for tally in range(MAX_TIMES_UNSOLD):
            for xi in range(N_PROPERTIES // MAX_TIMES_UNSOLD):
                tallies_to_add.append(tally)

        properties_needed = N_PROPERTIES - len(self._properties)
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
            raise AssertionError(
                "couldn't generate {} properties in {} tries".format(
                    properties_needed, max_tries
                )
            )
