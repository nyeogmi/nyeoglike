from .item import Item, ItemData, Tile
from ds.code_registry import Ref, ref_named, singleton


@ref_named("item.Bed")
@singleton
class _Bed(ItemData):
    def tile(self) -> Tile: return Tile.new(s="\xe9", fg=15)
    def fixed_in_place(self) -> bool: return True


def bed() -> Item:
    return Item.new(_Bed, 1)


@ref_named("item.Table")
@singleton
class _Table(ItemData):
    def tile(self) -> Tile: return Tile.new(s="\xd1", fg=15)
    def fixed_in_place(self) -> bool: return True


def table() -> Item:
    return Item.new(_Table, 1)


@ref_named("item.Snack")
@singleton
class _Snack(ItemData):
    def tile(self) -> Tile: return Tile.new(s="\xf6", fg=11)


def snack() -> Item:
    # Musubi
    return Item.new(_Snack, 2)

LEVEL_CODES = {
    "b": bed,
    "t": table,
    "s": snack,
}
