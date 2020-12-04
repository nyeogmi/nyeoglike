from ..npc import NPCHandle
from .schedule_item import ScheduleItem
from .time_of_day import TimeOfDay
from . import schedule_items

import random


class Schedules(object):
    def __init__(self):
        self._prev_schedule = {}
        self._next_schedule = {}

    def next_schedule(self, npch: NPCHandle) -> ScheduleItem:
        assert isinstance(npch, NPCHandle)

        return self._next_schedule[npch]

    def calculate_schedules(self, world: "World", time_of_day: TimeOfDay):
        from ..world import World
        assert isinstance(world, World)
        assert isinstance(time_of_day, TimeOfDay)

        next_schedule = {}

        # TODO: NPCs who have nighttime jobs

        not_sleepy = set()
        for npc in world.npcs.all():
            sleepy = random.choice([False, True])  # TODO: Smarter way to calculate this
            if sleepy:
                next_schedule[npc] = schedule_items.HomeSleep
            else:
                next_schedule[npc] = schedule_items.HomeFun
                not_sleepy.add(npc)

        for npc in not_sleepy:
            # write the friends in random order
            some_friends = list(world.friendships.friends(npc))
            random.shuffle(some_friends)

            for possible_engagement in some_friends:
                if possible_engagement in not_sleepy:
                    date = possible_engagement
                    # it's a date!
                    break
            else:
                # no one to do stuff with
                # TODO: In the future, solo activities outside the house with randoms
                break

            # NOTE: This is the only group activity right now
            next_schedule[npc] = schedule_items.SleepOver(date)
            next_schedule[date] = schedule_items.HostSleepOver  # it doesn't make sense for the sleepover guy to be asleep for his own party

        self._prev_schedule, self._next_schedule = self._next_schedule, next_schedule


def transition(world: "World", npch: NPCHandle, time_of_day: TimeOfDay) -> ScheduleItem:
    from ..world import World
    assert isinstance(world, World)
    assert isinstance(time_of_day, TimeOfDay)

    npc = world.npcs.get(npch)

    if time_of_day == TimeOfDay.Evening:
        raise AssertionError("NPCs can't transition into evening")

    elif time_of_day == TimeOfDay.Dusk:
        if npc.asleep:
            return schedule_items.HomeSleep

        if random.random() < 0.2:
            return schedule_items.HomeFun

        return schedule_items.HomeSleep

    elif time_of_day == TimeOfDay.Midnight:
        if npc.asleep:
            return schedule_items.HomeSleep

        if random.random() < 0.1:
            return schedule_items.HomeFun

        return schedule_items.HomeSleep

    elif time_of_day == TimeOfDay.Dawn:
        if npc.asleep and random.random() < 0.5:
            return schedule_items.HomeSleep

        if random.random() < 0.7:
            return schedule_items.HomeFun

        return schedule_items.HomeSleep

    elif time_of_day == TimeOfDay.Morning:
        # TODO
        return schedule_items.HomeFun


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..world import World