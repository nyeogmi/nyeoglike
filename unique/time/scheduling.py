from ..npc import NPCHandle
from .schedule_item import ScheduleItem
from .time_of_day import TimeOfDay
from . import schedule_items

from ds.relational import OneToMany
from typing import Dict, List, Optional
from .schedule_item import ALL as SCHEDULE_ITEMS
from .schedule_item import DestinationRule

import random


class Schedule(object):
    def __init__(self):
        self._items: Dict[NPCHandle, ScheduleItem] = {}
        self._calculated_location: Dict[NPCHandle, LevelHandle] = {}
        self._calculated_location_determines: OneToMany[NPCHandle, NPCHandle] = OneToMany()

    def __getitem__(self, npch: NPCHandle) -> ScheduleItem:
        assert isinstance(npch, NPCHandle)
        return self._items[npch]

    def __setitem__(self, npch: NPCHandle, schedule_item: ScheduleItem):
        assert isinstance(npch, NPCHandle)
        assert isinstance(schedule_item, ScheduleItem)
        del self[npch]

        self._items[npch] = schedule_item

    def __delitem__(self, npch: NPCHandle):
        assert isinstance(npch, NPCHandle)
        if npch in self._items:
            del self._items[npch]

        self.clear_location(npch)

    def get_location(self, world: "World", npch: NPCHandle) -> "LevelHandle":
        return self._get_location(world, npch, [])

    def _get_location(self, world: "World", npch: NPCHandle, breadcrumbs: List[NPCHandle]) -> "LevelHandle":
        from ..world import World
        assert isinstance(world, World)
        assert isinstance(npch, NPCHandle)
        assert isinstance(breadcrumbs, list)

        def recurse(onto):
            breadcrumbs.append(npch)
            res = self._get_location(world, onto, breadcrumbs)
            breadcrumbs.pop()
            return res

        schedule_item: ScheduleItem = self[npch]

        if npch in self._calculated_location:
            return self._calculated_location[npch]

        dependency = None
        if npch in breadcrumbs:
            result = world.households.get_home(world, world.households.household_of(npch))

        else:
            rule = SCHEDULE_ITEMS.get(schedule_item.name).destination_rule
            if rule == DestinationRule.MyHousehold:
                result = world.households.get_home(world, world.households.household_of(npch))
            elif rule == DestinationRule.FollowNPC:
                assert isinstance(schedule_item.arg, NPCHandle)
                result = recurse(schedule_item.arg)
                dependency = npch
            else:
                raise AssertionError("unrecognized rule: {}".format(rule))

        self._calculated_location[result] = result
        if dependency:
            self._calculated_location_determines.add(dependency, npch)
        else:
            self._calculated_location_determines.remove_b(npch)
        return result

    def set_location(self, npch: NPCHandle, level_handle: "LevelHandle"):
        from ..worldmap import LevelHandle
        assert isinstance(npch, NPCHandle)
        assert isinstance(level_handle, LevelHandle)
        self.clear_location(npch)
        self._calculated_location[npch] = level_handle

    def clear_location(self, npch: NPCHandle):
        assert isinstance(npch, NPCHandle)
        if npch in self._calculated_location:
            del self._calculated_location[npch]

        dependers = list(self._calculated_location_determines.get_bs(npch))
        self._calculated_location_determines.remove_a(npch)
        for depender in dependers:
            self.clear_location(depender)


class Schedules(object):
    def __init__(self):
        self._prev_schedule = Schedule()
        self._next_schedule = Schedule()

    def next_schedule(self, npch: NPCHandle) -> ScheduleItem:
        return self._next_schedule[npch]

    def next_location(self, world: "World", npch: NPCHandle) -> "LevelHandle":
        from ..world import World
        assert isinstance(world, World)
        assert isinstance(npch, NPCHandle)
        return self._next_schedule.get_location(world, npch)

    def calculate_schedules(self, world: "World", time_of_day: TimeOfDay):
        from ..world import World
        assert isinstance(world, World)
        assert isinstance(time_of_day, TimeOfDay)

        next_schedule = Schedule()

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


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..world import World
    from ..worldmap import LevelHandle
