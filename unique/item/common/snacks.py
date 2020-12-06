from unique.item.item import Item, Resource, Profile
from unique.item.item_list import ItemList
from display import Color, Colors

_SNACK_SMALL = dict(res0=Resource.Snack, n0=10)
_SNACK_MEDIUM = dict(res0=Resource.Snack, n0=50)
_SNACK_HUGE = dict(res0=Resource.Snack, n0=100)

ALL = ItemList()

ICE_CREAM = ALL.add(Item.new(
    Profile.new(name="ice cream", icon="\xeb", ascii_icon="i", fg=Colors.CreamWhite),
    **_SNACK_MEDIUM,
))

MUSUBI = ALL.add(Item.new(
    Profile.new(name="musubi", icon="\xf6", ascii_icon="m", fg=Colors.BrightPink),
    **_SNACK_SMALL,
))

NACHOS = ALL.add(Item.new(
    Profile.new(name="nachos", icon="\xa4", ascii_icon="n", fg=Colors.BrightOrange),
    **_SNACK_MEDIUM,
))

PIZZA = ALL.add(Item.new(
    # TODO: Better graphic?
    Profile.new(name="pizza", icon="O", ascii_icon="p", fg=Colors.BloodRed),
    **_SNACK_HUGE,
))

SUSHI = ALL.add(Item.new(
    Profile.new(name="sushi", icon="\xed", ascii_icon="s", fg=Colors.BrightWhite),
    **_SNACK_SMALL
))

