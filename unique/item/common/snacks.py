from display import Color, Colors, ItemColors as IC
from unique.item.item import Item, Profile, Resource
from unique.item.item_list import ItemList

_SNACK_SMALL = dict(res0=Resource.Snack, n0=10)
_SNACK_MEDIUM = dict(res0=Resource.Snack, n0=30)
_SNACK_HUGE = dict(res0=Resource.Snack, n0=100)


ALL = ItemList()


def adder(size):
    def _adder(*args) -> Item:
        return ALL.add(Item.new(Profile.new(*args), **size))

    return _adder


small = adder(_SNACK_SMALL)
medium = adder(_SNACK_MEDIUM)
huge = adder(_SNACK_HUGE)


BANH_MI = medium("banh mi", "\xed", IC.Fuchsia1)
BRATWURST = medium("bratwurst", "\xe1", IC.Red1)
BULGOGI = medium("bulgogi", "\xf0", IC.Red1)
BURGER = medium("burger", "\xec", IC.Red1)
CHICKEN_FETTUCINE_ALFREDO = medium("chicken fettucine alfredo", "\xfb", IC.Red1)
CHICKEN_NUGGETS = medium("chicken nuggets", "\x05", IC.Sky1)
CHICKEN_TIKKA_MASALA = medium("chicken tikka masala", "\xef", IC.Red1)
CHIPS = small("chips", "\xe6", IC.Red1)
CINNAMON_BUN = small("cinnamon bun", "\x9b", IC.Sky0)
CURRY = medium("curry", "\xea", IC.Green1)
DONUT = small("donut", "\x6f", IC.Sky1)
FALAFEL = small("falafel", "\xa6", IC.Green1)
FISH = medium("fish", "\xe0", IC.Sky1)
FRIED_ICE_CREAM = small("fried ice cream", "\x9e", IC.Fuchsia1)
FRIES = small("fries", "\x9f", IC.Green1)
JELLY_DONUT = medium("jelly donut", "\x6f", IC.Fuchsia1)
JEON = medium("jeon", "\xec", IC.Sky1)
KALBIJJIM = medium("kalbijjim", "\xa8", IC.Red0)
LOBSTER = medium("lobster", "\x9d", IC.Red1)
MEAT_LOAF = medium("meat loaf", "\xe4", IC.Red1)
PAD_THAI = medium("pad thai", "\xab", IC.Green1)
PEACH = small("peach", "\x7f", IC.Fuchsia1)
PET_FOOD = small("pet food", "\x9e", IC.Red0)
POMEGRANATE = small("pomegranate", "\x7f", IC.Fuchsia0)
POPCORN = small("popcorn", "\x2a", IC.Red1)
SALT = small("salt", "\xf9", IC.Mundane)
SHRIMP = small("shrimp", "\x0f", IC.Fuchsia1)
SOUP = medium("soup", "\xf7", IC.Sky0)
SPARE_RIB = medium("spare rib", "\xe2", IC.Red1)
STEAK = medium("steak", "\x9c", IC.Red1)
STRAWBERRY = small("strawberry", "\x7f", IC.Red1)
STROGANOFF = medium("stroganoff", "\xf2", IC.Red1)
TACOS = medium("tacos", "\xee", IC.Sky0)
TTEOKBOKKI = medium("tteokbokki", "\xaa", IC.Red0)
TUNA = medium("tuna", "\xe0", IC.Fuchsia1)
WAFFLES = medium("waffles", "\xaf", IC.Fuchsia1)
