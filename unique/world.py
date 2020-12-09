from ds.vecs import V2
import os.path

from .biology import Rhythms
from .event import Event, Verbs
from .eventmonitor import EventMonitors, EventMonitor
from .interest import InterestTracker
from .inventory import Inventory
from .level import UnloadedLevel, LoadedLevel, SpawnNPC
from .worldmap import Levels, LevelHandle
from .notifications import Notifications, Notification
from .npc import NPCs, NPC, NPCHandle
from .social import Friendships, Enterprises, Households, HouseholdHandle
from .time import Clock, Schedules

import random
from typing import Optional, List

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
        self.schedules = Schedules()

        self.camera_xy: V2 = V2.zero()
        self.player_xy: V2 = V2.zero()
        self.inventory: Inventory = Inventory()

        self.level: Optional[LoadedLevel] = None

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

    def end_time_period(self):
        pass

    def follow_npc(self, npc: NPCHandle):
        # TODO: Figure out where the NPC will be using their schedule
        location = self.schedules.next_location(self, npc)
        self.activate_level(location)

    def activate_level(self, level: LevelHandle):
        # figure out who will be there
        # for now, the whole household. in the future use the schedule info
        spawns = []
        for npch in self.npcs.all():
            # TODO: Move this to schedules object
            if self.schedules.next_location(self, npch) == level:
                spawns.append(SpawnNPC(npc=npch, schedule=self.schedules.next_schedule(npch)))

        lvl = self.levels.get(level)
        self._activate_level(lvl, spawns)

    def _activate_level(self, level: UnloadedLevel, npcs: List[SpawnNPC]):
        assert isinstance(level, UnloadedLevel)

        if self.level:
            # TODO: Save level status
            pass

        self.camera_xy = level.player_start_xy
        self.player_xy = level.player_start_xy
        self.level = level.load(npcs)

    def notify(self, event: Event):
        if Verbs.quest_only(event.verb):
            # No need for NPCs to know. This event pertains to quests
            self.eventmonitors.notify(self, event)
        else:
            self.eventmonitors.notify(self, event)
            self.npcs.notify(self, event)
