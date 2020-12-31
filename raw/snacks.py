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

# much like the Telugu-speaking people of eastern India, we distinguish course by
# food _type_ rather than by time
#
# this means that lunch and dinner are not regarded as separate courses from each other
# but breakfast and dessert are
breakfast = "breakfast"
dessert = "dessert"

ALL = ItemList()


def add(item_kw: dict, culture: Optional[str], course: Optional[str] = None):
    assert culture is None or isinstance(culture, str)
    assert course is None or isinstance(course, str)

    keywords = tuple(i for i in [culture, course] if i is not None)

    def _adder(*args, **kw) -> Item:
        return ALL.add(Item.new(Profile.new(*args, **kw), keywords=keywords, **item_kw))

    return _adder


BANH_MI = add(medium, vietnamese)("banh mi", "\xed", fg=IC.Fuchsia1)
BRATWURST = add(medium, german)("bratwurst", "\xe1", fg=IC.Red1)
BULGOGI = add(medium, korean)("bulgogi", "\xf0", fg=IC.Red1)
BURGER = add(medium, american)("burger", "\xec", fg=IC.Red1)
CHICKEN_FETTUCINE_ALFREDO = add(medium, italian)(
    "chicken fettucine alfredo", "\xfb", fg=IC.Red1
)
CHICKEN_NUGGETS = add(medium, american)("chicken nuggets", "\x05", fg=IC.Sky1)
CHICKEN_TIKKA_MASALA = add(medium, indian)("chicken tikka masala", "\xef", fg=IC.Red1)
CHIPS = add(small, american)("chips", "\xe6", fg=IC.Red1)
CINNAMON_BUN = add(small, american, course=dessert)("cinnamon bun", "\x9b", fg=IC.Sky0)
CURRY = add(medium, indian)("curry", "\xea", fg=IC.Green1)
DONUT = add(small, american, course=dessert)("donut", "\x6f", fg=IC.Sky1)
FALAFEL = add(small, mediterranean)("falafel", "\xa6", fg=IC.Green1)
FISH = add(medium, None)("fish", "\xe0", fg=IC.Sky1)
FRIED_ICE_CREAM = add(small, chinese)("fried ice cream", "\x9e", fg=IC.Fuchsia1)
FRIES = add(small, american)("fries", "\x9f", fg=IC.Green1)
JELLY_DONUT = add(medium, american, course=dessert)(
    "jelly donut", "\x6f", fg=IC.Fuchsia1
)
JEON = add(medium, korean)("jeon", "\xec", fg=IC.Sky1)
KALBIJJIM = add(medium, korean)("kalbijjim", "\xa8", fg=IC.Red0)
LOBSTER = add(medium, None)("lobster", "\x9d", fg=IC.Red1)
MEAT_LOAF = add(medium, american)("meat loaf", "\xe4", fg=IC.Red1)
PAD_THAI = add(medium, thai)("pad thai", "\xab", fg=IC.Green1)
PEACH = add(small, fruit)("peach", "\x7f", fg=IC.Fuchsia1)
PET_FOOD = add(small, None)("pet food", "\x9e", fg=IC.Red0)
POMEGRANATE = add(small, fruit)("pomegranate", "\x7f", fg=IC.Fuchsia0)
POPCORN = add(small, american)("popcorn", "\x2a", fg=IC.Red1)
SALT = add(small, None)("salt", "\xf9", fg=IC.Mundane)
SHRIMP = add(small, None)("shrimp", "\x0f", fg=IC.Fuchsia1)
SOUP = add(medium, None)("soup", "\xf7", fg=IC.Sky0)
SPARE_RIB = add(medium, american)("spare rib", "\xe2", fg=IC.Red1)
STEAK = add(medium, american)("steak", "\x9c", fg=IC.Red1)
STRAWBERRY = add(small, fruit)("strawberry", "\x7f", fg=IC.Red1)
STROGANOFF = add(medium, russian)("stroganoff", "\xf2", fg=IC.Red1)
TACOS = add(medium, mexican)("tacos", "\xee", fg=IC.Sky0)
TTEOKBOKKI = add(medium, korean)("tteokbokki", "\xaa", fg=IC.Red0)
TUNA = add(medium, None)("tuna", "\xe0", fg=IC.Fuchsia1)
WAFFLES = add(medium, american, breakfast)("waffles", "\xaf", fg=IC.Fuchsia1)
