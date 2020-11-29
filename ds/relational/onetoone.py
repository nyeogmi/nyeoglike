from typing import Dict, Generic, Iterator, Optional, Tuple, TypeVar

A = TypeVar("A")
B = TypeVar("B")


class OneToOne(Generic[A, B]):
    def __init__(self):
        self.a_to_b: Dict[A, B] = dict()
        self.b_to_a: Dict[B, A] = dict()

    def add(self, a: A, b: B):
        assert a is not None
        assert b is not None

        old_a = self.get_a(b)
        old_b = self.get_b(a)

        if old_a: self.remove(old_a, b)
        if old_b: self.remove(old_b, a)

        self.a_to_b[a] = b
        self.b_to_a[b] = a

    def remove(self, a: A, b: B):
        if self.a_to_b.get(a) == b:
            del self.a_to_b[a]
            del self.b_to_a[b]

    def has(self, a: A, b: B):
        return self.a_to_b.get(a) == b

    def remove_a(self, a: A):
        if a not in self.a_to_b: return
        b = self.a_to_b.pop(a)
        self.b_to_a.pop(b)

    def remove_b(self, b: B):
        if b not in self.b_to_a: return
        a = self.b_to_a.pop(b)
        self.a_to_b.pop(a)

    def get_b(self, a: A) -> Optional[B]:
        return self.a_to_b.get(a)

    def get_a(self, b: B) -> Optional[A]:
        return self.b_to_a.get(b)

    def all(self) -> Iterator[Tuple[A, B]]:
        for a, b in self.a_to_b.items():
            yield a, b

    def all_as(self) -> Iterator[A]:
        for a, b in self.a_to_b.items():
            yield a

    def all_bs(self) -> Iterator[B]:
        for b, a in self.b_to_a.items():
            yield b
