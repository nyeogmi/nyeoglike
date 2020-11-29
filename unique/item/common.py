from .item import Item, Resource, Profile

import random

_CASH_LOOT = [
    Item.new(Profile.new(name="Laptop", icon="]"), res0=Resource.Money, n0=29999),
    Item.new(Profile.new(name="Phone", icon="'"), res0=Resource.Money, n0=29999),
]


def cash_loot() -> Item:
    return random.choice(_CASH_LOOT)


_SNACK = [
    Item.new(Profile.new(name="Musubi", icon="\xf6", fg=13), res0=Resource.Snack, n0=10),
]


def snack() -> Item:
    return random.choice(_SNACK)


_FURNITURE = [
    Item.new(Profile.new(name="Table", icon="\xd1", fg=14), res0=Resource.Furniture, n0=10),
]


def furniture() -> Item:
    return random.choice(_FURNITURE)


LEVEL_CODES = {
    "m": cash_loot,
    "s": snack,
    "f": furniture,
}
