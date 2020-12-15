from enum import Enum
from typing import Dict, Set, Iterator

from ..npc import NPCHandle


class SceneFlag(Enum):
    # TODO: Rude awakening (reduces the value of the sleep)
    # TODO: Ate food
    GotSleep = 0


# TODO: Send an event the first time the event flag is set
class SceneFlags(object):
    def __init__(self):
        self._npc_scene_flags: Dict[NPCHandle, Set[SceneFlag]] = {}

    def add_scene_flag(self, npc: NPCHandle, scene_flag: SceneFlag):
        assert isinstance(npc, NPCHandle)
        assert isinstance(scene_flag, SceneFlag)

        self._npc_scene_flags[npc] = self._npc_scene_flags.get(npc, set())
        if scene_flag in self._npc_scene_flags[npc]:
            return

        self._npc_scene_flags[npc].add(scene_flag)
        # send event

    def has_scene_flag(self, npc: NPCHandle, scene_flag: SceneFlag):
        return self._npc_scene_flags[npc] and scene_flag in self._npc_scene_flags[npc]

    def get_scene_flags(self, npc: NPCHandle) -> Iterator[SceneFlag]:
        return (flag for flag in self._npc_scene_flags.get(npc, set()))
