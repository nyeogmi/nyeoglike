from ds.code_registry import ref, ref_unnamed, ref_named
from ds.grid import Grid
from ds.vecs import V2, R2
from typing import NamedTuple, Optional, Union
from .palette import Colors, Color
import threading
from contextlib import contextmanager


class Cell(NamedTuple):
    bg: int
    fg: int
    character: str

    @classmethod
    def new(cls, bg: int, fg: int, character: str):
        assert isinstance(bg, int) and 0 <= bg < Colors.N
        assert isinstance(fg, int) and 0 <= fg < Colors.N
        assert isinstance(character, str)
        assert len(character) == 1
        # assert character in string.printable
        # assert character not in "\r\n\t"

        return Cell(
            bg=bg,
            fg=fg,
            character=character
        )


class Screen(object):
    def __init__(self, size: V2):
        self._cells: Grid[Cell] = Grid(R2.new(V2.zero(), size), default_cell, is_cell)
        self._cursor = V2.new(0, 0)
        self._lock = threading.Lock()

    @contextmanager
    def lock(self):
        with self._lock:
            yield

    def snapshot(self) -> "Screen":
        screen = Screen(self._cells.bounds.size)
        for v in self._cells.bounds:
            screen._cells[v] = self._cells[v]
        return screen

    @property
    def bounds(self) -> R2:
        return self._cells.bounds

    def draw(self) -> "Drawer":
        return Drawer(self, self.bounds, self.bounds, V2.zero(), self._cursor)

    def __getitem__(self, v2: V2) -> Cell:
        return self._cells[v2]


@ref
def default_cell(v2: V2) -> Cell:
    return Cell.new(
        bg=Colors.TermBG.color,
        fg=Colors.TermFG.color,
        character=" "
    )


@ref
def is_cell(c: Cell):
    assert isinstance(c, Cell)


def measure(s: str) -> V2:
    # Rely on the fact that measure() doesn't use the screen if actually_put is false
    return Drawer(None, None, None, V2.zero(), V2.zero()).measure(s, wrap=False)


class Drawer(object):
    def __init__(self, screen: Optional[Screen], bounds: Optional[R2], actual_bounds: Optional[R2], offset: V2, cursor: V2):
        assert screen is None or isinstance(screen, Screen)
        assert bounds is None or isinstance(bounds, R2)
        assert actual_bounds is None or isinstance(actual_bounds, R2)
        assert isinstance(offset, V2)
        assert isinstance(cursor, V2)

        self._screen = screen
        self._bounds = bounds  # this is always set if screen is set
        self._actual_bounds = actual_bounds
        self._offset = offset
        self._xy = cursor

        self._fg: Optional[Color] = None
        self._bg: Optional[Color] = None

    @property
    def xy(self):
        return self._xy

    @property
    def bounds(self):
        return self._bounds

    def copy(self) -> "Drawer":
        d = Drawer(self._screen, self._bounds, self._actual_bounds, self._offset, self._xy)
        d._fg = self._fg
        d._bg = self._bg
        return d

    def fg(self, fg: Optional[Color]) -> "Drawer":
        assert fg is None or isinstance(fg, Color)
        self._fg = fg
        return self

    def bg(self, bg: Optional[Color]) -> "Drawer":
        assert bg is None or isinstance(bg, Color)
        self._bg = bg
        return self

    def zeroed(self) -> "Drawer":
        return self.offset_v2(-self._bounds.top)

    def offset(self, xv: Union[V2, int], y: Optional[int] = None) -> "Drawer":
        if y is None:
            assert isinstance(xv, V2)
            return self.offset_v2(xv)
        else:
            assert isinstance(xv, int)
            assert isinstance(y, int)
            return self.offset_xy(xv, y)

    def offset_xy(self, x: int, y: int) -> "Drawer":
        return self.offset_v2(V2.new(x, y))

    def offset_v2(self, v2: V2) -> "Drawer":
        self._bounds = R2.new(self._bounds.top + v2, self._bounds.size)
        self._actual_bounds = R2.new(self._actual_bounds.top + v2, self._actual_bounds.size)
        self._offset = self._offset - v2
        self._xy -= v2
        return self

    def expand(self, xv: Union[V2, int], y: Optional[int] = None) -> "Drawer":
        if y is None:
            assert isinstance(xv, V2)
            return self.expand_v2(xv)
        else:
            assert isinstance(xv, int)
            assert isinstance(y, int)
            return self.expand_xy(xv, y)

    def expand_xy(self, x: int, y: int) -> "Drawer":
        return self.expand_v2(V2.new(x, y))

    def expand_v2(self, v2: V2) -> "Drawer":
        self._bounds = self._bounds.expand(v2)
        return self

    def box(self, xv: Union[V2, int], y: Optional[int] = None) -> "Drawer":
        if y is None:
            assert isinstance(xv, V2)
            return self.box_v2(xv)
        else:
            assert isinstance(xv, int)
            assert isinstance(y, int)
            return self.box_xy(xv, y)

    def box_xy(self, x: int, y: int) -> "Drawer":
        return self.box_v2(V2.new(x, y))

    def box_v2(self, v: V2) -> "Drawer":
        assert isinstance(v, V2)

        bounds2 = self._xy.to(v)
        assert self._bounds.contains(bounds2)
        self._bounds = bounds2

        return self

    def goto(self, xv: Union[V2, int], y: Optional[int] = None) -> "Drawer":
        if y is None:
            assert isinstance(xv, V2)
            return self.goto_v2(xv)
        else:
            assert isinstance(xv, int)
            assert isinstance(y, int)
            return self.goto_xy(xv, y)

    def goto_xy(self, x: int, y: int) -> "Drawer":
        return self.goto_v2(V2.new(x, y))

    def goto_v2(self, v: V2) -> "Drawer":
        assert isinstance(v, V2)

        self._xy = v
        return self

    def puts(self, s: str, wrap: bool = False) -> "Drawer":
        assert isinstance(s, str)
        assert isinstance(wrap, bool)

        self._puts(s, wrap, actually_put=True)
        return self

    def putdw(self, i: int) -> "Drawer":
        assert isinstance(i, int)

        if i == -1:  # blank double wide
            self.puts("  ", wrap=False)
            return self

        assert i >= 0

        # DW index
        dw_ix = 256 + i * 2
        self.puts(chr(dw_ix) + chr(dw_ix + 1), wrap=False)
        return self

    def fillc(self, c: str) -> "Drawer":  # TODO: Fill DW?
        assert isinstance(c, str)
        assert len(c) == 1
        old_xy = self._xy
        for i in self._bounds:
            self.goto(i).puts(c, wrap=False)
        self.goto(old_xy)
        return self

    def measure(self, s: str, wrap: bool = False):
        assert isinstance(s, str)
        assert isinstance(wrap, bool)

        new_xy = self._puts(s, wrap, actually_put=False)
        return new_xy - self._xy

    def _puts(self, s: str, wrap: bool, actually_put: bool) -> V2:
        assert isinstance(s, str)
        assert isinstance(wrap, bool)
        assert isinstance(actually_put, bool)

        if actually_put:
            assert self._screen is not None

        start_xy = self._xy
        new_xy = self._xy
        just_wrapped = False

        if wrap:
            # count the characters until the next break for each word
            chars_to_next_break = [0 for c in s]
            last_break = len(s)
            for i in range(len(s) - 1, -1, -1):  # indices in s in reverse
                if s[i] in "\r\n ":
                    last_break = i
                chars_to_next_break[i] = last_break - i

            # count the chars in each word for each word
            chars_in_word = [0 for c in s]
            for i, n in enumerate(chars_to_next_break):
                if chars_to_next_break[i] == 0:
                    chars_in_word[i] = 0
                else:
                    chars_in_word[i] = max(0 if i == 0 else chars_in_word[i - 1], chars_to_next_break[i])
            print(s, chars_in_word)

        for i, c in enumerate(s):
            if c == "\r":
                just_wrapped = False
                new_xy = V2.new(start_xy.x, new_xy.y)
            elif c == "\n":
                just_wrapped = True
                new_xy = V2.new(start_xy.x, new_xy.y + 1)
            elif c == " " and just_wrapped: # collapse one space right after wrapping
                just_wrapped = False
                continue
            else:
                if (
                    wrap and
                    chars_in_word[i] < self.bounds.size.x - start_xy.x and
                    chars_to_next_break[i] > self.bounds.bot_exclusive.x - new_xy.x
                ):
                    new_xy = V2.new(start_xy.x, new_xy.y + 1)

                # if it's a space and the next word will wrap, wrap now
                if (
                    wrap and
                    c == " " and i < len(s) - 1 and
                    chars_in_word[i + 1] < self.bounds.size.x - start_xy.x and
                    chars_to_next_break[i + 1] > self.bounds.bot_exclusive.x - new_xy.x
                ):
                    new_xy = V2.new(start_xy.x, new_xy.y + 1)
                    just_wrapped = True
                    continue

                just_wrapped = False
                if actually_put and new_xy in self._bounds and new_xy in self._actual_bounds:
                    old_cell = self._screen._cells[new_xy + self._offset]
                    new_cell = self._putc_of(old_cell, c)
                    self._screen._cells[new_xy + self._offset] = new_cell

                new_xy_1 = V2.new(new_xy.x + 1, new_xy.y)
                new_xy_2 = V2.new(start_xy.x, new_xy.y + 1)  # try a newline

                if wrap and self._bounds:
                    if new_xy_1 in self._bounds:
                        new_xy = new_xy_1
                    elif new_xy_2 in self._bounds:
                        just_wrapped = True
                        new_xy = new_xy_2
                    else:
                        new_xy = new_xy_1
                else:
                    # ignore newlines that would be forced
                    new_xy = new_xy_1

        if actually_put:
            self._xy = new_xy

        return new_xy

    def clear(self) -> "Drawer":
        assert self._screen is not None
        self._screen._cells.delete_region(self._bounds)
        return self

    def _putc_of(self, old: Cell, new_char: str) -> Cell:
        assert isinstance(old, Cell)
        assert isinstance(new_char, str) and len(new_char) == 1

        return Cell.new(
            bg=self._bg.color if self._bg is not None else old.bg,
            fg=self._fg.color if self._fg is not None else old.fg,
            character=new_char
        )

    def etch(self, double=False) -> "Drawer":
        from . import boxart
        boxart.draw(self, self._bounds, double=double)
        return self

    def fade(self):
        old_xy = self._xy
        for i in self._bounds:
            self.goto(i).fadec()
        self.goto(old_xy)
        return self

    def fadec(self):
        if not (self._xy in self._bounds and self._xy in self._actual_bounds):
            return

        old = self._screen._cells[self._xy + self._offset]
        self._screen._cells[self._xy + self._offset] = Cell.new(
            bg=Colors.FadeBG.color,
            fg=Colors.FadeFG.color,
            character=old.character,
        )
