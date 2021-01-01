from . import alcohol, furniture, snacks, technology
from unique.item.item_list import ItemList

ALL = ItemList()

for module in [alcohol, furniture, snacks, technology]:
    ALL.incorporate(module.ALL)
