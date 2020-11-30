from ..event import Event, Verbs
from ..eventmonitor import EventMonitor, EMHandle, Done, QuestOutcome, QuestStatus
from ..npc import NPCHandle
from ..world import World

from typing import Optional


class WaitQuest(EventMonitor):
    def __init__(self, handle: "EMHandle", npc: NPCHandle):
        assert isinstance(handle, EMHandle)

        self._handle = handle
        self._npc = npc
        self._ticks = 10

    def notify(self, world: "World", event: "Event") -> Optional["Done"]:
        if event.verb == Verbs.Tick:
            self._ticks -= 1

        if self._ticks < 0:
            self._ticks = 0

        return None

    def quest_status(self, world: "World") -> Optional["QuestStatus"]:
        return QuestStatus(
            name="Hey! ({})".format(world.npcs.get(self._npc).name),
            description="I'm a quest, and you can complete me.",
            oneliner="Wait {} ticks".format(self._ticks) if self._ticks else "You win!",
            outcome=QuestOutcome.InProgress if self._ticks else QuestOutcome.Succeeded,
            assigner=self._npc,
        )

    def key(self):
        return WaitQuest, self._npc
