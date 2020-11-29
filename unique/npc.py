from typing import NamedTuple, Optional
from ds.gensym import Gensym, Sym
from ds.vecs import V2
import random

from .event import Event, Verbs
from .eventmonitor import Done, EventMonitor, QuestStatus, QuestOutcome


class NPCHandle(NamedTuple):
    ident: Sym


class NPCs(object):
    def __init__(self):
        self._all = {}
        self._sym = Gensym("NPC")

    def generate(self) -> NPCHandle:
        handle = NPCHandle(self._sym.gen())
        self._all[handle] = NPC.generate(handle)
        return handle

    def get(self, handle: NPCHandle) -> "NPC":
        return self._all[handle]

    def notify(self, world: "World", event: "Event"):
        # TODO: Notify npcs near the player more often?
        from .world import World

        assert isinstance(world, World)
        assert isinstance(event, Event)

        for npc in list(world.level.loaded_npcs()):
            xy = world.level.npc_location(npc)
            self.get(npc).notify(world, Me(me_xy=xy), event)


class Me(NamedTuple):
    me_xy: V2


class NPC(object):
    def __init__(self, ident, name):
        self._ident = ident
        self.name = name

    @property
    def ident(self):
        return self._ident

    @classmethod
    def generate(cls, ident):
        # TODO: Name gen
        return NPC(
            ident=ident,
            name=random.choice([
                "Margaret Morris",
                "Laura Roman",
                "Sandra Branton",
                "Daniel Weiss",
                "Peter Fischer",
            ]),
        )

    def notify(self, world: "World", me: Me, event: Event):
        from .world import World

        assert isinstance(world, World)
        assert isinstance(me, Me)
        assert isinstance(event, Event)

        if world.player_xy.manhattan(me.me_xy) <= 1:
            # offer a quest
            world.eventmonitors.add(world, lambda handle: TestQuest(handle, self._ident))


class TestQuest(EventMonitor):
    def __init__(self, handle: "EMHandle", npc: NPCHandle):
        from .eventmonitor import EMHandle
        assert isinstance(handle, EMHandle)

        self._handle = handle
        self._npc = npc
        self._ticks = 10

    def notify(self, world: "World", event: "Event") -> Optional["Done"]:
        print(world, event)
        if event.verb == Verbs.Tick:
            self._ticks -= 1

        if self._ticks < 0:
            self._ticks = 0

    def quest_status(self, world: "World") -> Optional["QuestStatus"]:
        return QuestStatus(
            name="Hey! ({})".format(world.npcs.get(self._npc).name),
            description="I'm a quest, and you can complete me.",
            oneliner="Wait {} ticks".format(self._ticks) if self._ticks else "You win!",
            outcome=QuestOutcome.InProgress if self._ticks else QuestOutcome.Succeeded,
            assigner=self._npc,
        )

    def key(self):
        return TestQuest, self._npc


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .eventmonitor import EMHandle
    from .world import World