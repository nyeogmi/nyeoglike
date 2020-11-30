from ds.vecs import V2
import os.path

from .event import Event, Verbs
from .eventmonitor import EventMonitors, EventMonitor
from .interest import InterestTracker
from .inventory import Inventory
from .level import Level
from .notifications import Notifications, Notification
from .npc import NPCs, NPC
from .scheduling import Schedules

from typing import Optional


class World(object):
    def __init__(self):
        self.eventmonitors = EventMonitors()
        self.notifications = Notifications()
        self.npcs = NPCs()
        self.interest = InterestTracker()
        self.schedules = Schedules()

        self.camera_xy: V2 = V2.zero()
        self.player_xy: V2 = V2.zero()
        self.inventory: Inventory = Inventory()

        self.level: Optional[Level] = None

    def activate_level(self, level: Level):
        assert isinstance(level, Level)

        if self.level:
            # save previous player position
            self.level.player_start_xy = self.player_xy

        self.camera_xy = level.player_start_xy
        self.player_xy = level.player_start_xy
        self.level = level

    def notify(self, event: Event):
        if Verbs.quest_only(event.verb):
            # No need for NPCs to know. This event pertains to quests
            self.eventmonitors.notify(self, event)
        else:
            self.eventmonitors.notify(self, event)
            self.npcs.notify(self, event)
