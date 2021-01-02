from display import Color, Colors, DoubleWide
from unique.item.item import Item, Profile, Resource
from unique.item.item_list import ItemList


ALL = ItemList("furniture")

BED = ALL.add(
    Item.new(
        # TODO: This display is bad
        Profile.new(name="bed", icon="\xea", fg=Colors.Grey1),
        occludes_npc_spawn=False,
        buy_price=55000,
        res0=Resource.Furniture,
        n0=10,
    )
)

CHAIR = ALL.add(
    Item.new(
        # TODO: This display is bad
        Profile.new(name="chair", icon="\xd2", fg=Colors.Grey1).with_double_icon(
            DoubleWide.Chair
        ),
        occludes_npc_spawn=False,
        buy_price=7500,
        res0=Resource.Furniture,
        n0=10,
    )
)

COUNTER = ALL.add(
    Item.new(
        # TODO: This display is bad
        Profile.new(name="counter", icon="\xd1", fg=Colors.Grey1).with_double_icon(
            DoubleWide.Counter
        ),
        occludes_npc_spawn=True,
        buy_price=25000,
        res0=Resource.Furniture,
        n0=10,
    )
)

TABLE = ALL.add(
    Item.new(
        # TODO: This display is bad
        Profile.new(name="table", icon="\xd1", fg=Colors.Grey1).with_double_icon(
            "\xd1\xd1"
        ),
        occludes_npc_spawn=True,
        buy_price=10000,
        res0=Resource.Furniture,
        n0=10,
    )
)
