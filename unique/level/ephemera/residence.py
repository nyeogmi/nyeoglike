from ds.code_registry import ref
from ..loaded_level import LoadedLevel
from raw import ALL

import random


@ref("ephemera/residence")
def generate(world: "World", ll: LoadedLevel):
    print("generating residence ephemera for {}".format(ll))
    print(ll.wallpaper.default)

    junk = list(ALL.get_all_by_keywords("junk"))
    assert len(junk) > 0

    for v2 in ll.in_bounds:
        if v2 in ll.blocks:
            continue

        if any(ll.items.view(v2)):
            continue

        if random.random() < 0.1:
            ll.items.put(v2, random.choice(junk), ephemeral=True)
    pass


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...world import World
