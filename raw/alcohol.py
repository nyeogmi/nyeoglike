from display import Color, Colors
from unique.item.item import Item, Profile, Resource
from unique.item.item_list import ItemList

# TODO: Separate from snacks
_DRINK_SMALL = dict(res0=Resource.Snack, n0=10)
_DRINK_MEDIUM = dict(res0=Resource.Snack, n0=50)
_DRINK_HUGE = dict(res0=Resource.Snack, n0=100)

ALL = ItemList("alcohol")

BEER = ALL.add(
    Item.new(
        Profile.new(name="beer", icon="\x97", fg=Colors.YellowGreen0),
        occludes_npc_spawn=False,
        buy_price=450,
        **_DRINK_MEDIUM,
    )
)

CIDER = ALL.add(
    Item.new(
        Profile.new(name="cider", icon="\x95", fg=Colors.YellowGreen0),
        occludes_npc_spawn=False,
        buy_price=550,
        **_DRINK_MEDIUM,
    )
)

VODKA = ALL.add(
    Item.new(
        Profile.new(name="vodka", icon="\xa7", fg=Colors.White1),
        occludes_npc_spawn=False,
        buy_price=550,
        **_DRINK_HUGE,
    )
)
