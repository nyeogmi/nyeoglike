from . import alcohol, furniture, junk, snacks, technology
from unique.item.item_list import ItemList

ALL = ItemList()

for module in [alcohol, furniture, junk, snacks, technology]:
    ALL.incorporate(module.ALL)
