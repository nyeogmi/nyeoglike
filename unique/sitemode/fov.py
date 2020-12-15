from math import sqrt
from typing import Callable, Dict, Optional

from ds.vecs import R2, V2

# Port of Eben Howard's implementation:
# http://www.roguebasin.com/index.php?title=FOV_using_recursive_shadowcasting_-_improved


def fov(
    has_wall: Callable[[V2], bool],
    view_rect: Optional[R2],
    start_xy: V2,
    radius: float,
) -> "Lightmap":
    fov = _FOV(has_wall, view_rect, start_xy, radius)
    fov._light()
    return Lightmap(fov._lightmap)


class Lightmap(object):
    def __init__(self, light_level: Dict[V2, float]):
        self._light_level = light_level

    def __getitem__(self, v: V2) -> float:
        assert isinstance(v, V2)
        return self._light_level.get(v, 0.0)


class _FOV(object):
    def __init__(
        self,
        has_wall: Callable[[V2], bool],
        view_rect: Optional[R2],
        start_xy: V2,
        radius: float,
    ):
        assert view_rect is None or isinstance(view_rect, R2)
        assert isinstance(start_xy, V2)
        assert isinstance(radius, float)

        self._has_wall: Callable[[V2], bool] = has_wall
        self._view_rect = view_rect
        self._start_xy = start_xy
        self._radius = radius
        self._lightmap = {}

    def _light(self):
        self._lightmap[self._start_xy] = 1.0
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            self._cast_light(1, 1.0, 0.0, 0, dx, dy, 0)
            self._cast_light(1, 1.0, 0.0, dx, 0, 0, dy)

    def _cast_light(
        self, row: int, start: float, end: float, xx: int, xy: int, yx: int, yy: int
    ):
        new_start = 0.0
        if start < end:
            return

        blocked = False
        distance = row - 1
        while True:
            distance += 1
            if distance > self._radius:
                break
            if blocked:
                break

            delta_y = -distance
            for delta_x in range(-distance, 0 + 1):
                current_x = self._start_xy.x + delta_x * xx + delta_y * xy
                current_y = self._start_xy.y + delta_x * yx + delta_y * yy
                current = V2.new(current_x, current_y)
                left_slope = (delta_x - 0.5) / (delta_y + 0.5)
                right_slope = (delta_x + 0.5) / (delta_y - 0.5)

                if (
                    self._view_rect and current not in self._view_rect
                ) or start < right_slope:
                    continue
                elif end > left_slope:
                    break

                if self._r_strat(delta_x, delta_y) <= self._radius:
                    bright = float(1 - (self._r_strat(delta_x, delta_y) / self._radius))
                    self._lightmap[current] = bright

                if blocked:
                    if self._has_wall(current):
                        new_start = right_slope
                        continue
                    else:
                        blocked = False
                        start = new_start
                else:
                    if self._has_wall(current) and distance < self._radius:
                        blocked = True
                        self._cast_light(
                            distance + 1, start, left_slope, xx, xy, yx, yy
                        )
                        new_start = right_slope

    def _r_strat(self, dx: float, dy: float):
        #  TODO: Use squared distances only?
        return sqrt(dx ** 2 + dy ** 2)
