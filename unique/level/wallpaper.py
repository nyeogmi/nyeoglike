from ds.vecs import V2
from display import Color, Colors, WallColors
from typing import List, NamedTuple, Set, Tuple, Union, Iterable
import random


class WallTile(NamedTuple):
    display: Union[str, int]
    fg: Color
    flip: bool

    @classmethod
    def new(cls, display: Union[str, int], fg: Color, flip: bool = False):
        assert isinstance(display, (str, int))
        assert isinstance(fg, Color)
        assert isinstance(flip, bool)

        if isinstance(display, str):
            assert len(display) == 2
        elif isinstance(display, int):
            pass

        return WallTile(display, fg, flip)

    @classmethod
    def default(cls) -> "WallTile":
        return cls.new(display="\xb0\xb0", fg=Colors.WorldFG)

    @classmethod
    def generate_wallpaper(cls) -> "WallTile":
        # also includes stuccos
        disp, flip = random.choice(
            [
                ("\xb0\xb0", False),
                ("\xb1\xb1", False),
            ]
        )
        return WallTile.new(disp, random.choice(WallColors.ALL), flip)

    @classmethod
    def generate_paneling(cls) -> "WallTile":
        disp, flip = random.choice(
            [
                ("\xdb\xdb", False),
                ("\xdb\xdb", True),
                ("\xc4\xc4", True),
                ("\xcd\xcd", True),
                ("\xcb\xcb", True),
            ]
        )
        return WallTile.new(disp, random.choice(WallColors.COLORFUL), flip)

    @classmethod
    def generate_tile(cls) -> "WallTile":
        disp, flip = random.choice(
            [
                ("\xb2\xb2", False),
            ]
        )
        return WallTile.new(disp, random.choice(WallColors.COLORFUL), flip)

    @classmethod
    def generate_bathroom_tile(cls) -> "WallTile":
        disp, flip = random.choice(
            [
                ("\xb2\xb2", False),
            ]
        )
        return WallTile.new(disp, random.choice(WallColors.BANAL), flip)


class Wallpaper(object):
    def __init__(self, default: WallTile):
        assert isinstance(default, WallTile)

        self._default = default
        self._layers: List[Tuple[Set[V2], WallTile]] = []

    def set_default(self, default: WallTile):
        assert isinstance(default, WallTile)
        self._default = default

    @property
    def default(self):
        return self._default

    def add(self, layer: Iterable[V2], tile: WallTile):
        assert isinstance(layer, Iterable)
        assert isinstance(tile, WallTile)

        # merge layers w/ identical tiles
        for set_, wt in self._layers:
            if wt == tile:
                set_.update(layer)
                return

        else:
            self._layers.append((set(layer), tile))

    def get(self, v2: V2) -> WallTile:
        for vs, wt in self._layers:
            if v2 in vs:
                return wt

        return self._default
