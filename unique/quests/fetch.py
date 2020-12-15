from ..event import Event, Verbs
from ..eventmonitor import EventMonitor, EMHandle, Done, QuestOutcome, QuestStatus
from ..inventory import ClaimHandle
from ..npc import NPCHandle
from ..world import World

from ds.vecs import V2
from enum import Enum
from typing import Optional


class FetchQuest(EventMonitor):
    def __init__(self, handle: "EMHandle", npc: NPCHandle, item_name: str):
        assert isinstance(handle, EMHandle)

        self._handle = handle
        self._npc = npc
        self._item_name = item_name

        self._claimed_item: Optional[ClaimHandle] = None
        self._returned = False

    def _state(self) -> "_FQState":
        # when we're done, we're done
        if self._returned:
            return _FQState.Returned

        # normal state machine
        if self._claimed_item is None:
            return _FQState.NotFetched
        elif not self._returned:
            return _FQState.NotReturned
        else:
            return _FQState.Returned

    def notify(self, world: "World", event: "Event") -> Optional["Done"]:
        # TODO: Unclaim verb

        if self._state() == _FQState.NotFetched:
            if event.verb == Verbs.Claim:
                (box,) = event.args
                if box.item.profile.name == self._item_name:
                    self._claimed_item = box.claim(self._handle)

        elif self._state() == _FQState.NotReturned:
            if event.verb == Verbs.Tick:
                # inclusive box
                xy0 = world.player_xy - V2.new(1, 1)
                xy1 = world.player_xy + V2.new(1 + 1, 1 + 1)  # inclusive bottom
                for xy in xy0.to(xy1):
                    for npc in world.level.npc_sites.get_bs(xy):
                        if npc == self._npc:
                            self._returned = True
                            world.inventory.claims.redeem(self._claimed_item)

                            # TODO: Add to the NPC's inventory, if that's possible
                            self._claimed_item = None  # get rid of old claim

        return None

    def quest_status(self, world: "World") -> Optional["QuestStatus"]:
        state = self._state()
        npc_name = world.npcs.get(self._npc).name

        if state == _FQState.NotFetched:
            return QuestStatus(
                name="{} ({})".format(self._item_name, npc_name),
                description="{} wants you to get {} and bring it back to them.".format(
                    npc_name, self._item_name
                ),
                oneliner="Get {} for {}".format(self._item_name, npc_name),
                outcome=QuestOutcome.InProgress,
                assigner=self._npc,
            )

        elif state == _FQState.NotReturned:
            return QuestStatus(
                name="{} ({})".format(self._item_name, npc_name),
                description="Take the {} and return it to {}.".format(
                    self._item_name, npc_name
                ),
                oneliner="Bring {} to {}".format(self._item_name, npc_name),
                outcome=QuestOutcome.InProgress,
                assigner=self._npc,
            )

        else:
            return QuestStatus(
                name="{} ({})".format(self._item_name, npc_name),
                description="You gave {} to {}.".format(self._item_name, npc_name),
                oneliner="You did it",
                outcome=QuestOutcome.Succeeded,
                assigner=self._npc,
            )

    def key(self):
        # TODO: Maybe limit each NPC to one fetch quest at a time?
        return FetchQuest, self._npc, self._item_name


class _FQState(Enum):
    NotFetched = 0
    NotReturned = 1
    Returned = 2
