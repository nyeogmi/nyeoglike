from enum import Enum
from ..npc import NPCHandle

from typing import Optional, NamedTuple, Type


class DestinationRule(Enum):
    MyHousehold = 0
    Follow = 1


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
        from ..social.enterprises import EnterpriseHandle
        if isinstance(self.arg, NPCHandle):
            tx = world.npcs.get(self.arg).name
        elif isinstance(self.arg, EnterpriseHandle):
            tx = world.enterprises.get_name(self.arg)
        else:
            tx = str(self.arg)

        return ALL.get(self.name).format.format(self, arg=tx)


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
    from ..world import World

