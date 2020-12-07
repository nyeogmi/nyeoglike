from ds.gensym import Gensym, Sym
from ds.relational import OneToMany, OneToOne

from enum import Enum
from typing import Dict, List, NamedTuple, Optional, Iterator
from ..npc import NPCHandle
from ..worldmap import LevelHandle, Demand, ZoneType
import random


class EnterpriseHandle(NamedTuple):
    ident: Sym


class ShiftHandle(NamedTuple):
    enterprise: EnterpriseHandle
    shift: int


class Shift(Enum):
    EveningDusk = 0
    DuskMidnight = 1
    MidnightDawn = 2
    DawnEvening = 3

    def active_at(self, time_of_day: "TimeOfDay"):
        from ..time import TimeOfDay
        if self == Shift.EveningDusk:
            return time_of_day == TimeOfDay.Evening or TimeOfDay == TimeOfDay.Dusk
        elif self == Shift.DuskMidnight:
            return time_of_day == TimeOfDay.Dusk or TimeOfDay == TimeOfDay.Midnight
        elif self == Shift.MidnightDawn:
            return time_of_day == TimeOfDay.Midnight or TimeOfDay == TimeOfDay.Dawn
        elif self == Shift.DawnEvening:
            return time_of_day == TimeOfDay.Dawn or TimeOfDay == TimeOfDay.Evening
        else:
            raise AssertionError("don't know when {} is active".format(self))


class Enterprise(object):
    def __init__(self, ident: EnterpriseHandle, zone_type: ZoneType, shifts: List[Shift]):
        assert isinstance(ident, EnterpriseHandle)
        assert isinstance(zone_type, ZoneType)
        assert isinstance(shifts, list)
        self._ident: EnterpriseHandle = ident
        self._zone_type: ZoneType = zone_type
        self._shifts: List[Shift] = shifts

    @property
    def name(self):
        return "International House of Bats"  # TODO

    @property
    def zone_type(self):
        return self._zone_type

    @classmethod
    def generate(cls, ident: EnterpriseHandle, zone_type: ZoneType) -> "Enterprise":
        assert isinstance(ident, EnterpriseHandle)
        needed_at_once = random.randint(1, 3)

        way_of_operation = random.choice([
            [Shift.EveningDusk, Shift.MidnightDawn],
            [Shift.DuskMidnight, Shift.DawnEvening],
        ])

        return Enterprise(ident, zone_type, way_of_operation * needed_at_once)

    def all_shifts(self) -> List[ShiftHandle]:
        return [
            ShiftHandle(self._ident, i)
            for i, shift in enumerate(self._shifts)
        ]


class Enterprises(object):
    def __init__(self):
        self._sym = Gensym("ENT")

        self._all: Dict[EnterpriseHandle, Enterprise] = {}
        self._works: OneToMany[NPCHandle, ShiftHandle] = OneToMany()
        self._located_at: OneToOne[EnterpriseHandle, LevelHandle] = OneToOne()

    def generate(self, world: "World", zone_type: ZoneType) -> EnterpriseHandle:
        from ..world import World
        assert isinstance(world, World)
        assert isinstance(zone_type, ZoneType)

        handle = EnterpriseHandle(self._sym.gen())
        self._all[handle] = Enterprise.generate(handle, zone_type)
        return handle

    def all(self) -> Iterator[EnterpriseHandle]:
        for e in self._all:
            yield e

    def get_name(self, enterprise: EnterpriseHandle) -> str:
        assert isinstance(enterprise, EnterpriseHandle)
        return self._all[enterprise].name

    def get_site(self, world: "World", enterprise: EnterpriseHandle) -> LevelHandle:
        from ..world import World

        assert isinstance(world, World)
        assert isinstance(enterprise, EnterpriseHandle)

        if self._located_at.get_b(enterprise) is None:
            real_enterprise = self._all[enterprise]
            self._located_at.add(
                enterprise,
                world.levels.zone(real_enterprise.zone_type, self._demand(enterprise))
            )

        level = self._located_at.get_b(enterprise)
        assert isinstance(level, LevelHandle)

        return level

    def shift_active_at(self, shift: ShiftHandle, time: "TimeOfDay") -> bool:
        return self._all[shift.enterprise]._shifts[shift.shift].active_at(time)

    def employ(self, shift: ShiftHandle, npc: NPCHandle):
        assert isinstance(shift, ShiftHandle)
        assert isinstance(npc, NPCHandle)
        self._works.add(npc, shift)

    def unemploy(self, shift: ShiftHandle, npc: NPCHandle):
        assert isinstance(shift, ShiftHandle)
        assert isinstance(npc, NPCHandle)
        self._works.remove(npc, shift)

    def get_employees(self, enterprise: EnterpriseHandle) -> Iterator[NPCHandle]:
        assert isinstance(enterprise, EnterpriseHandle)
        for shift in self.all_shifts_of(enterprise):
            emp = self.get_employee(shift)
            if emp:
                yield emp

    def get_employee(self, shift: ShiftHandle) -> Optional[NPCHandle]:
        assert isinstance(shift, ShiftHandle)
        return self._works.get_a(shift)

    def get_shifts_worked_by(self, npc: NPCHandle) -> Iterator[ShiftHandle]:
        assert isinstance(npc, NPCHandle)
        for shift in self._works.get_bs(npc):
            yield shift

    def all_shifts_of(self, enterprise: EnterpriseHandle):
        assert isinstance(enterprise, EnterpriseHandle)
        for shift in self._all[enterprise].all_shifts():
            yield shift

    def all_shifts(self) -> Iterator[ShiftHandle]:
        for enterprise in self._all:
            for shift in self.all_shifts_of(enterprise):
                yield shift

    def _demand(self, enterprise: EnterpriseHandle) -> Demand:
        return Demand()


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..world import World
    from ..time import TimeOfDay
