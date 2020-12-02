from unique.item.item import Item, Resource, Profile
from unique.item.item_list import ItemList
from display import Color, Colors

ALL = ItemList()

BED = ALL.add(Item.new(
    # Color?
    Profile.new(name="bed", icon="\xea", ascii_icon="b", fg=Colors.DarkBlue),
    res0=Resource.Furniture, n0=10,
))


TABLE = ALL.add(Item.new(
    # Color?
    Profile.new(name="table", icon="\xd1", ascii_icon="T", fg=Colors.DarkBlue),
    occludes_walk=True,
    res0=Resource.Furniture, n0=10,
))

