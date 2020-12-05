from display import Drawer
from ds.vecs import V2, R2

from typing import Set, Optional, Protocol, runtime_checkable


class Scrollbar(object):
    def __init__(self, data, proto: "ScrollbarData"):
        assert isinstance(proto, ScrollbarData)
        self._data = data
        self._proto = proto

        self._scroll_i = 0
        self._i: Optional[int] = None

    @property
    def i(self):
        return self._i

    def up(self):
        self._i = 0 if self._i is None else self._i
        self._i -= 1
        self._wrap()

    def down(self):
        self._i = -1 if self._i is None else self._i
        self._i += 1
        self._wrap()

    def get_selected(self):
        if self._i is None:
            return None
        return self._data[self._i]

    def _wrap(self):
        if len(self._data) == 0: return
        if self._i is not None:
            self._i %= len(self._data)

    def fix_view(self, size: V2):
        if self._i is None or len(self._data) == 0:
            self._scroll_i = 0
            return

        scroll_top = 0
        item_top = 0
        for i in range(0, max(self._i, self._scroll_i)):
            height = self._proto.measure_item(self._data[i], size.x).y
            if i < self._scroll_i:
                scroll_top += height
            if i < self._i:
                item_top += height

        top = item_top - scroll_top
        height = self._proto.measure_item(self._data[self._i], size.x).y

        while top > size.y - height:
            self._scroll_i += 1
            top -= self._proto.measure_item(self._data[self._scroll_i], size.x).y

        while top < 0:
            self._scroll_i -= 1
            top += self._proto.measure_item(self._data[self._scroll_i + 1], size.x).y

        if self._scroll_i < 0:
            self._scroll_i = 0

    def draw(self, region: Drawer):
        region = region.copy().zeroed()

        self.fix_view(region.bounds.size - V2.new(2, 0))
        y = 0
        for i in range(self._scroll_i, len(self._data)):
            sz = self._proto.measure_item(self._data[i], region.bounds.size.x - 2)
            region2 = region.copy().goto(2, y).box(2 + sz.x, min(y + sz.y, region.bounds.size.y)).zeroed()
            self._proto.draw_item(self._data[i], region2, i == self._i)
            y += sz.y

            if y >= region.bounds.size.y: break


@runtime_checkable
class ScrollbarData(Protocol):
    def measure_item(self, item, width: int) -> V2:
        raise NotImplementedError

    def draw_item(self, item, draw: Drawer, selected: bool):
        raise NotImplementedError
