from enum import Enum
from typing import Dict, Iterator, Set

from ..event import Event, Verbs
from ..npc import NPCHandle


class SceneFlag(Enum):
    # TODO: Rude awakening (reduces the value of the sleep)
    # TODO: Ate food
    GotSleep = 0


# TODO: Send an event the first time the event flag is set
class SceneFlags(object):
    def __init__(self):
        self._npc_scene_flags: Dict[NPCHandle, Set[SceneFlag]] = {}

    def add_scene_flag(self, world: "World", npc: NPCHandle, scene_flag: SceneFlag):
        assert isinstance(npc, NPCHandle)
        assert isinstance(scene_flag, SceneFlag)

        self._npc_scene_flags[npc] = self._npc_scene_flags.get(npc, set())
        if scene_flag in self._npc_scene_flags[npc]:
            return

        self._npc_scene_flags[npc].add(scene_flag)
        world.notify(
            Event.new(
                Verbs.AddFlag,
                (
                    npc,
                    scene_flag,
                ),
            )
        )

    def has_scene_flag(self, npc: NPCHandle, scene_flag: SceneFlag):
        return self._npc_scene_flags[npc] and scene_flag in self._npc_scene_flags[npc]

    def get_scene_flags(self, npc: NPCHandle) -> Iterator[SceneFlag]:
        return (flag for flag in self._npc_scene_flags.get(npc, set()))

    def reset(self):
        self._npc_scene_flags = {}

    def notify(self, world: "World", event: Event):
        # TODO: Spy on ticks, spy on NPCs to determine if they fell asleep
        pass

    def populate_from_schedules(self, world: "World"):
        from ..time.scheduling import schedule_items

        for npc in world.npcs.all():
            schedule = world.schedules.prev_schedule(npc)

            if schedule is None:
                continue

            if schedule.name == schedule_items.HomeSleep.name:
                self.add_scene_flag(world, npc, SceneFlag.GotSleep)

            # TODO: Any others?


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world import World
