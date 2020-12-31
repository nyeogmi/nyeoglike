from ds.code_registry import ref
from ds.lists import shuffled
from raw.snacks import SOUP
from ..loaded_level import LoadedLevel


@ref("ephemera/restaurant")
def generate(world: "World", ll: LoadedLevel):
    print("generating restaurant ephemera for {}".format(ll))
    print(ll.wallpaper.default)

    # For now, _every_ NPC gets a meal
    for location, npc in ll.npc_sites.all():
        print(location, npc)

        for xy in shuffled(location.ortho_neighbors()):
            all_spawns = ll.items.view(xy)
            if any(
                any(kw in s.item.profile.name for kw in ["table", "counter"])
                for s in all_spawns
            ):
                break
        else:
            # no food for this cell
            continue

        food = SOUP  # TODO: Random food
        ll.items.put(xy, food, ephemeral=True)


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...world import World
