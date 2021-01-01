from typing import Iterable, Optional, Tuple

from .item import Item


class ItemList(object):
    def __init__(self, *extra_keywords: str):
        assert isinstance(extra_keywords, tuple)

        self._all = []
        self._extra_keywords = extra_keywords

        self._by_keywords = {}

    def add(self, item: Item) -> Item:
        item = item.plus_keywords(self._extra_keywords)
        ix = len(self._all)
        self._all.append(item)

        for kws in _powerset(item.keywords):
            self._by_keywords[kws] = self._by_keywords.get(kws, [])
            self._by_keywords[kws].append(ix)

        return item

    def get_all_by_keywords(self, *keywords: str) -> Iterable[Item]:
        assert all(isinstance(kw, str) for kw in keywords)
        for i in self._by_keywords[tuple(sorted({*keywords}))]:
            yield self._all[i]

    def incorporate(self, item_list: "ItemList"):
        for item in item_list._all:
            self.add(item)


def _powerset(keywords: Tuple[str, ...]):
    if len(keywords) == 0:
        yield ()
        return

    kw, kws = keywords[0], keywords[1:]
    for kw_item in _powerset(kws):
        yield kw_item

    for kw_item in _powerset(kws):
        yield (kw, *kw_item)
