from .item import Item, Resource, Profile
from display import Color, Colors

import random

_CASH_LOOT = [
    Item.new(Profile.new(name="laptop", icon="]"), res0=Resource.Money, n0=29999),
    Item.new(Profile.new(name="phone", icon="'"), res0=Resource.Money, n0=29999),
]


def cash_loot() -> Item:
    return random.choice(_CASH_LOOT)


_SNACK = [
    Item.new(Profile.new(name="musubi", icon="\xf6", fg=Colors.BrightPink), res0=Resource.Snack, n0=10),
]


def snack() -> Item:
    return random.choice(_SNACK)


_FURNITURE = [
    Item.new(Profile.new(name="table", icon="\xd1", fg=Colors.DarkBlue), res0=Resource.Furniture, n0=10),
]


def furniture() -> Item:
    return random.choice(_FURNITURE)


LEVEL_CODES = {
    "m": cash_loot,
    "s": snack,
    "f": furniture,
}


# TODO:
#
# Luxuries:
# - Light bulbs (+Spark)
# - Makeup (nail polish, lip gloss, eyeliner)
# - Wireless headphones
# - Graphing calculator
#
# Snacks:
# - Ice cream
# - Nachos
# - Pizza
# - Sushi
# - Steak (+Blood)
# - Falafel
# - Salt
# - Popcorn
# - Banh mi
# - Tacos
# - Soup (pho, carne en su jugo)
#
# Spark items:
# - Dice
# - Pencils
# - Sticky notes
# - Toothpicks
# - Microphone (+Cash)
# - Markers (+Cash)
# - Musical instruments
# - Game controller
# - Sketchbook
# - Tablet
# - Stuffed animal
# - Magazine
# - Glue
# - Scissors
# - Game cartridge
# - TV
#
# TODO: Luxuries and spark items seem similar. Maybe make them always be $ and you can only get spark by completing a quest
#