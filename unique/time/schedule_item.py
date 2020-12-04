from enum import Enum
from ..npc import NPCHandle

from typing import Optional, NamedTuple, Type


class DestinationRule(Enum):
    MyHousehold = 0
    NPCArgHousehold = 1


class _Verb(NamedTuple):
    name: str
    arg_type: Type
    format: str
    destination_rule: DestinationRule

    def __call__(self, arg) -> "ScheduleItem":
        assert isinstance(arg, self.arg_type)
        return ScheduleItem(self.name, arg)


class ScheduleItem(NamedTuple):
    name: str
    arg: object

    def to_text(self, world: "World") -> str:
        if isinstance(self.arg, NPCHandle):
            tx = world.npcs.get(self.arg).name
        else:
            tx = str(self.arg)

        return ALL.get(self.name).format.format(self, arg=tx)

    def location(self, me: NPCHandle, world: "World") -> Optional["HouseholdHandle"]:  # TODO: Other location types
        rule = ALL.get(self.name).destination_rule

        if rule == DestinationRule.MyHousehold:
            return world.households.household_of(me)
        elif rule == DestinationRule.NPCArgHousehold:
            assert isinstance(self.arg, NPCHandle)
            return world.households.household_of(self.arg)
        else:
            raise AssertionError("unrecognized rule: {}".format(rule))


class _Verbs(object):
    def __init__(self):
        self._all = {}

    def verb(self, name: str, arg_type: Type, format: str, destination_rule: DestinationRule) -> _Verb:
        assert name not in self._all
        self._all[name] = _Verb(name, arg_type, format, destination_rule)
        return self._all[name]

    def get(self, name: str) -> _Verb:
        return self._all[name]


ALL = _Verbs()


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..social import HouseholdHandle
    from ..world import World

