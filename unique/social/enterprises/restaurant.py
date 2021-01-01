import random
from raw import ALL
from raw.snacks import CUISINES

from unique.item import Item
from typing import List, Set, Tuple


class Restaurant(object):
    def __init__(self, menu: "Menu"):
        assert isinstance(menu, Menu)

        self.menu = menu

    @classmethod
    def generate(cls):
        # TODO: Make it so duplicate restaurants of the same type are unlikely to be generated
        cuisine_type = random.choice(CUISINES)
        return Restaurant(menu=Menu.generate(cuisine_type))


class Menu(object):
    def __init__(self, items: Tuple[Item]):
        self.items = items

    @classmethod
    def generate(cls, cuisine_type: str) -> "Menu":
        snacks: Set[Item] = set()

        options_1 = list(ALL.get_all_by_keywords("snack", cuisine_type))
        options_2 = list(ALL.get_all_by_keywords("snack"))

        random.shuffle(options_1)
        random.shuffle(options_2)

        n_wanted = random.randint(5, 7)
        while any(options_1) and len(snacks) < n_wanted:
            snacks.add(options_1.pop())

        while any(options_2) and len(snacks) < n_wanted:
            snacks.add(options_2.pop())

        final_snacks = tuple(sorted(snacks, key=lambda i: i.profile.name))
        return Menu(final_snacks)
