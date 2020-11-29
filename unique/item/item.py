from ds.code_registry import Ref, ref_named, singleton
from typing import NamedTuple, Optional, Protocol, runtime_checkable


@runtime_checkable
class ItemData(Protocol):
    def tile(self) -> "Tile":
        raise NotImplementedError()

    def fixed_in_place(self) -> bool:
        raise NotImplementedError()


class Item(NamedTuple):
    data: Ref["ItemData"]
    n: int
    # TODO: Custom color?
    # TODO: Unique handle?

    def tile(self) -> "Tile":
        return self.data.resolve().tile()

    @classmethod
    def new(cls, data: Ref["ItemData"], n: int):
        assert isinstance(data, Ref) and isinstance(data.resolve(), ItemData)
        assert isinstance(n, int)

        return Item(data, n)


class Tile(NamedTuple):
    s: str
    bg: Optional[int]
    fg: Optional[int]

    @classmethod
    def new(cls, s: str, bg: Optional[int] = None, fg: Optional[int] = None):
        assert isinstance(s, str) and len(s) == 1
        assert bg is None or isinstance(bg, int)
        assert fg is None or isinstance(fg, int)
        return Tile(s, bg, fg)
