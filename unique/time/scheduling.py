import random
from typing import Dict, List, Optional

from ds.relational import OneToMany

from ..npc import NPCHandle
from . import schedule_items
from .schedule_item import ALL as SCHEDULE_ITEMS
from .schedule_item import DestinationRule, ScheduleItem
from .time_of_day import TimeOfDay


class Schedule(object):
    def __init__(self):
        self._items: Dict[NPCHandle, ScheduleItem] = {}
        self._calculated_location: Dict[NPCHandle, LevelHandle] = {}
        self._calculated_location_determines: OneToMany[
            NPCHandle, NPCHandle
        ] = OneToMany()

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

    def _get_location(
        self, world: "World", npch: NPCHandle, breadcrumbs: List[NPCHandle]
    ) -> "LevelHandle":
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
            result = world.households.get_home(
                world, world.households.household_of(npch)
            )

        else:
            rule = SCHEDULE_ITEMS.get(schedule_item.name).destination_rule
            if rule == DestinationRule.MyHousehold:
                result = world.households.get_home(
                    world, world.households.household_of(npch)
                )
            elif rule == DestinationRule.Follow:
                from ..social import EnterpriseHandle
                from ..worldmap import LevelHandle

                if isinstance(schedule_item.arg, NPCHandle):
                    result = recurse(schedule_item.arg)
                    dependency = npch
                elif isinstance(schedule_item.arg, EnterpriseHandle):
                    result = world.enterprises.get_site(world, schedule_item.arg)
                elif isinstance(schedule_item.arg, LevelHandle):
                    result = schedule_item.arg
                else:
                    raise AssertionError(
                        "don't know how to follow: {}", schedule_item.arg
                    )
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

    def prev_schedule(self, npch: NPCHandle) -> Optional[ScheduleItem]:
        try:
            return self._prev_schedule[npch]
        except KeyError:
            return None

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

        # emergencies
        all_npcs = set(world.npcs.all())
        no_emergency = set()
        for npc in all_npcs:
            if world.rhythms.is_very_sleepy(npc):
                next_schedule[npc] = schedule_items.HomeSleep
            else:
                no_emergency.add(npc)

        # otherwise, try to go to work
        not_busy = set()
        for npc in no_emergency:
            shifts_now = [
                shift
                for shift in world.enterprises.get_shifts_worked_by(npc)
                if world.enterprises.get_shift(shift).active_at(time_of_day)
            ]
            if not shifts_now:
                not_busy.add(npc)
                continue

            go_to = random.choice(shifts_now)
            next_schedule[npc] = schedule_items.GoToWork(go_to.enterprise)

        # otherwise, find something to do
        up_for_fun = set()
        for npc in not_busy:
            sleepy = world.rhythms.can_sleep(npc)
            if sleepy:
                next_schedule[npc] = schedule_items.HomeSleep
            else:
                next_schedule[npc] = schedule_items.HomeFun
                up_for_fun.add(npc)

        for npc in up_for_fun:
            # write the friends in random order
            some_friends = list(world.friendships.friends(npc))
            random.shuffle(some_friends)

            for possible_engagement in some_friends:
                if possible_engagement in up_for_fun:
                    date = possible_engagement
                    # it's a date!
                    break
            else:
                # no one to do stuff with
                # TODO: In the future, solo activities outside the house with randoms
                break

            # NOTE: This is the only group activity right now
            next_schedule[npc] = schedule_items.SleepOver(date)
            next_schedule[
                date
            ] = (
                schedule_items.HostSleepOver
            )  # it doesn't make sense for the sleepover guy to be asleep for his own party

        self._prev_schedule, self._next_schedule = self._next_schedule, next_schedule


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..social import EnterpriseHandle
    from ..world import World
    from ..worldmap import LevelHandle
