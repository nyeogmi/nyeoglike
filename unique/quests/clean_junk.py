from typing import Optional

from ..event import Event, Verbs
from ..eventmonitor import Done, EMHandle, EventMonitor, QuestOutcome, QuestStatus
from ..world import World


class CleanJunkQuest(EventMonitor):
    def __init__(self, handle: "EMHandle", junk_left: int):
        assert isinstance(handle, EMHandle)

        self._handle = handle
        self._initial_junk = junk_left
        self._junk_left = self._initial_junk
        self._completed = False

    def notify(self, world: "World", event: "Event") -> Optional["Done"]:
        if event.verb == Verbs.Tick:
            self._junk_left = world.level.items.junk_left

            if self._junk_left == 0:
                # TODO: If we're just flipping this for the first time during this quest, make the NPCs happy
                self._completed = True

        return None

    def quest_status(self, world: "World") -> Optional["QuestStatus"]:
        if not self._completed:
            return QuestStatus(
                name="Clean up junk",
                description="This place is full of junk. Clean it!",
                oneliner="Clean junk ({}/{})".format(
                    self._junk_left, self._initial_junk
                ),
                outcome=QuestOutcome.InProgress,
                assigner=None,
                is_challenge=True,
            )
        else:
            return QuestStatus(
                name="Clean up junk",
                description="You cleaned the junk!",
                oneliner="Junk cleaned!".format(self._junk_left, self._initial_junk),
                outcome=QuestOutcome.Succeeded,
                assigner=None,
                is_challenge=True,
            )

    def key(self):
        return CleanJunkQuest
