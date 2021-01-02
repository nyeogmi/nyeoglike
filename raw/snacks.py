from display import Color, Colors, ItemColors as IC
from unique.item.item import Item, Profile, Resource
from unique.item.item_list import ItemList
from typing import Optional

small = dict(res0=Resource.Snack, n0=10)
medium = dict(res0=Resource.Snack, n0=30)
huge = dict(res0=Resource.Snack, n0=100)

american = "american"
chinese = "chinese"
german = "german"
indian = "indian"
italian = "italian"
korean = "korean"
mediterranean = "mediterranean"
mexican = "mexican"
thai = "thai"
vietnamese = "vietnamese"
russian = "russian"

fruit = "fruit"

CUISINES = [
    american,
    chinese,
    german,
    indian,
    italian,
    korean,
    mediterranean,
    mexican,
    thai,
    vietnamese,
    russian,
    fruit,
]

# much like the Telugu-speaking people of eastern India, we distinguish course by
# food _type_ rather than by time
#
# this means that lunch and dinner are not regarded as separate courses from each other
# but breakfast and dessert are
breakfast = "breakfast"
dessert = "dessert"

ALL = ItemList("snack")


def add(
    buy_price: int, item_kw: dict, culture: Optional[str], course: Optional[str] = None
):
    assert culture is None or isinstance(culture, str)
    assert course is None or isinstance(course, str)

    keywords = tuple(i for i in [culture, course] if i is not None)

    def _adder(*args, **kw) -> Item:
        return ALL.add(
            Item.new(
                Profile.new(*args, **kw),
                occludes_npc_spawn=False,
                buy_price=buy_price,
                keywords=keywords,
                **item_kw
            )
        )

    return _adder


BANH_MI = add(750, medium, vietnamese)("banh mi", "\xed", fg=IC.Fuchsia1)
BRATWURST = add(500, medium, german)("bratwurst", "\xe1", fg=IC.Red1)
BULGOGI = add(1200, medium, korean)("bulgogi", "\xf0", fg=IC.Red1)
BURGER = add(600, medium, american)("burger", "\xec", fg=IC.Red1)
CHICKEN_FETTUCINE_ALFREDO = add(850, medium, italian)(
    "chicken fettucine alfredo", "\xfb", fg=IC.Red1
)
CHICKEN_NUGGETS = add(400, medium, american)("chicken nuggets", "\x05", fg=IC.Sky1)
CHICKEN_TIKKA_MASALA = add(900, medium, indian)(
    "chicken tikka masala", "\xef", fg=IC.Red1
)
CHIPS = add(250, small, american)("chips", "\xe6", fg=IC.Red1)
CINNAMON_BUN = add(300, small, american, course=dessert)(
    "cinnamon bun", "\x9b", fg=IC.Sky0
)
CURRY = add(750, medium, indian)("curry", "\xea", fg=IC.Green1)
DONUT = add(175, small, american, course=dessert)("donut", "\x6f", fg=IC.Sky1)
FALAFEL = add(475, small, mediterranean)("falafel", "\xa6", fg=IC.Green1)
FISH = add(825, medium, None)("fish", "\xe0", fg=IC.Sky1)
FRIED_ICE_CREAM = add(550, small, chinese)("fried ice cream", "\x9e", fg=IC.Fuchsia1)
FRIES = add(325, small, american)("fries", "\x9f", fg=IC.Green1)
JELLY_DONUT = add(225, medium, american, course=dessert)(
    "jelly donut", "\x6f", fg=IC.Fuchsia1
)
JEON = add(875, medium, korean)("jeon", "\xec", fg=IC.Sky1)
KALBIJJIM = add(1450, medium, korean)("kalbijjim", "\xa8", fg=IC.Red0)
LOBSTER = add(1350, medium, None)("lobster", "\x9d", fg=IC.Red1)
MEAT_LOAF = add(850, medium, american)("meat loaf", "\xe4", fg=IC.Red1)
PAD_THAI = add(800, medium, thai)("pad thai", "\xab", fg=IC.Green1)
PEACH = add(125, small, fruit)("peach", "\x7f", fg=IC.Fuchsia1)
PET_FOOD = add(75, small, None)("pet food", "\x9e", fg=IC.Red0)
POMEGRANATE = add(140, small, fruit)("pomegranate", "\x7f", fg=IC.Fuchsia0)
POPCORN = add(175, small, american)("popcorn", "\x2a", fg=IC.Red1)
SALT = add(25, small, None)("salt", "\xf9", fg=IC.Mundane)
SHRIMP = add(250, small, None)("shrimp", "\x0f", fg=IC.Fuchsia1)
SOUP = add(800, medium, None)("soup", "\xf7", fg=IC.Sky0)
SPARE_RIB = add(1300, medium, american)("spare rib", "\xe2", fg=IC.Red1)
STEAK = add(1350, medium, american)("steak", "\x9c", fg=IC.Red1)
STRAWBERRY = add(50, small, fruit)("strawberry", "\x7f", fg=IC.Red1)
STROGANOFF = add(1100, medium, russian)("stroganoff", "\xf2", fg=IC.Red1)
TACOS = add(650, medium, mexican)("tacos", "\xee", fg=IC.Sky0)
TTEOKBOKKI = add(850, medium, korean)("tteokbokki", "\xaa", fg=IC.Red0)
TUNA = add(925, medium, None)("tuna", "\xe0", fg=IC.Fuchsia1)
WAFFLES = add(750, medium, american, breakfast)("waffles", "\xaf", fg=IC.Fuchsia1)
