from ds.vecs import V2
import os.path

from .event import Event, Verbs
from .eventmonitor import EventMonitors, EventMonitor
from .interest import InterestTracker
from .inventory import Inventory
from .level import UnloadedLevel, LoadedLevel, SpawnNPC
from .worldmap import Levels
from .notifications import Notifications, Notification
from .npc import NPCs, NPC
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

    def activate_level(self, level: UnloadedLevel, npcs: List[SpawnNPC]):
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
