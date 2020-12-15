import random
from typing import List, NamedTuple, Optional

from ds.gensym import Gensym, Sym
from ds.vecs import V2

from . import namegen
from .event import Event, Verbs
from .eventmonitor import Done, EventMonitor, QuestOutcome, QuestStatus


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

    def all(self) -> List[NPCHandle]:
        return list(self._all.keys())

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
        self.seen = False  # set in sitemode

        self.asleep = False

    @property
    def ident(self):
        return self._ident

    @classmethod
    def generate(cls, ident):
        # TODO: Name tools
        return NPC(
            ident=ident,
            name=namegen.generate(),
        )

    def notify(self, world: "World", me: Me, event: Event):
        from .quests import FetchQuest
        from .world import World

        assert isinstance(world, World)
        assert isinstance(me, Me)
        assert isinstance(event, Event)

        if world.player_xy.manhattan(me.me_xy) <= 1:
            # offer a quest
            # world.eventmonitors.add(world, lambda handle: TestQuest(handle, self._ident))
            world.eventmonitors.add(
                world, lambda handle: FetchQuest(handle, self._ident, "pizza")
            )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .eventmonitor import EMHandle
    from .world import World
