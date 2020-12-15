from display import Color, Colors
from unique.item.item import Item, Profile, Resource
from unique.item.item_list import ItemList

ALL = ItemList()

BED = ALL.add(
    Item.new(
        # TODO: This display is bad
        Profile.new(name="bed", icon="\xea", ascii_icon="b", fg=Colors.DarkBlue),
        res0=Resource.Furniture,
        n0=10,
    )
)

CHAIR = ALL.add(
    Item.new(
        # TODO: This display is bad
        Profile.new(
            name="chair", icon="\xd2", ascii_icon="T", fg=Colors.DarkBlue
        ).with_double_icon("\xd2 "),
        occludes_walk=True,
        res0=Resource.Furniture,
        n0=10,
    )
)

COUNTER = ALL.add(
    Item.new(
        # TODO: This display is bad
        Profile.new(
            name="counter", icon="\xd1", ascii_icon="T", fg=Colors.DarkBlue
        ).with_double_icon("\xcd\xd1"),
        occludes_walk=True,
        res0=Resource.Furniture,
        n0=10,
    )
)

TABLE = ALL.add(
    Item.new(
        # TODO: This display is bad
        Profile.new(
            name="table", icon="\xd1", ascii_icon="T", fg=Colors.DarkBlue
        ).with_double_icon("\xd1\xd1"),
        occludes_walk=True,
        res0=Resource.Furniture,
        n0=10,
    )
)
