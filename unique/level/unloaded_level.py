from .block import Block
from ..item import Item
from ..time import schedule_items, ScheduleItem

from enum import Enum

from ds.relational import OneToMany
from ds.vecs import V2
from typing import Dict, Set, List, NamedTuple

from .loaded_level import LoadedLevel
from ..npc import NPCHandle

import random


class SpawnType(Enum):
    Sleep = 0
    Bedside = 1


class SpawnNPC(NamedTuple):
    npc: NPCHandle
    schedule: ScheduleItem


class UnloadedLevel(object):
    def __init__(
        self,
        player_start_xy: V2,
        blocks: Dict[V2, Block],
        items: Dict[V2, List[Item]],
        npc_spawns: Dict[SpawnType, Set[V2]]
    ):
        assert isinstance(player_start_xy, V2)
        assert isinstance(blocks, dict)
        assert isinstance(items, dict)
        assert isinstance(npc_spawns, dict)

        self._player_start_xy = player_start_xy
        self._blocks = blocks
        self._items = items
        self._npc_spawns = npc_spawns

    @property
    def player_start_xy(self):
        return self._player_start_xy

    def load(self, spawns: List[SpawnNPC]) -> LoadedLevel:
        all_possible_spots = []
        possible_spots = []
        for spawn_type, possible_vs in self._npc_spawns.items():
            for v in possible_vs:
                possible_spots.append((v, spawn_type))
                all_possible_spots.append((v, spawn_type))

        npc_sites = OneToMany()
        for npc in spawns:
            random.shuffle(possible_spots)

            # TODO: Give bedside spawn points an equivalence class so NPCs avoid spawning two next to the same bed
            checks = [
                lambda spawn_type: spawn_type_compatible(npc.schedule, spawn_type),
                lambda spawn_type: spawn_type_compatible(npc.schedule, spawn_type, lax=True),
                lambda spawn_type: True,
            ]

            def find_spot():
                for ch in checks:
                    for i, (spot, spawn_type) in enumerate(possible_spots):
                        if ch(spawn_type):
                            possible_spots.pop(i)
                            return spot
                return random.choice(all_possible_spots)[0]

            found_spot = find_spot()
            assert found_spot is not None

            if any(npc_sites.get_bs(found_spot)):
                neighbors = [n for n in found_spot.neighbors() if n not in self._blocks]
                random.shuffle(neighbors)
                for n in neighbors:
                    if n in self._blocks:
                        continue

                    if n in self._items:
                        if any(item.occludes_walk for item in self._items[n]):
                            continue

                    if not any(npc_sites.get_bs(n)):
                        npc_sites.add(n, npc.npc)
                        break
                else:
                    npc_sites.add(found_spot, npc.npc)
            else:
                npc_sites.add(found_spot, npc.npc)

        return LoadedLevel(
            blocks=dict(self._blocks),
            # TODO: Spawn temporary items?
            items={k: list(v) for k, v in self._items.items()},
            npc_sites=npc_sites,
        )


def spawn_type_compatible(schedule_item: ScheduleItem, spawn_type: SpawnType, lax=False) -> bool:
    if schedule_item == schedule_items.HomeSleep:
        if spawn_type == SpawnType.Sleep:
            return True
        if lax and spawn_type == SpawnType.Bedside:
            return True

    elif schedule_item == schedule_items.HomeFun:
        # more fun than sleep, I guess
        if lax and spawn_type == SpawnType.Bedside:
            return True

    return False


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..world import World