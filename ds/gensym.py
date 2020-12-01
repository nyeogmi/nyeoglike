from typing import NamedTuple


class Sym(NamedTuple):
    prefix: str
    ix: int

    def __str__(self):
        return ".".join([self.prefix, str(self.ix)])


class Gensym(object):
    def __init__(self, prefix):
        self._prefix = prefix
        self._number = 0

    def gen(self) -> Sym:
        n = self._number
        self._number += 1
        return Sym(self._prefix, n)


class FastGensym(object):
    def __init__(self):
        self._number = 0

    def gen(self) -> int:
        n = self._number
        self._number += 1
        return n

    def ungen(self):
        self._number -= 1
        return self._number