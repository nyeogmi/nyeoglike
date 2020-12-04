from ds.vecs import V2
import os.path

from .event import Event, Verbs
from .eventmonitor import EventMonitors, EventMonitor
from .interest import InterestTracker
from .inventory import Inventory
from .level import UnloadedLevel, LoadedLevel, SpawnNPC
from .worldmap import Levels, LevelHandle
from .notifications import Notifications, Notification
from .npc import NPCs, NPC, NPCHandle
from .scheduling import Schedules
from .social import Households

import random
from typing import Optional, List

N_HOUSEHOLDS = 30
N_HOUSEHOLD_NPCS = (1, 5)


class World(object):
    def __init__(self):
        self.eventmonitors = EventMonitors()
        self.interest = InterestTracker()
        self.households = Households()
        self.levels = Levels()
        self.notifications = Notifications()
        self.npcs = NPCs()
        self.schedules = Schedules()

        self.camera_xy: V2 = V2.zero()
        self.player_xy: V2 = V2.zero()
        self.inventory: Inventory = Inventory()

        self.level: Optional[LoadedLevel] = None

    @classmethod
    def generate(cls):
        world = cls()
        for i in range(N_HOUSEHOLDS):
            world.households.generate(world, random.randint(*N_HOUSEHOLD_NPCS))
        return world

    def advance_time(self):
        self.schedules.advance_time()

    def follow_npc(self, npc: NPCHandle):
        # TODO: Figure out where the NPC will be using their schedule
        household = self.households.household_of(npc)
        home = self.households.get_home(self, household)
        self.activate_level(home)

    def activate_level(self, level: LevelHandle):
        # figure out who will be there
        # for now, the whole household. in the future use the schedule info
        spawns = []
        household_there = self.households.living_at(level)
        for npc in self.households.members(household_there):
            spawns.append(SpawnNPC(npc=npc, schedule=self.schedules.next_location(self, npc)))
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
