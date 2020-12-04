from typing import NamedTuple, Iterator, Union


class V2(NamedTuple):
    x: int
    y: int

    @classmethod
    def new(cls, x: int, y: int) -> "V2":
        assert isinstance(x, int)
        assert isinstance(y, int)

        return V2(x, y)

    @classmethod
    def zero(cls) -> "V2":
        return V2.new(0, 0)

    def is_unsigned(self) -> bool:
        return self.x >= 0 and self.y >= 0

    def to(self, other: "V2") -> "R2":
        assert isinstance(other, V2)
        return R2.new_4i(self.x, self.y, other.x, other.y)

    def sized(self, other: "V2") -> "R2":
        assert isinstance(other, V2)
        return R2.new_4i(self.x, self.y, self.x + other.x, self.y + other.y)

    def __add__(self, other: "V2") -> "V2":
        assert isinstance(other, V2)
        return V2.new(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "V2") -> "V2":
        assert isinstance(other, V2)
        return V2.new(self.x - other.x, self.y - other.y)

    def __mul__(self, other: Union[int, "V2"]) -> "V2":
        assert isinstance(other, (int, V2))
        if isinstance(other, int):
            return V2.new(self.x * other, self.y * other)
        else:
            return V2.new(self.x * other.x, self.y * other.y)

    def __neg__(self) -> "V2":
        return V2.new(-self.x, -self.y)

    def manhattan(self, other: "V2") -> int:
        assert isinstance(other, V2)
        return abs(self.x - other.x) + abs(self.y - other.y)

    def neighbors(self) -> Iterator["V2"]:
        for y in range(self.y - 1, self.y + 2):
            for x in range(self.x - 1, self.x + 2):
                if x == self.x and y == self.y: continue
                yield V2.new(x, y)


class R2(NamedTuple):
    top: V2
    size: V2

    @classmethod
    def new(cls, top: V2, size: V2):
        assert isinstance(top, V2)
        assert isinstance(size, V2) and size.is_unsigned()

        return R2(top, size)

    @classmethod
    def new_4i(cls, x0: int, y0: int, x1: int, y1: int):
        x_top = min(x0, x1)
        y_top = min(y0, y1)
        x_bot = max(x0, x1)
        y_bot = max(y0, y1)

        return R2.new(V2(x_top, y_top), V2(x_bot - x_top, y_bot - y_top))

    @property
    def bot_inclusive(self) -> V2:
        assert self.size.x > 0 and self.size.y > 0
        return self.top + self.size - V2.new(1, 1)

    @property
    def bot_exclusive(self) -> V2:
        return self.top + self.size

    def expand(self, amt: "V2"):
        return R2.new(self.top - amt, self.size + amt * 2)

    def zeroed(self) -> "R2":
        return R2(V2.zero(), self.size)

    def __iter__(self) -> Iterator["V2"]:
        for y in range(self.size.y):
            for x in range(self.size.x):
                yield V2.new(self.top.x + x, self.top.y + y)

    def __contains__(self, v: V2):
        assert isinstance(v, V2)
        return (
            self.top.x <= v.x < self.top.x + self.size.x and
            self.top.y <= v.y < self.top.y + self.size.y
        )

    def contains(self, other: "R2") -> bool:
        assert isinstance(other, R2)
        return other.top in self and other.bot_inclusive in self