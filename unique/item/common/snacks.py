from unique.item.item import Item, Resource, Profile
from unique.item.item_list import ItemList
from display import Color, Colors

ALL = ItemList()

MUSUBI = ALL.add(Item.new(
    Profile.new(name="musubi", icon="\xf6", ascii_icon="m"),
    res0=Resource.Snack, n0=10,
))

PIZZA = ALL.add(Item.new(
    # TODO: Better graphic?
    Profile.new(name="pizza", icon="O", ascii_icon="p", fg=Colors.BloodRed),
    res0=Resource.Snack, n0=50,
))

