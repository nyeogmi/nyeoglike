from enum import Enum
from .npc import NPCHandle

import random


class TimeOfDay(Enum):
    Evening = 0
    Dusk = 1
    Midnight = 2
    Dawn = 3
    Morning = 4  # TODO: Purely cosmetic transitions seems bad to me

    def display(self) -> str:
        return self.name

    def next(self):
        if self == TimeOfDay.Evening:
            return TimeOfDay.Dusk
        if self == TimeOfDay.Dusk:
            return TimeOfDay.Midnight
        if self == TimeOfDay.Midnight:
            return TimeOfDay.Dawn
        if self == TimeOfDay.Dawn:
            return TimeOfDay.Morning
        if self == TimeOfDay.Morning:
            raise ValueError("it should never be morning")

    def next_gameplay(self):
        # TODO: Sleep thru the night
        if self == TimeOfDay.Evening:
            return TimeOfDay.Dusk
        if self == TimeOfDay.Dusk:
            return TimeOfDay.Midnight
        if self == TimeOfDay.Midnight:
            return TimeOfDay.Dawn
        if self == TimeOfDay.Dawn:
            return TimeOfDay.Evening
        if self == TimeOfDay.Morning:
            raise ValueError("it should never be morning")


class ScheduleItem(Enum):
    HomeFun = 0
    HomeSleep = 1

    def to_text(self) -> str:
        if self == ScheduleItem.HomeFun:
            return "home, not sleepy"
        elif self == ScheduleItem.HomeSleep:
            return "home to sleep"
        raise NotImplementedError


class Schedules(object):
    def __init__(self):
        self._next_location = {}
        self._time_of_day = TimeOfDay.Evening

    @property
    def time_of_day(self):
        return self._time_of_day

    def advance_time(self):
        self._next_location = {}
        self._time_of_day = self._time_of_day.next_gameplay()

    def next_location(self, world: "World", npch: NPCHandle) -> ScheduleItem:
        from .world import World
        assert isinstance(world, World)
        assert isinstance(npch, NPCHandle)

        if npch not in self._next_location:
            self._next_location[npch] = transition(world, npch, self._time_of_day.next())
        return self._next_location[npch]


def transition(world: "World", npch: NPCHandle, time_of_day: TimeOfDay) -> ScheduleItem:
    from .world import World
    assert isinstance(world, World)
    assert isinstance(time_of_day, TimeOfDay)

    npc = world.npcs.get(npch)

    if time_of_day == TimeOfDay.Evening:
        raise AssertionError("NPCs can't transition into evening")

    elif time_of_day == TimeOfDay.Dusk:
        if npc.asleep:
            return ScheduleItem.HomeSleep

        if random.random() < 0.2:
            return ScheduleItem.HomeFun

        return ScheduleItem.HomeSleep

    elif time_of_day == TimeOfDay.Midnight:
        if npc.asleep:
            return ScheduleItem.HomeSleep

        if random.random() < 0.1:
            return ScheduleItem.HomeFun

        return ScheduleItem.HomeSleep

    elif time_of_day == TimeOfDay.Dawn:
        if npc.asleep and random.random() < 0.5:
            return ScheduleItem.HomeSleep

        if random.random() < 0.7:
            return ScheduleItem.HomeFun

        return ScheduleItem.HomeSleep

    elif time_of_day == TimeOfDay.Morning:
        # TODO
        return ScheduleItem.HomeFun


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .world import World