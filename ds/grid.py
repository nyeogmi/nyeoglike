from typing import Callable, Generic, Optional, TypeVar

from ds.code_registry import Ref
from .vecs import R2, V2

T = TypeVar("T")


class Grid(Generic[T]):
    def __init__(
        self,
        bounds: R2,
        default: Ref[Callable[[V2], T]],
        typecheck: Optional[Ref[Callable[[T], None]]],
    ):
        assert isinstance(bounds, R2)
        assert isinstance(default, Ref)
        assert isinstance(typecheck, Ref)

        self._default = default
        self._typecheck = typecheck

        self._bounds = R2.new(V2.zero(), V2.zero())
        self._grid = [[]]

        self.resize(bounds)

    @property
    def bounds(self):
        return self._bounds

    def resize(self, bounds: R2):
        assert isinstance(bounds, R2)

        old_bounds = self._bounds
        new_bounds = bounds

        default = self._default.resolve()

        old_grid = self._grid
        new_grid = [[None for y in range(new_bounds.size.y)] for x in range(new_bounds.size.x)]

        for xy in new_bounds:
            x_, y_ = xy - new_bounds.top
            if xy in old_bounds:
                new_grid[x_][y_] = old_grid[x_][y_]
            else:
                new_grid[x_][y_] = default(xy)

        self._bounds = bounds
        self._grid = new_grid

    def __delitem__(self, key: V2):
        assert isinstance(key, V2)
        assert key in self._bounds
        self[key] = self._default.resolve()(key)

    def __getitem__(self, key: V2):
        assert isinstance(key, V2)
        assert key in self._bounds
        x, y = key - self._bounds.top
        return self._grid[x][y]

    def __setitem__(self, key: V2, value: T):
        assert isinstance(key, V2)
        assert key in self._bounds
        assert self._typecheck.resolve()(value) is None
        x, y = key - self._bounds.top
        self._grid[x][y] = value

    def delete_region(self, region: R2):
        for v in region: del self[v]

    def get_region(self, region: R2) -> "Grid[T]":
        assert self.bounds.contains(region)
        grid: Grid[T] = Grid(region, self._default, self._typecheck)

        for v in self.bounds:
            grid[v] = self[v]

        return grid

    def set_region(self, region: R2, value_fn: Callable[[V2], T]):
        assert self.bounds.contains(region)
        for v in self.bounds:
            self[v] = value_fn(v)
