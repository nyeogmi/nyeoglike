from typing import Dict
from .item import Item, Resource


class Inventory(object):
    def __init__(self):
        self.resources: Dict[Resource, int] = {}
        # self.earmarked_items: Dict[<quest>, Item] = []

        # TODO:
        # self.blood = 0  # Vampires need this to live
        # self.spark = 0  # Vampires need this to control minds

    def add(self, item: Item):
        assert isinstance(item, Item)
        # TODO: Allow quests to earmark this before I go on

        for c in item.contributions:
            self.resources[c.resource] = self.resources.get(c.resource, 0)
            self.resources[c.resource] += c.n

        """
        if self.resources[Resource.Blood] > 100:
            self.resources[Resource.Blood] = 100

        if self.resources[Resource.Spark] > 100:
            self.resources[Resource.Spark] = 100
        """

    def get(self, resource: Resource) -> int:
        return self.resources.get(resource, 0)

    def take(self, resource: Resource, n: int) -> bool:
        assert isinstance(n, int)
        if n == 0:
            return True

        if n > self.resources.get(resource, 0):
            return False

        self.resources[resource] -= n
        if self.resources[resource] == 0:
            del self.resources[resource]