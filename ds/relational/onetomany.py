from typing import Dict, Generic, Iterator, List, Optional, Tuple, TypeVar

A = TypeVar("A")
B = TypeVar("B")


class OneToMany(Generic[A, B]):
    def __init__(self):
        self.a_to_bs: Dict[A, List[B]] = dict()
        self.b_to_a: Dict[B, A] = dict()

    def add(self, a: A, b: B):
        assert a is not None
        assert b is not None

        old_a = self.get_a(b)

        if old_a: self.remove(old_a, b)

        self.a_to_bs[a] = self.a_to_bs.get(a, [])
        self.a_to_bs[a].append(b)
        self.b_to_a[b] = a

    def remove(self, a: A, b: B):
        if a in self.a_to_bs and b in self.a_to_bs[a]:
            self.a_to_bs[a].remove(b)
            if len(self.a_to_bs[a]) == 0:
                del self.a_to_bs[a]

            del self.b_to_a[b]

    def has(self, a: A, b: B):
        return self.b_to_a.get(b) == a

    def remove_a(self, a: A):
        if a not in self.a_to_bs: return
        bs = self.a_to_bs.pop(a)
        for b in bs:
            self.b_to_a.pop(b)

    def remove_b(self, b: B):
        if b not in self.b_to_a: return
        a = self.b_to_a.pop(b)
        self.a_to_bs[a].remove(b)

        if len(self.a_to_bs[a]) == 0:
            del self.a_to_bs[a]

    def get_bs(self, a: A) -> Iterator[B]:
        for b in self.a_to_bs.get(a, []):
            yield b

    def get_a(self, b: B) -> Optional[A]:
        return self.b_to_a.get(b)

    def all(self) -> Iterator[Tuple[A, B]]:
        for a, bs in self.a_to_bs.items():
            for b in bs:
                yield a, b

    def all_as(self) -> Iterator[A]:
        for a, bs in self.a_to_bs.items():
            yield a

    def all_bs(self) -> Iterator[B]:
        for b, a in self.b_to_a.items():
            yield b