from display import Color, Colors
from unique.item.item import Item, Profile, Resource
from unique.item.item_list import ItemList

ALL = ItemList()

LAPTOP = ALL.add(
    Item.new(
        Profile.new(name="laptop", ascii_icon="'"),
        res0=Resource.Money,
        n0=29999,
    )
)

PHONE = ALL.add(
    Item.new(
        Profile.new(name="phone", ascii_icon="'"),
        res0=Resource.Money,
        n0=9999,
    )
)
