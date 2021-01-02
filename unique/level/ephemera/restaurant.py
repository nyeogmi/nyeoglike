from ds.code_registry import ref
from ds.lists import shuffled
from ..loaded_level import LoadedLevel
import random


@ref("ephemera/restaurant")
def generate(world: "World", ll: LoadedLevel):
    print("generating restaurant ephemera for {}".format(ll))
    print(ll.wallpaper.default)
    enterprise = world.enterprises.located_at(ll.ident)
    restaurant = world.enterprises.get_restaurant(world, enterprise)
    menu_items = restaurant.menu.items
    # TODO

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

        food = random.choice(menu_items)  # TODO: Random food
        ll.items.put(xy, food, ephemeral=True)


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...world import World
