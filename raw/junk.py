from display import Color, Colors, ItemColors as IC
from unique.item.item import Item, Profile, Resource
from unique.item.item_list import ItemList
from typing import Optional


small = dict(res0=Resource.Junk, n0=5)
medium = dict(res0=Resource.Junk, n0=15)
huge = dict(res0=Resource.Junk, n0=50)


ALL = ItemList("junk")


def add(buy_price: int, item_kw: dict):
    def _adder(*args, **kw) -> Item:
        return ALL.add(
            Item.new(
                Profile.new(*args, **kw),
                occludes_npc_spawn=False,
                buy_price=buy_price,
                keywords=(),
                **item_kw
            )
        )

    return _adder


ALUMINUM_FOIL = add(25, small)("aluminum foil", "\x60", fg=IC.Fuchsia1)
BOTTLE_CAP = add(20, small)("bottle cap", "\xf9", fg=IC.Sky1)
BOX = add(500, huge)("box", "\xf1", fg=IC.Sky1)
BROCHURE = add(150, medium)("brochure", "\xf6", fg=IC.Red1)
CARDBOARD = add(50, small)("cardboard", "\xae", fg=IC.Sky1)
JUICE_BOTTLE = add(100, medium)("juice bottle", "\x92", fg=IC.Fuchsia1)
LEAFLET = add(120, medium)("leaflet", "\xf6", fg=IC.Green1)
MAGAZINE = add(250, medium)("magazine", "\xf6", fg=IC.Sky1)
OLD_MAIL = add(300, medium)("old mail", "\xac", fg=IC.Fuchsia1)
PAPER_BOWL = add(70, small)("paper bowl", "\x29", fg=IC.Green1)
PAPER_CUP = add(60, small)("paper cup", "\xf0", fg=IC.Sky0)
PAPER_PLATE = add(40, small)("paper plate", "\x7b", fg=IC.Green1)
PAPER_TOWEL = add(40, small)("paper towel", "\x2e", fg=IC.Green1)
PLASTIC_CUP = add(45, small)("plastic cup", "\xf0", fg=IC.Sky1)
PLASTIC_UTENSIL = add(20, small)("plastic utensil", "\x5c", fg=IC.Sky1)
RAG = add(145, medium)("rag", "\xe1", fg=IC.Fuchsia1)
SNACK_WRAPPER = add(45, small)("snack wrapper", "\xa7", fg=IC.Green1)
SODA_BOTTLE = add(85, small)("soda bottle", "\x92", fg=IC.Red1)
SODA_CAN = add(40, small)("soda can", "\xe8", fg=IC.Sky0)
SOUP_CAN = add(65, small)("soup can", "\xf7", fg=IC.Red1)
TAKEOUT_BOX = add(80, small)("takeout box", "\xa9", fg=IC.Red0)
UNDERWEAR = add(320, medium)("underwear", "\x9a", fg=IC.Fuchsia1)
