from display import Color, Colors
from unique.item.item import Item, Profile, Resource
from unique.item.item_list import ItemList

_SNACK_SMALL = dict(res0=Resource.Snack, n0=10)
_SNACK_MEDIUM = dict(res0=Resource.Snack, n0=50)
_SNACK_HUGE = dict(res0=Resource.Snack, n0=100)

ALL = ItemList()

ICE_CREAM = ALL.add(
    Item.new(
        Profile.new(name="ice cream", icon="\xeb", ascii_icon="i", fg=Colors.White0),
        **_SNACK_MEDIUM,
    )
)

MUSUBI = ALL.add(
    Item.new(
        Profile.new(name="musubi", icon="\xf6", ascii_icon="m", fg=Colors.Fuchsia1),
        **_SNACK_SMALL,
    )
)

NACHOS = ALL.add(
    Item.new(
        Profile.new(name="nachos", icon="\xa4", ascii_icon="n", fg=Colors.YellowGreen0),
        **_SNACK_MEDIUM,
    )
)

PIZZA = ALL.add(
    Item.new(
        # TODO: Better graphic?
        Profile.new(name="pizza", icon="O", ascii_icon="p", fg=Colors.Red1),
        **_SNACK_HUGE,
    )
)

SUSHI = ALL.add(
    Item.new(
        Profile.new(name="sushi", icon="\xed", ascii_icon="s", fg=Colors.White1),
        **_SNACK_SMALL,
    )
)
