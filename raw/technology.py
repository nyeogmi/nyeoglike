from display import Color, Colors
from unique.item.item import Item, Profile, Resource
from unique.item.item_list import ItemList

ALL = ItemList("technology")

LAPTOP = ALL.add(
    Item.new(
        Profile.new(name="laptop", icon="'"),
        buy_price=37500,
        res0=Resource.Money,
        n0=29999,
    )
)

PHONE = ALL.add(
    Item.new(
        Profile.new(name="phone", icon="'"),
        buy_price=8500,
        res0=Resource.Money,
        n0=9999,
    )
)
