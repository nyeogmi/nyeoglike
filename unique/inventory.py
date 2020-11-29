from typing import Dict, List
from ds.code_registry import Ref
from .item import Item, ItemData


class Slot(object):
    def __init__(self):
        # TODO: Earmark items for quests
        self.n = 0



class Inventory(object):
    def __init__(self):
        # Measured in cents.
        self.money: int = 0

        self.common_items: Dict[Ref[ItemData], Slot] = {}
        # self.unique_items: List[Item] = []

        # TODO:
        # self.blood = 0  # Vampires need this to live
        # self.spark = 0  # Vampires need this to control minds

    def add(self, item: Item):
        self.common_items[item.data] = self.common_items.get(item.data, Slot())
        self.common_items[item.data].n += item.n

    def take(self, kind: Ref[ItemData], n: ):