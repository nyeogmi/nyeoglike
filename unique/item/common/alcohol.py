from display import Color, Colors
from unique.item.item import Item, Profile, Resource
from unique.item.item_list import ItemList

# TODO: Separate from snacks
_DRINK_SMALL = dict(res0=Resource.Snack, n0=10)
_DRINK_MEDIUM = dict(res0=Resource.Snack, n0=50)
_DRINK_HUGE = dict(res0=Resource.Snack, n0=100)

ALL = ItemList()

BEER = ALL.add(
    Item.new(
        Profile.new(name="beer", icon="\x97", ascii_icon="b", fg=Colors.Yellow),
        **_DRINK_MEDIUM,
    )
)

CIDER = ALL.add(
    Item.new(
        Profile.new(name="cider", icon="\x95", ascii_icon="b", fg=Colors.Yellow),
        **_DRINK_MEDIUM,
    )
)

VODKA = ALL.add(
    Item.new(
        Profile.new(name="vodka", icon="\xa7", ascii_icon="v", fg=Colors.BrightWhite),
        **_DRINK_HUGE,
    )
)
