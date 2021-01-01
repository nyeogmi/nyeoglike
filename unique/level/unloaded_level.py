import random
from enum import Enum
from typing import Callable, Dict, List, NamedTuple, Set

from ds.code_registry import Ref
from ds.relational import OneToMany
from ds.vecs import V2

from ..item import Item
from ..npc import NPCHandle
from .block import Block
from .wallpaper import Wallpaper
from .loaded_level import LoadedLevel


class SpawnType(Enum):
    Sleep = 0
    Bedside = 1
    Employee = 2


class SpawnNPC(NamedTuple):
    npc: NPCHandle
    schedule: "ScheduleItem"


class UnloadedLevel(object):
    def __init__(
        self,
        player_start_xy: V2,
        wallpaper: Wallpaper,
        blocks: Dict[V2, Block],
        items: Dict[V2, List[Item]],
        npc_spawns: Dict[SpawnType, Set[V2]],
        ephemera_source: Ref[Callable[["World", LoadedLevel], None]],
    ):
        assert isinstance(player_start_xy, V2)
        assert isinstance(wallpaper, Wallpaper)
        assert isinstance(blocks, dict)
        assert isinstance(items, dict)
        assert isinstance(npc_spawns, dict)
        assert isinstance(ephemera_source, Ref)

        self._player_start_xy = player_start_xy
        self._wallpaper = wallpaper
        self._blocks = blocks
        self._items = items
        self._npc_spawns = npc_spawns
        self._ephemera_source = ephemera_source

    @property
    def player_start_xy(self):
        return self._player_start_xy

    def load(
        self, world: "World", ident: "LevelHandle", spawns: List[SpawnNPC]
    ) -> LoadedLevel:
        from ..worldmap import LevelHandle

        assert isinstance(ident, LevelHandle)

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
                lambda spawn_type: spawn_type_compatible(
                    npc.schedule, spawn_type, lax=True
                ),
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

        loaded_level = LoadedLevel(
            ident=ident,
            wallpaper=self._wallpaper,
            blocks=dict(self._blocks),
            # TODO: Spawn temporary items?
            items={k: list(v) for k, v in self._items.items()},
            npc_sites=npc_sites,
        )
        self._ephemera_source.resolve()(world, loaded_level)
        return loaded_level


def spawn_type_compatible(
    schedule_item: "ScheduleItem", spawn_type: SpawnType, lax=False
) -> bool:
    # TODO: Sleepover types

    from ..time import schedule_items

    if schedule_item.name == schedule_items.HomeSleep.name:
        if spawn_type == SpawnType.Sleep:
            return True
        if lax and spawn_type == SpawnType.Bedside:
            return True

    elif schedule_item.name == schedule_items.HomeFun.name:
        # more fun than sleep, I guess
        if lax and spawn_type == SpawnType.Bedside:
            return True

    elif schedule_item.name == schedule_items.GoToWork.name:
        if spawn_type == SpawnType.Employee:
            return True

    return False


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..time import ScheduleItem
    from ..world import World
    from ..worldmap import LevelHandle
