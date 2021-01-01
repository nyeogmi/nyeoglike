import os.path
import random
from typing import List, Optional

from ds.vecs import V2

from .biology import Rhythms
from .event import Event, Verbs
from .eventmonitor import EventMonitor, EventMonitors
from .interest import InterestTracker
from .inventory import Inventory
from .level import LoadedLevel, SpawnNPC, UnloadedLevel
from .notifications import Notification, Notifications
from .npc import NPC, NPCHandle, NPCs
from .scene_flags import SceneFlags
from .social import Enterprises, Friendships, HouseholdHandle, Households
from .time import Clock, Schedules
from .worldmap import LevelHandle, Levels

N_HOUSEHOLDS = 30
N_HOUSEHOLD_NPCS = (1, 5)


class World(object):
    def __init__(self):
        self.clock = Clock()
        self.enterprises = Enterprises()
        self.eventmonitors = EventMonitors()
        self.friendships = Friendships()
        self.households = Households()
        self.interest = InterestTracker()
        self.levels = Levels()
        self.notifications = Notifications()
        self.npcs = NPCs()
        self.rhythms = Rhythms()
        self.scene_flags = SceneFlags()
        self.schedules = Schedules()

        self.camera_xy: V2 = V2.zero()
        self.player_xy: V2 = V2.zero()
        self.inventory: Inventory = Inventory()

        self.level: Optional[LoadedLevel] = None

        self._notifying = False
        self._notify_queue = []

    @classmethod
    def generate(cls):
        from .bigprocs.worldgen import main

        world = cls()
        main(world)
        return world

    def advance_time(self):
        self.clock.advance_time()
        self.end_time_period()
        self.start_time_period()

    def start_time_period(self):
        if not self.clock.started:
            # This can be called more than once

            self.clock.start()
            self.rhythms.advance_time()
            self.schedules.calculate_schedules(self, self.clock.time_of_day.next())
            self.scene_flags.reset()
            self.scene_flags.populate_from_schedules(
                self
            )  # (calculated from their prev. schedules, which they are acting out now)

    def end_time_period(self):
        if not self.clock.started:
            return

        # TODO: Provide rewards for scene flags, like sleep?
        # Although those should generally be awarded as soon as they are added
        pass

    def follow_npc(self, npc: NPCHandle):
        location = self.schedules.next_location(self, npc)
        self.activate_level(location)

    def activate_level(self, level: LevelHandle):
        # figure out who will be there
        # for now, the whole household. in the future use the schedule info
        spawns = []
        for npch in self.npcs.all():
            # TODO: Move this to schedules object
            if self.schedules.next_location(self, npch) == level:
                spawns.append(
                    SpawnNPC(npc=npch, schedule=self.schedules.next_schedule(npch))
                )

        lvl = self.levels.get(level)
        self._activate_level(level, lvl, spawns)

    def _activate_level(
        self, ident: LevelHandle, level: UnloadedLevel, npcs: List[SpawnNPC]
    ):
        assert isinstance(level, UnloadedLevel)

        if self.level:
            # TODO: Save level status
            pass

        self.camera_xy = level.player_start_xy
        self.player_xy = level.player_start_xy
        self.level = level.load(self, ident, npcs)

    def notify(self, event: Event):
        self._notify_queue.append(event)
        if self._notifying:
            return

        self._notifying = True
        try:
            while any(self._notify_queue):
                event = self._notify_queue.pop(0)
                if Verbs.quest_only(event.verb):
                    # No need for NPCs to know. This event pertains to quests
                    self.eventmonitors.notify(self, event)
                else:
                    self.eventmonitors.notify(self, event)
                    self.npcs.notify(self, event)
                    self.rhythms.notify(self, event)
                    self.scene_flags.notify(self, event)
        finally:
            self._notifying = False
