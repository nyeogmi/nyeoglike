from typing import Optional

from .item import Item


class ItemList(object):
    def __init__(self):
        self._all = []

    # args to Item.new
    def add(self, item: Item) -> Item:
        self._all.append(item)
        return item
