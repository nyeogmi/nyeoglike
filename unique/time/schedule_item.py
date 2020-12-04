from enum import Enum
from ..npc import NPCHandle

from typing import Optional, NamedTuple, Type


class _Verb(NamedTuple):
    name: str
    arg_type: Type
    format: str

    def __call__(self, arg) -> "ScheduleItem":
        assert isinstance(arg, self.arg_type)
        return ScheduleItem(self.name, arg)


class ScheduleItem(NamedTuple):
    name: str
    arg: object

    def to_text(self) -> str:
        return ALL.get(self.name).format.format(self, arg=self.arg)


class _Verbs(object):
    def __init__(self):
        self._all = {}

    def verb(self, name: str, arg_type: Type, format: str) -> _Verb:
        assert name not in self._all
        self._all[name] = _Verb(name, arg_type, format)
        return self._all[name]

    def get(self, name: str) -> _Verb:
        return self._all[name]


ALL = _Verbs()
